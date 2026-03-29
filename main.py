from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(
    name="Jordan",
    available_start=time(7, 0),
    available_end=time(21, 0),
)

# --- Pets ---
luna = Pet(name="Luna", species="dog", age=3)
milo = Pet(name="Milo", species="cat", age=5)

# --- Tasks for Luna ---
luna.add_task(Task(id=1, title="Morning Walk",  duration_minutes=30, priority="high",   preferred_time=time(7, 0)))
luna.add_task(Task(id=2, title="Evening Walk",  duration_minutes=30, priority="high",   preferred_time=time(18, 0)))
luna.add_task(Task(id=3, title="Grooming",      duration_minutes=20, priority="low",    preferred_time=time(11, 0)))

# --- Tasks for Milo ---
milo.add_task(Task(id=4, title="Feeding",          duration_minutes=10, priority="high",   preferred_time=time(8, 0)))
milo.add_task(Task(id=5, title="Enrichment Play",  duration_minutes=15, priority="medium", preferred_time=time(10, 0)))
milo.add_task(Task(id=6, title="Litter Box Clean", duration_minutes=5,  priority="medium", preferred_time=time(9, 0)))

# --- Scheduler ---
scheduler = Scheduler(owner=owner)
scheduler.add_pet(luna)
scheduler.add_pet(milo)

schedule = scheduler.build_schedule()

# --- Output ---
print("=" * 45)
print(f"  PawPal+ — Today's Schedule for {owner.name}")
print("=" * 45)
print(f"  Window: {owner.available_start.strftime('%I:%M %p')} – {owner.available_end.strftime('%I:%M %p')}")
print(f"  Total available time: {owner.get_total_available_time()} minutes")
print(f"  Tasks scheduled: {len(schedule)} of {len(scheduler.get_all_tasks())}")
print("-" * 45)

for st in schedule:
    print(f"  {st.to_display_string()}")

print("=" * 45)
