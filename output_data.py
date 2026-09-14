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
    def report(self, data):
        data['max_volume_coin'] = data['max_volume_coin'].to_dict()

        with open('crypto_report.json', 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


class CsvReporter(Reporter):
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

        with open('crypto_report.csv', 'w', newline='') as file:
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

        