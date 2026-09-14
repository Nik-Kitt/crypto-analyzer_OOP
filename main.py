import os
import typer

from typing import Literal
from dotenv import load_dotenv
from datetime import datetime

from api import CoinGecko, CoinMarketCap
from cripto_date import CryptoAsset, CryptoCollection
from output_data import ConsoleReporter, JsonReporter, CsvReporter

load_dotenv()
api_key = os.getenv('CMC_API_KEY')
app = typer.Typer()

urlCG = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1'
urlCMC = (
    'https://pro-api.coinmarketcap.com'
    '/v3/cryptocurrency/listings/latest'
)

@app.command()
def main(
    source: Literal['coingecko', 'coinmarketcap'] = typer.Option(...),
    output: Literal['console', 'json', 'csv'] = typer.Option(...),
    top: int = typer.Option(3)
):
    print(f'Вы выбрали для анализа источник: {source}')
    print(f'Обработанные данные будут представлены в формате: {output}')
    print(f'Количество монет в топе: {top}')

    providers = {
        'coingecko': lambda: CoinGecko(urlCG),
        'coinmarketcap': lambda: CoinMarketCap(urlCMC, api_key),
    }
    provider_factory = providers[source]
    provider = provider_factory()

    with provider as api:
        data = api.get_api_info() # Получили данные от API

    result_data = provider.get_correct_data(data) # Преобразовали ответ для анализатора
     
    crypto_asset = []
    for data in result_data: # Сделали список объектов класса CryptoAsset
        crypto_asset.append(CryptoAsset(**data))
    collection = CryptoCollection(crypto_asset) # Объекты CryptoCollection - списки объектов CryptoAsset

    top_max = collection.get_top_coins('price_change_24h', top, True) # Топ роста
    top_min = collection.get_top_coins('price_change_24h', top) # Топ падения

    top_gainers = collection.prepare_top_coins(top_max) # Топ лидеров роста в конечном формате
    top_losers = collection.prepare_top_coins(top_min) # Топ лидеров падения в конечном формате

    max_total_volume = collection.get_top_coins('volume_24h', 1, True)[0] # Монета с максимальным объемом торгов
    total_market_cap_usd = collection.sum_market_cap()
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    report_data = { # Создаем словарь выходных данных
        'generated_at': generated_at,
        'total_coins_analyzed': len(collection.assets),
        'top_gainers': top_gainers,
        'top_losers': top_losers,
        'max_volume_coin': max_total_volume,
        'total_market_cap_usd': total_market_cap_usd,
    }

    reporters = {
        'console': ConsoleReporter,
        'json': JsonReporter,
        'csv': CsvReporter,
    }

    reporter = reporters[output]()
    reporter.report(report_data)


if __name__ == '__main__':
    app()

