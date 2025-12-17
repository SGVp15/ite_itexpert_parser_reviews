import pathlib
import re
from typing import List, Dict, Any

import pandas as pd

from config import dir_path, dir_report_path, FINAL_REPORT_NAME
from parser import parse_all_review_html


def clean_test_infp(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очищает строковые значения в словаре и форматирует числовые данные.
    """
    cleaned_data = {}

    for key, value in data.items():
        if isinstance(value, str):
            cleaned_value = re.sub(r'\s+', ' ', value).strip()

            if key == 'Оценка' and re.search(r'\d+,\d+', cleaned_value):
                cleaned_value = re.sub(r'[,\/].*$', '', cleaned_value).strip()

            cleaned_data[key] = cleaned_value
        else:
            cleaned_data[key] = value

    return cleaned_data


def save_combined_excel(all_participants_data: List[Dict[str, Any]], output_filepath: pathlib.Path):
    """
    Сохраняет все собранные данные участников в один Excel-файл с фильтрацией.
    """
    if not all_participants_data:
        print("Нечего сохранять: Список объединенных данных пуст.")
        return

    # 1. Создание общего DataFrame
    df = pd.DataFrame(all_participants_data)

    column_to_filter = 'Разрешение на публикацию'

    if column_to_filter in df.columns:
        # Приводим к строке на случай, если там числа, и фильтруем по значению '1'
        df = df[df[column_to_filter].astype(str) == '1']
        print(f"Применен фильтр: {column_to_filter} == '1'")
    else:
        print(f"⚠️ Предупреждение: Колонка '{column_to_filter}' не найдена. Фильтрация не применена.")

    col_quality = 'Качество курса комментарий'
    col_teacher = 'Работа преподавателя комментарий'
    df = df[~(
            (df[col_teacher].isna() | (df[col_teacher].astype(str).str.strip() == '')) &
            (df[col_quality].isna() | (df[col_quality].astype(str).str.strip() == ''))
    )]
    print(f"Исключены записи, где оба комментария ('{col_teacher}' и '{col_quality}') отсутствуют.")

    if df.empty:
        print("После фильтрации данных не осталось. Файл не будет сохранен.")
        return

    try:
        # Сохранение в Excel (.xlsx)
        df.to_excel(output_filepath, index=False, engine='openpyxl')
        print(f"\nОБЪЕДИНЕННЫЙ ОТЧЕТ УСПЕШНО СОХРАНЕН:")
        print(f"Файл: {output_filepath.name}")
        print(f"Всего записей после фильтрации: {len(df)}\n")
        print(f"🆗 Сохранено в XLSX: {output_filepath.resolve()}")
    except Exception as e:
        print(f"\n❌ ФАТАЛЬНАЯ ОШИБКА при сохранении объединенного Excel-файла: {e}")
    finally:
        csv_filepath = output_filepath.with_suffix('.csv')
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        print(f"🆗 Сохранено в CSV: {csv_filepath.resolve()}")


def process_html_file(filename_path: pathlib.Path) -> List[Dict[str, Any]]:
    """
    Обрабатывает один HTML-файл и возвращает список словарей.
    """
    print(f"    -> Парсинг: {filename_path.name}")
    raw_blocks = parse_all_review_html(filename=filename_path)

    combined_data_list = []

    if not raw_blocks:
        print(f"    ⚠️ Файл {filename_path.name}: Парсинг не вернул данных.")
        return []

    for data_block in raw_blocks:
        course_info = data_block.get('course_info', {})
        participants_data = data_block.get('participants_data', [])

        if not participants_data:
            continue

        cleaned_course_info = clean_test_infp(course_info)

        for participant in participants_data:
            row = cleaned_course_info.copy()
            row.update(participant)
            combined_data_list.append(row)

    return combined_data_list


if __name__ == '__main__':
    dir_path.mkdir(parents=True, exist_ok=True)
    dir_report_path.mkdir(parents=True, exist_ok=True)

    all_html_files = list(dir_path.glob('*.html'))

    print("-" * 30)
    print(f"Найдено HTML файлов: {len(all_html_files)}")
    print(f"Итоговый отчет будет сохранен в: {FINAL_REPORT_NAME}")
    print("-" * 30)

    all_combined_data = []
    final_report_filepath = dir_report_path / FINAL_REPORT_NAME

    for filename_path in all_html_files:
        file_data = process_html_file(filename_path)
        all_combined_data.extend(file_data)

    print("-" * 30)
    if all_combined_data:
        save_combined_excel(all_combined_data, final_report_filepath)
    else:
        print("Обработка завершена, но данные для сохранения отсутствуют.")

    print("-" * 30)