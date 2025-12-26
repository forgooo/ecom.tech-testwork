import pytest
from app.services.grade_service import GradeService
from app.schemas import GradeRecord
from app.database import execute_update


@pytest.mark.asyncio
async def test_insert_grades(clean_db):
    records = [
        GradeRecord(full_name="Иванов Иван", subject="Математика", grade=5),
        GradeRecord(full_name="Иванов Иван", subject="Русский язык", grade=4),
        GradeRecord(full_name="Петров Пётр", subject="Математика", grade=3),
    ]
    records_loaded, students_count = await GradeService.insert_grades(records)
    assert records_loaded == 3
    assert students_count == 2


@pytest.mark.asyncio
async def test_insert_empty_grades_list(clean_db):
    records = []
    records_loaded, students_count = await GradeService.insert_grades(records)
    assert records_loaded == 0
    assert students_count == 0


@pytest.mark.asyncio
async def test_get_students_with_more_than_n_twos(clean_db):
    for i in range(5):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Иванов Иван", f"Предмет{i}", 2
        )
    for i in range(2):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Петров Пётр", f"Предмет{i}", 2
        )
    students = await GradeService.get_students_with_more_than_n_twos(n=3)
    assert len(students) == 1
    assert students[0].full_name == "Иванов Иван"
    assert students[0].count_twos == 5


@pytest.mark.asyncio
async def test_get_students_with_less_than_n_twos(clean_db):
    for i in range(3):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Иванов Иван", f"Предмет{i}", 2
        )
    
    for i in range(2):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Петров Пётр", f"Предмет{i}", 2
        )
    students = await GradeService.get_students_with_less_than_n_twos(n=5)
    assert len(students) == 2
    assert students[0].full_name == "Иванов Иван"
    assert students[0].count_twos == 3
    assert students[1].full_name == "Петров Пётр"
    assert students[1].count_twos == 2


@pytest.mark.asyncio
async def test_get_student_stats(clean_db):
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Математика", 5
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Русский язык", 3
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Петров Пётр", "Математика", 4
    )
    stats = await GradeService.get_student_stats()
    assert stats["total_students"] == 2
    assert stats["total_grades"] == 3
    assert stats["average_grade"] == 4.0
    assert stats["min_grade"] == 3
    assert stats["max_grade"] == 5


@pytest.mark.asyncio
async def test_insert_same_student_multiple_subjects(clean_db):
    records = [
        GradeRecord(full_name="Иванов Иван", subject="Математика", grade=5),
        GradeRecord(full_name="Иванов Иван", subject="Русский язык", grade=4),
        GradeRecord(full_name="Иванов Иван", subject="История", grade=2),
        GradeRecord(full_name="Иванов Иван", subject="География", grade=2),
    ]
    records_loaded, students_count = await GradeService.insert_grades(records)
    assert records_loaded == 4
    assert students_count == 1  # Один студент


@pytest.mark.asyncio
async def test_get_students_with_different_thresholds(clean_db):
    for i in range(7):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Иванов Иван", f"Предмет{i}", 2
        )
    more_than_5 = await GradeService.get_students_with_more_than_n_twos(n=5)
    more_than_7 = await GradeService.get_students_with_more_than_n_twos(n=7)
    more_than_10 = await GradeService.get_students_with_more_than_n_twos(n=10)
    assert len(more_than_5) == 1
    assert len(more_than_7) == 0
    assert len(more_than_10) == 0
