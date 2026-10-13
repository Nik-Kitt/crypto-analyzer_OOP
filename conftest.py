import pytest

from cripto_date import CryptoAsset


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
