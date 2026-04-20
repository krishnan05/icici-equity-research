import yfinance as yf
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from rich.console import Console
from rich.table import Table
from rich import box
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

FINBERT_MODEL = "ProsusAI/finbert"
DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")

RELEVANT_KEYWORDS = [
    "bank", "loan", "credit", "rate", "profit", "earnings",
    "revenue", "ebitda", "growth", "margin", "debt", "interest",
    "quarter", "results", "dividend", "guidance", "outlook",
    "acquisition", "merger", "capex", "cashflow", "upgrade",
    "downgrade", "target", "forecast", "beat", "miss",
    "investment", "shares", "stock", "market", "financial",
    "sales", "income", "loss", "gain", "expand", "launch"
]

# ── Load FinBERT once at module level ────────────────────────────────────────
_tokenizer = None
_model     = None

def load_finbert():
    global _tokenizer, _model
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL)
        _model     = AutoModelForSequenceClassification.from_pretrained(
                         FINBERT_MODEL).to(DEVICE)
        _model.eval()

def get_finbert_score(text):
    """
    FinBERT returns 3 classes: positive, negative, neutral
    We convert to a compound score: positive_prob - negative_prob
    Range: -1.0 (very negative) to +1.0 (very positive)
    """
    load_finbert()
    inputs = _tokenizer(
        text, return_tensors="pt",
        truncation=True, max_length=512,
        padding=True
    ).to(DEVICE)

    with torch.no_grad():
        outputs = _model(**inputs)
        probs   = torch.softmax(outputs.logits, dim=1)[0]

    # FinBERT label order: positive=0, negative=1, neutral=2
    positive = probs[0].item()
    negative = probs[1].item()
    neutral  = probs[2].item()

    compound = positive - negative  # -1 to +1
    label    = (
        "🟢 Positive" if compound >= 0.05  else
        "🔴 Negative" if compound <= -0.05 else
        "⚪ Neutral"
    )
    return round(compound, 3), label, positive, negative, neutral


def fetch_news(ticker, max_articles=20):
    t    = yf.Ticker(ticker)
    news = t.news or []
    articles = []
    for item in news[:max_articles]:
        content = item.get("content", {})
        title   = content.get("title") or item.get("title") or ""
        summary = content.get("summary") or item.get("summary") or ""
        if title:
            articles.append({
                "title":   title,
                "summary": summary[:300],
            })
    return articles


def is_relevant(text):
    return any(kw in text.lower() for kw in RELEVANT_KEYWORDS)


def score_sentiment(articles):
    scored = []
    for a in articles:
        text = a["title"] + " " + a["summary"]
        if not is_relevant(text):
            continue
        compound, label, pos, neg, neu = get_finbert_score(text)
        scored.append({
            "title":    a["title"][:75] + "..." if len(a["title"]) > 75
                        else a["title"],
            "score":    compound,
            "label":    label,
            "positive": round(pos, 3),
            "negative": round(neg, 3),
            "neutral":  round(neu, 3),
        })
    return scored


def aggregate_sentiment(scored):
    if not scored:
        return None
    scores   = [s["score"] for s in scored]
    avg      = round(sum(scores) / len(scores), 3)
    positive = sum(1 for s in scores if s >= 0.05)
    negative = sum(1 for s in scores if s <= -0.05)
    neutral  = len(scores) - positive - negative
    signal   = (
        "🐂 BULLISH  — Lean toward Bull case"  if avg >= 0.10 else
        "🐻 BEARISH  — Lean toward Bear case"  if avg <= -0.05 else
        "📊 NEUTRAL  — Stick with Base case"
    )
    return {
        "avg_score": avg,
        "positive":  positive,
        "negative":  negative,
        "neutral":   neutral,
        "total":     len(scored),
        "signal":    signal,
    }


def scenario_adjustment(avg_score):
    if avg_score >= 0.15:
        return +0.05, "Strong positive sentiment → +5% premium"
    elif avg_score >= 0.05:
        return +0.02, "Mild positive sentiment → +2% premium"
    elif avg_score <= -0.10:
        return -0.05, "Strong negative sentiment → -5% discount"
    elif avg_score <= -0.05:
        return -0.02, "Mild negative sentiment → -2% discount"
    else:
        return 0.00,  "Neutral sentiment → no adjustment"


def print_sentiment(ticker):
    from src.financial.scenarios import get_price_targets

    console = Console()
    console.print("\n[bold blue]━━━ FinBERT Sentiment Analysis ━━━[/bold blue]")
    console.print(f"[dim]Model: ProsusAI/finbert (financial domain BERT)[/dim]")
    console.print(f"[dim]Fetching and scoring news for {ticker}...[/dim]\n")

    articles = fetch_news(ticker)
    if not articles:
        console.print("[red]No news found.[/red]")
        return

    scored = score_sentiment(articles)
    if not scored:
        console.print("[yellow]No relevant articles found.[/yellow]")
        return

    # Article table
    t = Table(show_header=True, header_style="bold magenta",
              box=box.SIMPLE_HEAVY, show_lines=False)
    t.add_column("Headline",   width=55)
    t.add_column("Sentiment",  width=14, justify="center")
    t.add_column("Score",      width=8,  justify="right")
    t.add_column("+ve",        width=6,  justify="right")
    t.add_column("-ve",        width=6,  justify="right")

    for s in scored:
        color = ("green" if "Positive" in s["label"] else
                 "red"   if "Negative" in s["label"] else "white")
        t.add_row(
            f"[{color}]{s['title']}[/{color}]",
            s["label"],
            f"{s['score']:+.3f}",
            f"{s['positive']:.2f}",
            f"{s['negative']:.2f}",
        )
    console.print(t)

    agg      = aggregate_sentiment(scored)
    adj, adj_note = scenario_adjustment(agg["avg_score"])

    console.print("\n[bold cyan]━━━ Sentiment Summary ━━━[/bold cyan]")
    console.print(f"  Articles analysed : {agg['total']}")
    console.print(f"  🟢 Positive       : {agg['positive']}")
    console.print(f"  🔴 Negative       : {agg['negative']}")
    console.print(f"  ⚪ Neutral        : {agg['neutral']}")
    console.print(f"  Avg Score         : {agg['avg_score']:+.3f}")
    console.print(f"\n  Signal → [bold]{agg['signal']}[/bold]")

    try:
        targets     = get_price_targets(ticker)
        base_target = int(targets.loc["📊 Base", "Avg Target (₹)"])
    except Exception:
        base_target = 1000

    adjusted = round(base_target * (1 + adj))

    console.print(f"\n[bold cyan]━━━ Sentiment-Adjusted Price Target ━━━[/bold cyan]")
    console.print(f"  Base model target    : ₹{base_target:,}")
    console.print(f"  Sentiment adjustment : {adj*100:+.0f}%  ({adj_note})")
    console.print(f"  Adjusted target      : [bold green]₹{adjusted:,}[/bold green]")
    console.print(f"\n  [dim]FinBERT trained on 10,000+ financial documents — "
                  f"understands domain-specific language unlike generic NLP.[/dim]\n")


if __name__ == "__main__":
    print_sentiment("RELIANCE.NS")