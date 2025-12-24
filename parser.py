import pathlib
from typing import List, Dict, Any

from bs4 import BeautifulSoup, Tag


def parse_all_review_html(filename: pathlib.Path) -> List[Dict[str, Any]]:
    """
    Основная функция для чтения файла, поиска всех блоков отзывов и парсинга каждого из них.
    Возвращает список всех найденных блоков отзывов.
    """
    all_parsed_reviews = []

    try:
        # with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        with open(filename, 'r', encoding='windows-1251', errors='ignore') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        review_blocks = soup.find_all('div', class_="rewiev-el")

        if not review_blocks:
            print("Предупреждение: Не найдено ни одного блока div class='rewiev-el'.")
            return []

        for review_element in review_blocks:
            parsed_data = parse_review_table(review_element)
            all_parsed_reviews.append(parsed_data)

        return all_parsed_reviews

    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename.name}' не найден.")
        return []
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")
        return []


def parse_review_table(html_element: Tag) -> Dict[str, Any]:
    """
    Парсит HTML-элемент блока rewiev-el, извлекая общую информацию о курсе и данные из таблицы.
    ПРИНИМАЕТ НА ВХОД ОБЪЕКТ BeautifulSoup (Tag).
    """

    # --- 1. Извлечение общей информации о курсе ---
    general_info = {}
    head_block = html_element.find('div', class_='rewiev-el-head')

    if head_block:
        # Добавляем проверку наличия элемента перед вызовом .get_text()
        date_tag = head_block.find('div', class_='rewiev-el__date')
        course_tag = head_block.find('div', class_='rewiev-el__name')
        teacher_name_val = head_block.find('div', class_='teacher-name-val')

        general_info['Дата'] = date_tag.get_text(strip=True) if date_tag else 'N/A'
        general_info['Курс'] = course_tag.get_text(strip=True) if course_tag else 'N/A'
        general_info['Тренер'] = teacher_name_val.get_text(strip=True) if teacher_name_val else 'Неизвестно'

    # --- 2. Извлечение заголовков столбцов (Thead) ---
    table = html_element.find('table', class_='table')
    headers = []
    if table:
        header_row = table.find('thead').find('tr')
        if header_row:
            for i, th in enumerate(header_row.find_all('th')):
                header_text = th.get_text(strip=True)
                if i == 0:
                    headers.append('ID Пользователя')
                elif header_text != '':
                    headers.append(header_text)

    if not headers:
        return {"course_info": general_info, "participants_data": []}

    # --- 3. Извлечение данных строк (Tbody) ---
    parsed_data = []

    if table:
        data_rows = table.find_all('tr', class_='userData')
        EXPECTED_CELLS = len(headers) + 1  # +1 для первой ячейки с иконкой

        for row in data_rows:
            row_data = {}
            user_id = row.get('data-id', 'N/A')
            row_data[headers[0]] = user_id

            cells = row.find_all('td')

            for i in range(1, len(cells)):
                cell = cells[i]
                header_index = i

                if header_index < len(headers):
                    header = headers[header_index]

                    if header == 'URL Удостоверения':
                        upload_form = cell.find('form', class_='upload-cert-form')
                        row_data[header] = 'Форма загрузки (URL отсутствует)' if upload_form else cell.get_text(
                            strip=True)
                    else:
                        row_data[header] = cell.get_text(strip=True)

            parsed_data.append(row_data)

    return {
        "course_info": general_info,
        "participants_data": parsed_data
    }
