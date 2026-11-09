import json
import sqlite3

from contextlib import contextmanager
from abc import ABC, abstractmethod


class BaseStorage(ABC):

    @abstractmethod
    def save(self, results: dict) -> None:
        pass


class JsonStorage(BaseStorage):

    def __init__(self, name_file='crypto_report.json'):
        if isinstance(name_file, str):
            self.name_file = name_file
        else:
            raise TypeError('Название файла должно быть строкой')

    def save(self, results: dict) -> None:
        with open(self.name_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=4, ensure_ascii=False)


class SqliteStorage(BaseStorage):

    def __init__(self, name_file='crypto.db', connection=None):
        if isinstance(name_file, str):
            self.db_path = name_file
        else:
            raise TypeError('Название файла должно быть строкой')

        self.connection = connection
        self.create_tables()

    @contextmanager
    def _get_connection(self):
        if self.connection is not None:
            connection = self.connection
            connection.execute('PRAGMA foreign_keys = ON')
            with connection:
                yield connection
        else:
            connection = sqlite3.connect(self.db_path)
            try:
                connection.execute('PRAGMA foreign_keys = ON')
                with connection:
                    yield connection
            finally:
                connection.close()

    def create_tables(self):
        with self._get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY,
                    generated_at TEXT,
                    total_coins_analyzed INTEGER,
                    total_market_cap_usd REAL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS coin_prices (
                    id INTEGER PRIMARY KEY,
                    snapshot_id INTEGER,
                    name TEXT,
                    symbol TEXT,
                    current_price REAL,
                    change_24h REAL,
                    volume_24h REAL,
                    market_cap REAL,
                    category TEXT,
                    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                )
            """)

    def save(self, results: dict) -> None:
        with self._get_connection() as connection:
            cursor = connection.execute("""
                INSERT INTO snapshots (
                    generated_at,
                    total_coins_analyzed,
                    total_market_cap_usd
                )
                VALUES (?, ?, ?)
            """, (
                results['generated_at'],
                results['total_coins_analyzed'],
                results['total_market_cap_usd']
            ))

            snapshot_id = cursor.lastrowid

            for coin in results['top_gainers']:
                connection.execute("""
                    INSERT INTO coin_prices (
                        snapshot_id,
                        name,
                        symbol,
                        current_price,
                        change_24h,
                        volume_24h,
                        market_cap,
                        category
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot_id,
                    coin['name'],
                    coin['symbol'],
                    coin['current_price'],
                    coin['change_24h'],
                    coin['volume_24h'],
                    coin['market_cap'],
                    'gainer'
                ))

            for coin in results['top_losers']:
                connection.execute("""
                    INSERT INTO coin_prices (
                        snapshot_id,
                        name,
                        symbol,
                        current_price,
                        change_24h,
                        volume_24h,
                        market_cap,
                        category
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot_id,
                    coin['name'],
                    coin['symbol'],
                    coin['current_price'],
                    coin['change_24h'],
                    coin['volume_24h'],
                    coin['market_cap'],
                    'loser'
                ))

    def compare_snapshots(
        self,
        snapshot_id_1: int,
        snapshot_id_2: int
    ) -> list[dict]:
        with self._get_connection() as connection:
            cursor = connection.execute("""
                SELECT
                    old.name,
                    old.current_price AS old_price,
                    new.current_price AS new_price,
                    new.current_price - old.current_price AS price_difference
                FROM coin_prices AS old
                JOIN coin_prices AS new
                    ON old.name = new.name
                WHERE old.snapshot_id = ?
                    AND new.snapshot_id = ?;
            """, (snapshot_id_1, snapshot_id_2))

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

    def get_price_history(self, name: str) -> list[dict]:
        with self._get_connection() as connection:
            cursor = connection.execute("""
                SELECT
                    coin_prices.name,
                    coin_prices.current_price,
                    snapshots.generated_at
                FROM coin_prices
                JOIN snapshots
                    ON coin_prices.snapshot_id = snapshots.id
                WHERE coin_prices.name = ?
                ORDER BY snapshots.generated_at ASC;
            """, (name,))

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

    def get_top_gainers(self, top_n: int) -> list[dict]:
        with self._get_connection() as connection:
            cursor = connection.execute("""
                SELECT *
                FROM coin_prices
                WHERE snapshot_id = (SELECT MAX(id) FROM snapshots)
                    AND change_24h > 0
                ORDER BY change_24h DESC
                LIMIT ?;
            """, (top_n,))

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

    def get_top_losers(self, top_n: int) -> list[dict]:
        with self._get_connection() as connection:
            cursor = connection.execute("""
                SELECT *
                FROM coin_prices
                WHERE snapshot_id = (SELECT MAX(id) FROM snapshots)
                    AND change_24h < 0
                ORDER BY change_24h ASC
                LIMIT ?;
            """, (top_n,))

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

    def get_snapshots(self) -> list[dict]:
        with self._get_connection() as connection:
            cursor = connection.execute("""
                SELECT
                    snapshots.id,
                    snapshots.generated_at
                FROM snapshots
                ORDER BY snapshots.id ASC;
            """)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result
