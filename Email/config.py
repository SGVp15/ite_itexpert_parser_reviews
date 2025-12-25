from pathlib import Path
from dotenv import dotenv_values, find_dotenv

# Поиск и загрузка конфигурации
config = dotenv_values(find_dotenv())

# Список обязательных переменных для проверки
REQUIRED_KEYS = ['EMAIL_LOGIN', 'EMAIL_PASSWORD']

missing_keys = []
for key in REQUIRED_KEYS:
    value = config.get(key)
    if not value:
        missing_keys.append(key)

# Проверка на наличие ошибок
if missing_keys:
    print(f"Ошибка: Следующие переменные в .env не заполнены: {', '.join(missing_keys)}")
    raise ValueError(f"Missing environment variables: {missing_keys}")

# Если всё хорошо, присваиваем значения
EMAIL_LOGIN = config.get('EMAIL_LOGIN')
EMAIL_PASSWORD = config.get('EMAIL_PASSWORD')

print("Все переменные успешно загружены.")

SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 465
EMAIL_BCC = ['exam@itexpert.ru', ]
EMAIL_BCC_course = ['exam@itexpert.ru', ]
email_login_password = {}

TEMPLATE_FOLDER = Path('./Email', 'template_email')
