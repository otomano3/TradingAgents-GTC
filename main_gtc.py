"""Run TradingAgents in GTC mode (six-week Global Trading Challenge).

    python main_gtc.py NVDA AMD --end 2026-11-27
    python main_gtc.py NVDA --date 2026-10-16 --check

Settings (LLM provider, models, API key) come from .env in this folder.
Each ticker's full report is saved under results_dir/reports, and one JSON
line per ticker is printed at the end: ticker, rating, report folder.
"""

import argparse
import json
import os
import sys
from datetime import date

from tradingagents.agents.gtc import gtc_window
from tradingagents.default_config import DEFAULT_CONFIG

_KEY_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tickers", nargs="+")
    parser.add_argument("--date", default=date.today().isoformat(), help="analysis date, YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="competition end date, YYYY-MM-DD")
    parser.add_argument("--check", action="store_true", help="validate settings and exit without calling the LLM")
    parser.add_argument("--debug", action="store_true", help="stream every agent message")
    args = parser.parse_args()

    config = DEFAULT_CONFIG.copy()
    config["gtc_mode"] = True
    if args.end:
        config["gtc_end_date"] = args.end

    provider = str(config.get("llm_provider", "")).lower()
    key_var = _KEY_VARS.get(provider)
    window = gtc_window(args.date, config.get("gtc_end_date"))
    status = {
        "provider": provider,
        "deep_model": config.get("deep_think_llm"),
        "quick_model": config.get("quick_think_llm"),
        "api_key_set": bool(os.environ.get(key_var)) if key_var else None,
        "window": window,
    }
    if args.check:
        print(json.dumps(status, ensure_ascii=False))
        return 0
    if key_var and not os.environ.get(key_var):
        print(f"{key_var} is not set; add it to .env in {os.getcwd()}", file=sys.stderr)
        return 2

    from tradingagents.graph.trading_graph import TradingAgentsGraph

    ta = TradingAgentsGraph(debug=args.debug, config=config)
    results = []
    for ticker in args.tickers:
        try:
            final_state, decision = ta.propagate(ticker, args.date)
            path = ta.save_reports(final_state, ticker)
            results.append({"ticker": ticker, "rating": decision, "report": str(path)})
        except Exception as exc:  # keep going so one bad ticker does not lose the rest
            results.append({"ticker": ticker, "error": f"{type(exc).__name__}: {exc}"})
    for row in results:
        print("GTC_RESULT " + json.dumps(row, ensure_ascii=False))
    return 0 if all("error" not in r for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
