"""
Tests for core/planning.py

Seam 1: Pure snapshot function taking manifest source and simulated now.
"""
from datetime import datetime, timezone
import pytest


def test_fresh_manifest_snapshot():
    from core.planning import parse_planning_snapshot

    manifest_yaml = """
schema_version: 1
synthetic: true
label: "SYNTHETIC EXAMPLE DATA"
run:
  prepared_at: "2026-10-12T08:00:00Z"
  status: "succeeded"
  stale_after_hours: 24
  sources:
    - name: "tasks"
      as_of: "2026-10-12T07:55:00Z"
week:
  start: "2026-10-12"
  timezone: "Europe/London"
blocks:
  - id: "b1"
    day: "Monday"
    start: "09:00"
    end: "10:00"
    kind: "focus"
    title: "Example focus block"
items:
  - id: "i1"
    title: "Example task"
    kind: "task"
    day: "Monday"
    block_id: "b1"
recurring:
  - id: "r1"
    title: "Example daily routine"
    cadence: "daily"
    days: []
"""
    now = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    snapshot = parse_planning_snapshot(manifest_yaml, now=now)

    assert snapshot.state == "fresh"
    assert snapshot.prepared_at == datetime(2026, 10, 12, 8, 0, 0, tzinfo=timezone.utc)
    assert snapshot.age_hours == pytest.approx(2.0)
    assert snapshot.stale_after_hours == 24
    assert snapshot.week["start"] == "2026-10-12"
    assert snapshot.week["timezone"] == "Europe/London"
    assert len(snapshot.sources) == 1
    assert snapshot.sources[0]["name"] == "tasks"
    assert len(snapshot.blocks) == 1
    assert len(snapshot.items) == 1
    assert len(snapshot.recurring) == 1


def test_stale_manifest_snapshot():
    from core.planning import parse_planning_snapshot

    manifest_yaml = """
schema_version: 1
synthetic: true
label: "SYNTHETIC EXAMPLE DATA"
run:
  prepared_at: "2026-10-10T08:00:00Z"
  status: "succeeded"
  stale_after_hours: 24
  sources: []
week:
  start: "2026-10-12"
  timezone: "Europe/London"
blocks:
  - id: "b1"
    day: "Monday"
    start: "09:00"
    end: "10:00"
    kind: "focus"
    title: "Example focus block"
items: []
recurring: []
"""
    # 50 hours later
    now = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    snapshot = parse_planning_snapshot(manifest_yaml, now=now)

    assert snapshot.state == "stale"
    assert snapshot.age_hours == pytest.approx(50.0)
    assert snapshot.stale_after_hours == 24


def test_exact_threshold_boundary_is_fresh():
    from core.planning import parse_planning_snapshot

    manifest_yaml = """
schema_version: 1
synthetic: true
label: "SYNTHETIC EXAMPLE DATA"
run:
  prepared_at: "2026-10-11T08:00:00Z"
  status: "succeeded"
  stale_after_hours: 24
  sources: []
week:
  start: "2026-10-12"
  timezone: "Europe/London"
blocks:
  - id: "b1"
    day: "Monday"
    start: "09:00"
    end: "10:00"
    kind: "focus"
    title: "Example focus block"
items: []
recurring: []
"""
    # Exactly 24 hours later -> age_hours == 24.0 -> fresh
    now = datetime(2026, 10, 12, 8, 0, 0, tzinfo=timezone.utc)
    snapshot = parse_planning_snapshot(manifest_yaml, now=now)

    assert snapshot.state == "fresh"
    assert snapshot.age_hours == pytest.approx(24.0)

    # 24 hours and 1 second later -> age_hours > 24.0 -> stale
    now_past = datetime(2026, 10, 12, 8, 0, 1, tzinfo=timezone.utc)
    snapshot_past = parse_planning_snapshot(manifest_yaml, now=now_past)
    assert snapshot_past.state == "stale"
