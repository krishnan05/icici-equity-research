import yfinance as yf
import pandas as pd
from rich import print as rprint


_ticker_cache = {}

def resolve_ticker(ticker):
    if ticker in _ticker_cache:
        return _ticker_cache[ticker]

    # Try original first
    t    = yf.Ticker(ticker)
    info = t.info
    if info.get("currentPrice") or info.get("regularMarketPrice"):
        _ticker_cache[ticker] = ticker
        return ticker

    # Try BSE only if NS failed — no further retries
    if ticker.endswith(".NS"):
        bse = ticker.replace(".NS", ".BO")
        t2  = yf.Ticker(bse)
        info2 = t2.info
        if info2.get("currentPrice") or info2.get("regularMarketPrice"):
            _ticker_cache[ticker] = bse
            return bse

    # Give up — return original, let caller handle None data
    _ticker_cache[ticker] = ticker
    return ticker

def get_ticker(ticker):
    ticker = resolve_ticker(ticker)
    return yf.Ticker(ticker)


def get_company_info(ticker):
    ticker = resolve_ticker(ticker)
    t = yf.Ticker(ticker)
    info = t.info

    # Detect currency — convert USD to INR if needed
    currency = info.get("currency", "INR")
    fx = 85.0 if currency == "USD" else 1.0  # approx USD/INR rate

    def to_cr(val):
        if val is None: return 0
        return round(val * fx / 1e7, 0)

    return {
        "name":           info.get("longName", ticker),
        "sector":         info.get("sector", "Unknown"),
        "industry":       info.get("industry", "Unknown"),
        "currency":       currency,
        "current_price":  info.get("currentPrice"),
        "market_cap_cr":  to_cr(info.get("marketCap")),
        "ev_cr":          to_cr(info.get("enterpriseValue")),
        "pe_ratio":       info.get("trailingPE"),
        "pb_ratio":       info.get("priceToBook"),
        "ev_ebitda":      info.get("enterpriseToEbitda"),
        "52w_high":       info.get("fiftyTwoWeekHigh"),
        "52w_low":        info.get("fiftyTwoWeekLow"),
        "book_value":     info.get("bookValue"),
        "eps_ttm":        info.get("trailingEps"),
        "dividend_yield": info.get("dividendYield"),
        "roe":            info.get("returnOnEquity"),
        "roce":           info.get("returnOnAssets"),
        "debt_to_equity": info.get("debtToEquity"),
        "free_cashflow":  to_cr(info.get("freeCashflow")),
        "revenue_cr":     to_cr(info.get("totalRevenue")),
        "ebitda_cr":      to_cr(info.get("ebitda")),
        "net_debt_cr":    to_cr(info.get("totalDebt", 0)) -
                          to_cr(info.get("totalCash", 0)),
        "shares_cr":      round((info.get("sharesOutstanding") or 0) * fx / 1e7, 2),
    }

def get_financials(ticker, annual=True):
    ticker = resolve_ticker(ticker)
    t = yf.Ticker(ticker)
    info = t.info
    currency = info.get("currency", "INR")
    fx = 85.0 if currency == "USD" else 1.0

    inc = t.financials      if annual else t.quarterly_financials
    bal = t.balance_sheet   if annual else t.quarterly_balance_sheet
    csh = t.cashflow        if annual else t.quarterly_cashflow

    # Scale all values to INR crore
    if fx != 1.0:
        if inc is not None: inc = inc * fx
        if bal is not None: bal = bal * fx
        if csh is not None: csh = csh * fx

    return {"income": inc, "balance": bal, "cashflow": csh}

def get_price_history(ticker, period="5y"):
    ticker = resolve_ticker(ticker)
    return get_ticker(ticker).history(period=period)

def get_news(ticker, max_articles=20):
    ticker = resolve_ticker(ticker)
    t = yf.Ticker(ticker)
    news = t.news or []
    articles = []
    for item in news[:max_articles]:
        content = item.get("content", {})
        title   = content.get("title") or item.get("title") or ""
        summary = content.get("summary") or item.get("summary") or ""
        if title:
            articles.append({
                "title":   title,
                "summary": summary[:200],
            })
    return articles

def print_summary(ticker):
    ticker = resolve_ticker(ticker)
    rprint(f"\n[bold blue]━━━ {ticker} – Live Market Data ━━━[/bold blue]")
    info = get_company_info(ticker)
    rprint(f"  [green]Company          [/green] {info['name']}")
    rprint(f"  [green]Sector           [/green] {info['sector']}")
    rprint(f"  [green]Current Price    [/green] ₹{info['current_price']}")
    rprint(f"  [green]Market Cap       [/green] ₹{info['market_cap_cr']:,.0f} cr")
    rprint(f"  [green]EV               [/green] ₹{info['ev_cr']:,.0f} cr")
    rprint(f"  [green]P/E              [/green] {info['pe_ratio']}")
    rprint(f"  [green]EV/EBITDA        [/green] {info['ev_ebitda']}")
    rprint(f"  [green]P/BV             [/green] {info['pb_ratio']}")
    rprint(f"  [green]ROE              [/green] {info['roe']}")
    rprint(f"  [green]Net Debt         [/green] ₹{info['net_debt_cr']:,.0f} cr")
    rprint(f"  [green]Free Cash Flow   [/green] ₹{info['free_cashflow']:,.0f} cr")
    rprint(f"  [green]52W Range        [/green] ₹{info['52w_low']} – ₹{info['52w_high']}")

if __name__ == "__main__":
    print_summary("RELIANCE.NS")