from datetime import datetime, timedelta, timezone

from pawpal_system import Owner, Pet, Schedule, Scheduler, Task


def print_tasks(header: str, tasks: list[Task]) -> None:
	print(f"\n{header}")
	if not tasks:
		print("- none")
		return

	for task in tasks:
		print(
			f"- task_id={task.task_id}, title='{task.title}', "
			f"pet_due={task.due_datetime.isoformat()}, "
			f"priority={task.priority}, frequency={task.frequency}, "
			f"completed={task.completed}"
		)


def main() -> None:
	print("PawPal+ data flow demo")
	print("Flow: Owner -> Pet -> Schedule -> Task | Scheduler reads across pets")

	# 1) One owner and two pets.
	owner = Owner(owner_id=1, name="Alex Rivera", email="alex@example.com")

	dog = Pet(
		pet_id=101,
		name="Milo",
		species="Dog",
		age=4,
		schedule=Schedule(schedule_id=9001),
	)
	cat = Pet(
		pet_id=102,
		name="Luna",
		species="Cat",
		age=2,
		schedule=Schedule(schedule_id=9002),
	)

	owner.add_pet(dog)
	owner.add_pet(cat)

	# 2) At least three tasks with timezone-aware datetimes.
	now = datetime.now(timezone.utc)
	t1 = Task(
		task_id=1,
		title="Morning Walk",
		description="30 minute walk in the park",
		due_datetime=now + timedelta(hours=1),
		priority=1,
		frequency="daily",
	)
	t2 = Task(
		task_id=2,
		title="Feed Dinner",
		description="Serve evening meal",
		due_datetime=now + timedelta(hours=3),
		priority=1,
		frequency="daily",
	)
	t3 = Task(
		task_id=3,
		title="Brush Fur",
		description="Brush coat for 10 minutes",
		due_datetime=now + timedelta(days=1),
		priority=2,
		frequency="weekly",
	)

	dog.add_task(t1)
	dog.add_task(t2)
	cat.add_task(t3)

	# 3) Test scheduler across pets.
	scheduler = Scheduler(owner=owner)

	print_tasks("All tasks from scheduler", scheduler.get_all_tasks())
	print_tasks("Pending tasks", scheduler.get_pending_tasks())
	print_tasks("Upcoming tasks within 4 hours", scheduler.get_upcoming_tasks(within_hours=4))
	print_tasks("Dog tasks only", scheduler.get_tasks_by_pet(pet_id=101))
	print_tasks("Tasks sorted by priority", scheduler.get_tasks_by_priority())

	# 4) Verify completion status updates are visible through scheduler retrieval.
	print("\nMarking task_id=1 complete...")
	t1.mark_complete()
	print_tasks("Pending tasks after mark_complete", scheduler.get_pending_tasks())

	# 5) Inspect one class method carefully: Schedule.get_tasks returns a copy.
	print("\nInspecting method behavior: Pet.get_tasks via Schedule.get_tasks copy safety")
	snapshot = dog.get_tasks()
	print(f"Dog tasks before external list mutation attempt: {len(dog.get_tasks())}")
	snapshot.clear()
	print(f"External list cleared length: {len(snapshot)}")
	print(f"Dog internal tasks after mutation attempt: {len(dog.get_tasks())}")

	# 6) Verify owner-level retrieval still works after operations.
	owner_tasks = owner.get_all_tasks()
	print(f"\nOwner can retrieve all tasks count: {len(owner_tasks)}")

if __name__ == "__main__":
	main()
