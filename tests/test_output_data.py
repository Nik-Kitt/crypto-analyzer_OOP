import pytest
import json
import csv

from output_data import ConsoleReporter, JsonReporter, CsvReporter


@pytest.fixture
def crypto_report_data():
    return {
        'top_gainers': [
            {
                'change_24h': 24.06924,
                'current_price': 1.72,
                'market_cap': 4648190336,
                'name': 'Bitway',
                'symbol': 'btw',
                'volume_24h': 35543101,
            },
            {
                'change_24h': 11.07332,
                'current_price': 5.83,
                'market_cap': 7631591773,
                'name': 'NEAR Protocol',
                'symbol': 'near',
                'volume_24h': 1207113189,
            },
            {
                'change_24h': 7.99871,
                'current_price': 1323.93,
                'market_cap': 22472979403,
                'name': 'Zcash',
                'symbol': 'zec',
                'volume_24h': 961966476,
            },
        ],
        'top_losers': [
            {
                'change_24h': -3.02757,
                'current_price': 0.01034737,
                'market_cap': 7338321407,
                'name': 'Rain',
                'symbol': 'rain',
                'volume_24h': 11501625,
            },
            {
                'change_24h': -0.85441,
                'current_price': 1.056,
                'market_cap': 25089705065,
                'name': 'Figure Heloc',
                'symbol': 'figr_heloc',
                'volume_24h': 106017,
            },
            {
                'change_24h': -0.31956,
                'current_price': 1.44,
                'market_cap': 4079549932,
                'name': 'Gram (prev. Toncoin)',
                'symbol': 'gram',
                'volume_24h': 31755740,
            },
        ],
        'max_volume_coin': {
            'change_24h': -0.00228,
            'current_price': 0.999147,
            'market_cap': 184101562270,
            'name': 'Tether',
            'symbol': 'usdt',
            'volume_24h': 38746878851,
        },
        'total_market_cap_usd': 2808347329290,
    }


def test_console_reporter(crypto_report_data, capsys):
    need_data = """
Топ лидеров роста:
[{'change_24h': 24.06924,
  'current_price': 1.72,
  'market_cap': 4648190336,
  'name': 'Bitway',
  'symbol': 'btw',
  'volume_24h': 35543101},
 {'change_24h': 11.07332,
  'current_price': 5.83,
  'market_cap': 7631591773,
  'name': 'NEAR Protocol',
  'symbol': 'near',
  'volume_24h': 1207113189},
 {'change_24h': 7.99871,
  'current_price': 1323.93,
  'market_cap': 22472979403,
  'name': 'Zcash',
  'symbol': 'zec',
  'volume_24h': 961966476}]

Топ лидеров падения:
[{'change_24h': -3.02757,
  'current_price': 0.01034737,
  'market_cap': 7338321407,
  'name': 'Rain',
  'symbol': 'rain',
  'volume_24h': 11501625},
 {'change_24h': -0.85441,
  'current_price': 1.056,
  'market_cap': 25089705065,
  'name': 'Figure Heloc',
  'symbol': 'figr_heloc',
  'volume_24h': 106017},
 {'change_24h': -0.31956,
  'current_price': 1.44,
  'market_cap': 4079549932,
  'name': 'Gram (prev. Toncoin)',
  'symbol': 'gram',
  'volume_24h': 31755740}]

Максимальный объём:
{'change_24h': -0.00228,
 'current_price': 0.999147,
 'market_cap': 184101562270,
 'name': 'Tether',
 'symbol': 'usdt',
 'volume_24h': 38746878851}

Общая капитализация:
2808347329290
"""
    reporter = ConsoleReporter()
    reporter.report(crypto_report_data)

    captured = capsys.readouterr()
    assert captured.out == need_data


def test_json_reporter_init():
    with pytest.raises(TypeError):
        JsonReporter(name_file=123)  # type: ignore[arg-type]


def test_json_reporter_report(crypto_report_data, tmp_path):
    file_path = tmp_path / 'test_report.json'
    reporter = JsonReporter(name_file=str(file_path))
    reporter.report(crypto_report_data)
    with open(file_path, encoding='utf-8') as file:
        result_data = json.load(file)
    assert result_data == crypto_report_data


def test_csv_reporter_init():
    with pytest.raises(TypeError):
        CsvReporter(name_file=123)  # type: ignore[arg-type]


def test_csv_reporter_report(crypto_report_data, tmp_path):
    file_path = tmp_path / 'test_report.csv'
    reporter = CsvReporter(name_file=str(file_path))
    reporter.report(crypto_report_data)
    with open(file_path, encoding='utf-8') as file:
        result_data = list(csv.DictReader(file))
    assert result_data[0]['category'] == 'gainer'
    assert result_data[0]['name'] == 'Bitway'
    assert result_data[0]['symbol'] == 'btw'
    assert result_data[0]['current_price'] == '1.72'
    assert result_data[0]['change_24h'] == '24.06924'
    assert result_data[0]['volume_24h'] == '35543101'
    assert result_data[0]['market_cap'] == '4648190336'

    assert result_data[3]['category'] == 'loser'
    assert result_data[3]['name'] == 'Rain'
    assert result_data[3]['symbol'] == 'rain'
    assert result_data[3]['current_price'] == '0.01034737'
    assert result_data[3]['change_24h'] == '-3.02757'
    assert result_data[3]['volume_24h'] == '11501625'
    assert result_data[3]['market_cap'] == '7338321407'

    assert result_data[-1]['category'] == 'max_volume_coin'
    assert result_data[-1]['name'] == 'Tether'
    assert result_data[-1]['symbol'] == 'usdt'
    assert result_data[-1]['current_price'] == '0.999147'
    assert result_data[-1]['change_24h'] == '-0.00228'
    assert result_data[-1]['volume_24h'] == '38746878851'
    assert result_data[-1]['market_cap'] == '184101562270'

    assert len(result_data) == 7
