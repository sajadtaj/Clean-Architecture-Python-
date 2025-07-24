from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from math import ceil
from core.config.market_rules import RISK_FREE_RATE

from core.entities.enum.enums import OptionType, ContractStatus
from core.entities.asset.asset import AbstractAsset
from core.entities.option.calculators.greeks.black_scholes import BlackScholesGreekCalculator
from core.entities.option.value_objects.greeks import OptionGreeks
from core.entities.option.calculators.greeks.base import BaseGreekCalculator


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
        
    def get_greeks(
        self,
        calculator: BaseGreekCalculator = BlackScholesGreekCalculator(),
        risk_free_rate: float = RISK_FREE_RATE,
        volatility: float = 0.3
    ) -> OptionGreeks:
        """
        محاسبه Greekها با استفاده از مدل مشخص شده
        پارامترها:
        - calculator: شیء محاسبه‌گر از کلاس GreekCalculator (مانند BlackScholesGreekCalculator)
        - risk_free_rate: نرخ بهره بدون ریسک (پیش‌فرض از کانفیگ)
        - volatility: نوسان دارایی پایه (پیش‌فرض 30 درصد)
        """
        return calculator.calculate(
            option_type=self.option_type,
            spot=self.spot_price,
            strike=self.strike_price,
            time_to_expiry=self.time_to_expiry_days / 365,
            risk_free_rate=risk_free_rate,
            volatility=volatility
        )
        
    @abstractmethod
    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        ...

    @abstractmethod
    def get_break_even_price(self) -> float:
        ...
