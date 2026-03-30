from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Pet:
    name: str
    species: str
    owner: Optional[Owner] = field(default=None, repr=False)

    def get_info(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str

    def to_dict(self) -> dict:
        pass

    def is_high_priority(self) -> bool:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: str = ""):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: List[Pet] = []

    def set_profile(self, name: str, available_minutes: int) -> None:
        pass

    def get_available_time(self) -> int:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: List[Task] = []
        self.scheduled_plan: Optional[DailyPlan] = None

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass

    def explain_plan(self) -> str:
        pass


class DailyPlan:
    def __init__(self):
        self.entries: List[Task] = []
        self.total_duration: int = 0
        self.reasoning: str = ""

    def display(self) -> str:
        pass

    def get_reasoning(self) -> str:
        pass