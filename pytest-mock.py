import sys

import root_config
from main import main


def set_var(monkeypatch):
    test_path = "./data/Contacts.txt"
    file_all_report = "./data/FILE_ALL_REPORT.txt"
    list_email = ['g.savushkin@itexpert.ru', ]

    # 1. Патчим сам конфиг
    monkeypatch.setattr(root_config, "FILE_CONTACT_1C", test_path)
    monkeypatch.setattr(root_config, "LIST_EMAIL", list_email)
    monkeypatch.setattr(root_config, "FILE_ALL_REPORT", file_all_report)

    # 2. ПЕРЕЗАПИСЫВАЕМ значение во всех уже загруженных модулях
    # Проходим по всем модулям, которые уже успели импортировать root_config
    for name, module in sys.modules.items():
        if hasattr(module, "FILE_CONTACT_1C"):
            monkeypatch.setattr(f"{name}.FILE_CONTACT_1C", test_path, raising=False)
        if hasattr(module, "LIST_EMAIL"):
            monkeypatch.setattr(f"{name}.LIST_EMAIL", list_email, raising=False)
        if hasattr(module, "FILE_ALL_REPORT"):
            monkeypatch.setattr(f"{name}.FILE_ALL_REPORT", file_all_report, raising=False)


def test_everything(monkeypatch):
    set_var(monkeypatch)
    main()
