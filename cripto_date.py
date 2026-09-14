import operator


OPERATORS = {
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne,
}


class CryptoAsset:
    def  __init__(
        self,
        name,
        symbol,
        current_price,
        price_change_24h,
        volume_24h,
        market_cap):
        self.name = name
        self.symbol = symbol
        self.current_price = current_price
        self.price_change_24h = price_change_24h
        self.volume_24h = volume_24h
        self.market_cap = market_cap

    def __str__(self):
        return (
            f'name = {self.name}\n'
            f'symbol = {self.symbol}\n'
            f'current_price = {self.current_price}\n'
            f'price_change_24h = {self.price_change_24h}\n'
            f'volume_24h = {self.volume_24h}\n'
            f'market_cap = {self.market_cap}'
        )
    
    def __repr__(self):
        return (
            f"CryptoAsset("
            f"name='{self.name}', "
            f"symbol='{self.symbol}', "
            f"current_price={self.current_price}, "
            f"price_change_24h={self.price_change_24h}, "
            f"volume_24h={self.volume_24h}, "
            f"market_cap={self.market_cap})"
        )
    
    def __lt__(self, other):
        return self.current_price < other.current_price
    
    def __gt__(self, other):
        return self.current_price > other.current_price

    def compare(self, self_two, field_compare, oper):
        ''' Метод сравнения по произвольнму полю'''
        oper = str(oper)
        if oper not in OPERATORS:
            raise ValueError('Введите корректный оператор сравнения')

        func = OPERATORS[oper]
        
        value = getattr(self, field_compare)
        value_2 = getattr(self_two, field_compare)
        return func(value, value_2)

    def to_dict(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'current_price': self.current_price,
            'change_24h': self.price_change_24h,
            'volume_24h': self.volume_24h,
            'market_cap': self.market_cap
        }

class CryptoCollection:
    def __init__(self, assets):
        self.assets = assets

    def get_top_coins(self, field_name, top_n, reverse=False):
        sorted_data = sorted(
            self.assets,
            key=lambda coin: getattr(coin, field_name),
            reverse=reverse
        )

        return sorted_data[:top_n]

    def sum_market_cap(self):
        result = 0

        for coin in self.assets:
            result += coin.market_cap

        return result

    def prepare_top_coins(self, top_coins):
        result_top_coins = []
        for coin in top_coins:
            new_dict = {}
            new_dict['name'] = coin.name
            new_dict['symbol'] = coin.symbol
            new_dict['change_24h'] = coin.price_change_24h
            result_top_coins.append(new_dict)
        return result_top_coins

    
