from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from math import ceil

from core.entities.enum.enums import OptionType, ContractStatus
from core.entities.asset.asset import AbstractAsset


@dataclass
class AbstractOption(ABC):
    contract_name: str
    option_type: OptionType
    strike_price: float
    premium: float
    expiry: datetime
    underlying_asset: AbstractAsset
    ask: Optional[float] = None
    bid: Optional[float] = None
    contract_size: int = 1000  # حجم هر قرارداد
    transaction_fee: Optional[float] = None  # درصد
    settlement_cost: Optional[float] = None  # درصد یا عددی ثابت بسته به بازار


    @property
    def time_to_expiry_days(self) -> int:
        """مدت زمان تا سررسید (برحسب روز، گرد شده به بالا)"""
        delta = self.expiry - datetime.utcnow()
        return max(ceil(delta.total_seconds() / 86400), 0)


    @property
    def spot_price(self) -> float:
        """قیمت لحظه‌ای دارایی پایه"""
        return self.underlying_asset.last_price

    @property
    def contract_status(self) -> ContractStatus:
        """وضعیت قرارداد: سود/زیان/بی‌تفاوت"""
        if self.is_in_the_money():
            return ContractStatus.IN_THE_MONEY
        elif self.is_out_of_the_money():
            return ContractStatus.OUT_OF_THE_MONEY
        return ContractStatus.AT_THE_MONEY

    def is_in_the_money(self) -> bool:
        if self.option_type == OptionType.CALL:
            return self.spot_price > self.strike_price
        return self.spot_price < self.strike_price

    def is_out_of_the_money(self) -> bool:
        if self.option_type == OptionType.CALL:
            return self.spot_price < self.strike_price
        return self.spot_price > self.strike_price

    def is_at_the_money(self) -> bool:
        return self.spot_price == self.strike_price

    def has_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.utcnow()
        return now >= self.expiry

    def is_valid(self) -> bool:
        return (
            self.strike_price > 0 and
            self.premium >= 0 and
            self.expiry > datetime.utcnow() and
            isinstance(self.underlying_asset, AbstractAsset)
        )

    @abstractmethod
    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        ...

    @abstractmethod
    def get_break_even_price(self) -> float:
        ...
