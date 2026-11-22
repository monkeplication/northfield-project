# Explanation Notes

All six building blocks are in `src/solutions.py`. "n" means the number of items given to a function.

## 1. Matching part labels: `labels_match`

Labels of different lengths cannot match. Otherwise I count how often each of the 26 letters appears in each label and compare the two tallies. That is O(n) time and O(1) extra memory, because there are always just 26 counters. The warehouse can match a misprint like "ktesco" to "socket" instead of logging an unknown part.

## 2. Grouping scrambled part codes: `group_families`

Each code gets a fingerprint, its 26 letter counts, and codes with the same fingerprint are kept together in a dictionary. Each letter is read once, so it is O(n × k) time and memory, where k is the longest code. Service centres get one record per part family, and repeated codes keep every occurrence.

## 3. Counting matching work windows: `count_windows`

I keep a running total of energy and remember how often each total has appeared. Whenever an earlier total equals the current total minus k, the slots in between add up to exactly k, so I add that number to the answer. One pass gives O(n) time and O(n) memory, and unlike a sliding window it works with negative readings. Finance can count periods with a target energy use without checking every start and end pair.

## 4. Most frequent fault codes: `top_faults`

I count every fault code once, then pick the k biggest counts while keeping only a short list of the current top k. That is O(n + d log k) time and O(d) memory, where d is the number of distinct codes. Service centres see the faults that matter most first. In the fleet report, codes tied at the cut-off are all shown.

## 5. Merging overlapping usage sessions: `merge_sessions`

I sort sessions by start time and walk through them once. A session that starts before or exactly when the current block ends extends that block; otherwise it starts a new block. That is O(n log n) time because of the sort, plus O(n) memory. It stops finance counting the same minutes twice: 453 minutes on 2 November.

## 6. Latest state per tool: `latest_state`

Bugs in the original:

1. **Shared memory between calls.** The default `result={}` is created once and reused, and callers can pass their own dictionary in, so earlier data leaks into later answers.
2. **Keeps the oldest event, not the newest.** `ts < ...` replaces the stored state whenever an *earlier* event arrives, so each tool ends up holding its oldest state. It must be `>=` so the newest event is kept and, on an exact timestamp tie, the later-arriving event wins.
3. **Missing timestamps are not ignored.** An empty or blank timestamp sorts before every real time, and `None` crashes the comparison.

```python
def latest_state(events):
    latest = {}
    for tool_id, ts, state in events:
        if not ts or not ts.strip():
            continue
        if tool_id not in latest or ts >= latest[tool_id][0]:
            latest[tool_id] = (ts, state)
    return {tool_id: state for tool_id, (_, state) in latest.items()}
```

Timestamps are fixed-width and zero-padded, so comparing them as text gives the right time order. On equal timestamps the later-arriving event wins. It takes O(n) time and O(number of tools) memory. Site managers get each tool's true current state, including safety states.

## Assumptions and messy-data handling

- **Duplicates:** a repeated `event_id` is a resend. All 8 were exact copies, so I kept the first.
- **Missing timestamp (1 row):** dropped, because it cannot be placed in the energy slot order.
- **Outside the reporting day (1 row, NT-105, dated 2026-11-09):** dropped. Its session 384–424 lies inside an existing NT-105 block, so merged minutes do not change either way.
- **Validity checks:** whitespace is stripped and states, session order and numbers are checked. No rows failed.
- **Session times:** taken as given, ignoring the upload timestamp. A session lasts `end - start` minutes. Some sessions run between 00:18 and 03:36, before any event timestamp; I kept them at face value.
- **Activity:** a non-zero energy reading, a fault, or a session still running counts as activity. Zero energy and part scans do not.
- **Part names:** the 8 unscrambled labels found in the data are taken as the catalogue.
- **Ties:** fault codes tied at the top-k cut-off are all included. For state, the later-arriving event wins.
