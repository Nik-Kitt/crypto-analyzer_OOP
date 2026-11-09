import os
import typer
import requests

from typing import Literal
from dotenv import load_dotenv
from datetime import datetime

from api import CoinGecko, CoinMarketCap
from cripto_date import CryptoAsset, CryptoCollection
from output_data import ConsoleReporter, CsvReporter
from storage import SqliteStorage
from storage_factory import create_storage

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
    output: Literal['console', 'csv'] = typer.Option(...),
    top: int = typer.Option(3)
):
    print(f'Вы выбрали для анализа источник: {source}')
    print(f'Обработанные данные будут представлены в формате: {output}')
    print(f'Количество монет в топе: {top}')

    session = requests.Session()
    providers = {
        'coingecko': lambda: CoinGecko(urlCG, session),
        'coinmarketcap': lambda: CoinMarketCap(urlCMC, session, api_key),
    }
    provider_factory = providers[source]
    provider = provider_factory()

    with provider as api:
        data = api.get_api_info()  # Получили данные от API

    result_data = provider.get_correct_data(data)  # Преобразовали ответ для анализатора

    crypto_asset = []
    for data in result_data:  # Сделали список объектов класса CryptoAsset
        crypto_asset.append(CryptoAsset(**data))
    collection = CryptoCollection(crypto_asset)  # Объекты CryptoCollection - списки объектов CryptoAsset

    top_max = collection.get_top_coins('price_change_24h', top, True)  # Топ роста
    top_min = collection.get_top_coins('price_change_24h', top)  # Топ падения

    top_gainers = collection.prepare_top_coins(top_max)  # Топ лидеров роста в конечном формате
    top_losers = collection.prepare_top_coins(top_min)  # Топ лидеров падения в конечном формате

    # Монета с максимальным объемом торгов
    max_total_volume = collection.get_top_coins('volume_24h', 1, True)[0].to_dict()
    total_market_cap_usd = collection.sum_market_cap()
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    report_data = {  # Создаем словарь выходных данных
        'generated_at': generated_at,
        'total_coins_analyzed': len(collection.assets),
        'top_gainers': top_gainers,
        'top_losers': top_losers,
        'max_volume_coin': max_total_volume,
        'total_market_cap_usd': total_market_cap_usd,
    }

    storage = create_storage()
    storage.save(report_data)

    reporters = {
        'console': ConsoleReporter,
        'csv': CsvReporter,
    }

    reporter = reporters[output]()
    reporter.report(report_data)


@app.command()
def list_snapshots():
    storage = create_storage()

    if not isinstance(storage, SqliteStorage):
        raise typer.BadParameter(
            'Команда доступна только при STORAGE=sqlite'
        )

    snapshots = storage.get_snapshots()
    if snapshots:
        for snapshot in snapshots:
            print(f"ID: {snapshot['id']} | Дата: {snapshot['generated_at']}")
    else:
        print('Сохраненных снимков пока нет')


@app.command()
def compare_snapshots(snapshot_id_1: int, snapshot_id_2: int):
    storage = create_storage()

    if not isinstance(storage, SqliteStorage):
        raise typer.BadParameter(
            'Команда доступна только при STORAGE=sqlite'
        )

    compares = storage.compare_snapshots(snapshot_id_1, snapshot_id_2)
    if compares:
        for compare in compares:
            print(
                f"Имя монеты: {compare['name']} | "
                f"Старая цена: {compare['old_price']} | "
                f"Новая цена: {compare['new_price']} | "
                f"Изменение цены: {compare['price_difference']}"
            )
    else:
        print('Нет данных для сравнения этих снимков')


if __name__ == '__main__':
    app()
