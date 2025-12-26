import pytest
import asyncio
import asyncpg
from app.main import app
from app.database import init_db, close_db, execute_update
from fastapi.testclient import TestClient


@pytest.fixture(scope='')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse='True')
async def setup_test_db():
    await init_db()
    create_table_query = '''
        DROP TABLE IF EXISTS grades CASCADE;
        CREATE TABLE grades (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            grade INTEGER NOT NULL CHECK (grade >= 1 AND grade <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_grades_full_name ON grades(full_name);
        CREATE INDEX idx_grades_grade ON grades(grade);
        CREATE INDEX idx_grades_subject ON grades(subject);
        CREATE INDEX idx_grades_full_name_grade ON grades(full_name, grade);
    '''
    try:
        for query in create_table_query.split(';'):
            if query.strip():
                await execute_update(query.strip())
    except Exception as e:
        print(f'Ошбика при создании бд: {e}')
    yield
    await close_db()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def clean_db():
    await execute_update("TRUNCATE TABLE grades RESTART IDENTITY")
    yield
    await execute_update("TRUNCATE TABLE grades RESTART IDENTITY")