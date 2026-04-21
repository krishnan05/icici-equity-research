from fastapi import APIRouter
from src.data.fetch import get_company_info
from src.financial.model import project_financials, calculate_ratios

router = APIRouter()

@router.get("/financials/{ticker}")
def get_financials(ticker: str):
    info   = get_company_info(ticker)
    proj   = project_financials(ticker)
    ratios = calculate_ratios(ticker, proj)
    return {
        "ticker": ticker,
        "info":   info,
        "projections": proj.reset_index().to_dict(orient="records"),
        "ratios":      ratios.reset_index().to_dict(orient="records"),
    }