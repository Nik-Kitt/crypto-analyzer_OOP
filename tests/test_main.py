import pytest
import main

from unittest.mock import Mock, patch


@pytest.fixture
def crypto_data():
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
        {
            'name': 'Bitcoin',
            'symbol': 'btc',
            'current_price': 65000,
            'price_change_percentage_24h': 3.5,
            'total_volume': 500000000,
            'market_cap': 1200000000000,
        },
        {
            'name': 'Ethereum',
            'symbol': 'eth',
            'current_price': 3200,
            'price_change_percentage_24h': 6.2,
            'total_volume': 300000000,
            'market_cap': 380000000000,
        },
        {
            'name': 'Solana',
            'symbol': 'sol',
            'current_price': 150,
            'price_change_percentage_24h': -4.5,
            'total_volume': 800000000,
            'market_cap': 70000000000,
        },
        {
            'name': 'Cardano',
            'symbol': 'ada',
            'current_price': 0.45,
            'price_change_percentage_24h': -8.3,
            'total_volume': 150000000,
            'market_cap': 16000000000,
        },
        {
            'name': 'Dogecoin',
            'symbol': 'doge',
            'current_price': 0.12,
            'price_change_percentage_24h': -2.1,
            'total_volume': 1000000000,
            'market_cap': 17000000000,
        },
    ]


@pytest.fixture
def mock_api_response(crypto_data):
    with patch('main.requests.Session') as mock_session:
        session = Mock()
        mock_session.return_value = session

        session.get.return_value = Mock()
        response = session.get.return_value

        response.status_code = 200
        response.json.return_value = crypto_data

        yield mock_session, session, response


@pytest.fixture
def report_data(mock_api_response):
    with patch('main.ConsoleReporter') as mock_console_reporter:
        main.main(
            source='coingecko',
            output='console',
            top=3,
        )

        report = mock_console_reporter.return_value.report
        report.assert_called_once()

        return report.call_args.args[0]


def test_main_coingecko(report_data):
    assert 'generated_at' in report_data
    assert 'total_coins_analyzed' in report_data
    assert 'top_gainers' in report_data
    assert 'top_losers' in report_data
    assert 'max_volume_coin' in report_data
    assert 'total_market_cap_usd' in report_data


def test_main_total_coins_analyzed(report_data):
    assert report_data['total_coins_analyzed'] == 7


def test_main_top_gainers(report_data):
    gainer_names = [
        coin['name'] for coin in report_data['top_gainers']
    ]
    assert len(report_data['top_gainers']) == 3
    assert gainer_names == ['Bitway', 'Ethereum', 'Bitcoin']


def test_main_top_losers(report_data):
    loser_name = [
        coin['name'] for coin in report_data['top_losers']
    ]
    assert len(report_data['top_losers']) == 3
    assert loser_name == ['Cardano', 'Solana', 'Dogecoin']


def test_main_max_volume_coin(report_data):
    assert report_data['max_volume_coin']['name'] == 'Dogecoin'
    assert report_data['max_volume_coin']['volume_24h'] == 1_000_000_000


def test_main_sum_market_cap(report_data, crypto_data):
    expected_market_cap = sum(coin['market_cap'] for coin in crypto_data)
    assert report_data['total_market_cap_usd'] == expected_market_cap


def test_main_calls_api(mock_api_response, report_data):
    mock_session, session, response = mock_api_response

    session.get.assert_called_once()


@pytest.mark.parametrize(
    ('output', 'expected_reporter'),
    [('console', 'ConsoleReporter'),
        ('json', 'JsonReporter'),
        ('csv', 'CsvReporter'),])
def test_main_selects_reporter(
    output,
    expected_reporter,
    mock_api_response,
):
    with (
        patch('main.ConsoleReporter') as mock_console,
        patch('main.JsonReporter') as mock_json,
        patch('main.CsvReporter') as mock_csv,
    ):
        main.main(
            source='coingecko',
            output=output,
            top=3,
        )

        reporters = {
            'ConsoleReporter': mock_console,
            'JsonReporter': mock_json,
            'CsvReporter': mock_csv,
        }

        selected_reporter = reporters[expected_reporter]
        selected_reporter.assert_called_once()
        selected_reporter.return_value.report.assert_called_once()

        for name, reporter in reporters.items():
            if name != expected_reporter:
                reporter.assert_not_called()
