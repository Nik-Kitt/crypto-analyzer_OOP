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

    
