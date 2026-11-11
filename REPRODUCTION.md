# Reproduction Notes — FTEC5660 Reproducibility Work

**Author:** RUAN Chenyang (1155262070), CUHK
**Date:** November 2026
**Paper reproduced:** No. 22 — *TradingAgents: Multi-Agents LLM Financial Trading Framework* (from the instructor-provided list)

This fork documents an independent reproduction of the TradingAgents
multi-agent trading pipeline, plus one controlled modification
(ablation of the bull/bear debate). All changes relative to upstream
are in the commits on top of the imported `main` branch.

## What was reproduced

End-to-end decision pipeline for a fixed case: **NVDA on 2026-09-01**,
run repeatedly under identical configuration.

- Baseline (default config, debate enabled), 3 trials:
  Overweight / Buy / Hold — see `results_baseline*_NVDA_2026-09-01.txt`
- Modification (`max_debate_rounds: 1 → 0`), 3 trials:
  Overweight / Buy / Buy — see `results_nodebate*_NVDA_2026-09-01.txt`

Full debug logs of every trial are in `repro/logs/`.

## Controlled variable: LLM swap

Upstream defaults target OpenAI models. All runs here use DeepSeek
(OpenAI-compatible): `deepseek-v4-pro` (deep tier) and
`deepseek-flash` (quick tier), default decoding parameters.
Results are therefore **not** directly comparable to the paper's
reported backtest metrics; comparisons are made only within this
setup (same tasks, same protocol, same evaluation).

## Patches (kept minimal, no agent logic changed)

1. `fix(data)`: `alpha_vantage/stock.py` — use the free-tier
   `TIME_SERIES_DAILY` endpoint instead of the premium
   `TIME_SERIES_DAILY_ADJUSTED`. Required because the free key is
   rejected by the premium endpoint.
2. `fix(llm)`: `llm_clients/factory.py` — forward a new
   `llm_timeout` config key into the chat client kwargs. Without a
   request timeout, two runs hung indefinitely (0% CPU, dead HTTP
   connection) inside `chat.completions.create`.

## Install and run

```bash
python3 -m venv .venv
.venv/bin/pip install -e .          # or: pip install -e . -i <your mirror>

cp .env.example .env                 # then fill in your keys:
# DEEPSEEK_API_KEY=...
# TRADINGAGENTS_LLM_PROVIDER=deepseek
# TRADINGAGENTS_DEEP_THINK_LLM=deepseek-v4-pro
# TRADINGAGENTS_QUICK_THINK_LLM=deepseek-flash
# ALPHA_VANTAGE_API_KEY=...          # free tier; 25 requests/day!

# Baseline trial:
.venv/bin/python run_exp.py NVDA 2026-09-01 baseline1

# Ablation trial (debate removed, tag prefix "nodebate" triggers it):
.venv/bin/python run_exp.py NVDA 2026-09-01 nodebate1
```

Each trial takes ~15–25 minutes, dominated by LLM latency, and writes
`results_<tag>_<ticker>_<date>.txt`.

## Known environment pitfalls (verified 2026-11-09/10)

- Yahoo Finance hard-rate-limits some IPs (HTTP 403/429 on every
  endpoint); do not rely on `yfinance` as the primary vendor.
- Alpha Vantage free tier: 25 requests/day; several endpoints used by
  upstream are premium-only (news sentiment, adjusted daily).
- Without `llm_timeout`, a stalled HTTP connection to the LLM provider
  hangs the run forever with no error.
