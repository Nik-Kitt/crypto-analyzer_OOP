from settings import Settings, StorageType
from storage import JsonStorage, SqliteStorage


def create_storage():
    settings = Settings()
    if settings.storage == StorageType.JSON:
        return JsonStorage()
    elif settings.storage == StorageType.SQLITE:
        return SqliteStorage()

    raise ValueError(
        f'Неподдерживаемый тип хранилища: {settings.storage}'
    )
