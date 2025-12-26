import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import execute_update


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["message"] == "aaa"


@pytest.mark.asyncio
async def test_upload_grades_success(client, clean_db):
    csv_content = """full_name,subject,grade
Иванов Иван,Математика,5
Иванов Иван,Русский язык,4
Петров Пётр,Математика,2
Петров Пётр,Русский язык,3"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/upload-grades", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["records_loaded"] == 4
    assert data["students"] == 2


@pytest.mark.asyncio
async def test_upload_grades_invalid_file_type(client):
    content = "some content"
    files = {"file": ("grades.txt", io.BytesIO(content.encode()), "text/plain")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_grades_invalid_csv_missing_columns(client):
    csv_content = """full_name,subject
Иванов Иван,Математика"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_grades_invalid_grade_value(client):
    csv_content = """full_name,subject,grade
Иванов Иван,Математика,10"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 400
    assert "Validation errors" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_grades_empty_csv(client):
    csv_content = """full_name,subject,grade"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 400
    assert "No valid records found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_grades_csv_with_extra_spaces(client, clean_db):
    csv_content = """full_name,subject,grade
  Иванов Иван  , Математика , 5
Петров Пётр,Русский язык,3"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["records_loaded"] == 2


@pytest.mark.asyncio
async def test_get_students_with_more_than_3_twos(client, clean_db):
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Предмет1", 2
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Предмет2", 2
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Предмет3", 2
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Предмет4", 2
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Петров Пётр", "Предмет1", 2
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Петров Пётр", "Предмет2", 2
    )
    
    response = client.get("/api/students/more-than-3-twos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Иванов Иван"
    assert data[0]["count_twos"] == 4


@pytest.mark.asyncio
async def test_get_students_with_more_than_3_twos_no_results(client, clean_db):
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Предмет1", 2
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Предмет2", 2
    )
    response = client.get("/api/students/more-than-3-twos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_students_with_less_than_5_twos(client, clean_db):
    for i in range(2):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Иванов Иван", f"Предмет{i}", 2
        )
    
    for i in range(4):
        await execute_update(
            "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
            "Петров Пётр", f"Предмет{i}", 2
        )
    
    response = client.get("/api/students/less-than-5-twos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["count_twos"] >= data[1]["count_twos"]


@pytest.mark.asyncio
async def test_get_students_with_less_than_5_twos_all_records(client, clean_db):
    test_data = [
        ("Студент1", 1),  # 1 двойка
        ("Студент2", 2),  # 2 двойки
        ("Студент3", 3),  # 3 двойки
        ("Студент4", 4),  # 4 двойки
        ("Студент5", 5),  # 5 двоек (не должен быть включен)
    ]
    
    for student, count in test_data:
        for i in range(count):
            await execute_update(
                "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
                student, f"Предмет{i}", 2
            )
    
    response = client.get("/api/students/less-than-5-twos")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert all(student["full_name"] != "Студент5" for student in data)


@pytest.mark.asyncio
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Математика", 5
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Иванов Иван", "Русский язык", 4
    )
    await execute_update(
        "INSERT INTO grades (full_name, subject, grade) VALUES ($1, $2, $3)",
        "Петров Пётр", "Математика", 3
    )
    
    response = client.get("/api/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] == 2
    assert data["total_grades"] == 3
    assert data["average_grade"] == 4.0
    assert data["min_grade"] == 3
    assert data["max_grade"] == 5


@pytest.mark.asyncio
async def test_get_stats_empty_database(client, clean_db):
    response = client.get("/api/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] == 0
    assert data["total_grades"] == 0


@pytest.mark.asyncio
async def test_full_workflow(client, clean_db):
    csv_content = """full_name,subject,grade
Иванов Иван,Математика,5
Иванов Иван,Русский язык,2
Иванов Иван,История,2
Иванов Иван,География,2
Иванов Иван,Физика,2
Петров Пётр,Математика,3
Петров Пётр,Русский язык,2
Петров Пётр,История,2"""
    
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    upload_response = client.post("/api/upload-grades", files=files)
    
    assert upload_response.status_code == 200
    assert upload_response.json()["records_loaded"] == 8
    assert upload_response.json()["students"] == 2
    more_response = client.get("/api/students/more-than-3-twos")
    assert more_response.status_code == 200
    more_data = more_response.json()
    assert len(more_data) == 1
    assert more_data[0]["full_name"] == "Иванов Иван"
    assert more_data[0]["count_twos"] == 4
    less_response = client.get("/api/students/less-than-5-twos")
    assert less_response.status_code == 200
    less_data = less_response.json()
    assert len(less_data) == 2
    stats_response = client.get("/api/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_students"] == 2
    assert stats["total_grades"] == 8


@pytest.mark.asyncio
async def test_multiple_uploads(client, clean_db):
    csv1 = """full_name,subject,grade
Иванов Иван,Математика,5
Иванов Иван,Русский язык,4"""
    files1 = {"file": ("grades1.csv", io.BytesIO(csv1.encode()), "text/csv")}
    response1 = client.post("/api/upload-grades", files=files1)
    assert response1.status_code == 200
    assert response1.json()["records_loaded"] == 2
    csv2 = """full_name,subject,grade
Петров Пётр,Математика,3
Петров Пётр,Русский язык,2"""
    files2 = {"file": ("grades2.csv", io.BytesIO(csv2.encode()), "text/csv")}
    response2 = client.post("/api/upload-grades", files=files2)
    assert response2.status_code == 200
    assert response2.json()["records_loaded"] == 2
    stats = client.get("/api/stats").json()
    assert stats["total_students"] == 2
    assert stats["total_grades"] == 4


@pytest.mark.asyncio
async def test_upload_csv_with_unicode(client, clean_db):
    csv_content = """full_name,subject,grade
Жданов Женя,Математика,5
Яковлев Яков,Русский язык,4
Ющенко Юра,История,3"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 200
    assert response.json()["records_loaded"] == 3


@pytest.mark.asyncio
async def test_upload_csv_max_grade_boundary(client, clean_db):
    csv_content = """full_name,subject,grade
Иванов Иван,Предмет1,1
Иванов Иван,Предмет2,5"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 200
    assert response.json()["records_loaded"] == 2


@pytest.mark.asyncio
async def test_upload_csv_with_long_names(client, clean_db):
    long_name = "А" * 255  # 255 символов
    csv_content = f"""full_name,subject,grade
{long_name},Математика,5"""
    files = {"file": ("grades.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/upload-grades", files=files)
    assert response.status_code == 200
    assert response.json()["records_loaded"] == 1
