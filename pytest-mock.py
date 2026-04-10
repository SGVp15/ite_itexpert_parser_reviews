import root_config
import pytest
import sys


def test_everything(monkeypatch):
    test_path = "./data/Contacts.txt"
    list_email = ['g.savushkin@itexpert.ru', ]

    # 1. Патчим сам конфиг
    monkeypatch.setattr(root_config, "FILE_CONTACT_1C", test_path)
    monkeypatch.setattr(root_config, "LIST_EMAIL", list_email)

    # 2. ПЕРЕЗАПИСЫВАЕМ значение во всех уже загруженных модулях
    # Проходим по всем модулям, которые уже успели импортировать root_config
    for name, module in sys.modules.items():
        if hasattr(module, "FILE_CONTACT_1C"):
            monkeypatch.setattr(f"{name}.FILE_CONTACT_1C", test_path, raising=False)
        if hasattr(module, "LIST_EMAIL"):
            monkeypatch.setattr(f"{name}.LIST_EMAIL", list_email, raising=False)

    from main import main
    main()