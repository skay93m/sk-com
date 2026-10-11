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


def test_empty_manifest_snapshot():
    from core.planning import parse_planning_snapshot

    manifest_yaml = """
schema_version: 1
synthetic: true
label: "SYNTHETIC EXAMPLE DATA"
run:
  prepared_at: "2026-10-12T08:00:00Z"
  status: "succeeded"
  stale_after_hours: 24
  sources: []
week:
  start: "2026-10-12"
  timezone: "Europe/London"
blocks: []
items: []
recurring: []
"""
    now = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    snapshot = parse_planning_snapshot(manifest_yaml, now=now)

    assert snapshot.state == "empty"
    assert snapshot.blocks == []
    assert snapshot.items == []
    assert snapshot.recurring == []


def test_failed_run_status_snapshot():
    from core.planning import parse_planning_snapshot

    manifest_yaml = """
schema_version: 1
synthetic: true
label: "SYNTHETIC EXAMPLE DATA"
run:
  prepared_at: "2026-10-12T08:00:00Z"
  status: "failed"
  stale_after_hours: 24
  sources: []
week:
  start: "2026-10-12"
  timezone: "Europe/London"
blocks: []
items: []
recurring: []
"""
    now = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    snapshot = parse_planning_snapshot(manifest_yaml, now=now)

    assert snapshot.state == "failed"
    assert snapshot.reason_code == "run_status_failed"


@pytest.mark.parametrize(
    "override_yaml,expected_reason",
    [
        ("unknown_key: true", "unknown_field"),
        ("synthetic: false", "synthetic_required"),
        (
            """
blocks:
  - id: "b1"
    day: "Monday"
    start: "09:00"
    end: "10:00"
    kind: "focus"
    title: "This title is intentionally way longer than eighty characters so that it triggers the validation limit properly"
""",
            "title_too_long",
        ),
        (
            """
week:
  start: "2026-10-13"
  timezone: "Europe/London"
""",
            "week_start_not_monday",
        ),
    ],
)
def test_invalid_manifest_reasons(override_yaml, expected_reason):
    from core.planning import parse_planning_snapshot

    base_yaml = """
schema_version: 1
synthetic: true
label: "SYNTHETIC EXAMPLE DATA"
run:
  prepared_at: "2026-10-12T08:00:00Z"
  status: "succeeded"
  stale_after_hours: 24
  sources: []
week:
  start: "2026-10-12"
  timezone: "Europe/London"
blocks: []
items: []
recurring: []
"""
    # If the override replaces an existing section or adds a key
    if "unknown_key" in override_yaml or "synthetic: false" in override_yaml:
        if "synthetic: false" in override_yaml:
            manifest_yaml = base_yaml.replace("synthetic: true", "synthetic: false")
        else:
            manifest_yaml = base_yaml + "\n" + override_yaml
    elif "blocks:" in override_yaml:
        manifest_yaml = base_yaml.replace("blocks: []", override_yaml.strip())
    elif "week:" in override_yaml:
        manifest_yaml = base_yaml.replace(
            """week:
  start: "2026-10-12"
  timezone: "Europe/London" """.strip(),
            override_yaml.strip(),
        )
    else:
        manifest_yaml = base_yaml + "\n" + override_yaml

    now = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    snapshot = parse_planning_snapshot(manifest_yaml, now=now)

    assert snapshot.state == "failed"
    assert snapshot.reason_code == expected_reason
    # Ensure no manifest content is leaked into reason_code
    assert "This title is intentionally" not in (snapshot.reason_code or "")


# ---------------------------------------------------------------------------
# Seam 2: View tests for /planning/synthetic/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize(
    "scenario,expected_state_text",
    [
        ("fresh", "Snapshot is fresh"),
        ("stale", "Snapshot is stale"),
        ("empty", "Snapshot is empty"),
        ("failed", "Snapshot failed"),
    ],
)
def test_planning_synthetic_page_renders_scenarios(client, scenario, expected_state_text):
    response = client.get(f"/planning/synthetic/?scenario={scenario}")
    assert response.status_code == 200
    assert b"SYNTHETIC" in response.content
    assert b"<title>SYNTHETIC Planning" in response.content
    assert b"SYNTHETIC EXAMPLE DATA" in response.content
    assert expected_state_text.encode("utf-8") in response.content


def test_planning_page_noindex_header(client):
    response = client.get("/planning/synthetic/")
    assert response.status_code == 200
    assert response.headers.get("X-Robots-Tag") == "noindex"


def test_robots_txt_disallows_planning(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"Disallow: /planning/\n" in response.content


def test_unknown_scenario_returns_404(client):
    response = client.get("/planning/synthetic/?scenario=nonexistent")
    assert response.status_code == 404


def test_no_absolute_external_urls_in_rendered_page(client):
    response = client.get("/planning/synthetic/")
    assert response.status_code == 200
    # The page itself should not link out to external websites (except standard footer links if in base template)
    # Inside the planning-container, ensure no external URLs exist
    content_str = response.content.decode("utf-8")
    assert "https://" not in content_str.split('<div class="planning-container">')[1].split('</main>')[0]
