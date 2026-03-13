"""
Retention Calculation Engine
────────────────────────────
Pure-Python module – no database or ORM dependency.

Provides three functions used by the Progress Agent:
  • compute_topic_retention   – decay-based retention for a single topic
  • compute_retention_after   – blends history with a new session score
  • compute_system_retention  – weighted aggregate retention across all topics
"""

# ──────────────────────────────────────────────
# Interval-day → weight / blend look-up tables
# ──────────────────────────────────────────────

# Maps an interval_day value to (new_weight, history_weight)
_BLEND_WEIGHTS: dict[int, tuple[float, float]] = {
    1:  (0.90, 0.10),
    3:  (0.75, 0.25),
    7:  (0.60, 0.40),
    21: (0.45, 0.55),
    60: (0.35, 0.65),
}

# Maps an interval_day value to a topic importance weight
_TOPIC_WEIGHTS: dict[int, float] = {
    1:  0.5,
    3:  0.7,
    7:  1.0,
    21: 1.3,
    60: 1.5,
}

# State-based multiplier applied to topic importance weight
_STATE_MULTIPLIERS: dict[str, float] = {
    "active":    1.0,
    "decaying":  0.8,
    "graduated": 1.0,
}

# Default fallback when interval_day is not in the table
_DEFAULT_BLEND = (0.60, 0.40)
_DEFAULT_TOPIC_WEIGHT = 1.0

# Retention clamp boundaries
_MIN_RETENTION = 0.10
_MAX_RETENTION = 1.00


# ──────────────────────────────────────────────
# 1. Topic-level retention (decay model)
# ──────────────────────────────────────────────

def compute_topic_retention(
    performance_score: float,
    days_since_session: int,
    interval_day: int,
) -> float:
    """Return the current retention score for a single topic.

    Uses an exponential-style linear decay:
        decay_rate = 0.30 / interval_day
        retention  = performance_score × (1 − decay_rate × days_since_session)

    The result is clamped to [0.10, 1.00] and rounded to 4 dp.
    """
    decay_rate = 0.30 / interval_day
    retention = performance_score * (1 - decay_rate * days_since_session)

    # Clamp
    retention = max(_MIN_RETENTION, min(_MAX_RETENTION, retention))

    return round(retention, 4)


# ──────────────────────────────────────────────
# 2. Post-session blended retention
# ──────────────────────────────────────────────

def compute_retention_after(
    prev_retention: float,
    session_performance: float,
    interval_day: int,
) -> float:
    """Blend the previous retention with the new session performance.

    The weighting between *new* and *history* depends on interval_day:
        Day  1 → 0.90 new / 0.10 history
        Day  3 → 0.75 new / 0.25 history
        Day  7 → 0.60 new / 0.40 history
        Day 21 → 0.45 new / 0.55 history
        Day 60 → 0.35 new / 0.65 history

    Returns a value clamped to [0.10, 1.00].
    """
    new_weight, history_weight = _BLEND_WEIGHTS.get(interval_day, _DEFAULT_BLEND)

    retention_after = (
        session_performance * new_weight
        + prev_retention * history_weight
    )

    # Clamp
    retention_after = max(_MIN_RETENTION, min(_MAX_RETENTION, retention_after))

    return round(retention_after, 4)


# ──────────────────────────────────────────────
# 3. System-wide (user-level) retention
# ──────────────────────────────────────────────

def compute_system_retention(topics: list[dict]) -> dict:
    """Calculate the overall retention percentage across all topics.

    Parameters
    ----------
    topics : list[dict]
        Each dict must contain:
            - latest_performance_score  (float)
            - days_since_last_session   (int)
            - current_interval_day      (int)
            - state                     (str)

    Returns
    -------
    dict
        {
            "retention_percent": int,   # 0-100
            "trend": "stable"
        }
    """
    if not topics:
        return {"retention_percent": 0, "trend": "stable"}

    weighted_sum = 0.0
    total_weight = 0.0

    for topic in topics:
        interval_day = topic["current_interval_day"]
        state = topic.get("state", "active")

        # Graduated topics are fully mastered – no decay
        if state == "graduated":
            topic_retention = topic["latest_performance_score"]
        else:
            topic_retention = compute_topic_retention(
                performance_score=topic["latest_performance_score"],
                days_since_session=topic["days_since_last_session"],
                interval_day=interval_day,
            )

        # Importance weight × state multiplier
        interval_weight = _TOPIC_WEIGHTS.get(interval_day, _DEFAULT_TOPIC_WEIGHT)
        state_multiplier = _STATE_MULTIPLIERS.get(state, 1.0)
        weight = interval_weight * state_multiplier

        weighted_sum += topic_retention * weight
        total_weight += weight

    # Weighted average → percentage
    retention_ratio = weighted_sum / total_weight if total_weight else 0.0
    retention_percent = int(round(retention_ratio * 100))

    return {
        "retention_percent": retention_percent,
        "trend": "stable",
    }
