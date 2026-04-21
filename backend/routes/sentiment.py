from fastapi import APIRouter
from src.ml.finbert import fetch_news, score_sentiment, aggregate_sentiment, scenario_adjustment
from src.financial.scenarios import get_price_targets

router = APIRouter()

@router.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):
    articles = fetch_news(ticker)
    scored   = score_sentiment(articles)
    agg      = aggregate_sentiment(scored)

    if not agg:
        return {"error": "No relevant news found"}

    adj, note = scenario_adjustment(agg["avg_score"])

    try:
        targets     = get_price_targets(ticker)
        base_target = int(targets.loc["📊 Base", "Avg Target (₹)"])
    except:
        base_target = 1000

    return {
        "articles":         scored,
        "summary":          agg,
        "adjustment":       adj,
        "note":             note,
        "base_target":      base_target,
        "adjusted_target":  round(base_target * (1 + adj)),
    }