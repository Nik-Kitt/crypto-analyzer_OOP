import requests
import time

from functools import wraps


def retry(max_attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    return result
                except requests.exceptions.RequestException:
                    if i == max_attempts - 1:
                        raise RuntimeError('Ошибка подключения к API')
                    time.sleep(delay)
                

        return wrapper
    return decorator


class API:

    def __init__(self, url, api_key=None):
       self.url = url
       self.api_key = api_key
       self.session = requests.Session()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


class CoinGecko(API):

    @retry(max_attempts=3, delay=2)
    def get_api_info(self):
        ''' Получаем информацию из API CoinGecko'''
        response = self.session.get(self.url)
        response.raise_for_status()
        data = response.json()
        return data

    def get_correct_data(self, data):
        ''' Преобразовываем ответ API в единый формат для анализатора'''
        result_data = []
        for coin in data:
            if coin['price_change_percentage_24h'] is None:
                continue
            result_dict = {
                'name': coin['name'],
                'symbol': coin['symbol'],
                'current_price': coin['current_price'],
                'price_change_24h': coin['price_change_percentage_24h'],
                'volume_24h': coin['total_volume'],
                'market_cap': coin['market_cap'],
            }
            
            result_data.append(result_dict)
        return result_data
        

class CoinMarketCap(API):
    
    @retry(max_attempts=3, delay=2)
    def get_api_info(self):
        ''' Получаем информацию из API CoinMarketCap'''
        response = self.session.get(
            self.url,
            headers={
        'X-CMC_PRO_API_KEY': self.api_key
        }
    )
        response.raise_for_status()
        data = response.json()
        return data

    def get_correct_data(self, data):
        ''' Преобразовываем ответ API в единый формат для анализатора'''
        result_data = []
        data = data['data']
        for coin in data:
            result_dict = {
                'name': coin['name'],
                'symbol': coin['symbol'],
                'current_price': coin['quote'][0]['price'],
                'price_change_24h': coin['quote'][0]['percent_change_24h'],
                'volume_24h':coin['quote'][0]['volume_24h'],
                'market_cap': coin['quote'][0]['market_cap'],
            }
            result_data.append(result_dict)
        return result_data