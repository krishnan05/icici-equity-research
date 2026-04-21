from fastapi import APIRouter
from src.ml.lstm import run_lstm_forecast
from src.ml.finbert import fetch_news, score_sentiment, aggregate_sentiment
from src.financial.valuation import run_full_valuation
from src.ml.ensemble import run_ensemble

router = APIRouter()

@router.get("/ml/{ticker}")
def get_ml(ticker: str):
    # LSTM
    mean, lower, upper, mae = run_lstm_forecast(ticker)
    lstm_result = None
    if mean is not None:
        lstm_result = {
            "quarters":    ["Q1 FY26E", "Q2 FY26E", "Q3 FY26E"],
            "forecast":    [round(v, 0) for v in mean],
            "lower":       [round(v, 0) for v in lower],
            "upper":       [round(v, 0) for v in upper],
            "annual_pat":  round(sum(mean), 0),
            "mae":         round(mae, 0) if isinstance(mae, float) else None,
        }

    # Ensemble
    val_results  = run_full_valuation(ticker)
    articles     = fetch_news(ticker)
    scored       = score_sentiment(articles)
    sent_agg     = aggregate_sentiment(scored)
    ensemble     = run_ensemble(ticker, val_results, mean, sent_agg)

    return {
        "lstm":     lstm_result,
        "ensemble": ensemble,
    }