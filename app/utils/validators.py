import csv
import io
from app.schemas import GradeRecord


async def validate_csv_file(file_content: bytes, filename: str):
    if not filename.lower().endswith('.csv'):
        raise ValueError('Только csv файлы')

    records = []
    errors = []

    try:
        content_str = file_content.decode('utf-8')
        if content_str.startswith('\ufeff'):
            content_str = content_str[1:]
        print(f"DEBUG: First line: {content_str.split(chr(10))[0]}")
        csv_reader = csv.DictReader(io.StringIO(content_str), delimiter=';')
        print(f"DEBUG: Fieldnames: {csv_reader.fieldnames}")
        required_fields = {'Дата', 'Номер группы', 'ФИО', 'Оценка'}
        if not required_fields.issubset(set(csv_reader.fieldnames or [])):
            raise ValueError(f'Нет необходимых колонок. Найдены: {csv_reader.fieldnames}')
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                print(f"DEBUG: Row {row_num}: {row}")
                record = GradeRecord(
                    full_name=row['ФИО'].strip(),
                    subject=row['Номер группы'].strip(),
                    grade=int(row['Оценка'])
                )
                records.append(record)
            except ValueError as e:
                errors.append(f'Строка {row_num}: {str(e)}')
    except UnicodeDecodeError:
        raise ValueError('Файл должен быть в UTF-8')
    
    return records, errors
