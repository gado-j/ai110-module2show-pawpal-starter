import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state initialization ---
# st.session_state acts like a dictionary that persists across reruns.
# The "if not in" guard ensures we only create these objects once,
# not every time the page refreshes or a button is clicked.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_start=time(8, 0),
        available_end=time(20, 0),
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1  # auto-increments so every Task gets a unique id

# --- Page header ---
st.title("🐾 PawPal+")
st.caption(f"Owner: {st.session_state.owner.name} | Available: {st.session_state.owner.available_start.strftime('%I:%M %p')} – {st.session_state.owner.available_end.strftime('%I:%M %p')}")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Luna")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    # Check if a pet with this name already exists
    existing_names = [p.name for p in st.session_state.scheduler.pets]
    if pet_name in existing_names:
        st.warning(f"A pet named '{pet_name}' is already registered.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=age)
        # scheduler.add_pet() registers the Pet so the scheduler can manage its tasks
        st.session_state.scheduler.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

# Show registered pets
if st.session_state.scheduler.pets:
    st.markdown("**Registered pets:**")
    for pet in st.session_state.scheduler.pets:
        st.write(f"- {pet.name} ({pet.species}, age {pet.age})")
else:
    st.info("No pets added yet.")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

if not st.session_state.scheduler.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_options = [p.name for p in st.session_state.scheduler.pets]

    col1, col2 = st.columns(2)
    with col1:
        selected_pet_name = st.selectbox("Assign to pet", pet_options)
    with col2:
        task_title = st.text_input("Task title", value="Morning Walk")

    col3, col4 = st.columns(2)
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add Task"):
        # Find the Pet object that matches the selected name
        target_pet = next(p for p in st.session_state.scheduler.pets if p.name == selected_pet_name)

        new_task = Task(
            id=st.session_state.next_task_id,
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
        )
        # pet.add_task() appends the task and stamps pet_name on it
        target_pet.add_task(new_task)
        st.session_state.next_task_id += 1
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # Show all current tasks grouped by pet
    all_tasks = st.session_state.scheduler.get_all_tasks()
    if all_tasks:
        st.markdown("**Current tasks:**")
        rows = [
            {"Pet": t.pet_name, "Task": t.title, "Duration (min)": t.duration_minutes, "Priority": t.priority}
            for t in all_tasks
        ]
        st.table(rows)

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Build Schedule"):
    all_tasks = st.session_state.scheduler.get_all_tasks()
    if not all_tasks:
        st.warning("Add at least one task before building a schedule.")
    else:
        # scheduler.build_schedule() sorts by priority and assigns time slots
        schedule = st.session_state.scheduler.build_schedule()
        st.success(f"Scheduled {len(schedule)} of {len(all_tasks)} tasks.")
        st.markdown("### Today's Schedule")
        for st_task in schedule:
            st.markdown(f"**{st_task.to_display_string()}**")
            st.caption(f"Reason: {st_task.reason}")
