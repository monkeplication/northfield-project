# Elevator Pitch: Speaking Points

## 1. Hook (5 s)
- "Adding up one day's usage sessions gives 2,613 minutes. The tools actually ran for 2,160."

## 2. The problem (10 s)
- Service centres don't trust the dashboard numbers.
- I traced the cause to the data: resent events, overlapping session uploads and stale tool states.

## 3. What I built (15 s)
- Six small, tested building blocks in plain Python with no dependencies.
- They match scrambled part labels, merge overlapping sessions, find each tool's latest state and rank faults. Each handles 100,000 events in under a tenth of a second.

## 4. What the data says (15 s)
- Usage is overstated by 21%: 453 minutes are counted twice.
- Two tools show IDLE but kept working, and three end the day in a safety state.

## 5. Recommendation (10 s)
- Deduplicate and merge sessions once, in the pipeline, not in every report.
- This helps finance, global operations and service centres. The measure of success is fewer "dashboard doesn't match site" reports each week.

## 6. Close (5 s)
- "Small, reliable pieces, each explainable in one sentence. That's how we make the numbers match the site."
