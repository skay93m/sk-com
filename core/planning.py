"""
core/planning.py - Snapshot parsing and data structures for the synthetic planning page.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional
import yaml


ALLOWED_MANIFEST_KEYS = {
    'schema_version',
    'synthetic',
    'label',
    'run',
    'week',
    'blocks',
    'items',
    'recurring',
}

ALLOWED_RUN_KEYS = {
    'prepared_at',
    'status',
    'stale_after_hours',
    'sources',
}

ALLOWED_WEEK_KEYS = {'start', 'timezone'}
ALLOWED_SOURCE_KEYS = {'name', 'as_of'}
ALLOWED_BLOCK_KEYS = {'id', 'day', 'start', 'end', 'kind', 'title'}
ALLOWED_ITEM_KEYS = {'id', 'title', 'kind', 'day', 'block_id'}
ALLOWED_RECURRING_KEYS = {'id', 'title', 'cadence', 'days'}

VALID_WEEKDAYS = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}
VALID_SOURCE_NAMES = {'tasks', 'calendar', 'email', 'shifts', 'recurring'}
VALID_BLOCK_KINDS = {'fixed', 'focus', 'admin', 'household', 'travel'}
VALID_ITEM_KINDS = {'task', 'event', 'household'}
VALID_CADENCES = {'daily', 'weekly'}

import zoneinfo
import re

TIME_RE = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d$')


@dataclass
class PlanningSnapshot:
    state: str  # 'fresh' | 'stale' | 'empty' | 'failed'
    label: str = ""
    prepared_at: Optional[datetime] = None
    age_hours: Optional[float] = None
    stale_after_hours: Optional[int] = None
    week: dict = field(default_factory=dict)
    sources: list[dict] = field(default_factory=list)
    blocks: list[dict] = field(default_factory=list)
    items: list[dict] = field(default_factory=list)
    recurring: list[dict] = field(default_factory=list)
    reason_code: Optional[str] = None


def parse_planning_snapshot(manifest_yaml: str, now: Optional[datetime] = None) -> PlanningSnapshot:
    """
    Parse a planning manifest YAML into a PlanningSnapshot.
    Validates according to manifest v1 rules.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    try:
        data = yaml.safe_load(manifest_yaml)
    except yaml.YAMLError:
        return PlanningSnapshot(state="failed", reason_code="invalid_yaml")

    if not isinstance(data, dict):
        return PlanningSnapshot(state="failed", reason_code="invalid_structure")

    # Reject unknown fields
    if any(k not in ALLOWED_MANIFEST_KEYS for k in data.keys()):
        return PlanningSnapshot(state="failed", reason_code="unknown_field")

    # schema_version must be 1
    if data.get('schema_version') != 1:
        return PlanningSnapshot(state="failed", reason_code="unsupported_schema_version")

    # synthetic must be True
    if data.get('synthetic') is not True:
        return PlanningSnapshot(state="failed", reason_code="synthetic_required")

    # label
    label = str(data.get('label', ''))

    # run validation
    run = data.get('run')
    if not isinstance(run, dict):
        return PlanningSnapshot(state="failed", reason_code="invalid_run")

    if any(k not in ALLOWED_RUN_KEYS for k in run.keys()):
        return PlanningSnapshot(state="failed", reason_code="unknown_field")

    # prepared_at
    prepared_at_raw = run.get('prepared_at')
    if not isinstance(prepared_at_raw, str):
        return PlanningSnapshot(state="failed", reason_code="invalid_prepared_at")
    try:
        prepared_at = datetime.fromisoformat(prepared_at_raw)
    except ValueError:
        return PlanningSnapshot(state="failed", reason_code="invalid_prepared_at")
    if prepared_at.tzinfo is None:
        return PlanningSnapshot(state="failed", reason_code="timezone_offset_required")

    # stale_after_hours
    stale_after_hours = run.get('stale_after_hours')
    if not isinstance(stale_after_hours, int) or stale_after_hours <= 0:
        return PlanningSnapshot(state="failed", reason_code="invalid_stale_after_hours")

    # status
    run_status = run.get('status')
    if run_status not in ('succeeded', 'failed'):
        return PlanningSnapshot(state="failed", reason_code="invalid_run_status")

    if run_status == 'failed':
        return PlanningSnapshot(
            state="failed",
            label=label,
            prepared_at=prepared_at,
            stale_after_hours=stale_after_hours,
            reason_code="run_status_failed",
        )

    # sources
    sources_raw = run.get('sources', [])
    if not isinstance(sources_raw, list):
        return PlanningSnapshot(state="failed", reason_code="invalid_sources")
    sources = []
    for s in sources_raw:
        if not isinstance(s, dict):
            return PlanningSnapshot(state="failed", reason_code="invalid_source_entry")
        if any(k not in ALLOWED_SOURCE_KEYS for k in s.keys()):
            return PlanningSnapshot(state="failed", reason_code="unknown_field")
        if s.get('name') not in VALID_SOURCE_NAMES or 'as_of' not in s:
            return PlanningSnapshot(state="failed", reason_code="invalid_source_entry")
        # Validate as_of format (ISO 8601 with offset)
        as_of_raw = s.get('as_of')
        if not isinstance(as_of_raw, str):
            return PlanningSnapshot(state="failed", reason_code="invalid_source_as_of")
        try:
            as_of_dt = datetime.fromisoformat(as_of_raw)
            if as_of_dt.tzinfo is None:
                return PlanningSnapshot(state="failed", reason_code="invalid_source_as_of")
        except ValueError:
            return PlanningSnapshot(state="failed", reason_code="invalid_source_as_of")
        sources.append(s)

    # week
    week = data.get('week')
    if not isinstance(week, dict) or 'start' not in week or 'timezone' not in week:
        return PlanningSnapshot(state="failed", reason_code="invalid_week")
    if any(k not in ALLOWED_WEEK_KEYS for k in week.keys()):
        return PlanningSnapshot(state="failed", reason_code="unknown_field")

    # Timezone validation
    tz_name = str(week['timezone'])
    try:
        zoneinfo.ZoneInfo(tz_name)
    except Exception:
        return PlanningSnapshot(state="failed", reason_code="invalid_timezone")

    try:
        start_date = date.fromisoformat(str(week['start']))
    except ValueError:
        return PlanningSnapshot(state="failed", reason_code="invalid_week_start")
    if start_date.weekday() != 0:  # Monday is 0
        return PlanningSnapshot(state="failed", reason_code="week_start_not_monday")

    # blocks
    blocks_raw = data.get('blocks', [])
    if not isinstance(blocks_raw, list):
        return PlanningSnapshot(state="failed", reason_code="invalid_blocks")
    blocks = []
    for b in blocks_raw:
        if not isinstance(b, dict):
            return PlanningSnapshot(state="failed", reason_code="invalid_block_entry")
        if any(k not in ALLOWED_BLOCK_KEYS for k in b.keys()):
            return PlanningSnapshot(state="failed", reason_code="unknown_field")
        if 'id' not in b or not str(b['id']).strip():
            return PlanningSnapshot(state="failed", reason_code="missing_id")
        if b.get('day') not in VALID_WEEKDAYS:
            return PlanningSnapshot(state="failed", reason_code="invalid_weekday")
        start_str = str(b.get('start', ''))
        end_str = str(b.get('end', ''))
        if not TIME_RE.match(start_str) or not TIME_RE.match(end_str):
            return PlanningSnapshot(state="failed", reason_code="invalid_time_format")
        title = str(b.get('title', ''))
        if len(title) > 80:
            return PlanningSnapshot(state="failed", reason_code="title_too_long")
        if b.get('kind') not in VALID_BLOCK_KINDS:
            return PlanningSnapshot(state="failed", reason_code="invalid_block_kind")
        blocks.append(b)

    # items
    items_raw = data.get('items', [])
    if not isinstance(items_raw, list):
        return PlanningSnapshot(state="failed", reason_code="invalid_items")
    items = []
    for it in items_raw:
        if not isinstance(it, dict):
            return PlanningSnapshot(state="failed", reason_code="invalid_item_entry")
        if any(k not in ALLOWED_ITEM_KEYS for k in it.keys()):
            return PlanningSnapshot(state="failed", reason_code="unknown_field")
        if 'id' not in it or not str(it['id']).strip():
            return PlanningSnapshot(state="failed", reason_code="missing_id")
        if 'day' in it and it['day'] is not None and it['day'] not in VALID_WEEKDAYS:
            return PlanningSnapshot(state="failed", reason_code="invalid_weekday")
        title = str(it.get('title', ''))
        if len(title) > 80:
            return PlanningSnapshot(state="failed", reason_code="title_too_long")
        if it.get('kind') not in VALID_ITEM_KINDS:
            return PlanningSnapshot(state="failed", reason_code="invalid_item_kind")
        items.append(it)

    # recurring
    recurring_raw = data.get('recurring', [])
    if not isinstance(recurring_raw, list):
        return PlanningSnapshot(state="failed", reason_code="invalid_recurring")
    recurring = []
    for r in recurring_raw:
        if not isinstance(r, dict):
            return PlanningSnapshot(state="failed", reason_code="invalid_recurring_entry")
        if any(k not in ALLOWED_RECURRING_KEYS for k in r.keys()):
            return PlanningSnapshot(state="failed", reason_code="unknown_field")
        if 'id' not in r or not str(r['id']).strip():
            return PlanningSnapshot(state="failed", reason_code="missing_id")
        title = str(r.get('title', ''))
        if len(title) > 80:
            return PlanningSnapshot(state="failed", reason_code="title_too_long")
        if r.get('cadence') not in VALID_CADENCES:
            return PlanningSnapshot(state="failed", reason_code="invalid_recurring_cadence")
        days = r.get('days', [])
        if not isinstance(days, list) or any(d not in VALID_WEEKDAYS for d in days):
            return PlanningSnapshot(state="failed", reason_code="invalid_weekday")
        recurring.append(r)

    # Calculate age
    age_seconds = (now - prepared_at).total_seconds()
    age_hours = max(0.0, age_seconds / 3600.0)

    # Determine state: empty, fresh, or stale
    if not blocks and not items and not recurring:
        state = "empty"
    elif age_hours > stale_after_hours:
        state = "stale"
    else:
        state = "fresh"

    return PlanningSnapshot(
        state=state,
        label=label,
        prepared_at=prepared_at,
        age_hours=age_hours,
        stale_after_hours=stale_after_hours,
        week=week,
        sources=sources,
        blocks=blocks,
        items=items,
        recurring=recurring,
    )


SCENARIO_CONFIG = {
    'fresh': {'fixture': 'fresh.yaml', 'offset_hours': 2},
    'stale': {'fixture': 'stale.yaml', 'offset_hours': 50},
    'empty': {'fixture': 'empty.yaml', 'offset_hours': 2},
    'failed': {'fixture': 'failed.yaml', 'offset_hours': 2},
}


def load_scenario_snapshot(scenario: str) -> tuple[PlanningSnapshot, datetime]:
    """
    Loads fixture for the requested scenario and parses it with simulated now clock.
    Returns (snapshot, simulated_now).
    Raises ValueError if scenario is unknown or fixture is missing.
    """
    if scenario not in SCENARIO_CONFIG:
        raise ValueError(f"Unknown scenario: {scenario}")

    cfg = SCENARIO_CONFIG[scenario]
    fixture_path = Path(__file__).parent / "fixtures" / "planning" / cfg['fixture']
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    raw_yaml = fixture_path.read_text(encoding="utf-8")

    # Determine prepared_at to set simulated now
    try:
        raw_data = yaml.safe_load(raw_yaml)
        prepared_at_raw = raw_data.get('run', {}).get('prepared_at')
        base_prepared_at = datetime.fromisoformat(prepared_at_raw)
    except Exception:
        base_prepared_at = datetime(2026, 10, 12, 8, 0, 0, tzinfo=timezone.utc)

    from datetime import timedelta
    simulated_now = base_prepared_at + timedelta(hours=cfg['offset_hours'])
    snapshot = parse_planning_snapshot(raw_yaml, now=simulated_now)
    return snapshot, simulated_now
