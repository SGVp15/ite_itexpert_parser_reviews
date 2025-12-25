from pathlib import Path

from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv())

LOGIN_ITE = config.get('LOGIN_ITE')
PASSWORD_ITE = config.get('PASSWORD_ITE')
ITEXPERT_URL = config.get('ITEXPERT_URL')

DIR_HTML_DOWNLOAD = Path('./data', 'input')
DIR_HTML_DOWNLOAD.mkdir(exist_ok=True, parents=True)

if not LOGIN_ITE:
    raise f'ERROR .ENV {LOGIN_ITE=}'
if not PASSWORD_ITE:
    raise f'ERROR .ENV {PASSWORD_ITE=}'
if not ITEXPERT_URL:
    raise f'ERROR .ENV {ITEXPERT_URL=}'
