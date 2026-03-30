from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask

# --- Setup ---
owner = Owner(
    name="Jordan",
    available_start=time(7, 0),
    available_end=time(21, 0),
)

# --- Pets ---
luna = Pet(name="Luna", species="dog", age=3)
milo = Pet(name="Milo", species="cat", age=5)

# --- Tasks added OUT OF ORDER (low -> medium -> high) to prove sorting works ---
luna.add_task(Task(id=1, title="Grooming",     duration_minutes=20, priority="low",    frequency="once",   preferred_time=time(11, 0)))
luna.add_task(Task(id=2, title="Evening Walk", duration_minutes=30, priority="high",   frequency="daily",  preferred_time=time(18, 0)))
luna.add_task(Task(id=3, title="Morning Walk", duration_minutes=30, priority="high",   frequency="daily",  preferred_time=time(7, 0)))

milo.add_task(Task(id=4, title="Enrichment Play",  duration_minutes=15, priority="medium", frequency="once",  preferred_time=time(10, 0)))
milo.add_task(Task(id=5, title="Litter Box Clean", duration_minutes=5,  priority="medium", frequency="daily", preferred_time=time(9, 0)))
milo.add_task(Task(id=6, title="Feeding",          duration_minutes=10, priority="high",   frequency="daily", preferred_time=time(8, 0)))

# Mark one task as completed to prove recurring logic filters it out
luna.tasks[0].mark_complete()  # Grooming (once) — should be skipped

scheduler = Scheduler(owner=owner)
scheduler.add_pet(luna)
scheduler.add_pet(milo)

# ── 1. SORTING DEMO ───────────────────────────────────────────────────────────
print("=" * 50)
print("  1. ALL TASKS (as added — unsorted)")
print("=" * 50)
for t in scheduler.get_all_tasks():
    pt = t.preferred_time.strftime("%I:%M %p") if t.preferred_time else "none"
    print(f"  [{t.priority:6}] {t.pet_name}: {t.title} (preferred: {pt})")

print()
print("=" * 50)
print("  2. SORTED by priority + preferred_time")
print("=" * 50)
sorted_tasks = scheduler._sort_by_priority(scheduler.get_all_tasks())
for t in sorted_tasks:
    pt = t.preferred_time.strftime("%I:%M %p") if t.preferred_time else "none"
    print(f"  [{t.priority:6}] {t.pet_name}: {t.title} (preferred: {pt})")

# ── 2. FILTERING DEMO ─────────────────────────────────────────────────────────
print()
print("=" * 50)
print("  3. FILTER — high priority tasks only")
print("=" * 50)
for t in scheduler.filter_by_priority("high"):
    print(f"  {t.pet_name}: {t.title}")

print()
print("=" * 50)
print("  4. FILTER — Luna's tasks only")
print("=" * 50)
for t in scheduler.filter_by_pet("Luna"):
    status = "DONE" if t.is_completed else "pending"
    print(f"  [{status}] {t.title} ({t.priority})")

# ── 3. RECURRING TASKS DEMO ───────────────────────────────────────────────────
print()
print("=" * 50)
print("  5. RECURRING — eligible tasks for today")
print("     (completed one-time tasks are excluded)")
print("=" * 50)
for t in scheduler.generate_recurring_tasks():
    print(f"  {t.pet_name}: {t.title} (frequency: {t.frequency})")

# ── 4. FULL SCHEDULE ──────────────────────────────────────────────────────────
print()
print("=" * 50)
print(f"  6. TODAY'S SCHEDULE for {owner.name}")
print(f"     Window: {owner.available_start.strftime('%I:%M %p')} – {owner.available_end.strftime('%I:%M %p')}")
print("=" * 50)
schedule = scheduler.build_schedule()
for st in schedule:
    print(f"  {st.to_display_string()}")

if scheduler.skipped_tasks:
    print()
    print("  Skipped (did not fit in window):")
    for t in scheduler.skipped_tasks:
        print(f"    - {t.pet_name}: {t.title} ({t.duration_minutes} min)")

print(f"\n  Scheduled: {len(schedule)} | Skipped: {len(scheduler.skipped_tasks)}")
print("=" * 50)

# ── 5. CONFLICT DETECTION DEMO ────────────────────────────────────────────────
print()
print("=" * 50)
print("  7. CONFLICT DETECTION")
print("=" * 50)
test_task = Task(id=99, title="Vet Visit", duration_minutes=60, priority="high")

# Propose a time that overlaps the first scheduled slot
first_slot_start = schedule[0].start_time
conflict = scheduler.check_conflicts(test_task, proposed_start=first_slot_start)
print(f"  'Vet Visit' at {first_slot_start.strftime('%I:%M %p')} (overlaps first slot) -> conflict: {conflict}")

# Propose a time well after the last scheduled task
last_slot_end = schedule[-1].end_time
no_conflict = scheduler.check_conflicts(test_task, proposed_start=last_slot_end)
print(f"  'Vet Visit' at {last_slot_end.strftime('%I:%M %p')} (after last slot)        -> conflict: {no_conflict}")
print("=" * 50)

# ── 6. WARN_CONFLICTS DEMO ────────────────────────────────────────────────────
print()
print("=" * 50)
print("  8. WARN_CONFLICTS — two tasks manually overlapping")
print("=" * 50)

# Force two tasks into the same time slot so warn_conflicts() has something to catch.
# Task A: Luna's Vet Visit at 10:00 AM, 60 min  → ends 11:00 AM
# Task B: Milo's Nail Trim  at 10:30 AM, 30 min  → ends 11:00 AM (30-min overlap)
conflict_task_a = Task(id=91, title="Vet Visit", duration_minutes=60, priority="high",   pet_name="Luna")
conflict_task_b = Task(id=92, title="Nail Trim", duration_minutes=30, priority="medium", pet_name="Milo")

scheduler.scheduled_tasks.append(ScheduledTask(task=conflict_task_a, start_time=time(10, 0),  reason="manually injected"))
scheduler.scheduled_tasks.append(ScheduledTask(task=conflict_task_b, start_time=time(10, 30), reason="manually injected"))

warnings = scheduler.warn_conflicts()
if warnings:
    for msg in warnings:
        print(f"  {msg}")
else:
    print("  No conflicts detected.")
print("=" * 50)
