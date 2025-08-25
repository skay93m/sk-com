# Product Backlog Management Template

## Backlog Information
- **Product**: [Product name]
- **Product Owner**: [Name]
- **Last Updated**: [DD/MM/YYYY]
- **Next Grooming Session**: [DD/MM/YYYY]

## Product Vision & Goals
**Product Vision**: [One-sentence vision statement]

**Product Goals**:
1. [Primary goal]
2. [Secondary goal]
3. [Tertiary goal]

## Epic Overview
| Epic ID | Epic Name | Status | Priority | Story Count | Story Points | Target Release |
|---------|-----------|--------|----------|-------------|--------------|----------------|
| EP-001 | [Epic name] | Active | High | 8 | 34 | v1.0 |
| EP-002 | [Epic name] | Planned | Medium | 5 | 21 | v1.1 |
| EP-003 | [Epic name] | Planned | Low | 3 | 13 | v2.0 |

## Prioritized Backlog
*Stories ordered by priority (highest to lowest)*

### Epic: [Epic Name] (EP-001)
| Story ID | Title | Priority | Story Points | Status | Sprint | Notes |
|----------|-------|----------|--------------|--------|--------|-------|
| US-001 | [Story title] | 1 | 8 | Done | Sprint 1 | [Notes] |
| US-002 | [Story title] | 2 | 5 | In Progress | Sprint 2 | [Notes] |
| US-003 | [Story title] | 3 | 3 | Ready | Backlog | [Notes] |
| US-004 | [Story title] | 4 | 5 | Draft | Backlog | [Notes] |

### Epic: [Epic Name] (EP-002)
| Story ID | Title | Priority | Story Points | Status | Sprint | Notes |
|----------|-------|----------|--------------|--------|--------|-------|
| US-005 | [Story title] | 5 | 2 | Ready | Backlog | [Notes] |
| US-006 | [Story title] | 6 | 8 | Draft | Backlog | [Notes] |

## Backlog Health Metrics
- **Total Stories**: [Number]
- **Ready Stories**: [Number with clear acceptance criteria]
- **Estimated Stories**: [Number with story points]
- **Groomed Stories**: [Number ready for sprint planning]
- **Average Story Size**: [Story points]

## Story Status Definitions
- **Draft**: Initial story idea, needs refinement
- **Groomed**: Story is detailed with acceptance criteria
- **Ready**: Story meets Definition of Ready
- **In Progress**: Story is being worked on
- **Done**: Story meets Definition of Done

## Backlog Grooming Schedule
| Date | Duration | Participants | Focus | Stories Groomed |
|------|----------|--------------|-------|-----------------|
| [Date] | 1 hour | PO, SM, Team | Epic 1 | US-003, US-004 |
| [Date] | 1 hour | PO, SM, Team | Epic 2 | US-005, US-006 |

## User Story Priorities
### Priority 1 (Must Have) - Release 1.0
- [ ] US-001: [Brief description]
- [ ] US-002: [Brief description]
- [ ] US-003: [Brief description]

### Priority 2 (Should Have) - Release 1.0
- [ ] US-004: [Brief description]
- [ ] US-005: [Brief description]

### Priority 3 (Could Have) - Release 1.1
- [ ] US-006: [Brief description]
- [ ] US-007: [Brief description]

### Priority 4 (Won't Have This Time) - Future
- [ ] US-008: [Brief description]
- [ ] US-009: [Brief description]

## Dependencies Map
```
Epic 1 (Authentication)
├── US-001 (User Registration) → US-002 (User Login)
├── US-002 (User Login) → US-003 (Password Reset)
└── US-003 (Password Reset)

Epic 2 (Core Features)
├── US-004 (Dashboard) ← Depends on US-002
├── US-005 (Settings) ← Depends on US-002
└── US-006 (Reports) ← Depends on US-004
```

## Stakeholder Feedback
| Date | Stakeholder | Feedback | Impact | Action Taken |
|------|-------------|----------|--------|--------------|
| [Date] | [Name/Role] | [Feedback summary] | High/Med/Low | [Action] |

## Technical Debt & Bugs
| Item ID | Description | Priority | Story Points | Planned Sprint |
|---------|-------------|----------|--------------|----------------|
| TD-001 | [Technical debt item] | High | 5 | Sprint 3 |
| BUG-001 | [Bug description] | Critical | 2 | Sprint 2 |

## Backlog Refinement Notes
### Session: [Date]
**Participants**: [Names]
**Duration**: [Time]

**Stories Refined**:
- US-003: Added acceptance criteria, estimated at 3 points
- US-004: Split into smaller stories, dependencies identified
- US-005: Needs UX mockups before next session

**Decisions Made**:
- [Decision 1]
- [Decision 2]

**Action Items**:
- [ ] [Action item 1] - [Owner] - [Due date]
- [ ] [Action item 2] - [Owner] - [Due date]

## Release Planning
### Release 1.0 (MVP)
**Target Date**: [DD/MM/YYYY]
**Goal**: [Release goal]
**Features**:
- [Feature 1] (Epic 1)
- [Feature 2] (Epic 1)

**Story Points**: [Total points]
**Estimated Sprints**: [Number based on velocity]

### Release 1.1
**Target Date**: [DD/MM/YYYY]
**Goal**: [Release goal]
**Features**:
- [Feature 3] (Epic 2)
- [Feature 4] (Epic 2)

## Backlog Management Rules
1. **Priority Changes**: Only Product Owner can change story priorities
2. **New Stories**: All new stories must go through grooming before sprint planning
3. **Story Size**: Stories larger than 8 points must be broken down
4. **Definition of Ready**: Stories must meet DoR before sprint planning
5. **Estimation**: Use planning poker for story point estimation
6. **Dependencies**: Identify and document all dependencies during grooming

## Metrics & KPIs
- **Velocity**: [Average story points per sprint]
- **Lead Time**: [Average time from idea to delivery]
- **Cycle Time**: [Average time from start to done]
- **Throughput**: [Stories completed per sprint]
- **Backlog Growth Rate**: [New stories vs completed stories]

## Backlog Review Checklist
- [ ] All high-priority stories have clear acceptance criteria
- [ ] Dependencies are identified and documented
- [ ] Story estimates are current and agreed upon
- [ ] Backlog is prioritized based on business value
- [ ] Technical debt is balanced with new features
- [ ] Stories meet Definition of Ready criteria
- [ ] Epic progress is tracked and communicated

---

**Backlog Maintained By**: [Product Owner name]  
**Last Review Date**: [DD/MM/YYYY]  
**Next Review Date**: [DD/MM/YYYY]