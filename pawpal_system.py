from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Category(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"


@dataclass(unsafe_hash=True)
class Pet:
    name: str
    species: str
    owner: Optional[Owner] = field(default=None, repr=False, hash=False, compare=False)
    tasks: List[Task] = field(default_factory=list, repr=False, hash=False, compare=False)

    def get_info(self) -> str:
        """Return a formatted summary of the pet's name, species, owner, and task count."""
        owner_name = self.owner.name if self.owner else "None"
        return (
            f"Pet: {self.name} | Species: {self.species} | "
            f"Owner: {owner_name} | Tasks: {len(self.tasks)}"
        )

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks assigned to this pet."""
        return self.tasks


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: Category
    pet: Optional[Pet] = None
    completed: bool = False

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary with enum values as strings."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.value,
            "category": self.category.value,
            "pet": self.pet.name if self.pet else None,
            "completed": self.completed,
        }

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is HIGH."""
        return self.priority == Priority.HIGH

    def mark_complete(self) -> None:
        """Mark the task as completed by setting completed to True."""
        self.completed = True


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: str = ""):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: List[Pet] = []
        self._remaining_minutes: int = available_minutes

    def set_profile(self, name: str, available_minutes: int) -> None:
        """Update the owner's name and daily time budget, resetting remaining time."""
        self.name = name
        self.available_minutes = available_minutes
        self._remaining_minutes = available_minutes

    def get_available_time(self) -> int:
        """Return the number of minutes still available for scheduling."""
        return self._remaining_minutes

    def spend_time(self, minutes: int) -> None:
        """Deduct the given minutes from the owner's remaining daily budget."""
        self._remaining_minutes -= minutes

    def reset_time(self) -> None:
        """Reset remaining time back to the full daily budget."""
        self._remaining_minutes = self.available_minutes

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner and set the pet's owner reference."""
        self.pets.append(pet)
        pet.owner = self


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: Dict[Pet, List[Task]] = {}
        self.scheduled_plan: Optional[DailyPlan] = None

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler, validating that the task's pet belongs to the owner."""
        if task.pet is None:
            raise ValueError("Task must be associated with a pet.")
        if task.pet not in self.owner.pets:
            raise ValueError(
                f"Pet '{task.pet.name}' is not registered with owner '{self.owner.name}'."
            )
        if task.pet not in self.tasks:
            self.tasks[task.pet] = []
        self.tasks[task.pet].append(task)

    def remove_task(self, title: str, pet: Optional[Pet] = None) -> None:
        """Remove a task by title, optionally scoped to a specific pet."""
        pets_to_search = [pet] if pet is not None else list(self.tasks.keys())
        for p in pets_to_search:
            if p in self.tasks:
                self.tasks[p] = [t for t in self.tasks[p] if t.title != title]

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan by greedily scheduling tasks sorted by priority then duration."""
        self.owner.reset_time()

        all_tasks: List[Task] = []
        for task_list in self.tasks.values():
            all_tasks.extend(task_list)

        # Sort by priority descending (HIGH=3 first), then duration ascending as tiebreaker
        all_tasks.sort(key=lambda t: (-t.priority.value, t.duration_minutes))

        plan = DailyPlan(owner=self.owner)

        for task in all_tasks:
            if self.owner.get_available_time() < task.duration_minutes:
                continue
            reason = (
                f"'{task.title}' scheduled (priority: {task.priority.value}, "
                f"duration: {task.duration_minutes}min, pet: {task.pet.name})"
            )
            plan.add_entry(task, reason)
            self.owner.spend_time(task.duration_minutes)

        self.scheduled_plan = plan
        return plan


class DailyPlan:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.entries: List[Task] = []
        self.total_duration: int = 0
        self.reasoning: str = ""

    def add_entry(self, task: Task, reason: str) -> None:
        """Add a scheduled task and append its reason to the plan's reasoning log."""
        self.entries.append(task)
        self.total_duration += task.duration_minutes
        if self.reasoning:
            self.reasoning += "\n" + reason
        else:
            self.reasoning = reason

    def display(self) -> str:
        """Return a formatted string listing all scheduled tasks and the total duration."""
        if not self.entries:
            return "No tasks scheduled."
        lines = [f"Daily Plan for {self.owner.name}:"]
        for task in self.entries:
            pet_name = task.pet.name if task.pet else "Unknown"
            lines.append(
                f"  - [{pet_name}] {task.title} | "
                f"Category: {task.category.value} | "
                f"Duration: {task.duration_minutes}min"
            )
        lines.append(f"Total Duration: {self.total_duration}min")
        return "\n".join(lines)

    def get_reasoning(self) -> str:
        """Return the newline-separated reasoning log for all scheduled tasks."""
        return self.reasoning
