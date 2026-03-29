```mermaid
classDiagram
    class Owner {
        +String name
        +time available_start
        +time available_end
        +get_available_window() tuple
        +get_total_available_time() int
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~Task~ tasks
        +add_task(task: Task)
        +remove_task(task_id: int)
        +get_tasks() List~Task~
    }

    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String frequency
        +time preferred_time
        +bool is_completed
        +mark_complete()
        +is_high_priority() bool
        +fits_in_window(start, end) bool
    }

    class Scheduler {
        +Owner owner
        +List~Pet~ pets
        +List~ScheduledTask~ scheduled_tasks
        +add_pet(pet: Pet)
        +get_all_tasks() List~Task~
        +build_schedule() List~ScheduledTask~
        +check_conflicts(task: Task) bool
        +explain_plan() String
    }

    class ScheduledTask {
        +Task task
        +time start_time
        +time end_time
        +String reason
        +get_time_range() tuple
        +to_display_string() String
    }

    Owner "1" --> "1..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : constrained by
    Scheduler "1" --> "1..*" Pet : manages
    Scheduler "1" --> "0..*" ScheduledTask : produces
    ScheduledTask "1" --> "1" Task : wraps
```

<!--
DESIGN NOTES

ScheduledTask as a separate class:
  Kept because it cleanly separates what a task is (Task) from when it runs today (ScheduledTask).
  This makes explain_plan() and the UI display much simpler — the Task holds the definition,
  the ScheduledTask holds the placement.

Owner as its own class:
  Kept because the scheduler needs time constraints to be first-class, not buried in the UI.
  available_start and available_end are the concrete inputs the scheduling algorithm depends on.

Owner.preferences removed:
  Too vague to model cleanly at this stage. The time window (available_start/available_end)
  is the concrete constraint that actually matters for scheduling. Preferences can be added
  later if specific preference types are identified.

Pet.owner back-reference removed:
  Unnecessary since Scheduler already manages both Owner and Pets. Adding a back-reference
  from Pet to Owner would create a circular dependency with no clear benefit.

Scheduler is the integration point:
  By design, Scheduler is the only class that touches everything — it reads Owner constraints,
  collects Tasks from all Pets, and produces ScheduledTasks. All scheduling logic lives here.
-->
