# Northfield Site Systems: SDE Case Assessment

Vaibhav Singh

## Layout

| Path | What it is |
| --- | --- |
| `src/solutions.py` | The six building blocks (Deliverable A) |
| `tests/` | pytest tests, one file per problem, plus the fleet analysis |
| `src/fleet_findings.py` | Cleans the fleet data and computes the findings (Deliverable C code) |
| `data/northfield_fleet_events.csv` | The fleet data provided |
| `docs/NOTES.md` | Explanation notes (Deliverable B), including the Problem 6 bug list and fix |
| `docs/FINDINGS.md` | Fleet data findings (Deliverable C) |
| `docs/PITCH.md` | Elevator pitch speaking points |
| `submission/` | Word and Excel versions of the deliverables |
| `scripts/build_deliverables.py` | Rebuilds the Word and Excel files from the docs and data |

The solutions and analysis use only the Python standard library. pytest is used for tests. openpyxl and python-docx are used only to build the Word and Excel files.

## Run

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv run pytest
uv run python src/fleet_findings.py
uv run python scripts/build_deliverables.py
```

Run these from the repository root. To analyse a different file, pass its path: `uv run python src/fleet_findings.py path/to/file.csv`.

## Using the functions

```python
import sys; sys.path.insert(0, "src")
from solutions import labels_match, group_families, count_windows, top_faults, merge_sessions, latest_state
```
