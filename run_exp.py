"""Experiment runner: same as main.py but with Alpha Vantage as primary market-data vendor."""
import sys
from dotenv import load_dotenv
load_dotenv()
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
date = sys.argv[2] if len(sys.argv) > 2 else "2026-09-01"
tag = sys.argv[3] if len(sys.argv) > 3 else "run"

config = DEFAULT_CONFIG.copy()
config["data_vendors"] = dict(config["data_vendors"])
config["data_vendors"]["core_stock_apis"] = "alpha_vantage"  # yfinance IP-blocked
config["data_vendors"]["technical_indicators"] = "alpha_vantage"
config["llm_timeout"] = 240          # seconds; fail fast instead of hanging
config["llm_max_retries"] = 2
config["data_vendors"]["news_data"] = "yfinance"  # will degrade gracefully if throttled

if tag.startswith("nodebate"):
    config["max_debate_rounds"] = 0  # ABLATION: remove bull/bear researcher debate
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate(ticker, date)

out = f"results_{tag}_{ticker}_{date}.txt"
with open(out, "w") as f:
    f.write(str(decision))
print("=== FINAL DECISION saved to", out, "===")
print(decision)
