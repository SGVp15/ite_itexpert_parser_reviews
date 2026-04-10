# Импорты ваших локальных модулей
# Если Contact находится в этом же файле, удалите строку ниже
import datetime
import re
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from Contact import Contact
from Email import EmailSending
from SeleniumWEB.ite_selenium import IteSelenium
from Utils.log import log
from parser import parse_all_review_html
from root_config import (FILE_DOWNLOAD_HTML, FILE_REPORT_SEND_EMAIL,
                         FILE_ALL_REPORT, FILE_TEMP_CSV, LIST_EMAIL,
                         FILE_CONTACT_1C)


def clean_test_infp(data: Dict[str, Any]) -> Dict[str, Any]:
    """Очищает строковые значения в словаре и форматирует числовые данные."""
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
    """Сохраняет данные участников в Excel и CSV с фильтрацией пустых комментариев."""
    if not all_participants_data:
        return False

    df = pd.DataFrame(all_participants_data)

    col_quality = 'Качество курса комментарий'
    col_teacher = 'Работа преподавателя комментарий'

    # Фильтрация (удаляем если оба поля пустые)
    if col_quality in df.columns and col_teacher in df.columns:
        df = df[~(
                (df[col_quality].isna() | (df[col_quality].astype(str).str.strip() == '')) &
                (df[col_teacher].isna() | (df[col_teacher].astype(str).str.strip() == ''))
        )]

    if df.empty:
        return False

    try:
        df.to_excel(output_filepath, index=False, engine='openpyxl')
        csv_filepath = output_filepath.with_suffix('.csv')
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False


def process_html_file(filename_path: Path) -> List[Dict[str, Any]]:
    """Обрабатывает HTML-файл и возвращает список словарей."""
    print(f"    -> Парсинг: {filename_path.name}")
    raw_blocks = parse_all_review_html(filename=filename_path)
    combined_data_list = []

    if not raw_blocks:
        return []

    for data_block in raw_blocks:
        course_info = data_block.get('course_info', {})
        participants_data = data_block.get('participants_data', [])
        cleaned_course_info = clean_test_infp(course_info)

        for participant in participants_data:
            row = cleaned_course_info.copy()
            row.update(participant)
            combined_data_list.append(row)
    return combined_data_list


def process_contacts_to_list() -> List[Dict[str, str]]:
    """Читает файл 1С через класс Contact и готовит список для Pandas."""
    contacts_list = []
    # Попробуйте utf-8, если ошибка - смените на windows-1251 или utf-16
    encodings = ['utf-8', 'windows-1251', 'utf-16']

    for enc in encodings:
        try:
            with open(FILE_CONTACT_1C, encoding=enc, mode='r') as f:
                rows = f.read().split('\n')

            for row in rows:
                if not row.strip(): continue
                c = Contact(row)
                if c.email:
                    contacts_list.append({
                        'email_1c': c.email.strip().lower(),  # Ключ в нижнем регистре
                        'Компания_1С': c.company,
                        'Должность_1С': c.prof,
                        'ФИО_1С': c.name
                    })
            return contacts_list  # Если успешно прочитали, выходим из цикла кодировок
        except Exception:
            continue
    return []


def main():
    log.info(f'[ Start ] {datetime.datetime.now()}')

    # 1. Загружаем справочник из 1С
    contacts_data = process_contacts_to_list()
    df_contacts_from_1c = pd.DataFrame(contacts_data)

    # 2. Парсим HTML
    all_combined_data = process_html_file(FILE_DOWNLOAD_HTML)
    if all_combined_data:
        save_combined_excel(all_participants_data=all_combined_data,
                            output_filepath=FILE_TEMP_CSV)
    else:
        print("Данные для обработки отсутствуют.")
        return

    # 3. Читаем временный CSV и сопоставляем с 1С
    print('Обогащение данных из 1С...')
    df_new_records = pd.read_csv(FILE_TEMP_CSV)

    column_permission = 'Разрешение на публикацию'
    if column_permission in df_new_records.columns:
        # Оставляем только те строки, где значение равно 1
        # (используем pd.to_numeric на случай, если 1 записана как строка "1")
        df_new_records = df_new_records[pd.to_numeric(df_new_records[column_permission], errors='coerce') == 1]

    # Предполагаемое имя колонки email в вашем HTML-парсере
    email_col_main = 'Пользователь'

    if not df_contacts_from_1c.empty and email_col_main in df_new_records.columns:
        # Приводим основной email к нижнему регистру для сравнения
        df_new_records[email_col_main] = df_new_records[email_col_main].astype(str).str.strip().str.lower()

        df_new_records = df_new_records.merge(df_contacts_from_1c, left_on=email_col_main, right_on='email_1c', how='left')
        df_new_records.drop(columns=['email_1c'], inplace=True, errors='ignore')

    # 4. Сравнение с накопленным отчетом (выделение только новых)
    try:
        df_all_report = pd.read_csv(FILE_ALL_REPORT)

        if email_col_main in df_all_report.columns:
            df_all_report[email_col_main] = df_all_report[email_col_main].astype(str).str.strip().str.lower()

        df_all_report = df_all_report.fillna('')
        df_all_report.drop_duplicates()
        df_new_records = df_new_records.fillna('')
        df_new_records.drop_duplicates()

        df_diff = df_new_records.merge(df_all_report, how='left', indicator=True)
        result_df = df_diff[df_diff['_merge'] == 'left_only'].drop('_merge', axis=1)

        all_report_df = pd.concat([df_new_records, df_all_report], ignore_index=True)

        result_df = result_df.fillna('')
        all_report_df = all_report_df.fillna('')
        all_report_df.drop_duplicates()
        result_df.drop_duplicates()
    except Exception:
        print("Создание нового файла истории.")
        result_df = df_new_records
        all_report_df = df_new_records

    # 5. Сохранение итогов
    have_new = save_combined_excel(result_df.to_dict('records'), FILE_REPORT_SEND_EMAIL)
    save_combined_excel(all_report_df.to_dict('records'), FILE_ALL_REPORT)

    # 6. Отправка почты
    if have_new and FILE_REPORT_SEND_EMAIL.is_file():
        print(f"Найдено новых отзывов: {len(result_df)}. Отправка почты...")
        EmailSending(subject='Новый отзыв на сайте.', to=LIST_EMAIL,
                     files_path=[FILE_REPORT_SEND_EMAIL]).send_email()

    log.info(f'[ End ] {datetime.datetime.now()}')


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
    main()
