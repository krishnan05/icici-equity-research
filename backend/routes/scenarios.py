from fastapi import APIRouter
from src.financial.scenarios import run_scenario, get_price_targets, SCENARIO_MULTIPLIERS

router = APIRouter()

@router.get("/scenarios/{ticker}")
def get_scenarios(ticker: str):
    targets = get_price_targets(ticker)
    result  = {}
    for name in SCENARIO_MULTIPLIERS:
        df = run_scenario(ticker, name)
        result[name] = {
            "projections": df.reset_index().to_dict(orient="records"),
            "target":      targets.loc[name].to_dict(),
            "description": SCENARIO_MULTIPLIERS[name]["description"],
        }
    return result