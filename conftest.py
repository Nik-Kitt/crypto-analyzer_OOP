import pytest
import sqlite3

from cripto_date import CryptoAsset
from storage import SqliteStorage


@pytest.fixture
def crypto_asset():
    return CryptoAsset(
        name='Bitway',
        symbol='btw',
        current_price=1.49,
        price_change_24h=9.2876,
        volume_24h=9054598,
        market_cap=4041061224
    )


@pytest.fixture
def crypto_other_asset():
    return CryptoAsset(
        name='Quant',
        symbol='qnt',
        current_price=241.93,
        price_change_24h=1.81487,
        volume_24h=198128517,
        market_cap=3516677535
    )


@pytest.fixture
def sqlite_storage():
    connection = sqlite3.connect(':memory:')
    storage = SqliteStorage(connection=connection)

    yield storage
    connection.close()


@pytest.fixture
def sample_results():
    return {
        'generated_at': '2026-11-07 10:00:00',
        'total_coins_analyzed': 3,
        'top_gainers': [
            {
                'name': 'Bitcoin',
                'symbol': 'btc',
                'current_price': 100000.0,
                'change_24h': 5.5,
                'volume_24h': 50000000000,
                'market_cap': 1900000000000
            }
        ],
        'top_losers': [
            {
                'name': 'Ethereum',
                'symbol': 'eth',
                'current_price': 3000.0,
                'change_24h': -2.3,
                'volume_24h': 20000000000,
                'market_cap': 360000000000
            }
        ],
        'total_market_cap_usd': 2260000000000
    }
