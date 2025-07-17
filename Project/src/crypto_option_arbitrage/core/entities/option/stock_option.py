# core/entities/option/stock_option.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.entities.option.option import AbstractOption
from core.entities.asset.stock_asset import StockAsset
from core.entities.enum.enums import OptionType



@dataclass
class StockOption(AbstractOption):
    underlying_asset: StockAsset  # LSP: وابستگی صریح به نوع صحیح دارایی پایه


    def calculate_raw_payoff(self, spot_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0.0, spot_price - self.strike_price)
        return max(0.0, self.strike_price - spot_price)

    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        spot = spot_price or self.spot_price
        raw = self.calculate_raw_payoff(spot)
        
        fee = (self.transaction_fee / 100 * spot) if self.transaction_fee else 0
        settle = self.settlement_cost if (self.settlement_cost and self.settlement_cost > 1) else (
            self.settlement_cost * spot if self.settlement_cost else 0)
        total_cost = self.premium + fee + settle

        return raw - total_cost


    def get_break_even_price(self) -> float:
        fee = (self.transaction_fee / 100 * self.strike_price) if self.transaction_fee else 0
        settle = self.settlement_cost if (self.settlement_cost and self.settlement_cost > 1) else (
            self.settlement_cost * self.strike_price if self.settlement_cost else 0)
        return self.strike_price + self.premium + fee + settle
