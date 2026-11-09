from settings import StorageType, Settings


def test_storage_none(monkeypatch):
    monkeypatch.delenv('STORAGE', raising=False)
    settings = Settings()
    assert settings.storage == StorageType.JSON


def test_storage_json(monkeypatch):
    monkeypatch.setenv('STORAGE', 'json')
    settings = Settings()
    assert settings.storage == StorageType.JSON


def test_storage_sqlite(monkeypatch):
    monkeypatch.setenv('STORAGE', 'sqlite')
    settings = Settings()
    assert settings.storage == StorageType.SQLITE
