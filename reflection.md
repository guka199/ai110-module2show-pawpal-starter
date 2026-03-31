# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Add/Edit a Pet Task — Create a care task (walk, feeding, meds, grooming, enrichment) with a duration and priority level.

Generate Daily Schedule — Auto-plan the day based on available time, task priorities, and constraints.

Set Owner & Pet Profile — Enter basic info (owner name, pet name, breed, available time per day) that constraints the planner.


View Schedule & Reasoning — See the generated daily plan with an explanation of why tasks were ordered/prioritized that way.

**b. Design changes**

Yes, several changes were made after reviewing the initial skeleton:

- **`Task` gained a `pet` reference** — the initial design had tasks as global, but tasks need to belong to a specific pet (e.g. Mochi's walk vs. Bella's feeding).
- **`Scheduler.tasks` changed from a flat list to `Dict[Pet, List[Task]]`** — to support multiple pets per owner without mixing their tasks together.
- **`DailyPlan` now holds an `owner` reference** — so the plan retains context of who it was generated for, enabling meaningful display and reasoning output.
- **`Owner` gained `spend_time()` and `reset_time()`** — the original `available_minutes` was a static field with no way to track time consumed during scheduling.
- **`priority` and `category` became enums** — raw strings like `"high"` are fragile to sort and compare; enums enforce valid values and make priority ordering reliable.
- **`explain_plan()` was removed from `Scheduler`** — reasoning is now built inside `DailyPlan` via `add_entry(task, reason)`, avoiding duplicated responsibility across two classes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector checks for exact `start_time` string matches rather than overlapping time windows. Two tasks at `"08:00"` and `"08:15"` will not be flagged even if the first task takes 30 minutes and clearly overlaps the second. This means some real conflicts go undetected. The tradeoff is reasonable for this stage because it keeps the logic simple and avoids needing end-time calculations — it still catches the most obvious double-bookings (same time slot) without adding significant complexity to the scheduler.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
