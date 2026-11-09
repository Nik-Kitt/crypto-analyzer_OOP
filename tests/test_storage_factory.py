import storage_factory

from storage import JsonStorage, SqliteStorage


def test_storage_factory_json(monkeypatch):
    monkeypatch.setenv('STORAGE', 'json')
    storage = storage_factory.create_storage()
    assert isinstance(storage, JsonStorage)


def test_storage_factory_sqlite(monkeypatch):
    monkeypatch.setenv('STORAGE', 'sqlite')
    storage = storage_factory.create_storage()
    assert isinstance(storage, SqliteStorage)
