import pathlib

base_dir = pathlib.Path(__file__).parent
DIR_PATH = base_dir / 'data' / 'input'
DIR_REPORT_PATH = base_dir / 'data' / 'reports'
FINAL_REPORT_NAME = 'Combined_Reviews_Report.xlsx'

DIR_PATH.mkdir(parents=True, exist_ok=True)
DIR_REPORT_PATH.mkdir(parents=True, exist_ok=True)
SYSTEM_LOG = './log.txt'
