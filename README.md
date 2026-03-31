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

## Smarter Scheduling

The scheduler includes four algorithmic improvements beyond basic task generation:

- **Sorting by time** — `Scheduler.sort_by_time(pet?)` returns tasks with a `start_time` ordered chronologically. Tasks added in any order will always display in the correct sequence.
- **Filtering** — `Scheduler.filter_tasks(pet_name?, completed?)` narrows the task list by pet name, completion status, or both. Useful for showing only a single pet's incomplete tasks.
- **Recurring tasks** — `Task` supports a `frequency` field (`"none"`, `"daily"`, `"weekly"`). Calling `mark_complete()` on a recurring task marks it done and returns a fresh copy ready for the next occurrence.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans all timed tasks and returns a warning string for every pair that shares the same `start_time` slot. Returns an empty list when no conflicts exist.

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite covers 20 test cases across six areas:

| Area | What's tested |
|---|---|
| Task completion | `mark_complete()` sets status; non-recurring returns `None` |
| Recurring tasks | Daily/weekly tasks return a fresh incomplete copy |
| Pet task management | `add_task()` increases count; new pet starts empty |
| Sorting | Chronological order, untimed tasks excluded, per-pet filter |
| Filtering | By pet name, completion status, and no criteria |
| Conflict detection | Same-time warning, different times, no timed tasks |
| Scheduler logic | Time budget respected, priority ordering, empty plan, validation errors |

**Confidence level: ★★★★☆** — all happy paths and key edge cases are covered. Overlap-aware conflict detection (tasks that span into each other's windows) is not yet tested.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
