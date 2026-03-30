# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

The scheduling engine was extended beyond the basic greedy algorithm with four improvements:

**Sort by time**
`Scheduler.sort_by_time()` orders any task list by `preferred_time` (earliest first), using priority as a tiebreaker within the same time slot. Tasks with no preferred time are pushed to the end. This lets the UI render a time-ordered view independently of how tasks were added.

**Filter by pet and status**
`Scheduler.filter_tasks(pet_name, completed)` returns a filtered slice of all tasks. Both parameters are optional — pass one, both, or neither. `filter_by_pet()` and `filter_by_priority()` offer quick single-axis lookups.

**Recurring task support**
Tasks carry a `frequency` field (`"once"`, `"daily"`, `"weekly"`). `generate_recurring_tasks()` excludes completed one-time tasks while always surfacing daily and weekly ones. When a recurring task is marked complete via `Scheduler.complete_task()`, a fresh copy is automatically created and added back to the pet's task list for the next scheduling cycle.

**Conflict detection**
`get_all_conflicts()` performs a pairwise scan of all scheduled tasks and returns every overlapping pair with the overlap duration and whether the clash is within the same pet or across pets. `warn_conflicts()` wraps this into plain warning strings — no exceptions, no crashing — so callers only need `if warnings:` to handle the result.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **33 tests** across 7 test classes:

| Class | What it checks |
|---|---|
| `TestTask` | `mark_complete()`, priority flag, `fits_in_window()` boundary |
| `TestPet` | Adding/removing tasks, `pet_name` stamping |
| `TestOwner` | Available window tuple, total minutes calculation |
| `TestScheduledTask` | `end_time` computation, time range, display string format |
| `TestScheduler` | Pet registration, task flattening, schedule build order, skip-on-overflow |
| `TestSortingCorrectness` | Chronological order, `None` preferred_time sorts last, priority tiebreak |
| `TestRecurrenceLogic` | Daily task creates new occurrence, one-time task does not, completed tasks excluded from schedule, unique IDs across completions |
| `TestConflictDetection` | Exact same start time flagged, warning strings, normal schedule has zero conflicts, empty schedule is safe, overlap true/false boundary |

### Confidence Level

**★★★★☆ (4 / 5)**

The core scheduling contract — priority ordering, greedy slot assignment, recurring task lifecycle, and conflict detection — is fully covered and all 33 tests pass. One star is withheld because the Streamlit UI layer (`app.py`) has no automated tests; user-facing input handling and edge cases there are only verified manually.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
