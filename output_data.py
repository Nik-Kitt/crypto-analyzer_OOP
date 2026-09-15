import json
import csv
import pprint

from abc import ABC, abstractmethod

class Reporter(ABC):
    @abstractmethod
    def report(self, data):
        pass


class ConsoleReporter(Reporter):
    def report(self, data):
        print('\nТоп лидеров роста:')
        pprint.pprint(data['top_gainers'])

        print('\nТоп лидеров падения:')
        pprint.pprint(data['top_losers'])

        print('\nМаксимальный объём:')
        pprint.pprint(data['max_volume_coin'])

        print('\nОбщая капитализация:')
        pprint.pprint(data['total_market_cap_usd'])
        


class JsonReporter(Reporter):
    def __init__(self, name_file='crypto_report.json'):
        if isinstance(name_file, str):
            self.name_file = name_file
        else:
            raise TypeError('Название файла должно быть строкой')

    def report(self, data):
        report_data = data.copy()
        report_data['max_volume_coin'] = data['max_volume_coin'].to_dict()

        with open(self.name_file, 'w') as file:
            json.dump(report_data, file, indent=4, ensure_ascii=False)


class CsvReporter(Reporter):
    def __init__(self, name_file='crypto_report.csv'):
        if isinstance(name_file, str):
            self.name_file = name_file
        else:
            raise TypeError('Название файла должно быть строкой')

    def report(self, data):
        fieldnames = [
            'category',
            'name',
            'symbol',
            'current_price',
            'change_24h',
            'volume_24h',
            'market_cap'
        ]

        with open(self.name_file, 'w', newline='') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for coin in data['top_gainers']:
                writer.writerow({
                    'category': 'gainer',
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'current_price': '',
                    'change_24h': coin['change_24h'],
                    'volume_24h': '',
                    'market_cap': ''
                })

            for coin in data['top_losers']:
                writer.writerow({
                    'category': 'loser',
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'current_price': '',
                    'change_24h': coin['change_24h'],
                    'volume_24h': '',
                    'market_cap': ''
                })

            coin = data['max_volume_coin']

            writer.writerow({
                'category': 'max_volume_coin',
                'name': coin.name,
                'symbol': coin.symbol,
                'current_price': coin.current_price,
                'change_24h': coin.price_change_24h,
                'volume_24h': coin.volume_24h,
                'market_cap': coin.market_cap
            })

        