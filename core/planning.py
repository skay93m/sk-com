"""
core/planning.py - Snapshot parsing and data structures for the synthetic planning page.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
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

VALID_SOURCE_NAMES = {'tasks', 'calendar', 'email', 'shifts', 'recurring'}
VALID_BLOCK_KINDS = {'fixed', 'focus', 'admin', 'household', 'travel'}
VALID_ITEM_KINDS = {'task', 'event', 'household'}
VALID_CADENCES = {'daily', 'weekly'}


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

    # sources
    sources_raw = run.get('sources', [])
    if not isinstance(sources_raw, list):
        return PlanningSnapshot(state="failed", reason_code="invalid_sources")
    sources = []
    for s in sources_raw:
        if not isinstance(s, dict) or s.get('name') not in VALID_SOURCE_NAMES or 'as_of' not in s:
            return PlanningSnapshot(state="failed", reason_code="invalid_source_entry")
        sources.append(s)

    # week
    week = data.get('week')
    if not isinstance(week, dict) or 'start' not in week or 'timezone' not in week:
        return PlanningSnapshot(state="failed", reason_code="invalid_week")

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
        title = str(r.get('title', ''))
        if len(title) > 80:
            return PlanningSnapshot(state="failed", reason_code="title_too_long")
        if r.get('cadence') not in VALID_CADENCES:
            return PlanningSnapshot(state="failed", reason_code="invalid_recurring_cadence")
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
