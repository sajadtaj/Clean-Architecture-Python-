from dataclasses import dataclass
from typing import Optional
from core.entities.option.option import AbstractOption
from core.entities.asset.leverage_etf_asset import LeverageETFAsset
from core.entities.enum.enums import OptionType


@dataclass
class LeverageETFOption(AbstractOption):
    underlying_asset: LeverageETFAsset
    leverage_ratio: Optional[float] = 2.0  # اهرم پیش‌فرض

    def calculate_raw_payoff(self, spot_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0.0, (spot_price - self.strike_price) * self.leverage_ratio)
        return max(0.0, (self.strike_price - spot_price) * self.leverage_ratio)

    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        spot = spot_price or self.spot_price
        raw_payoff_per_unit = self.calculate_raw_payoff(spot)

        fee_per_unit = (self.transaction_fee / 100 * spot) if self.transaction_fee else 0
        settle_per_unit = (self.settlement_cost / 100 * spot) if self.settlement_cost else 0

        total_cost_per_unit = self.premium + fee_per_unit + settle_per_unit
        return (raw_payoff_per_unit - total_cost_per_unit) * self.contract_size

    def get_break_even_price(self) -> float:
        fee = (self.transaction_fee / 100 * self.strike_price) if self.transaction_fee else 0
        settle = (self.settlement_cost / 100 * self.strike_price) if self.settlement_cost else 0
        return self.strike_price + self.premium + fee + settle

    def get_max_loss(self) -> float:
        """حداکثر زیان = کل هزینه پرداختی برای قرارداد"""
        spot = self.spot_price or self.strike_price
        fee = (self.transaction_fee / 100 * spot) if self.transaction_fee else 0
        settle = (self.settlement_cost / 100 * spot) if self.settlement_cost else 0
        total_cost_per_unit = self.premium + fee + settle
        return total_cost_per_unit * self.contract_size

    def get_max_gain(self, max_spot: float = None) -> Optional[float]:
        """
        حداکثر سود = (سقف قیمت بازار - قیمت اعمال) × اهرم × contract_size - هزینه کل
        در صورت نبود سقف قیمت، مقدار None برمی‌گرداند
        """
        if self.option_type == OptionType.CALL and max_spot:
            raw = max(0, (max_spot - self.strike_price) * self.leverage_ratio)
            return raw * self.contract_size - self.get_max_loss()
        if self.option_type == OptionType.PUT and max_spot:
            raw = max(0, (self.strike_price - max_spot) * self.leverage_ratio)
            return raw * self.contract_size - self.get_max_loss()
        return None
