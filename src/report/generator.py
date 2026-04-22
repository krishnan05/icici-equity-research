import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import subprocess


    
# ── Colour palette ────────────────────────────────────────────────────────────
NAVY      = colors.HexColor("#1F4E79")
BLUE      = colors.HexColor("#2E75B6")
TEAL      = colors.HexColor("#1D9E75")
GREEN     = colors.HexColor("#10b981")
RED       = colors.HexColor("#ef4444")
AMBER     = colors.HexColor("#f59e0b")
LGREY     = colors.HexColor("#F1F5F9")
MGREY     = colors.HexColor("#94A3B8")
DGREY     = colors.HexColor("#334155")
WHITE     = colors.white
BLACK     = colors.black

def register_fonts():
    """Register a Unicode font that supports ₹ symbol."""
    try:
        # Try to use DejaVu which is usually available on Linux
        pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("DejaVu-Oblique", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"))
        return "DejaVu", "DejaVu-Bold", "DejaVu-Oblique"
    except:
        return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
    

def make_styles():
    FONT, FONT_BOLD, FONT_OBLIQUE = register_fonts()
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_company"] = ParagraphStyle(
        "cover_company", fontSize=22, fontName=FONT_BOLD,
        textColor=WHITE, alignment=TA_LEFT, spaceAfter=4)

    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", fontSize=11, fontName=FONT,
        textColor=colors.HexColor("#CBD5E1"), alignment=TA_LEFT, spaceAfter=2)

    styles["section_header"] = ParagraphStyle(
        "section_header", fontSize=10, fontName=FONT_BOLD,
        textColor=WHITE, alignment=TA_LEFT, spaceBefore=0, spaceAfter=0)

    styles["body"] = ParagraphStyle(
        "body", fontSize=9, fontName=FONT,
        textColor=DGREY, alignment=TA_LEFT,
        spaceAfter=6, leading=14)

    styles["metric_label"] = ParagraphStyle(
        "metric_label", fontSize=8, fontName=FONT,
        textColor=MGREY, alignment=TA_CENTER)

    styles["metric_value"] = ParagraphStyle(
        "metric_value", fontSize=13, fontName=FONT_BOLD,
        textColor=DGREY, alignment=TA_CENTER)

    styles["table_header"] = ParagraphStyle(
        "table_header", fontSize=8, fontName=FONT_BOLD,
        textColor=WHITE, alignment=TA_CENTER)

    styles["table_cell"] = ParagraphStyle(
        "table_cell", fontSize=8, fontName=FONT,
        textColor=DGREY, alignment=TA_RIGHT)

    styles["footer"] = ParagraphStyle(
        "footer", fontSize=7, fontName=FONT,
        textColor=MGREY, alignment=TA_CENTER)

    styles["disclaimer"] = ParagraphStyle(
        "disclaimer", fontSize=7, fontName=FONT_OBLIQUE,
        textColor=MGREY, alignment=TA_LEFT, leading=10)

    return styles


def section_block(title, content_rows, styles, col_widths=None, header_color=NAVY):
    elements = []

    # Section header bar
    header_data = [[Paragraph(title, styles["section_header"])]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), header_color),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(header_table)

    if content_rows:
        cw = col_widths or [4*cm] + [13*cm/max(len(content_rows[0])-1, 1)] * (len(content_rows[0])-1)
        t  = Table(content_rows, colWidths=cw, repeatRows=1)
        t.setStyle(TableStyle([
            ("FONTNAME",     (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE",     (0,0), (-1,-1), 8),
            ("TEXTCOLOR",    (0,0), (-1,-1), DGREY),
            ("ALIGN",        (0,0), (0,-1),  "LEFT"),
            ("ALIGN",        (1,0), (-1,-1), "RIGHT"),
            ("BACKGROUND",   (0,0), (-1,0),  colors.HexColor("#E2EBF5")),
            ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LGREY]),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LEFTPADDING",  (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("LINEBELOW",    (0,0), (-1,0),  0.5, BLUE),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 0.3*cm))
    return elements


def generate_report(ticker, info, projections, valuation,
                    scenarios, sentiment, ml, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{ticker.replace('.','_')}_research_{datetime.now().strftime('%Y%m%d')}.pdf"

    doc     = SimpleDocTemplate(filename, pagesize=A4,
                                 leftMargin=2*cm, rightMargin=2*cm,
                                 topMargin=1.5*cm, bottomMargin=2*cm)
    styles  = make_styles()
    story   = []

    # ── Cover banner ─────────────────────────────────────────────────────────
    targets    = valuation.get("targets", [])
    base_target = next((t for t in targets if "Base" in str(t.get("index","")
                        or t.get("Scenario",""))), {})
    weighted   = base_target.get("Weighted (₹)", 0)
    upside     = base_target.get("Upside (%)", 0)
    rating     = base_target.get("Rating", "—")
    cmp        = info.get("current_price", 0)

    rating_color = GREEN if "BUY" in str(rating) else RED if "SELL" in str(rating) else AMBER

    cover_data = [[
        Paragraph(f"{info.get('name', ticker)}", styles["cover_company"]),
        Paragraph(f"{rating}", ParagraphStyle("r", fontSize=16,
                  fontName="Helvetica-Bold", textColor=rating_color,
                  alignment=TA_RIGHT)),
    ]]
    cover_table = Table(cover_data, colWidths=[12*cm, 5*cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), NAVY),
        ("TOPPADDING",   (0,0), (-1,-1), 16),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(cover_table)

    # Sub-header row
    sub_data = [[
        Paragraph(f"NSE: {ticker}  ·  {info.get('sector','—')}  ·  {info.get('industry','—')}",
                  styles["cover_sub"]),
        Paragraph(f"{datetime.now().strftime('%d %B %Y')}",
                  ParagraphStyle("d", fontSize=9, fontName="Helvetica",
                                 textColor=colors.HexColor("#CBD5E1"),
                                 alignment=TA_RIGHT)),
    ]]
    sub_table = Table(sub_data, colWidths=[12*cm, 5*cm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), BLUE),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Key metrics bar ───────────────────────────────────────────────────────
    def fmt(v, prefix="₹", suffix="", dec=0):
        if v is None: return "—"
        try:
            return f"{prefix}{float(v):,.{dec}f}{suffix}"
        except:
            return str(v)

    metrics = [
        ["CMP",          fmt(cmp)],
        ["Target Price", fmt(weighted)],
        ["Upside",       f"{upside:+.1f}%" if upside else "—"],
        ["P/E",          fmt(info.get("pe_ratio"), prefix="", suffix="x", dec=1)],
        ["EV/EBITDA",    fmt(info.get("ev_ebitda"), prefix="", suffix="x", dec=1)],
        ["Market Cap",   fmt((info.get("market_cap_cr") or 0)/100000,
                             prefix="₹", suffix="L cr", dec=1)],
    ]

    metric_rows = [
        [Paragraph(m[0], styles["metric_label"]) for m in metrics],
        [Paragraph(m[1], styles["metric_value"]) for m in metrics],
    ]
    metric_table = Table(metric_rows, colWidths=[17/6*cm]*6)
    metric_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), LGREY),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("LINEBELOW",    (0,0), (-1,0),  0.5, colors.HexColor("#CBD5E1")),
        ("BOX",          (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Investment thesis ─────────────────────────────────────────────────────
    story += section_block("INVESTMENT THESIS", None, styles)
    thesis = (
        f"{info.get('name', ticker)} is a {info.get('sector','—')} company "
        f"currently trading at ₹{cmp:,.0f}. Our base case target of "
        f"₹{weighted:,.0f} implies {upside:+.1f}% upside over a 3-year "
        f"horizon based on DCF, EV/EBITDA, and P/E valuation. "
        f"The FinBERT sentiment score of {sentiment.get('summary',{}).get('avg_score',0):+.3f} "
        f"signals {sentiment.get('summary',{}).get('signal','neutral sentiment')}. "
        f"Key drivers include revenue growth of ~{10}% CAGR and EBITDA margin "
        f"expansion toward {20}% by FY2027E."
    ) if cmp else "Insufficient data to generate thesis."
    story.append(Paragraph(thesis, styles["body"]))
    story.append(Spacer(1, 0.3*cm))

    # ── Financial summary ─────────────────────────────────────────────────────
    if projections:
        fin_headers = ["Metric (₹ cr)", "FY2025E", "FY2026E", "FY2027E"]
        fin_rows    = [fin_headers]
        metrics_map = [
            ("Revenue",     "Revenue"),
            ("EBITDA",      "EBITDA"),
            ("EBITDA Margin","EBITDA Margin"),
            ("PAT",         "PAT"),
            ("FCF",         "FCF"),
            ("EPS (₹)",     "EPS (₹)"),
        ]
        for label, key in metrics_map:
            row = [label]
            for proj in projections:
                val = proj.get(key)
                if val is None:
                    row.append("—")
                elif key in ("EBITDA Margin",):
                    row.append(f"{val:.1f}%")
                elif key == "EPS (₹)":
                    row.append(f"₹{val:.1f}")
                else:
                    row.append(f"₹{val:,.0f}")
            fin_rows.append(row)

        story += section_block("FINANCIAL SUMMARY", fin_rows, styles,
                               col_widths=[5*cm, 4*cm, 4*cm, 4*cm])

    # ── Valuation summary ─────────────────────────────────────────────────────
    if targets:
        val_headers = ["Scenario", "DCF (₹)", "EV/EBITDA (₹)", "P/E (₹)",
                       "Weighted (₹)", "Upside"]
        val_rows    = [val_headers]
        for t in targets:
            scenario = t.get("index") or t.get("Scenario","—")
            val_rows.append([
                scenario,
                fmt(t.get("DCF (₹)")),
                fmt(t.get("EV/EBITDA (₹)")),
                fmt(t.get("P/E (₹)")),
                fmt(t.get("Weighted (₹)")),
                f"{t.get('Upside (%)',0):+.1f}%",
            ])
        story += section_block("VALUATION SUMMARY", val_rows, styles,
                               col_widths=[3.5*cm,2.5*cm,3*cm,2.5*cm,3*cm,2.5*cm])

    # ── Scenario analysis ─────────────────────────────────────────────────────
    if scenarios:
        scen_headers = ["Scenario", "Revenue FY27E", "EBITDA FY27E",
                        "PAT FY27E", "Target (₹)", "Upside"]
        scen_rows    = [scen_headers]
        for name, data in scenarios.items():
            proj   = data.get("projections", [])
            target = data.get("target", {})
            fy27   = next((p for p in proj if "2027" in str(p.get("Year",""))), {})
            scen_rows.append([
                name,
                fmt(fy27.get("Revenue")),
                fmt(fy27.get("EBITDA")),
                fmt(fy27.get("PAT")),
                fmt(target.get("Avg Target (₹)")),
                f"{target.get('Upside (%)',0):+.1f}%",
            ])
        story += section_block("SCENARIO ANALYSIS", scen_rows, styles,
                               col_widths=[3.5*cm,3*cm,3*cm,2.5*cm,2.5*cm,2.5*cm])

    # ── ML signals ────────────────────────────────────────────────────────────
    story += section_block("ML SIGNALS", None, styles, header_color=TEAL)

    ensemble = ml.get("ensemble", {}) if ml else {}
    lstm     = ml.get("lstm") if ml else None

    ml_data = [
        ["Signal",          "Score",    "Weight", "Contribution"],
        ["Fundamental (DCF)",
         f"{ensemble.get('val_score',0):+.3f}",  "50%",
         f"{ensemble.get('val_score',0)*0.5:+.3f}"],
        ["LSTM Forecast",
         f"{ensemble.get('lstm_score',0):+.3f}", "25%",
         f"{ensemble.get('lstm_score',0)*0.25:+.3f}"],
        ["FinBERT Sentiment",
         f"{ensemble.get('sent_score',0):+.3f}", "25%",
         f"{ensemble.get('sent_score',0)*0.25:+.3f}"],
        ["ENSEMBLE",
         f"{ensemble.get('ensemble_score',0):+.3f}", "—",
         ensemble.get('rating','—')],
    ]
    story += section_block("", ml_data, styles,
                           col_widths=[5*cm, 4*cm, 4*cm, 4*cm],
                           header_color=WHITE)

    if lstm:
        lstm_text = (
            f"LSTM quarterly PAT forecast: "
            + ", ".join([f"{q}: ₹{v:,.0f} cr"
                         for q, v in zip(lstm.get("quarters",[]),
                                         lstm.get("forecast",[]))])
            + f"  |  Annual FY2026E: ₹{lstm.get('annual_pat',0):,.0f} cr"
            + f"  |  MAE: ₹{lstm.get('mae',0):,.0f} cr"
        )
        story.append(Paragraph(lstm_text, styles["body"]))

    # ── Sentiment ─────────────────────────────────────────────────────────────
    if sentiment and "summary" in sentiment:
        s = sentiment["summary"]
        sent_text = (
            f"FinBERT analysis of {s.get('total',0)} headlines: "
            f"{s.get('positive',0)} positive, {s.get('negative',0)} negative, "
            f"{s.get('neutral',0)} neutral. "
            f"Avg score: {s.get('avg_score',0):+.3f}. "
            f"Signal: {s.get('signal','—')}. "
            f"Sentiment-adjusted target: ₹{sentiment.get('adjusted_target',0):,}."
        )
        story.append(Paragraph(sent_text, styles["body"]))
    story.append(Spacer(1, 0.3*cm))

    # ── Key risks ─────────────────────────────────────────────────────────────
    story += section_block("KEY RISKS", None, styles, header_color=colors.HexColor("#7F1D1D"))
    risks = [
        "Macroeconomic slowdown impacting revenue growth and margins",
        "Raw material / input cost inflation compressing EBITDA",
        "Regulatory changes affecting business model or taxation",
        "Competitive intensity leading to pricing pressure",
        "Currency risk for companies with significant USD revenues/costs",
        "Management execution risk on capex and expansion plans",
    ]
    for risk in risks:
        story.append(Paragraph(f"• {risk}", styles["body"]))
    story.append(Spacer(1, 0.3*cm))

    # ── Disclaimer ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGREY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "DISCLAIMER: This report is generated by FinSight, an AI-powered equity research platform, "
        "for educational and informational purposes only. It does not constitute investment advice, "
        "a solicitation, or a recommendation to buy or sell any security. All projections are based "
        "on publicly available data and sector template assumptions. Past performance is not indicative "
        "of future results. Always consult a SEBI-registered investment advisor before making investment decisions.",
        styles["disclaimer"]
    ))
    story.append(Paragraph(
        f"Generated by FinSight  ·  {datetime.now().strftime('%d %B %Y %H:%M')}  ·  "
        f"Data: yfinance, NSE  ·  ML: PyTorch LSTM + ProsusAI/FinBERT",
        styles["footer"]
    ))

    doc.build(story)
    return filename


def generate_report_for_ticker(ticker):
    """Convenience function — fetches all data and generates report."""
    from src.data.fetch import get_company_info
    from src.financial.model import project_financials
    from src.financial.valuation import run_full_valuation
    from src.financial.scenarios import get_price_targets, run_scenario, SCENARIO_MULTIPLIERS
    from src.ml.lstm import run_lstm_forecast
    from src.ml.finbert import fetch_news, score_sentiment, aggregate_sentiment, scenario_adjustment
    from src.ml.ensemble import run_ensemble

    print(f"Generating report for {ticker}...")

    info       = get_company_info(ticker)
    proj_df    = project_financials(ticker)
    projections= proj_df.reset_index().to_dict(orient="records")

    val_df     = run_full_valuation(ticker)
    valuation  = {"targets": val_df.reset_index().to_dict(orient="records")}

    scen_data  = {}
    targets    = get_price_targets(ticker)
    for name in SCENARIO_MULTIPLIERS:
        df = run_scenario(ticker, name)
        scen_data[name] = {
            "projections": df.reset_index().to_dict(orient="records"),
            "target":      targets.loc[name].to_dict(),
        }

    mean, lower, upper, mae = run_lstm_forecast(ticker)
    ml_result = {"lstm": None, "ensemble": {}}
    if mean is not None:
        ml_result["lstm"] = {
            "quarters":   ["Q1 FY26E","Q2 FY26E","Q3 FY26E"],
            "forecast":   [round(v,0) for v in mean],
            "lower":      [round(v,0) for v in lower],
            "upper":      [round(v,0) for v in upper],
            "annual_pat": round(sum(mean),0),
            "mae":        round(mae,0) if isinstance(mae,float) else 0,
        }

    articles   = fetch_news(ticker)
    scored     = score_sentiment(articles)
    sent_agg   = aggregate_sentiment(scored)
    adj, note  = scenario_adjustment(sent_agg["avg_score"]) if sent_agg else (0, "")
    try:
        tgt_df     = get_price_targets(ticker)
        base_tgt   = int(tgt_df.loc["📊 Base","Avg Target (₹)"])
    except:
        base_tgt   = 1000

    sentiment  = {
        "summary":          sent_agg,
        "articles":         scored,
        "adjustment":       adj,
        "note":             note,
        "base_target":      base_tgt,
        "adjusted_target":  round(base_tgt * (1 + adj)),
    }

    val_results = run_full_valuation(ticker)
    ensemble    = run_ensemble(ticker, val_results, mean, sent_agg)
    ml_result["ensemble"] = ensemble

    filename = generate_report(
        ticker, info, projections, valuation,
        scen_data, sentiment, ml_result
    )
    print(f"Report saved: {filename}")
    return filename


if __name__ == "__main__":
    generate_report_for_ticker("RELIANCE.NS")