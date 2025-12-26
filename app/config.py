from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    API_TITLE: str = 'ecom.tech test'
    API_VERSION: str = '0.0.1'
    API_DESCRIPTION: str = ''
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/student_grades"
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'postgres'
    DB_NAME: str = 'students_grades'
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20
    NAX_FILE_SIZE: int = 10 * 1024 * 1024
    MAX_RECORDS_PER_FILE: int = 10000
    MIN_GRADE: int = 1
    MAX_GRADE: int = 5
    GRADE_TO_ANALYZE: int = 2


@lru_cache()
def get_settings() -> Settings:
    return Settings()# кэшированный объект настроек