import os

from dotenv import load_dotenv
from enum import Enum

load_dotenv()


class StorageType(Enum):
    JSON = 'json'
    SQLITE = 'sqlite'


class Settings:

    def __init__(self):
        storage = os.getenv('STORAGE', 'json')
        self.storage = StorageType(storage)
