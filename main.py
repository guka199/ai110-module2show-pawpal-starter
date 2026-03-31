from pawpal_system import Category, Owner, Pet, Priority, Scheduler, Task

# ── Setup ─────────────────────────────────────────────────────────────────────
owner = Owner(name="Jordan", available_minutes=120)
mochi = Pet(name="Mochi", species="dog")
bella = Pet(name="Bella", species="cat")
owner.add_pet(mochi)
owner.add_pet(bella)

# Tasks added OUT OF ORDER with start_times, frequencies, and varied priorities
tasks = [
    Task("Evening Walk",  30, Priority.MEDIUM, Category.WALK,       pet=mochi, start_time="17:00"),
    Task("Feeding",       10, Priority.HIGH,   Category.FEEDING,    pet=mochi, start_time="08:00"),
    Task("Meds",           5, Priority.HIGH,   Category.MEDS,       pet=bella, start_time="08:00"),  # conflict!
    Task("Grooming",      20, Priority.MEDIUM, Category.GROOMING,   pet=bella, start_time="10:00"),
    Task("Morning Walk",  30, Priority.HIGH,   Category.WALK,       pet=mochi, start_time="07:30"),
    Task("Enrichment",    15, Priority.LOW,    Category.ENRICHMENT, pet=mochi, start_time="15:00", frequency="daily"),
]

scheduler = Scheduler(owner)
for task in tasks:
    scheduler.add_task(task)
    task.pet.add_task(task)

# ── 1. Today's Schedule ───────────────────────────────────────────────────────
plan = scheduler.generate_plan()
print("=" * 55)
print("              TODAY'S SCHEDULE")
print("=" * 55)
print(f"Owner : {owner.name}  |  Budget: {owner.available_minutes} min")
print("-" * 55)
for i, task in enumerate(plan.entries, start=1):
    pet_name = task.pet.name if task.pet else "?"
    print(
        f"{i}. [{pet_name}] {task.title:<20} {task.duration_minutes:>3} min"
        f"  |  {task.priority.name:<6}  |  {task.category.value}"
    )
print("-" * 55)
print(f"Total: {plan.total_duration} min  |  Remaining: {owner.get_available_time()} min")
print("=" * 55)

# ── 2. Sorting by Start Time ──────────────────────────────────────────────────
print("\n--- Sorted by Start Time (all pets) ---")
for t in scheduler.sort_by_time():
    print(f"  {t.start_time}  [{t.pet.name}] {t.title}")

print("\n--- Sorted by Start Time (Mochi only) ---")
for t in scheduler.sort_by_time(pet=mochi):
    print(f"  {t.start_time}  {t.title}")

# ── 3. Filtering ──────────────────────────────────────────────────────────────
print("\n--- Filter: Bella's tasks ---")
for t in scheduler.filter_tasks(pet_name="Bella"):
    print(f"  {t.title} | completed: {t.completed}")

print("\n--- Filter: Incomplete tasks ---")
for t in scheduler.filter_tasks(completed=False):
    print(f"  [{t.pet.name}] {t.title}")

# ── 4. Recurring Task ─────────────────────────────────────────────────────────
enrichment = next(t for t in scheduler.filter_tasks(pet_name="Mochi") if t.title == "Enrichment")
print(f"\n--- Recurring Task: '{enrichment.title}' (frequency: {enrichment.frequency}) ---")
next_task = enrichment.mark_complete()
print(f"  Original completed : {enrichment.completed}")
if next_task:
    print(f"  Next occurrence    : '{next_task.title}' | completed: {next_task.completed} | frequency: {next_task.frequency}")

# ── 5. Conflict Detection ─────────────────────────────────────────────────────
print("\n--- Conflict Detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠ {warning}")
else:
    print("  No conflicts found.")
