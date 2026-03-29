from dataclasses import dataclass, field
from datetime import time
from typing import List, Optional


@dataclass
class Owner:
    name: str
    available_start: time
    available_end: time

    def get_available_window(self) -> tuple:
        pass

    def get_total_available_time(self) -> int:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    preferred_time: Optional[time] = None
    is_completed: bool = False

    def mark_complete(self):
        pass

    def is_high_priority(self) -> bool:
        pass

    def fits_in_window(self, start: time, end: time) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        pass

    def remove_task(self, task_title: str):
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time
    reason: str = ""

    def get_time_range(self) -> tuple:
        pass

    def to_display_string(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.pets: List[Pet] = []
        self.scheduled_tasks: List[ScheduledTask] = []

    def add_pet(self, pet: Pet):
        pass

    def get_all_tasks(self) -> List[Task]:
        pass

    def build_schedule(self) -> List[ScheduledTask]:
        pass

    def check_conflicts(self, task: Task) -> bool:
        pass

    def explain_plan(self) -> str:
        pass
