import os
import pprint

from dotenv import load_dotenv

from api import CoinGecko, CoinMarketCap
from cripto_date import CryptoAsset, CryptoCollection

load_dotenv()
api_key = os.getenv('CMC_API_KEY')


urlCG = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1'
urlCMC = (
    "https://pro-api.coinmarketcap.com"
    "/v3/cryptocurrency/listings/latest"
)

coin_gecko = CoinGecko(urlCG)
coin_market_cap = CoinMarketCap(urlCMC, api_key)

data_cg = coin_gecko.get_api_info() # Получили данные от API CoinGecko
data_cmc = coin_market_cap.get_api_info() # Получили данные от API CoinMarketCap

result_data_cg = coin_gecko.get_correct_data(data_cg) # Преобразовали оба ответа для анализатора
result_data_cmc = coin_market_cap.get_correct_data(data_cmc)

crypto_asset_cg = []
crypto_asset_cmc = []
for data in result_data_cg: # Сделали список объектов класса CryptoAsset
    crypto_asset_cg.append(CryptoAsset(**data))
for data in result_data_cmc: 
    crypto_asset_cmc.append(CryptoAsset(**data))

collection_cg = CryptoCollection(crypto_asset_cg)
collection_cmc = CryptoCollection(crypto_asset_cmc)

Top_3_max_cg = collection_cg.get_top_coins('price_change_24h', 3, True)
Top_3_min_cg = collection_cg.get_top_coins('price_change_24h', 3)

Top_3_max_cmc = collection_cmc.get_top_coins('price_change_24h', 3, True)
Top_3_min_cmc = collection_cmc.get_top_coins('price_change_24h', 3)
