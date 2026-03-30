# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- My initial UML design for PawPal+ focused on separating the system into clear object-oriented components so that each class had a single responsibility. Since the app needs to collect pet and owner information, manage care tasks, and generate a daily plan, I'll design the system around those three major responsibilities.

- What classes did you include, and what responsibilities did you assign to each?
-For the classes:
The main classes I included were:

- Owner
- The Owner class stores information about the pet owner, such as name, available time for the day, and any preferences that affect scheduling. Its responsibility is to represent the person using the system and provide planning constraints, such as how many minutes they have available for pet care.

- Pet
- The Pet class stores the pet’s details, such as name, species, breed, age, and any notes relevant to care. Its responsibility is to represent the pet and act as the central object to which care tasks are connected.

- Task
- The Task class represents a pet care activity, such as feeding, walking, medication, grooming, or enrichment. I gave this class attributes such as task name, category, duration, priority, required status, and optional preferences like preferred time of day. Its responsibility is to model an individual care activity in a way the scheduler can evaluate.

- DailyPlan / Schedule
- I included a DailyPlan or Schedule class to store the results of scheduling. Its responsibility is to hold the selected tasks for the day, total planned time, skipped tasks, and explanation text describing why certain tasks were included or left out.

- Scheduler / Planner
- The Scheduler class is responsible for the core algorithmic logic. It takes the list of tasks, the owner’s available time, and any preferences or constraints, then generates the best daily plan. This class handles prioritization, time fitting, and plan explanation.

Owner provides constraints
Pet represents the animal being cared for
Task represents individual care needs
Scheduler makes decisions
DailyPlan stores the final output

**b. Design changes**

Several things changed when the initial UML was converted into actual Python stubs:

1. **`DailyPlan` was removed, replaced by `ScheduledTask`.**
   The initial design included a `DailyPlan` class to hold the full day's output (selected tasks, total time, skipped tasks, explanation). During implementation, this was replaced by a list of individual `ScheduledTask` objects. Each `ScheduledTask` wraps one `Task` with an assigned `start_time`, `end_time`, and a `reason` string. This is more granular — it lets the UI display per-task reasoning rather than one bulk explanation — but it means there is no longer a single object representing the complete day's plan.

2. **`Task.category` and `Pet.breed` were dropped.**
   The initial design mentioned a `category` attribute on `Task` (e.g., feeding, grooming) and implied `breed` on `Pet`. Neither made it into the stubs because neither is needed by the scheduling algorithm — `priority` and `duration_minutes` are the inputs that actually drive decisions. These can be added back later if the UI needs them for display purposes.

3. **`remove_task` signature changed from `task_title: str` to `task_id: int`.**
   The original stub used the task title as a lookup key, which is fragile if two tasks share the same name. Fixed by adding an `id: int` field to `Task` and updating `remove_task` to use that instead. IDs are unique by definition, titles are not.

4. **`Task.pet_name` added to preserve ownership context.**
   Tasks are stored on `Pet.tasks`, but once `Scheduler.get_all_tasks()` flattens everything into one list, the pet association is lost. Fixed by adding an optional `pet_name: str` field to `Task`, which `Pet.add_task()` will set when a task is registered. This lets the scheduler and UI display "Luna: Morning Walk" without needing to reverse-lookup the pet.

5. **`ScheduledTask.end_time` converted from a stored field to a `@property`.**
   Storing `end_time` as a plain attribute meant it could go stale if `start_time` or `task.duration_minutes` changed. Fixed by removing it from `__init__` and making it a computed `@property`, so it is always derived on demand and can never be inconsistent.

6. **`build_schedule()` broken into private helpers `_sort_by_priority()` and `_assign_time_slots()`.**
   The original single method was responsible for collecting tasks, sorting, fitting to the time window, conflict checking, and producing `ScheduledTask` objects — too many responsibilities to implement or test cleanly. Fixed by extracting two private helpers and having `build_schedule()` orchestrate them. Each helper can now be tested independently.

7. **`Scheduler.scheduled_tasks` dual-role resolved.**
   Previously unclear whether `self.scheduled_tasks` or the return value of `build_schedule()` was the source of truth. Fixed by having `build_schedule()` write to `self.scheduled_tasks` and also return it, making both consistent and unambiguous.

8. **`explain_plan()` removed.**
   The per-task `reason` field on `ScheduledTask` already covers this. A separate method that returned a monolithic string would duplicate that logic and be harder to test. Removed in favour of using `ScheduledTask.reason` directly in the UI.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: the owner's available time window, task priority, and preferred time of day.

The available time window is the hard outer boundary — no task can be scheduled before `available_start` or end after `available_end`. This is non-negotiable because the owner simply cannot act outside those hours.

Within that window, priority is the primary ordering rule. Tasks are ranked high → medium → low using `PRIORITY_ORDER`, so critical care needs like feeding and medication always claim time slots before optional activities like grooming. This matters most when the window is tight and not everything can fit.

Preferred time acts as a tiebreaker within the same priority level. If two high-priority tasks both need to be placed and one has `preferred_time=time(7, 0)`, it is sorted ahead of one with `preferred_time=time(18, 0)`. This lets the schedule respect natural rhythms — a morning walk lands near morning — without overriding priority.

The decision to rank these in that order (window → priority → preferred time) came from asking what causes the most harm if violated. Missing the time window entirely means the task cannot happen. Ignoring priority means a pet's medical need could be bumped by a low-stakes activity. Ignoring a preferred time is the least harmful — a walk scheduled 30 minutes later than ideal is still a walk.

**b. Tradeoffs**

The scheduler uses a greedy first-fit algorithm: it sorts tasks by priority, then assigns them one at a time from the start of the available window, advancing the clock after each placement. If a task does not fit in the remaining time, it is skipped and added to `skipped_tasks` — the algorithm never backtracks or tries rearranging earlier tasks to make room.

The tradeoff is scheduling completeness for simplicity. A more optimal algorithm — such as a bin-packing solver or dynamic programming approach — could potentially fit more tasks into the same window by trying different orderings. For example, if a 60-minute low-priority task fills the last available slot, a 15-minute high-priority task that arrived later gets skipped, even though swapping them would have fit both. The greedy approach will not catch that.

This tradeoff is reasonable for a daily pet care app for two reasons. First, the number of tasks is small — a typical owner might have 5 to 15 tasks across one or two pets — so even a suboptimal schedule rarely leaves out more than one or two items. The gap between greedy and optimal is negligible at that scale. Second, the owner sees the skipped tasks list and can manually adjust priorities or durations for the next run, which is a simpler and more transparent recovery path than a black-box optimizer silently reordering their day. Predictability matters more than perfection when a person has to actually follow the schedule.

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
