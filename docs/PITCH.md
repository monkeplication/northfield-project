# Elevator Pitch: Speaking Points

## 1. Hook (5 s)
- "On 2 November, a tool showed IDLE from 07:26 and then logged nine more energy and fault events."

## 2. The problem (10 s)
- Service centres don't trust the dashboard numbers.
- I traced the cause to the data: resent events, overlapping session uploads and stale tool states.

## 3. What I built (15 s)
- Six small, tested building blocks in plain Python with no dependencies.
- They match scrambled part labels, merge overlapping sessions, find each tool's latest state and rank faults. Each is tested on 100,000 events and runs in well under a second.

## 4. What the data says (15 s)
- Two tools show IDLE but kept working, and one kept working after overheating.
- Usage is overstated by 21%: 453 minutes are counted twice.

## 5. Recommendation (10 s)
- Flag a state as stale when the tool's own activity contradicts it, and alert when a tool works after a safety state.
- Clean the data once, in the pipeline: drop resent events, merge sessions, group part families.
- Measure: tools whose state disagrees with their activity. That's 4 of 12 today, and the goal is 0.

## 6. Close (5 s)
- "Small, reliable pieces, each explainable in one sentence. That's how we make the numbers match the site."
