from pawpal_system import Category, Owner, Pet, Priority, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should set task.completed to True."""
    task = Task(
        title="Morning Walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        category=Category.WALK,
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by one."""
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    owner.add_pet(mochi)

    assert len(mochi.get_tasks()) == 0

    task = Task(
        title="Feeding",
        duration_minutes=10,
        priority=Priority.MEDIUM,
        category=Category.FEEDING,
        pet=mochi,
    )
    mochi.add_task(task)

    assert len(mochi.get_tasks()) == 1
