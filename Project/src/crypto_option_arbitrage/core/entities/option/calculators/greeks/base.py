from abc import ABC, abstractmethod
from core.entities.option.value_objects.greeks import OptionGreeks
from core.entities.enum.enums import OptionType

class BaseGreekCalculator(ABC):
    @abstractmethod
    def calculate(
        self,
        option_type: OptionType,
        spot: float,
        strike: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float
    ) -> OptionGreeks:
        pass
