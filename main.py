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

    # Сначала очистка на основе переданных данных
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_value = re.sub(r'\s+', ' ', value).strip()

            # Специальная обработка для "Оценка"
            if key == 'Оценка' and re.search(r'\d+,\d+', cleaned_value):
                cleaned_value = re.sub(r'[,\/].*$', '', cleaned_value).strip()

            cleaned_data[key] = cleaned_value
        else:
            cleaned_data[key] = value

    # Дополнительная очистка, если словарь был изменен в процессе
    # (Хотя 'cleaned_data' уже содержит все очищенные данные,
    # эта секция может быть удалена, так как дублирует логику выше.)
    for key in list(cleaned_data.keys()):
        if isinstance(cleaned_data[key], str):
            cleaned_data[key] = re.sub(r'\s+', ' ', cleaned_data[key]).strip()

    return cleaned_data


def save_combined_excel(all_participants_data: List[Dict[str, Any]], output_filepath: pathlib.Path):
    """
    Сохраняет все собранные данные участников в один Excel-файл.
    """
    if not all_participants_data:
        print("Нечего сохранять: Список объединенных данных пуст.")
        return

    # 1. Создание общего DataFrame из списка всех словарей
    df = pd.DataFrame(all_participants_data)

    try:
        # Сохранение в Excel (.xlsx)
        df.to_excel(output_filepath, index=False, engine='openpyxl')
        print(f"\nОБЪЕДИНЕННЫЙ ОТЧЕТ УСПЕШНО СОХРАНЕН:")
        print(f"Файл: {output_filepath.name}")
        print(f"Всего записей: {len(df)}\n")
        print(f"🆗 Сохранено в XLSX: {output_filepath.resolve()}")
    except Exception as e:
        print(f"\n❌ ФАТАЛЬНАЯ ОШИБКА при сохранении объединенного Excel-файла: {e}")
    finally:
        csv_filepath = output_filepath.with_suffix('.csv')
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        print(f"🆗 Сохранено в CSV: {csv_filepath.resolve()}")


def process_html_file(filename_path: pathlib.Path) -> List[Dict[str, Any]]:
    """
    Обрабатывает один HTML-файл, извлекает данные и возвращает список
    словарей, где каждый словарь - это строка участника с добавленной
    информацией о курсе.
    """
    print(f"    -> Парсинг: {filename_path.name}")
    # parse_all_review_html теперь возвращает список блоков
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

        # 1. Очистка данных курса
        cleaned_course_info = clean_test_infp(course_info)

        # 2. Объединение данных курса с данными участников
        for participant in participants_data:
            row = cleaned_course_info.copy()
            row.update(participant)
            combined_data_list.append(row)

    return combined_data_list


if __name__ == '__main__':
    dir_path.mkdir(parents=True, exist_ok=True)
    dir_report_path.mkdir(parents=True, exist_ok=True)

    # 2. Сбор всех файлов для обработки
    all_html_files = list(dir_path.glob('*.html'))

    print("-" * 30)
    print(f"Найдено HTML файлов: {len(all_html_files)}")
    print(f"Итоговый отчет будет сохранен в: {FINAL_REPORT_NAME}")
    print("-" * 30)

    # 3. Основной цикл: сбор всех данных в один список
    all_combined_data = []
    final_report_filepath = dir_report_path / FINAL_REPORT_NAME

    for filename_path in all_html_files:
        file_data = process_html_file(filename_path)
        all_combined_data.extend(file_data)

    # 4. Сохранение объединенного отчета
    print("-" * 30)
    if all_combined_data:
        save_combined_excel(all_combined_data, final_report_filepath)
    else:
        print("Обработка завершена, но данные для сохранения отсутствуют.")

    print("-" * 30)
