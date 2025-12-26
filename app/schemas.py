from pydantic import BaseModel, Field
from typing import Optional


class GradeRecord(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=255)
    grade: int = Field(..., ge=1, le=5)


class UploadGradesResponse(BaseModel):
    status: str
    records_loaded: int
    students: int
    message: Optional[str] = None


class StudentGradeCount(BaseModel):
    full_name: str
    twos_count: int