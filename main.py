import os
import pprint

from dotenv import load_dotenv

from api import CoinGecko, CoinMarketCap


load_dotenv()
api_key = os.getenv('CMC_API_KEY')


urlCG = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1'
urlCMC = (
    "https://pro-api.coinmarketcap.com"
    "/v3/cryptocurrency/listings/latest"
)

coin_gecko = CoinGecko(urlCG)
coin_market_cap = CoinMarketCap(urlCMC, api_key)

data_cg = coin_gecko.get_api_info()

print(type(data_cg))
print(len(data_cg))
pprint.pprint(data_cg[0])


data_cmc = coin_market_cap.get_api_info()

print(type(data_cmc))
pprint.pprint(data_cmc)