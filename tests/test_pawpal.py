import pytest
from pawpal_system import Category, Owner, Pet, Priority, Scheduler, Task


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def owner():
    """Owner with 120 minutes available."""
    return Owner(name="Jordan", available_minutes=120)

@pytest.fixture
def mochi(owner):
    """Dog registered to owner."""
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    return pet

@pytest.fixture
def bella(owner):
    """Cat registered to owner."""
    pet = Pet(name="Bella", species="cat")
    owner.add_pet(pet)
    return pet

@pytest.fixture
def scheduler(owner):
    """Scheduler bound to owner."""
    return Scheduler(owner)


# ── Task completion ───────────────────────────────────────────────────────────

def test_mark_complete_changes_status(mochi):
    """mark_complete() sets completed to True."""
    task = Task("Morning Walk", 30, Priority.HIGH, Category.WALK, pet=mochi)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_non_recurring_mark_complete_returns_none(mochi):
    """Non-recurring task returns None from mark_complete()."""
    task = Task("Grooming", 20, Priority.MEDIUM, Category.GROOMING, pet=mochi, frequency="none")
    result = task.mark_complete()
    assert result is None


def test_daily_recurring_returns_new_task(mochi):
    """Daily task returns a fresh incomplete copy when marked complete."""
    task = Task("Enrichment", 15, Priority.LOW, Category.ENRICHMENT, pet=mochi,
                start_time="15:00", frequency="daily")
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "daily"
    assert next_task.title == task.title
    assert next_task.start_time == "15:00"


def test_weekly_recurring_returns_new_task(mochi):
    """Weekly task returns a fresh incomplete copy when marked complete."""
    task = Task("Bath", 30, Priority.MEDIUM, Category.GROOMING, pet=mochi, frequency="weekly")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "weekly"


# ── Pet task management ───────────────────────────────────────────────────────

def test_add_task_increases_pet_task_count(mochi):
    """Adding a task to a Pet increases its task count by one."""
    assert len(mochi.get_tasks()) == 0
    task = Task("Feeding", 10, Priority.HIGH, Category.FEEDING, pet=mochi)
    mochi.add_task(task)
    assert len(mochi.get_tasks()) == 1


def test_pet_with_no_tasks_returns_empty_list(mochi):
    """A newly created pet has an empty task list."""
    assert mochi.get_tasks() == []


# ── Sorting ───────────────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order(owner, mochi, scheduler):
    """sort_by_time() returns tasks in HH:MM chronological order."""
    tasks = [
        Task("Evening Walk", 30, Priority.MEDIUM, Category.WALK,    pet=mochi, start_time="17:00"),
        Task("Feeding",      10, Priority.HIGH,   Category.FEEDING, pet=mochi, start_time="08:00"),
        Task("Morning Walk", 30, Priority.HIGH,   Category.WALK,    pet=mochi, start_time="07:30"),
    ]
    for t in tasks:
        scheduler.add_task(t)

    sorted_tasks = scheduler.sort_by_time()
    times = [t.start_time for t in sorted_tasks]
    assert times == ["07:30", "08:00", "17:00"]


def test_sort_by_time_excludes_untimed_tasks(owner, mochi, scheduler):
    """sort_by_time() only includes tasks that have a start_time set."""
    timed   = Task("Walk",    30, Priority.HIGH,   Category.WALK,    pet=mochi, start_time="09:00")
    untimed = Task("Meds",     5, Priority.HIGH,   Category.MEDS,    pet=mochi)
    scheduler.add_task(timed)
    scheduler.add_task(untimed)

    result = scheduler.sort_by_time()
    assert len(result) == 1
    assert result[0].title == "Walk"


def test_sort_by_time_for_specific_pet(owner, mochi, bella, scheduler):
    """sort_by_time(pet=...) returns only that pet's timed tasks."""
    scheduler.add_task(Task("Walk",     30, Priority.HIGH,   Category.WALK,    pet=mochi, start_time="07:00"))
    scheduler.add_task(Task("Grooming", 20, Priority.MEDIUM, Category.GROOMING, pet=bella, start_time="09:00"))

    result = scheduler.sort_by_time(pet=mochi)
    assert all(t.pet == mochi for t in result)
    assert len(result) == 1


# ── Filtering ─────────────────────────────────────────────────────────────────

def test_filter_by_pet_name(owner, mochi, bella, scheduler):
    """filter_tasks(pet_name=...) returns only that pet's tasks."""
    scheduler.add_task(Task("Walk",  30, Priority.HIGH,   Category.WALK,    pet=mochi))
    scheduler.add_task(Task("Meds",   5, Priority.HIGH,   Category.MEDS,    pet=bella))

    result = scheduler.filter_tasks(pet_name="Bella")
    assert all(t.pet.name == "Bella" for t in result)
    assert len(result) == 1


def test_filter_by_completed_status(owner, mochi, scheduler):
    """filter_tasks(completed=True) returns only completed tasks."""
    done    = Task("Feeding",  10, Priority.HIGH, Category.FEEDING, pet=mochi)
    pending = Task("Walk",     30, Priority.HIGH, Category.WALK,    pet=mochi)
    scheduler.add_task(done)
    scheduler.add_task(pending)
    done.mark_complete()

    result = scheduler.filter_tasks(completed=True)
    assert len(result) == 1
    assert result[0].title == "Feeding"


def test_filter_no_criteria_returns_all(owner, mochi, bella, scheduler):
    """filter_tasks() with no arguments returns all tasks."""
    scheduler.add_task(Task("Walk",  30, Priority.HIGH, Category.WALK,    pet=mochi))
    scheduler.add_task(Task("Meds",   5, Priority.HIGH, Category.MEDS,    pet=bella))

    assert len(scheduler.filter_tasks()) == 2


# ── Conflict detection ────────────────────────────────────────────────────────

def test_detect_conflict_same_time(owner, mochi, bella, scheduler):
    """detect_conflicts() flags two tasks at the same start_time."""
    scheduler.add_task(Task("Feeding", 10, Priority.HIGH, Category.FEEDING, pet=mochi, start_time="08:00"))
    scheduler.add_task(Task("Meds",     5, Priority.HIGH, Category.MEDS,    pet=bella, start_time="08:00"))

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Feeding" in conflicts[0]
    assert "Meds" in conflicts[0]


def test_no_conflict_different_times(owner, mochi, bella, scheduler):
    """detect_conflicts() returns empty list when all start_times are different."""
    scheduler.add_task(Task("Walk",    30, Priority.HIGH,   Category.WALK,    pet=mochi, start_time="07:30"))
    scheduler.add_task(Task("Grooming",20, Priority.MEDIUM, Category.GROOMING, pet=bella, start_time="10:00"))

    assert scheduler.detect_conflicts() == []


def test_no_conflict_when_no_timed_tasks(owner, mochi, scheduler):
    """detect_conflicts() returns empty list when no tasks have a start_time."""
    scheduler.add_task(Task("Meds", 5, Priority.HIGH, Category.MEDS, pet=mochi))
    assert scheduler.detect_conflicts() == []


# ── Scheduler: generate_plan ──────────────────────────────────────────────────

def test_generate_plan_respects_time_budget(owner, mochi, scheduler):
    """generate_plan() does not schedule tasks that exceed the owner's time budget."""
    owner.available_minutes = 20
    owner.reset_time()
    scheduler.add_task(Task("Walk",     30, Priority.HIGH, Category.WALK,    pet=mochi))
    scheduler.add_task(Task("Feeding",  10, Priority.HIGH, Category.FEEDING, pet=mochi))

    plan = scheduler.generate_plan()
    assert plan.total_duration <= 20


def test_generate_plan_prioritises_high_over_low(owner, mochi, scheduler):
    """generate_plan() schedules HIGH priority tasks before LOW ones."""
    owner.available_minutes = 15
    owner.reset_time()
    scheduler.add_task(Task("Enrichment", 10, Priority.LOW,  Category.ENRICHMENT, pet=mochi))
    scheduler.add_task(Task("Meds",       10, Priority.HIGH, Category.MEDS,       pet=mochi))

    plan = scheduler.generate_plan()
    assert len(plan.entries) == 1
    assert plan.entries[0].title == "Meds"


def test_generate_plan_empty_when_no_tasks(owner, mochi, scheduler):
    """generate_plan() returns an empty DailyPlan when no tasks are added."""
    plan = scheduler.generate_plan()
    assert plan.entries == []
    assert plan.total_duration == 0


# ── Scheduler: validation ─────────────────────────────────────────────────────

def test_add_task_raises_if_pet_not_registered(owner, scheduler):
    """add_task() raises ValueError if the task's pet is not in owner.pets."""
    stray = Pet(name="Stray", species="dog")  # not added to owner
    task = Task("Walk", 30, Priority.HIGH, Category.WALK, pet=stray)
    with pytest.raises(ValueError):
        scheduler.add_task(task)


def test_add_task_raises_if_no_pet(owner, scheduler):
    """add_task() raises ValueError if task has no pet attached."""
    task = Task("Mystery Task", 10, Priority.LOW, Category.ENRICHMENT)
    with pytest.raises(ValueError):
        scheduler.add_task(task)
