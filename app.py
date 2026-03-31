import streamlit as st

# ── Step 1: Import classes from pawpal_system.py ─────────────────────────────
# These give us access to all the logic written in Phase 2.
from pawpal_system import Category, DailyPlan, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Step 2: Application "Memory" via st.session_state ────────────────────────
# Streamlit reruns the entire script on every interaction. st.session_state acts
# as a persistent vault — we only create objects the FIRST time they are needed.
# On every subsequent rerun the existing objects are reused, preserving all data.
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "plan" not in st.session_state:
    st.session_state.plan = None

# ── 1. Owner & Pet Profile ────────────────────────────────────────────────────
st.header("1. Owner & Pet Profile")

with st.form("profile_form"):
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Available time today (minutes)", min_value=10, max_value=480, value=120
    )
    preferences = st.text_input("Preferences (optional)", value="")
    st.markdown("**First pet**")
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    submitted = st.form_submit_button("Save Profile")

if submitted:
    if st.session_state.owner is None:
        # First save — create Owner, Pet, and Scheduler and store them in the vault.
        owner = Owner(owner_name, int(available_minutes), preferences)
        pet = Pet(pet_name, species)
        owner.add_pet(pet)                          # Owner.add_pet() registers the pet
        st.session_state.owner = owner
        st.session_state.scheduler = Scheduler(owner)
        st.session_state.plan = None
        st.success(f"Profile saved! {owner.name} with pet {pet.name} ({pet.species}).")
    else:
        # Re-save — update profile without discarding existing pets or tasks.
        st.session_state.owner.set_profile(owner_name, int(available_minutes))
        st.success("Profile updated. Pets and tasks are unchanged.")

# ── Step 3: Wire "Add another pet" to Owner.add_pet() ────────────────────────
# When the user submits this form, we call owner.add_pet(new_pet) directly.
# Streamlit then reruns and the updated owner.pets list is reflected immediately.
if st.session_state.owner:
    with st.expander("Add another pet"):
        with st.form("add_pet_form"):
            extra_pet_name = st.text_input("Pet name")
            extra_species = st.selectbox("Species", ["dog", "cat", "other"])
            add_pet_btn = st.form_submit_button("Add pet")

        if add_pet_btn and extra_pet_name:
            new_pet = Pet(extra_pet_name, extra_species)
            st.session_state.owner.add_pet(new_pet)  # Owner.add_pet() sets pet.owner too
            st.success(f"Added {new_pet.name}!")

    st.markdown("**Registered pets:**")
    for p in st.session_state.owner.pets:
        st.write(f"- {p.get_info()}")              # Pet.get_info() formats the summary

st.divider()

# ── 2. Add Tasks ──────────────────────────────────────────────────────────────
st.header("2. Add Tasks")

if not st.session_state.owner:
    st.info("Save an owner profile first.")
else:
    owner: Owner = st.session_state.owner
    scheduler: Scheduler = st.session_state.scheduler
    pet_names = [p.name for p in owner.pets]

    with st.form("task_form"):
        task_title = st.text_input("Task title", value="Morning walk")
        task_pet_name = st.selectbox("For pet", pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=2)
        with col3:
            category = st.selectbox(
                "Category", ["WALK", "FEEDING", "MEDS", "GROOMING", "ENRICHMENT"]
            )
        add_task_btn = st.form_submit_button("Add task")

    if add_task_btn:
        pet_obj = next(p for p in owner.pets if p.name == task_pet_name)
        task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority[priority],
            category=Category[category],
            pet=pet_obj,
        )
        # ── Step 3: Wire task form to Scheduler.add_task() and Pet.add_task() ──
        # scheduler.add_task() stores the task in the scheduler's per-pet dict.
        # pet_obj.add_task() stores it on the pet itself for get_info() task count.
        # Both must be called so each class stays in sync with its own task list.
        scheduler.add_task(task)
        pet_obj.add_task(task)
        st.success(f"Task '{task_title}' added for {task_pet_name}.")

    all_tasks = [t for tasks in scheduler.tasks.values() for t in tasks]
    if all_tasks:
        st.markdown("**Current tasks:**")
        st.table([t.to_dict() for t in all_tasks])
    else:
        st.info("No tasks yet.")

st.divider()

# ── 3. Generate Daily Schedule ────────────────────────────────────────────────
st.header("3. Generate Daily Schedule")

if not st.session_state.scheduler:
    st.info("Save an owner profile and add tasks first.")
else:
    scheduler: Scheduler = st.session_state.scheduler
    all_tasks = [t for tasks in scheduler.tasks.values() for t in tasks]

    if not all_tasks:
        st.info("Add at least one task before generating a schedule.")
    elif st.button("Generate schedule"):
        # Scheduler.generate_plan() sorts by priority, fits tasks within the time
        # budget, and returns a DailyPlan stored back into session_state.
        st.session_state.plan = scheduler.generate_plan()

# ── 4. View Schedule & Reasoning ─────────────────────────────────────────────
if st.session_state.plan:
    plan: DailyPlan = st.session_state.plan
    st.divider()
    st.header("4. Schedule & Reasoning")

    if not plan.entries:
        st.warning("No tasks could be scheduled within the available time.")
    else:
        st.success(f"Scheduled {len(plan.entries)} task(s) — {plan.total_duration} min total.")
        st.code(plan.display(), language=None)   # DailyPlan.display() formats the output

        with st.expander("Why was this plan chosen?"):
            st.text(plan.get_reasoning())        # DailyPlan.get_reasoning() returns the log

        time_used = plan.total_duration
        time_total = st.session_state.owner.available_minutes
        st.progress(
            min(time_used / time_total, 1.0),
            text=f"{time_used}/{time_total} min used"
        )
