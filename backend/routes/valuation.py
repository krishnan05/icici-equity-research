from fastapi import APIRouter
from src.financial.valuation import run_full_valuation, cost_of_equity

router = APIRouter()

@router.get("/valuation/{ticker}")
def get_valuation(ticker: str):
    ke      = cost_of_equity()
    results = run_full_valuation(ticker)
    return {
        "ke":      round(ke * 100, 2),
        "targets": results.reset_index().to_dict(orient="records"),
    }