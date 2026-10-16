"""GTC mode: frame every agent around a six-week trading competition.

The Global Trading Challenge (GTC) ranks portfolios by return over a fixed
window, so the question each agent answers changes from "is this a good
long-term holding?" to "can this position earn a risk-adjusted return before
the competition ends?". The block built here is appended to the instrument
context, which every analyst, researcher, debater, the trader and both
managers already read, so the whole graph shares one horizon.

The rating scale is unchanged: the GTC labels map onto the existing five tiers
so the rating parser, memory log and reports keep working.
"""

from datetime import date, datetime, timedelta

DEFAULT_GTC_WEEKS = 6


def _parse(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()


def _weekdays_between(start: date, end: date) -> int:
    """Weekdays after ``start`` up to and including ``end`` (holidays ignored)."""
    days = 0
    current = start
    while current < end:
        current += timedelta(days=1)
        if current.weekday() < 5:
            days += 1
    return days


def gtc_window(trade_date, end_date=None) -> dict:
    """Days left in the competition as of ``trade_date``.

    Without an explicit end date the window is six weeks from ``trade_date``,
    which treats the run as the competition's first day.
    """
    start = _parse(trade_date) or date.today()
    end = _parse(end_date) or start + timedelta(weeks=DEFAULT_GTC_WEEKS)
    calendar_days = max((end - start).days, 0)
    return {
        "trade_date": start.isoformat(),
        "end_date": end.isoformat(),
        "calendar_days": calendar_days,
        "trading_days": _weekdays_between(start, end) if end > start else 0,
        "weeks": round(calendar_days / 7, 1),
    }


def build_gtc_context(trade_date, end_date=None) -> str:
    """The competition framing appended to the instrument context."""
    w = gtc_window(trade_date, end_date)
    if w["calendar_days"] == 0:
        stage = (
            "The competition ends today or has ended: no new position can pay off. "
            "Favor closing or holding cash unless the position is already working."
        )
    elif w["calendar_days"] <= 14:
        stage = (
            "The competition is in its final stretch: rely only on catalysts that "
            "resolve before the end date, cut high-drawdown exposure and favor liquidity."
        )
    else:
        stage = (
            "There is still room for a thesis to play out, but it must resolve "
            "inside the window."
        )
    return (
        "\n\nGTC MODE (Global Trading Challenge). This analysis is for a six-week "
        "trading competition ranked by portfolio return, not for long-term investing. "
        f"Analysis date: {w['trade_date']}. Competition end: {w['end_date']}. "
        f"Remaining: {w['calendar_days']} calendar days, about {w['trading_days']} "
        f"trading days ({w['weeks']} weeks). {stage}\n"
        "Answer one question: can this stock earn a significant risk-adjusted return "
        "before the end date? A great company is not automatically a great GTC trade.\n"
        "Priorities, in order: catalysts dated inside the window (earnings, guidance, "
        "regulatory decisions, major contracts, investor days), expected size of the "
        "move, probability the thesis works, momentum and technical setup, market and "
        "sector regime (risk-on, neutral, risk-off), earnings and revisions, valuation, "
        "fundamental quality, downside risk, liquidity.\n"
        "A catalyst dated after the end date is not a major catalyst. For each catalyst "
        "in the window give its date, expected direction, rough probability, possible "
        "magnitude, whether it is priced in, and the risk of a sell-the-news reaction.\n"
        "Where you weigh the trade, give bull, base and bear scenarios with returns to "
        "the end date and probabilities summing to about 100%, labelled as estimates, "
        "and the expected return they imply. Name an entry zone, a stop or "
        "invalidation level, and a target reachable before the end date.\n"
        "Map the GTC decision onto the five-tier rating: BUY = Buy; BUY ON PULLBACK = "
        "Overweight (say the entry level); HOLD = Hold; SELL = Underweight or Sell by "
        "conviction; AVOID = Sell for a new position (no position should be opened)."
    )
