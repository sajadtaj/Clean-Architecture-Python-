from datetime import datetime
from crypto_option_arbitrage.core.entities.option import AbstractOption, OptionType


class CryptoOption(AbstractOption):
    def is_in_the_money(self, spot_price: float) -> bool:
        if self.option_type == OptionType.CALL:
            return spot_price > self.strike_price
        else:
            return spot_price < self.strike_price

    def get_payoff(self, spot_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0.0, spot_price - self.strike_price)
        else:
            return max(0.0, self.strike_price - spot_price)

    def get_break_even_price(self) -> float:
        if self.option_type == OptionType.CALL:
            return self.strike_price + self.premium
        else:
            return self.strike_price - self.premium
