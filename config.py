import pathlib

base_dir = pathlib.Path(__file__).parent
dir_path = base_dir / 'data' / 'input'
dir_report_path = base_dir / 'data' / 'reports'
FINAL_REPORT_NAME = 'Combined_Reviews_Report.xlsx'

dir_path.mkdir(parents=True, exist_ok=True)
dir_report_path.mkdir(parents=True, exist_ok=True)
