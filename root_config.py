import pathlib

base_dir = pathlib.Path(__file__).parent
DIR_PATH = base_dir / 'data' / 'input'
DIR_REPORT_PATH = base_dir / 'data' / 'reports'

FILE_DOWNLOAD_HTML = DIR_PATH / 'temp.html'
FILE_TEMP_CSV = DIR_REPORT_PATH / 'TEMP.csv'
FILE_ALL_REPORT = DIR_REPORT_PATH / 'ALL_REPORTS.csv'
FILE_REPORT_SEND_EMAIL = DIR_REPORT_PATH / 'FILE_REPORT_SEND_EMAIL.xlsx'

LIST_EMAIL = ['sale@itexpert.ru', 'itstrain@itexpert.ru']
try:
    FILE_REPORT_SEND_EMAIL.unlink()
except FileNotFoundError:
    pass

DIR_PATH.mkdir(parents=True, exist_ok=True)
DIR_REPORT_PATH.mkdir(parents=True, exist_ok=True)
SYSTEM_LOG = './log.txt'
