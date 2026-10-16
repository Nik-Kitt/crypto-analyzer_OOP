import pytest

from cripto_date import CryptoCollection, CryptoAsset


@pytest.fixture
def crypto_asset_none_price_change_24h():
    return CryptoAsset(
        name='Figure Heloc',
        symbol='figr_heloc',
        current_price=1.065,
        price_change_24h=None,
        volume_24h=152439,
        market_cap=25304079164
    )


@pytest.fixture
def crypto_collection(crypto_asset, crypto_other_asset):
    assets = [crypto_asset, crypto_other_asset]
    return CryptoCollection(assets)


def test_crypto_collection_creation(
        crypto_asset,
        crypto_other_asset,
        crypto_asset_none_price_change_24h):
    assets = [
        crypto_asset,
        crypto_other_asset,
        crypto_asset_none_price_change_24h]
    test_assets_collection = CryptoCollection(assets)
    assert test_assets_collection.assets == [crypto_asset, crypto_other_asset]


def test_get_top_coins(crypto_collection, crypto_asset, crypto_other_asset):
    sorted_data_reverse = crypto_collection.get_top_coins('market_cap', 2, True)
    assert sorted_data_reverse == [crypto_asset, crypto_other_asset]
    sorted_data = crypto_collection.get_top_coins('volume_24h', 2)
    assert sorted_data == [crypto_asset, crypto_other_asset]


def test_get_top_coin_invalid_field(crypto_collection):
    with pytest.raises(AttributeError):
        crypto_collection.get_top_coins('unknown_field', 2)


def test_sum_market_cap(crypto_collection):
    assert crypto_collection.sum_market_cap() == 7557738759


def test_prepare_top_coins(crypto_collection, crypto_asset, crypto_other_asset):
    result = crypto_collection.prepare_top_coins([crypto_asset, crypto_other_asset])
    need_result = [
        {
            'name': 'Bitway',
            'symbol': 'btw',
            'current_price': 1.49,
            'change_24h': 9.2876,
            'volume_24h': 9054598,
            'market_cap': 4041061224
        },
        {
            'name': 'Quant',
            'symbol': 'qnt',
            'current_price': 241.93,
            'change_24h': 1.81487,
            'volume_24h': 198128517,
            'market_cap': 3516677535
        }
    ]
    assert result == need_result
