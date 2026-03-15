from datetime import datetime, timedelta, timezone

import streamlit as st

from pawpal_system import Owner, Pet, Schedule, Scheduler, Task


def init_state() -> None:
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")
    if "pet_id_counter" not in st.session_state:
        st.session_state.pet_id_counter = 100
    if "schedule_id_counter" not in st.session_state:
        st.session_state.schedule_id_counter = 9000
    if "task_id_counter" not in st.session_state:
        st.session_state.task_id_counter = 1
    if "ui_trace" not in st.session_state:
        st.session_state.ui_trace = []


def add_pet(owner: Owner, name: str, species: str, age: int) -> Pet:
    st.session_state.pet_id_counter += 1
    st.session_state.schedule_id_counter += 1

    pet = Pet(
        pet_id=st.session_state.pet_id_counter,
        name=name,
        species=species,
        age=age,
        schedule=Schedule(schedule_id=st.session_state.schedule_id_counter),
    )
    owner.add_pet(pet)
    st.session_state.ui_trace.append(
        f"UI -> add_pet() -> Owner.add_pet(): created pet_id={pet.pet_id}"
    )
    return pet


def schedule_task(
    owner: Owner,
    pet_id: int,
    title: str,
    description: str,
    due_in_hours: int,
    duration_minutes: int,
    priority_label: str,
    frequency: str,
) -> Task:
    priority_map = {"high": 1, "medium": 2, "low": 3}
    pet = next((p for p in owner.get_pets() if p.pet_id == pet_id), None)
    if pet is None:
        raise ValueError(f"Pet with id {pet_id} was not found")

    task = Task(
        task_id=st.session_state.task_id_counter,
        title=title,
        description=description,
        due_datetime=datetime.now(timezone.utc) + timedelta(hours=due_in_hours),
        priority=priority_map[priority_label],
        duration_minutes=duration_minutes,
        frequency=frequency,
    )
    st.session_state.task_id_counter += 1

    pet.add_task(task)
    st.session_state.ui_trace.append(
        "UI -> schedule_task() -> Pet.add_task() -> Schedule.add_task() "
        f": created task_id={task.task_id} for pet_id={pet_id}"
    )
    return task


def task_rows(tasks: list[Task]) -> list[dict[str, str | int | bool]]:
    return [
        {
            "task_id": task.task_id,
            "title": task.title,
            "due_utc": task.due_datetime.strftime("%Y-%m-%d %H:%M UTC"),
            "duration_min": task.duration_minutes,
            "priority": task.priority,
            "frequency": task.frequency,
            "completed": task.completed,
        }
        for task in tasks
    ]


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
init_state()
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner=owner)

st.title("🐾 PawPal+")
st.caption("Backend integrated with Owner, Pet, Task, and Scheduler classes.")

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
owner_email = st.text_input("Owner email", value=owner.email)
owner.name = owner_name
owner.email = owner_email

st.divider()

st.subheader("Add Pet")
pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col3:
    pet_age = st.number_input("Age", min_value=0, max_value=40, value=2)

if st.button("Add pet"):
    try:
        new_pet = add_pet(owner, pet_name, species, int(pet_age))
        st.success(f"Added pet: {new_pet.name} (id={new_pet.pet_id})")
    except ValueError as exc:
        st.error(str(exc))

pets = owner.get_pets()
if pets:
    st.write("Current pets")
    st.table(
        [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
                "task_count": len(pet.get_tasks()),
            }
            for pet in pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule Task")
if not pets:
    st.warning("Add at least one pet before scheduling tasks.")
else:
    pet_options = {f"{pet.name} (id={pet.pet_id})": pet.pet_id for pet in pets}
    selected_pet_label = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet_id = pet_options[selected_pet_label]

    task_col1, task_col2 = st.columns(2)
    with task_col1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_description = st.text_area("Description", value="20 minute walk")
        due_in_hours = st.number_input("Due in (hours)", min_value=1, max_value=168, value=2)
        duration_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    with task_col2:
        priority_label = st.selectbox("Priority", ["high", "medium", "low"], index=0)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"], index=0)

    if st.button("Schedule task"):
        try:
            task = schedule_task(
                owner=owner,
                pet_id=selected_pet_id,
                title=task_title,
                description=task_description,
                due_in_hours=int(due_in_hours),
                duration_minutes=int(duration_minutes),
                priority_label=priority_label,
                frequency=frequency,
            )
            st.success(f"Scheduled task '{task.title}' (task_id={task.task_id})")
        except ValueError as exc:
            st.error(str(exc))

st.divider()

st.subheader("Scheduler Output")
if st.button("Generate schedule"):
    all_tasks = scheduler.get_all_tasks()
    pending_tasks = scheduler.get_pending_tasks()
    upcoming_tasks = scheduler.get_upcoming_tasks(within_hours=24)
    filtered_sorted_tasks = scheduler.filter_and_sort_tasks(
        include_completed=False,
        max_priority=2,
    )
    conflicts = scheduler.detect_conflicts()

    st.markdown("**All tasks (across pets)**")
    st.table(task_rows(all_tasks) if all_tasks else [])

    st.markdown("**Pending tasks**")
    st.table(task_rows(pending_tasks) if pending_tasks else [])

    st.markdown("**Upcoming in next 24h**")
    st.table(task_rows(upcoming_tasks) if upcoming_tasks else [])

    st.markdown("**Filtered + Sorted (pending, priority <= 2)**")
    st.table(task_rows(filtered_sorted_tasks) if filtered_sorted_tasks else [])

    st.markdown("**Conflict detection (overlapping task windows)**")
    if conflicts:
        st.table(
            [
                {
                    "task_a_id": task_a.task_id,
                    "task_a_title": task_a.title,
                    "task_b_id": task_b.task_id,
                    "task_b_title": task_b.title,
                }
                for task_a, task_b in conflicts
            ]
        )
    else:
        st.success("No conflicts detected.")

st.divider()

with st.expander("Trace one UI action to backend logic", expanded=True):
    st.markdown(
        """
Example flow for clicking **Schedule task**:
1. Streamlit button triggers `schedule_task(...)`.
2. Function creates a typed `Task` with UTC due time.
3. Function finds the selected `Pet` under `Owner`.
4. `Pet.add_task(...)` delegates to `Schedule.add_task(...)`.
5. `Scheduler.get_all_tasks()` can now retrieve it across all pets.
"""
    )
    if st.session_state.ui_trace:
        st.write("Recent action log")
        for event in reversed(st.session_state.ui_trace[-5:]):
            st.write(f"- {event}")
    else:
        st.info("No actions logged yet. Add a pet or schedule a task.")

with st.expander("Common state reset bug", expanded=False):
    st.markdown(
        """
Common bug: storing pets/tasks in normal local variables, so every rerun clears them.

Why it happens:
- Streamlit reruns top-to-bottom on every widget interaction.

How this app avoids it:
- Owner object, ID counters, and trace logs are initialized once in `st.session_state`.
- All UI actions mutate that persistent state instead of transient local lists.
"""
    )
