# ICICI Bank – Equity Research Platform

End-to-end financial modelling project built for MBA finance portfolio.

## What This Does
- Fetches live ICICI Bank financial data via yfinance
- Projects 3-year Income Statement (FY2025–FY2027)
- Runs Bull / Base / Bear scenario analysis
- Values the bank using DDM, P/E, and P/BV methods
- Computes CAPM cost of equity and blended price target

## Tech Stack
Python · pandas · yfinance · rich · numpy

## How to Run
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Project Phases
- ✅ Phase 1: Excel financial model (3-statement + DCF)
- ✅ Phase 2: Python automation engine
- 🔄 Phase 3: ML valuation layer (in progress)
- 🔄 Phase 4: Hosted React web app

## Data Sources
ICICI Bank Annual Reports FY2022–FY2024 · yfinance · NSE
