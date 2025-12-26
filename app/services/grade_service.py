from app.database import execute_query, execute_many, execute_query_single
from typing import List, Tuple
from app.schemas import GradeRecord, StudentGradeCount


class GradeService:
    @staticmethod
    async def insert_grades(records: List[GradeRecord]) -> Tuple[int, int]:
        insert_data = [(record.full_name, record.subject, record.grade) for record in records]
        insert_query = '''
            INSERT INTO grades (full_name, subject, grade)
            VALUES ($1, $2, $3)
        '''
        await execute_many(insert_query, insert_data)
        count_student_query = '''
            SELECT COUNT(DISTINCT full_name) as student_count
            FROM grades
        '''
        result = await execute_query_single(count_student_query)
        student_count = result['student_count']
        return len(records), student_count

    @staticmethod
    async def get_students_with_more_than_n_twos(n: int = 3) -> List[StudentGradeCount]:
        query = '''
            SELECT 
                full_name,
                COUNT(*) as twos_count
            FROM grades
            WHERE grade = 2
            GROUP BY full_name
            HAVING COUNT(*) > $1
            ORDER BY twos_count DESC, full_name ASC
        '''
        rows = await execute_query(query, n)
        return [
            StudentGradeCount(
                full_name=row['full_name'],
                twos_count=row['twos_count']
            )
            for row in rows
        ]

    @staticmethod
    async def get_students_with_less_than_n_twos(n: int = 5) -> List[StudentGradeCount]:
        query = '''
            SELECT 
                full_name,
                COUNT(*) as twos_count
            FROM grades
            WHERE grade = 2
            GROUP BY full_name
            HAVING COUNT(*) < $1
            ORDER BY twos_count DESC, full_name ASC
        '''
        rows = await execute_query(query, n)
        return [
            StudentGradeCount(
                full_name=row['full_name'],
                twos_count=row['twos_count']
            )
            for row in rows
        ]
