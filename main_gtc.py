"""Run TradingAgents in GTC mode (six-week Global Trading Challenge)."""

import sys

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
trade_date = sys.argv[2] if len(sys.argv) > 2 else "2026-10-16"
end_date = sys.argv[3] if len(sys.argv) > 3 else None

config = DEFAULT_CONFIG.copy()
config["gtc_mode"] = True
if end_date:
    config["gtc_end_date"] = end_date

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate(ticker, trade_date)
print(decision)
