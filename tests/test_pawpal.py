import pytest
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner(name="Jordan", available_start=time(8, 0), available_end=time(20, 0))


@pytest.fixture
def basic_task():
    return Task(id=1, title="Morning Walk", duration_minutes=30, priority="high")


@pytest.fixture
def pet_with_tasks():
    pet = Pet(name="Luna", species="dog", age=3)
    pet.add_task(Task(id=1, title="Morning Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task(id=2, title="Evening Walk", duration_minutes=30, priority="high"))
    pet.add_task(Task(id=3, title="Grooming",     duration_minutes=20, priority="low"))
    return pet


@pytest.fixture
def scheduler_with_pets(owner, pet_with_tasks):
    milo = Pet(name="Milo", species="cat", age=5)
    milo.add_task(Task(id=4, title="Feeding",         duration_minutes=10, priority="high"))
    milo.add_task(Task(id=5, title="Enrichment Play", duration_minutes=15, priority="medium"))

    scheduler = Scheduler(owner=owner)
    scheduler.add_pet(pet_with_tasks)
    scheduler.add_pet(milo)
    return scheduler


# --- Task tests ---

class TestTask:
    def test_mark_complete(self, basic_task):
        assert basic_task.is_completed is False
        basic_task.mark_complete()
        assert basic_task.is_completed is True

    def test_is_high_priority_true(self, basic_task):
        assert basic_task.is_high_priority() is True

    def test_is_high_priority_false(self):
        task = Task(id=2, title="Grooming", duration_minutes=20, priority="low")
        assert task.is_high_priority() is False

    def test_fits_in_window_true(self, basic_task):
        assert basic_task.fits_in_window(time(8, 0), time(20, 0)) is True

    def test_fits_in_window_false(self):
        task = Task(id=3, title="Long Hike", duration_minutes=120, priority="medium")
        assert task.fits_in_window(time(8, 0), time(8, 30)) is False


# --- Pet tests ---

class TestPet:
    def test_add_task_appends(self, pet_with_tasks):
        assert len(pet_with_tasks.get_tasks()) == 3

    def test_add_task_sets_pet_name(self, basic_task):
        pet = Pet(name="Luna", species="dog", age=3)
        pet.add_task(basic_task)
        assert basic_task.pet_name == "Luna"

    def test_remove_task_by_id(self, pet_with_tasks):
        pet_with_tasks.remove_task(task_id=1)
        ids = [t.id for t in pet_with_tasks.get_tasks()]
        assert 1 not in ids
        assert len(ids) == 2

    def test_remove_nonexistent_task_does_nothing(self, pet_with_tasks):
        pet_with_tasks.remove_task(task_id=999)
        assert len(pet_with_tasks.get_tasks()) == 3


# --- Owner tests ---

class TestOwner:
    def test_get_available_window(self, owner):
        assert owner.get_available_window() == (time(8, 0), time(20, 0))

    def test_get_total_available_time(self, owner):
        assert owner.get_total_available_time() == 720


# --- ScheduledTask tests ---

class TestScheduledTask:
    def test_end_time_computed_correctly(self, basic_task):
        st = ScheduledTask(task=basic_task, start_time=time(8, 0))
        assert st.end_time == time(8, 30)

    def test_get_time_range(self, basic_task):
        st = ScheduledTask(task=basic_task, start_time=time(8, 0))
        assert st.get_time_range() == (time(8, 0), time(8, 30))

    def test_to_display_string_includes_pet_name(self):
        task = Task(id=1, title="Morning Walk", duration_minutes=30, priority="high", pet_name="Luna")
        st = ScheduledTask(task=task, start_time=time(8, 0))
        assert "Luna" in st.to_display_string()
        assert "Morning Walk" in st.to_display_string()


# --- Scheduler tests ---

class TestScheduler:
    def test_add_pet(self, owner):
        scheduler = Scheduler(owner=owner)
        pet = Pet(name="Luna", species="dog", age=3)
        scheduler.add_pet(pet)
        assert len(scheduler.pets) == 1

    def test_get_all_tasks_flattens_pets(self, scheduler_with_pets):
        tasks = scheduler_with_pets.get_all_tasks()
        assert len(tasks) == 5

    def test_build_schedule_returns_scheduled_tasks(self, scheduler_with_pets):
        schedule = scheduler_with_pets.build_schedule()
        assert len(schedule) > 0
        assert all(isinstance(st, ScheduledTask) for st in schedule)

    def test_build_schedule_sorted_high_before_low(self, scheduler_with_pets):
        schedule = scheduler_with_pets.build_schedule()
        priorities = [st.task.priority for st in schedule]
        # high priority tasks should appear before low
        assert priorities.index("high") < priorities.index("low")

    def test_build_schedule_skips_tasks_that_dont_fit(self, owner):
        scheduler = Scheduler(owner=owner)
        pet = Pet(name="Luna", species="dog", age=3)
        # fill the window with one giant task, then add a second that won't fit
        pet.add_task(Task(id=1, title="Very Long Task", duration_minutes=700, priority="high"))
        pet.add_task(Task(id=2, title="Short Task",     duration_minutes=30,  priority="medium"))
        scheduler.add_pet(pet)
        schedule = scheduler.build_schedule()
        titles = [st.task.title for st in schedule]
        assert "Very Long Task" in titles
        assert "Short Task" not in titles

    def test_scheduled_tasks_stored_on_instance(self, scheduler_with_pets):
        schedule = scheduler_with_pets.build_schedule()
        assert scheduler_with_pets.scheduled_tasks is schedule
