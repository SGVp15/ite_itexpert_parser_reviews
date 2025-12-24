from pathlib import Path

from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv())

EMAIL_LOGIN = config.get('EMAIL_LOGIN')
EMAIL_PASSWORD = config.get('EMAIL_PASSWORD')

if not EMAIL_PASSWORD:
    raise f'ERROR .ENV {EMAIL_PASSWORD=}'
if not EMAIL_LOGIN:
    raise f'ERROR .ENV {EMAIL_LOGIN=}'

SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 465
EMAIL_BCC = ['exam@itexpert.ru', ]
EMAIL_BCC_course = ['exam@itexpert.ru', ]
email_login_password = {}

TEMPLATE_FOLDER = Path('./Email', 'template_email')
