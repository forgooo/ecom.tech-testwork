from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import List
from app.schemas import UploadGradesResponse, StudentGradeCount
from app.services.grade_service import GradeService
from app.utils.validators import validate_csv_file


router = APIRouter(prefix='/api', tags=['grades'])


@router.post(
    '/upload-grades',
    response_model = UploadGradesResponse,
    status_code = status.HTTP_200_OK,
)
async def upload_grades(file: UploadFile = File(...)) -> UploadGradesResponse:
    if file.content_type not in ['text/csv', 'application/vnd.ms-excel']: # application/vnd.ms-excel
        raise HTTPException(
            status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail = f'Unsupported file type'
        )
    file_content = await file.read()
    records, errors = await validate_csv_file(file_content, file.filename or '')
    if errors:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"На стадии парсинга ошибки: {';'.join(errors[:5])}"
        )
    records_loaded, students_count = await GradeService.insert_grades(records)
    return UploadGradesResponse(
        status = 'ok',
        records_loaded = records_loaded,
        students = students_count,
        message = f'Загруженны записи о {records_loaded} студентах'
    )


@router.get(
    '/students/more-than-3-twos',
    response_model = List[StudentGradeCount],
    status_code = status.HTTP_200_OK
)
async def get_students_with_more_than_3_twos() -> List[StudentGradeCount]:
    students = await GradeService.get_students_with_more_than_n_twos(n = 3)
    return students

@router.get('/students/less-than-5-twos')
async def get_students_with_less_than_5_twos() -> List[StudentGradeCount]:
    students = await GradeService.get_students_with_less_than_n_twos(n=5)
    return students
