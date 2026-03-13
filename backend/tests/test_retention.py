"""Quick smoke test for core/retention.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.retention import (
    compute_topic_retention,
    compute_retention_after,
    compute_system_retention,
)

# --- 1. compute_topic_retention ---
r1 = compute_topic_retention(0.85, 2, 7)
print(f"topic_retention(0.85, 2, 7) = {r1}")
assert 0.10 <= r1 <= 1.00

r2 = compute_topic_retention(0.95, 0, 1)
print(f"topic_retention(0.95, 0, 1) = {r2}")
assert r2 == 0.95  # no decay when days=0

r3 = compute_topic_retention(0.50, 100, 1)
print(f"topic_retention(0.50, 100, 1) = {r3}  (clamped to min)")
assert r3 == 0.10

# --- 2. compute_retention_after ---
ra1 = compute_retention_after(0.60, 0.90, 1)
print(f"retention_after(0.60, 0.90, day=1) = {ra1}")
expected = 0.90 * 0.90 + 0.60 * 0.10
assert abs(ra1 - round(expected, 4)) < 1e-6

ra2 = compute_retention_after(0.70, 0.80, 7)
print(f"retention_after(0.70, 0.80, day=7) = {ra2}")

# --- 3. compute_system_retention ---
topics = [
    {"latest_performance_score": 0.85, "days_since_last_session": 2,
     "current_interval_day": 7, "state": "active"},
    {"latest_performance_score": 0.70, "days_since_last_session": 5,
     "current_interval_day": 21, "state": "active"},
]
sr = compute_system_retention(topics)
print(f"system_retention = {sr}")
assert "retention_percent" in sr
assert "trend" in sr
assert sr["trend"] == "stable"
assert 0 <= sr["retention_percent"] <= 100

empty = compute_system_retention([])
print(f"system_retention([]) = {empty}")
assert empty["retention_percent"] == 0

# --- 4. Graduated topics must NOT decay ---
graduated_topic = [
    {"latest_performance_score": 0.92, "days_since_last_session": 30,
     "current_interval_day": 60, "state": "graduated"},
]
gr = compute_system_retention(graduated_topic)
print(f"system_retention(graduated, days=30) = {gr}")
# Retention should be based on raw score (0.92), NOT decayed
expected_pct = int(round(0.92 * 100))
assert gr["retention_percent"] == expected_pct, (
    f"Graduated topic should not decay: expected {expected_pct}, got {gr['retention_percent']}"
)

# --- 5. Decaying state multiplier ---
# Same topic as "active" vs "decaying" — decaying should get 0.8× weight
active_topics = [
    {"latest_performance_score": 0.80, "days_since_last_session": 1,
     "current_interval_day": 7, "state": "active"},
]
decaying_topics = [
    {"latest_performance_score": 0.80, "days_since_last_session": 1,
     "current_interval_day": 7, "state": "decaying"},
]
ar = compute_system_retention(active_topics)
dr = compute_system_retention(decaying_topics)
print(f"active  = {ar}")
print(f"decaying = {dr}")
# Same single topic → same retention score, but weight differs in aggregate;
# with a single topic the *percent* should still match (weighted avg of 1 item).
# The real difference shows with multiple topics — verify the multiplier exists:
from core.retention import _STATE_MULTIPLIERS
assert _STATE_MULTIPLIERS["decaying"] == 0.8, "Decaying multiplier must be 0.8"
assert _STATE_MULTIPLIERS["active"] == 1.0
assert _STATE_MULTIPLIERS["graduated"] == 1.0

# --- 6. Mixed topics: graduated + decaying ---
mixed = [
    {"latest_performance_score": 0.95, "days_since_last_session": 50,
     "current_interval_day": 60, "state": "graduated"},
    {"latest_performance_score": 0.60, "days_since_last_session": 3,
     "current_interval_day": 7, "state": "decaying"},
]
mr = compute_system_retention(mixed)
print(f"system_retention(mixed) = {mr}")
assert 0 <= mr["retention_percent"] <= 100

print("\n✅ All retention tests passed!")
