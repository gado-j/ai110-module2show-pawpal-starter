from dataclasses import dataclass, field
from datetime import time, datetime, timedelta
from typing import List, Optional


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Owner:
    name: str
    available_start: time
    available_end: time

    def get_available_window(self) -> tuple:
        """Return the owner's available start and end times as a tuple."""
        return (self.available_start, self.available_end)

    def get_total_available_time(self) -> int:
        """Return the total number of minutes available between start and end times."""
        start_dt = datetime.combine(datetime.today(), self.available_start)
        end_dt = datetime.combine(datetime.today(), self.available_end)
        return int((end_dt - start_dt).total_seconds() // 60)


@dataclass
class Task:
    id: int
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    preferred_time: Optional[time] = None
    is_completed: bool = False
    pet_name: Optional[str] = None  # set by Pet.add_task() to preserve ownership context

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is high."""
        return self.priority == "high"

    def fits_in_window(self, start: time, end: time) -> bool:
        """Return True if the task's duration fits within the given time window."""
        start_dt = datetime.combine(datetime.today(), start)
        end_dt = datetime.combine(datetime.today(), end)
        available_minutes = (end_dt - start_dt).total_seconds() // 60
        return self.duration_minutes <= available_minutes


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    reason: str = ""

    @property
    def end_time(self) -> time:
        """Compute end time from start time and task duration."""
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = start_dt + timedelta(minutes=self.task.duration_minutes)
        return end_dt.time()

    def get_time_range(self) -> tuple:
        """Return the scheduled start and end times as a tuple."""
        return (self.start_time, self.end_time)

    def to_display_string(self) -> str:
        """Return a formatted string showing the time slot, pet, task, and priority."""
        start_str = self.start_time.strftime("%I:%M %p")
        end_str = self.end_time.strftime("%I:%M %p")
        pet = f"{self.task.pet_name}: " if self.task.pet_name else ""
        return f"{start_str} – {end_str} | {pet}{self.task.title} ({self.task.priority} priority)"


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.pets: List[Pet] = []
        self.scheduled_tasks: List[ScheduledTask] = []

    def add_pet(self, pet: Pet):
        """Register a pet with the scheduler."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of all tasks across every registered pet."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def build_schedule(self) -> List[ScheduledTask]:
        """Sort all tasks by priority and assign them to time slots within the owner's window."""
        tasks = self._sort_by_priority(self.get_all_tasks())
        self.scheduled_tasks = self._assign_time_slots(tasks)
        return self.scheduled_tasks

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered high → medium → low priority."""
        return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    def _assign_time_slots(self, tasks: List[Task]) -> List[ScheduledTask]:
        """Greedily assign start times to tasks, skipping any that exceed the available window."""
        scheduled = []
        current_dt = datetime.combine(datetime.today(), self.owner.available_start)
        end_dt = datetime.combine(datetime.today(), self.owner.available_end)

        for task in tasks:
            task_end_dt = current_dt + timedelta(minutes=task.duration_minutes)
            if task_end_dt > end_dt:
                continue  # not enough time left in the day

            reason = (
                f"Scheduled at {current_dt.strftime('%I:%M %p')} — "
                f"{task.priority} priority, fits in remaining window."
            )
            scheduled.append(ScheduledTask(task=task, start_time=current_dt.time(), reason=reason))
            current_dt = task_end_dt

        return scheduled

    def check_conflicts(self, task: Task) -> bool:
        """Return True if the given task overlaps with any already-scheduled task."""
        for st in self.scheduled_tasks:
            existing_start = datetime.combine(datetime.today(), st.start_time)
            existing_end = datetime.combine(datetime.today(), st.end_time)
            new_end = datetime.combine(datetime.today(), self.owner.available_start) + timedelta(minutes=task.duration_minutes)
            # a conflict exists if the ranges overlap
            if existing_start < new_end and existing_end > existing_start:
                return True
        return False


if __name__ == "__main__":
    owner = Owner(name="Jordan", available_start=time(8, 0), available_end=time(20, 0))

    luna = Pet(name="Luna", species="dog", age=3)
    luna.add_task(Task(id=1, title="Morning Walk",    duration_minutes=30, priority="high"))
    luna.add_task(Task(id=2, title="Evening Walk",    duration_minutes=30, priority="high"))
    luna.add_task(Task(id=3, title="Grooming",        duration_minutes=20, priority="low"))

    milo = Pet(name="Milo", species="cat", age=5)
    milo.add_task(Task(id=4, title="Feeding",         duration_minutes=10, priority="high"))
    milo.add_task(Task(id=5, title="Enrichment Play", duration_minutes=15, priority="medium"))

    scheduler = Scheduler(owner=owner)
    scheduler.add_pet(luna)
    scheduler.add_pet(milo)

    print(f"Owner: {owner.name}")
    print(f"Available: {owner.available_start.strftime('%I:%M %p')} – {owner.available_end.strftime('%I:%M %p')}")
    print(f"Total available time: {owner.get_total_available_time()} minutes\n")

    schedule = scheduler.build_schedule()
    print("=== Daily Schedule ===")
    for st in schedule:
        print(f"  {st.to_display_string()}")
        print(f"    Reason: {st.reason}")
