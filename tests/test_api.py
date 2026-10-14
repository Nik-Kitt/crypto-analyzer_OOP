import pytest
import requests
import os

from unittest.mock import Mock, patch
from api import API, RetryableError, CoinGecko, retry, CoinMarketCap


@pytest.fixture
def session():
    return Mock()


@pytest.fixture
def api(session):
    return API(
        url='test_url',
        session=session,
        api_key='test_key'
    )


@pytest.fixture
def response():
    return Mock()


@pytest.fixture
def coin_gecko(session):
    return CoinGecko(
        url='test_url',
        session=session,
        api_key='test_key')


@pytest.fixture
def coin_market_cap(session):
    return CoinMarketCap(
        url='test_url',
        session=session,
        api_key='test_key')


@pytest.fixture
def coingecko_response_data():
    return [
        {
            'name': 'Bitway',
            'symbol': 'btw',
            'current_price': 1.49,
            'price_change_percentage_24h': 9.2876,
            'total_volume': 9054598,
            'market_cap': 4041061224,
        },
        {
            'name': 'Quant',
            'symbol': 'qnt',
            'current_price': 241.93,
            'price_change_percentage_24h': 1.81487,
            'total_volume': 198128517,
            'market_cap': 3516677535,
        },
    ]


@pytest.fixture
def coinmarketcap_response_data():
    return {
        'data': [
            {
                'name': 'Bitway',
                'symbol': 'btw',
                'quote': [
                    {
                        'price': 1.49,
                        'percent_change_24h': 9.2876,
                        'volume_24h': 9054598,
                        'market_cap': 4041061224,
                    }
                ],
            },
            {
                'name': 'Quant',
                'symbol': 'qnt',
                'quote': [
                    {
                        'price': 241.93,
                        'percent_change_24h': 1.81487,
                        'volume_24h': 198128517,
                        'market_cap': 3516677535,
                    }
                ],
            },
        ]
    }


@pytest.fixture
def expected_crypto_data():
    return [
        {
            'name': 'Bitway',
            'symbol': 'btw',
            'current_price': 1.49,
            'price_change_24h': 9.2876,
            'volume_24h': 9054598,
            'market_cap': 4041061224,
        },
        {
            'name': 'Quant',
            'symbol': 'qnt',
            'current_price': 241.93,
            'price_change_24h': 1.81487,
            'volume_24h': 198128517,
            'market_cap': 3516677535,
        },
    ]


def test_api(api, session):
    assert api.url == 'test_url'
    assert api.session is session
    assert api.api_key == 'test_key'


def test_enter(api):
    assert api.__enter__() == api


def test_exit(api, session):
    api.__exit__(
        None,
        None,
        None)
    session.close.assert_called_once_with()


def test_check_response_200(api, response):
    response.status_code = 200
    api.check_response(response)


def test_check_response_401(api, response):
    response.status_code = 401
    with pytest.raises(RuntimeError):
        api.check_response(response)


def test_check_response_429(api, response):
    response.status_code = 429
    with pytest.raises(RetryableError):
        api.check_response(response)


def test_check_response_500(api, response):
    response.status_code = 500
    with pytest.raises(RetryableError):
        api.check_response(response)


def test_retry_success_after_error():
    mock_func = Mock(side_effect=[RetryableError('Ошибка'), 'success'])
    decorated_func = retry(max_attempts=3, delay=2)(mock_func)
    with patch('api.time.sleep') as mock_sleep:
        result = decorated_func()
        assert result == 'success'
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(2)


def test_retry_all_attempts_failed():
    mock_func = Mock(
        side_effect=RetryableError('Ошибка')
    )
    decorated_func = retry(max_attempts=3, delay=2)(mock_func)
    with patch('api.time.sleep') as mock_sleep:
        with pytest.raises(RuntimeError, match='Ошибка подключения к API'):
            decorated_func()
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2


@pytest.mark.parametrize(
    'coin_api',
    ['coin_gecko', 'coin_market_cap']
)
def test_network_error(request, coin_api):
    api_client = request.getfixturevalue(coin_api)
    api_client.session.get.side_effect = requests.exceptions.ConnectionError

    with patch('api.time.sleep') as mock_sleep:
        with pytest.raises(RuntimeError, match='Ошибка подключения к API'):
            api_client.get_api_info()
        assert api_client.session.get.call_count == 3
        assert mock_sleep.call_count == 2


@pytest.mark.parametrize(
    'coin_api, data_fixture, expected_headers',
    [
        ('coin_gecko', 'coingecko_response_data', None),
        (
            'coin_market_cap',
            'coinmarketcap_response_data',
            {'X-CMC_PRO_API_KEY': 'test_key'},
        ),
    ],
)
def test_get_api_info(
    request,
    coin_api,
    data_fixture,
    expected_headers,
    session,
    response,
):
    expected_data = request.getfixturevalue(data_fixture)
    response.status_code = 200
    response.json.return_value = expected_data
    session.get.return_value = response

    api_client = request.getfixturevalue(coin_api)

    result = api_client.get_api_info()

    assert result == expected_data

    if expected_headers is None:
        session.get.assert_called_once_with(api_client.url)
    else:
        session.get.assert_called_once_with(
            api_client.url,
            headers=expected_headers,
        )

    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize('status_code', [429, 500])
def test_get_api_info_retry_http_error(
    coin_gecko,
    session,
    response,
    status_code,
):
    response.status_code = status_code
    session.get.return_value = response

    with patch('api.time.sleep') as mock_sleep:
        with pytest.raises(
            RuntimeError,
            match='Ошибка подключения к API',
        ):
            coin_gecko.get_api_info()

    assert session.get.call_count == 3
    assert mock_sleep.call_count == 2


@pytest.mark.parametrize(
    'coin_api, data_fixture',
    [
        ('coin_gecko', 'coingecko_response_data'),
        ('coin_market_cap', 'coinmarketcap_response_data'),
    ],
)
def test_get_correct_data(
    request,
    coin_api,
    data_fixture,
    expected_crypto_data,
):
    api_client = request.getfixturevalue(coin_api)
    source_data = request.getfixturevalue(data_fixture)

    result_data = api_client.get_correct_data(source_data)

    assert result_data == expected_crypto_data


@pytest.mark.integration
def test_coingecko_real_api_response():
    url = (
        'https://api.coingecko.com/api/v3/coins/markets'
        '?vs_currency=usd&order=market_cap_desc'
        '&per_page=5&page=1'
    )

    with requests.Session() as session:
        api = CoinGecko(url=url, session=session)
        data = api.get_api_info()

    assert isinstance(data, list)
    assert len(data) > 0

    required_fields = {
        'name',
        'symbol',
        'current_price',
        'price_change_percentage_24h',
        'total_volume',
        'market_cap',
    }

    for coin in data:
        assert isinstance(coin, dict)
        assert required_fields.issubset(coin.keys())

    converted_data = api.get_correct_data(data)

    assert len(converted_data) == len(data)
    assert all(
        {
            'name',
            'symbol',
            'current_price',
            'price_change_24h',
            'volume_24h',
            'market_cap',
        }.issubset(coin.keys())
        for coin in converted_data
    )


@pytest.mark.integration
def test_coin_market_cap_real_api_response():
    api_key = os.getenv('CMC_API_KEY')
    if not api_key:
        pytest.skip('Не задан CMC_API_KEY')

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    with requests.Session() as session:
        api = CoinMarketCap(
            url=url,
            session=session,
            api_key=api_key,
        )
        data = api.get_api_info()
        converted_data = api.get_correct_data(data)

    assert isinstance(data, dict)
    assert isinstance(data.get('data'), list)
    assert len(data['data']) > 0

    required_fields = {
        'name',
        'symbol',
        'quote',
    }

    for coin in data['data']:
        assert required_fields.issubset(coin.keys())
        assert isinstance(coin['quote'], list)
        assert len(coin['quote']) > 0

        quote = coin['quote'][0]
        assert {
            'price',
            'percent_change_24h',
            'volume_24h',
            'market_cap',
        }.issubset(quote.keys())

    assert len(converted_data) == len(data['data'])
    assert {
        'name',
        'symbol',
        'current_price',
        'price_change_24h',
        'volume_24h',
        'market_cap',
    }.issubset(converted_data[0].keys())
