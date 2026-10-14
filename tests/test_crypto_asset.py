import pytest


def test_crypto_asset_creation(crypto_asset):
    assert crypto_asset.name == 'Bitway'
    assert crypto_asset.symbol == 'btw'
    assert crypto_asset.current_price == 1.49
    assert crypto_asset.price_change_24h == 9.2876
    assert crypto_asset.volume_24h == 9054598
    assert crypto_asset.market_cap == 4041061224


def test_crypto_asset_str(crypto_asset):
    need_str = ('name = Bitway\n'
                'symbol = btw\n'
                'current_price = 1.49\n'
                'price_change_24h = 9.2876\n'
                'volume_24h = 9054598\n'
                'market_cap = 4041061224')
    assert str(crypto_asset) == need_str


def test_crypto_asset_repr(crypto_asset):
    need_repr = (
            "CryptoAsset("
            "name='Bitway', "
            "symbol='btw', "
            "current_price=1.49, "
            "price_change_24h=9.2876, "
            "volume_24h=9054598, "
            "market_cap=4041061224)"
        )
    assert repr(crypto_asset) == need_repr


def test_crypto_asset_lt(crypto_asset, crypto_other_asset):
    assert crypto_asset < crypto_other_asset
    assert not crypto_other_asset < crypto_asset


def test_crypto_asset_gt(crypto_asset, crypto_other_asset):
    assert crypto_other_asset > crypto_asset
    assert not crypto_asset > crypto_other_asset


@pytest.mark.parametrize('operator, expected', [
    ('<', False),
    ('>', True),
    ('<=', False),
    ('>=', True),
    ('==', False),
    ('!=', True),
])
def test_compare(crypto_asset, crypto_other_asset, operator, expected):
    assert crypto_asset.compare(
            crypto_other_asset,
            'market_cap',
            operator) is expected


def test_compare_fail(crypto_asset, crypto_other_asset):
    with pytest.raises(ValueError):
        crypto_asset.compare(
            crypto_other_asset,
            'market_cap',
            '===')


def test_to_dict(crypto_asset):
    need_dict = {
            'name': 'Bitway',
            'symbol': 'btw',
            'current_price': 1.49,
            'change_24h': 9.2876,
            'volume_24h': 9054598,
            'market_cap': 4041061224
        }
    assert crypto_asset.to_dict() == need_dict
