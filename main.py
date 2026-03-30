from pawpal_system import Category, Owner, Pet, Priority, Scheduler, Task

# ── 1. Create Owner ───────────────────────────────────────────────────────────
owner = Owner(name="Jordan", available_minutes=90)

# ── 2. Create at least two Pets ───────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog")
bella = Pet(name="Bella", species="cat")
owner.add_pet(mochi)
owner.add_pet(bella)

# ── 3. Create at least three Tasks with different durations ───────────────────
tasks = [
    Task("Morning Walk",  30, Priority.HIGH,   Category.WALK,       pet=mochi),
    Task("Feeding",       10, Priority.HIGH,   Category.FEEDING,    pet=mochi),
    Task("Meds",           5, Priority.HIGH,   Category.MEDS,       pet=bella),
    Task("Grooming",      20, Priority.MEDIUM, Category.GROOMING,   pet=bella),
    Task("Enrichment",    15, Priority.LOW,    Category.ENRICHMENT, pet=mochi),
    Task("Evening Walk",  30, Priority.MEDIUM, Category.WALK,       pet=mochi),
]

scheduler = Scheduler(owner)
for task in tasks:
    scheduler.add_task(task)
    task.pet.add_task(task)

# ── 4. Generate and print Today's Schedule ────────────────────────────────────
plan = scheduler.generate_plan()

print("=" * 50)
print("         TODAY'S SCHEDULE")
print("=" * 50)
print(f"Owner : {owner.name}")
print(f"Pets  : {', '.join(p.name for p in owner.pets)}")
print(f"Budget: {owner.available_minutes} min")
print("-" * 50)

for i, task in enumerate(plan.entries, start=1):
    pet_name = task.pet.name if task.pet else "?"
    print(
        f"{i}. [{pet_name}] {task.title:<20} "
        f"{task.duration_minutes:>3} min  |  "
        f"priority: {task.priority.name:<6}  |  "
        f"category: {task.category.value}"
    )

print("-" * 50)
print(f"Total scheduled : {plan.total_duration} min")
print(f"Time remaining  : {owner.get_available_time()} min")
print("=" * 50)
print("\nWhy this plan?")
for line in plan.get_reasoning().splitlines():
    print(f"  • {line}")
