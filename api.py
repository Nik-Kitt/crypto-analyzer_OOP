import requests


class API:

    def __init__(self, url, api_key=None):
       self.url = url
       self.api_key = api_key

class CoinGecko(API):

    def get_api_info(self):
        response = requests.get(self.url)
        response.raise_for_status()
        data = response.json()
        return data


class CoinMarketCap(API):
    
    def get_api_info(self):
        response = requests.get(
            self.url,
            headers={
        'X-CMC_PRO_API_KEY': self.api_key
        }
    )
        response.raise_for_status()
        data = response.json()
        return data
