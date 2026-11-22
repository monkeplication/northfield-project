# Fleet Data Findings: 2 November 2026

Code: `src/fleet_findings.py`; full tables in the Excel workbook. Checks for bad states, session order and whitespace found nothing.

## Data cleaning log

| Problem | Action | Rows |
| --- | --- | --- |
| Duplicate event_id (exact copies) | Kept first copy | 8 |
| Missing timestamp (EV0060) | Dropped | 1 |
| Dated 2026-11-09 (EV0099) | Dropped | 1 |
| **Loaded / kept** | | **256 / 246** |

## Finding 1: summing raw sessions overstates usage by 21%

| Tool | Raw minutes | Merged minutes | Double counted |
| --- | --- | --- | --- |
| NT-102 | 452 | 309 | 143 |
| NT-112 | 227 | 157 | 70 |
| Fleet (12 tools) | 2,613 | 2,160 | **453** |

9 of 12 tools have overlapping sessions, so 453 minutes (7.5 hours) are counted twice.

## Finding 2: IDLE is wrong for 2 tools, and 3 tools end in a safety state

| Tool | Latest state | At | Reported afterwards |
| --- | --- | --- | --- |
| NT-106 | IDLE | 07:26 | 9 energy/fault events, 2 sessions |
| NT-112 | IDLE | 14:04 | 3 energy/fault events |
| NT-111 | OVERHEATED | 09:23 | 7 energy/fault events |
| NT-103 / NT-110 | OVERHEATED / OVERLOAD | 12:52 / 13:08 | 1 / 0 events |

NT-106 and NT-112 look idle but kept working. NT-111 kept working after overheating: either a stale state or unsafe use.

## Finding 3: four fault codes cause 85% of faults

| Fault code | Count | Share |
| --- | --- | --- |
| 205 | 8 | 31% |
| 101 | 6 | 23% |
| 620, 518 (tied) | 4 each | 15% each |
| 310, 412 | 3, 1 | 12%, 4% |

620 and 518 tie at the top-3 cut-off, so I include both instead of dropping one at random.

## Recommendation

**Deduplicate on `event_id` and merge overlapping sessions once, inside the cloud pipeline, before any dashboard or report reads the data.**

**Affects** finance, global operations and service centres. **Metric:** weekly "dashboard doesn't match site" reports from service centres, before vs after.
