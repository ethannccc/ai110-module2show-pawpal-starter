from datetime import datetime, timedelta, timezone

import pytest

from pawpal_system import Owner, Pet, Schedule, Scheduler, Task


def _sample_owner_with_pets() -> tuple[Owner, Pet, Pet]:
    owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")
    dog = Pet(pet_id=101, name="Milo", species="dog", age=4, schedule=Schedule(schedule_id=9001))
    cat = Pet(pet_id=102, name="Luna", species="cat", age=2, schedule=Schedule(schedule_id=9002))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat


def test_task_requires_timezone_aware_datetime() -> None:
    naive = datetime(2026, 3, 16, 10, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        Task(
            task_id=1,
            title="Walk",
            description="Morning walk",
            due_datetime=naive,
            priority=1,
        )


def test_schedule_get_tasks_returns_copy_not_internal_list() -> None:
    now = datetime.now(timezone.utc)
    task = Task(task_id=1, title="Feed", description="Dinner", due_datetime=now, priority=1)
    schedule = Schedule(schedule_id=1)
    schedule.add_task(task)

    snapshot = schedule.get_tasks()
    snapshot.clear()

    assert len(snapshot) == 0
    assert len(schedule.get_tasks()) == 1


def test_filter_and_sort_tasks_applies_filters() -> None:
    owner, dog, _ = _sample_owner_with_pets()
    now = datetime.now(timezone.utc)

    t1 = Task(1, "Walk", "", now + timedelta(hours=2), 1, frequency="daily")
    t2 = Task(2, "Brush", "", now + timedelta(hours=1), 2, frequency="weekly")
    t3 = Task(3, "Play", "", now + timedelta(hours=3), 3, frequency="daily")
    t3.mark_complete()

    dog.add_task(t1)
    dog.add_task(t2)
    dog.add_task(t3)

    scheduler = Scheduler(owner)
    results = scheduler.filter_and_sort_tasks(
        pet_id=101,
        include_completed=False,
        frequency="daily",
        max_priority=2,
    )

    assert [t.task_id for t in results] == [1]


def test_detect_conflicts_same_pet_overlap() -> None:
    owner, dog, _ = _sample_owner_with_pets()
    now = datetime.now(timezone.utc)

    t1 = Task(1, "Walk", "", now, 1, duration_minutes=60)
    t2 = Task(2, "Feed", "", now + timedelta(minutes=30), 1, duration_minutes=20)
    dog.add_task(t1)
    dog.add_task(t2)

    conflicts = Scheduler(owner).detect_conflicts(pet_id=101)
    assert len(conflicts) == 1
    assert conflicts[0][0].task_id == 1
    assert conflicts[0][1].task_id == 2


def test_detect_conflicts_should_ignore_different_pets() -> None:
    """Intentional strict expectation to reveal current cross-pet conflict behavior."""
    owner, dog, cat = _sample_owner_with_pets()
    now = datetime.now(timezone.utc)

    dog.add_task(Task(1, "Dog Walk", "", now, 1, duration_minutes=60))
    cat.add_task(Task(2, "Cat Feed", "", now + timedelta(minutes=30), 1, duration_minutes=20))

    # Expected by this test: conflicts should be per-pet only.
    # Current implementation checks all owner tasks when pet_id is None.
    conflicts = Scheduler(owner).detect_conflicts()
    assert conflicts == []
