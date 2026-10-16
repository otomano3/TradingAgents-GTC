"""GTC mode: competition window and the framing appended to the instrument context."""

from tradingagents.agents.gtc import build_gtc_context, gtc_window
from tradingagents.default_config import build_default_config
from tradingagents.graph.trading_graph import TradingAgentsGraph


def test_window_defaults_to_six_weeks():
    w = gtc_window("2026-10-16")
    assert w["end_date"] == "2026-11-27"
    assert w["calendar_days"] == 42
    assert w["trading_days"] == 30


def test_window_counts_to_explicit_end_date():
    w = gtc_window("2026-10-16", "2026-10-23")
    assert w["calendar_days"] == 7
    assert w["trading_days"] == 5


def test_window_after_end_is_zero():
    w = gtc_window("2026-12-01", "2026-11-27")
    assert w["calendar_days"] == 0
    assert w["trading_days"] == 0


def test_context_states_horizon_and_rating_map():
    text = build_gtc_context("2026-10-16", "2026-11-27")
    assert "GTC MODE" in text
    assert "2026-11-27" in text
    assert "BUY ON PULLBACK = Overweight" in text


def test_final_stretch_wording():
    assert "final stretch" in build_gtc_context("2026-11-20", "2026-11-27")


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_GTC_MODE", "true")
    monkeypatch.setenv("TRADINGAGENTS_GTC_END_DATE", "2026-11-27")
    config = build_default_config()
    assert config["gtc_mode"] is True
    assert config["gtc_end_date"] == "2026-11-27"


def _context(monkeypatch, config):
    monkeypatch.setattr(
        "tradingagents.graph.trading_graph.resolve_instrument_identity", lambda t: {}
    )
    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = config
    return graph.resolve_instrument_context("NVDA", "stock", "2026-10-16")


def test_graph_appends_gtc_context_only_when_enabled(monkeypatch):
    off = _context(monkeypatch, {"gtc_mode": False})
    on = _context(monkeypatch, {"gtc_mode": True, "gtc_end_date": "2026-11-27"})
    assert "GTC MODE" not in off
    assert on.startswith(off) and "GTC MODE" in on
