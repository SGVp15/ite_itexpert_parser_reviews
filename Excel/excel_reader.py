import json
import os


def save_json_questions(path_questions, all_questions):
    file_json = os.path.join(path_questions, f'{all_questions[0].exam}.json')
    with open(file_json, 'w', encoding='utf-8') as f:
        f.write(json.dumps(all_questions))


def read_excel(excel, page_name, column, row):
    sheet_ranges = excel[page_name]
    v = sheet_ranges[f'{column}{row}'].value
    if v is None:
        return None
    value = str(v).strip()
    if value == '':
        return None
    return value
