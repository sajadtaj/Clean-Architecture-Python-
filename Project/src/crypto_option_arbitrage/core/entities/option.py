from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


class AbstractOption(ABC):
    def __init__(
        self,
        contract_name: str,
        option_type: OptionType,
        strike_price: float,
        expiry: datetime,
        premium: float,
        underlying_symbol: str
    ):
        self.contract_name = contract_name
        self.option_type = option_type
        self.strike_price = strike_price
        self.expiry = expiry
        self.premium = premium
        self.underlying_symbol = underlying_symbol

    @abstractmethod
    def is_in_the_money(self, spot_price: float) -> bool:
        pass

    @abstractmethod
    def get_payoff(self, spot_price: float) -> float:
        pass

    @abstractmethod
    def get_break_even_price(self) -> float:
        pass

    def has_expired(self, reference_time: Optional[datetime] = None) -> bool:
        ref_time = reference_time or datetime.utcnow()
        return ref_time >= self.expiry

    def is_valid(self) -> bool:
        return (
            self.strike_price > 0 and
            self.premium >= 0 and
            self.expiry > datetime.utcnow()
        )
