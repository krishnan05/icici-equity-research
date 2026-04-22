from fastapi import APIRouter
from src.data.fetch import get_company_info
from src.financial.model import project_financials, calculate_ratios
from fastapi.responses import FileResponse
from src.report.generator import generate_report_for_ticker
import os


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

@router.get("/report/{ticker}")
def download_report(ticker: str):
    filename = generate_report_for_ticker(ticker)
    return FileResponse(
        path=filename,
        filename=os.path.basename(filename),
        media_type="application/pdf"
    )