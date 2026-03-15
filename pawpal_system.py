from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


def _require_aware_datetime(value: datetime) -> datetime:
	"""Validate datetime is timezone-aware and normalize it to UTC."""
	if value.tzinfo is None or value.utcoffset() is None:
		raise ValueError("due_datetime must be timezone-aware")
	return value.astimezone(timezone.utc)


VALID_FREQUENCIES = {"once", "daily", "weekly", "monthly"}


@dataclass
class Task:
	task_id: int
	title: str
	description: str
	due_datetime: datetime
	priority: int
	frequency: str = "once"
	completed: bool = False

	def __post_init__(self) -> None:
		self.due_datetime = _require_aware_datetime(self.due_datetime)
		if self.frequency not in VALID_FREQUENCIES:
			raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}")

	def mark_complete(self) -> None:
		self.completed = True

	def mark_incomplete(self) -> None:
		self.completed = False

	def reschedule(self, new_datetime: datetime) -> None:
		self.due_datetime = _require_aware_datetime(new_datetime)


@dataclass
class Schedule:
	schedule_id: int
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		if any(t.task_id == task.task_id for t in self.tasks):
			raise ValueError(f"Task with id {task.task_id} already exists in this schedule")
		self.tasks.append(task)

	def remove_task(self, task_id: int) -> None:
		task = next((t for t in self.tasks if t.task_id == task_id), None)
		if task is None:
			raise ValueError(f"Task with id {task_id} not found in this schedule")
		self.tasks.remove(task)

	def get_tasks(self) -> List[Task]:
		return list(self.tasks)

	def get_pending_tasks(self) -> List[Task]:
		return [t for t in self.tasks if not t.completed]

	def sort_by_due_date(self) -> List[Task]:
		return sorted(self.tasks, key=lambda t: t.due_datetime)


@dataclass
class Pet:
	pet_id: int
	name: str
	species: str
	age: int
	schedule: Schedule

	def __post_init__(self) -> None:
		if self.age < 0:
			raise ValueError("age cannot be negative")

	def update_profile(self, name: str, age: int) -> None:
		if age < 0:
			raise ValueError("age cannot be negative")
		self.name = name
		self.age = age

	def add_task(self, task: Task) -> None:
		self.schedule.add_task(task)

	def remove_task(self, task_id: int) -> None:
		self.schedule.remove_task(task_id)

	def get_tasks(self) -> List[Task]:
		return self.schedule.get_tasks()

	def get_schedule(self) -> Schedule:
		return self.schedule


@dataclass
class Owner:
	owner_id: int
	name: str
	email: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		if any(p.pet_id == pet.pet_id for p in self.pets):
			raise ValueError(f"Pet with id {pet.pet_id} already exists for this owner")
		self.pets.append(pet)

	def remove_pet(self, pet_id: int) -> None:
		pet = next((p for p in self.pets if p.pet_id == pet_id), None)
		if pet is None:
			raise ValueError(f"Pet with id {pet_id} not found for this owner")
		self.pets.remove(pet)

	def get_pets(self) -> List[Pet]:
		return list(self.pets)

	def get_all_tasks(self) -> List[Task]:
		return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Scheduler:
	owner: Owner

	def get_all_tasks(self) -> List[Task]:
		return self.owner.get_all_tasks()

	def get_pending_tasks(self) -> List[Task]:
		return [t for t in self.owner.get_all_tasks() if not t.completed]

	def get_overdue_tasks(self) -> List[Task]:
		now = datetime.now(tz=timezone.utc)
		return [t for t in self.owner.get_all_tasks() if not t.completed and t.due_datetime < now]

	def get_upcoming_tasks(self, within_hours: int) -> List[Task]:
		from datetime import timedelta
		now = datetime.now(tz=timezone.utc)
		cutoff = now + timedelta(hours=within_hours)
		return [t for t in self.owner.get_all_tasks() if not t.completed and now <= t.due_datetime <= cutoff]

	def get_tasks_by_pet(self, pet_id: int) -> List[Task]:
		pet = next((p for p in self.owner.get_pets() if p.pet_id == pet_id), None)
		if pet is None:
			raise ValueError(f"Pet with id {pet_id} not found")
		return pet.get_tasks()

	def get_tasks_by_priority(self) -> List[Task]:
		return sorted(self.owner.get_all_tasks(), key=lambda t: t.priority)
