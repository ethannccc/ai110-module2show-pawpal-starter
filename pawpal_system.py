from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Task:
	task_id: int
	title: str
	description: str
	due_datetime: datetime
	priority: int
	completed: bool = False
    
	def mark_complete(self) -> None:
		pass

	def mark_incomplete(self) -> None:
		pass

	def reschedule(self, new_datetime: datetime) -> None:
		pass


@dataclass
class Schedule:
	schedule_id: int
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		pass

	def remove_task(self, task_id: int) -> None:
		pass

	def get_tasks(self) -> List[Task]:
		pass

	def get_pending_tasks(self) -> List[Task]:
		pass

	def sort_by_due_date(self) -> List[Task]:
		pass


@dataclass
class Pet:
	pet_id: int
	name: str
	species: str
	age: int
	schedule: Schedule

	def update_profile(self, name: str, age: int) -> None:
		pass

	def get_schedule(self) -> Schedule:
		pass


@dataclass
class Owner:
	owner_id: int
	name: str
	email: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		pass

	def remove_pet(self, pet_id: int) -> None:
		pass

	def get_pets(self) -> List[Pet]:
		pass
