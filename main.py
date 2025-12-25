import datetime
import re
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from Email import EmailSending
from SeleniumWEB.ite_selenium import IteSelenium
from Utils.log import log
from parser import parse_all_review_html
from root_config import FILE_DOWNLOAD_HTML, FILE_REPORT_SEND_EMAIL, FILE_ALL_REPORT, FILE_TEMP_CSV, LIST_EMAIL


def clean_test_infp(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очищает строковые значения в словаре и форматирует числовые данные.
    """
    cleaned_data = {}

    for key, value in data.items():
        if isinstance(value, str):
            cleaned_value = re.sub(r'\s+', ' ', value).strip()

            if key == 'Оценка' and re.search(r'\d+,\d+', cleaned_value):
                cleaned_value = re.sub(r'[,/].*$', '', cleaned_value).strip()

            cleaned_data[key] = cleaned_value
        else:
            cleaned_data[key] = value

    return cleaned_data


def save_combined_excel(all_participants_data: List[Dict[str, Any]], output_filepath: Path):
    """
    Сохраняет все собранные данные участников в один Excel-файл с фильтрацией.
    """
    # if not all_participants_data:
    #     print("Нечего сохранять: Список объединенных данных пуст.")
    #     return

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


def process_html_file(filename_path: Path) -> List[Dict[str, Any]]:
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


def download_html_file():
    html_file = FILE_DOWNLOAD_HTML
    web_driver = IteSelenium()
    web_driver.authorization()
    s = web_driver.get_page_source()
    with open(html_file, mode='w', encoding='windows-1251', errors='ignore') as f:
        f.write(s)


if __name__ == '__main__':
    log.info(f'[ Start ] {datetime.datetime.now()}')
    download_html_file()
    all_combined_data = process_html_file(FILE_DOWNLOAD_HTML)
    if all_combined_data:
        save_combined_excel(all_participants_data=all_combined_data,
                            output_filepath=FILE_TEMP_CSV)
    else:
        print("Обработка завершена, но данные для сохранения отсутствуют.")

    # Оставляем только новые отзывы
    print('Оставляем только новые отзывы')
    df1 = pd.read_csv(FILE_TEMP_CSV)
    try:
        df2 = pd.read_csv(FILE_ALL_REPORT)
        df_diff = df1.merge(df2, how='left', indicator=True)
        result = df_diff[df_diff['_merge'] == 'left_only'].drop('_merge', axis=1)
        all_report = df1 + df2
    except Exception as e:
        result = df1
        all_report = df1
    print("-" * 30)
    save_combined_excel(all_participants_data=result,
                        output_filepath=FILE_REPORT_SEND_EMAIL)
    save_combined_excel(all_participants_data=all_report,
                        output_filepath=FILE_ALL_REPORT)
    if FILE_REPORT_SEND_EMAIL.is_file():
        EmailSending(subject='Новый отзыв на сайте.', to=LIST_EMAIL,
                     files_path=[FILE_REPORT_SEND_EMAIL, ]).send_email()
