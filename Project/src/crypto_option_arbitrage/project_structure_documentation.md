# 🧱 Clean Architecture Project Structure
📁 Root: `src/crypto_option_arbitrage`

---

## 🗂️ Layer: Core
📂 Path: `core`


## 🗂️ Layer: Config
📂 Path: `core/config`

- **File**: `asset_rules.py`
  - 📍 Path: `core/config/asset_rules.py`

```python
from core.entities.enum.enums import AssetClass

# کارمزد معاملات به درصد
ASSET_TRANSACTION_FEES = {
    AssetClass.STOCK: 1.5,
    AssetClass.ETF: 0.5,
    AssetClass.LEVERAGE_ETF: 1.0,
    AssetClass.CRYPTO: 0.2,
    AssetClass.COMMODITY: 0.8,
}
```

- **File**: `__init__.py`
  - 📍 Path: `core/config/__init__.py`

```python
```

- **File**: `market_rules.py`
  - 📍 Path: `core/config/market_rules.py`

```python
from core.entities.enum.enums import Market

# دامنه نوسان مجاز (بر حسب درصد)
MARKET_PRICE_LIMITS = {
    Market.TSE_FIRST: 5.0,
    Market.TSE_SECOND: 5.0,
    Market.IFB_FIRST: 5.0,
    Market.IFB_SECOND: 5.0,
    Market.IFB_THIRD: 5.0,
    Market.IFB_INNOVATION: 10.0,
    Market.IFB_BASE_YELLOW: 3.0,
    Market.IFB_BASE_ORANGE: 2.0,
    Market.IFB_BASE_RED: 1.0,
    Market.ENERGY: 7.0,
    Market.COMMODITY: 10.0,
    Market.GLOBAL: 0.0  # معمولاً بدون محدودیت نوسان
}


# نرخ بهره بدون ریسک ایران به صورت عدد اعشاری (مثلاً 20 درصد = 0.2)
RISK_FREE_RATE = 0.2
```

- **File**: `trading_rules.py`
  - 📍 Path: `core/config/trading_rules.py`

```python
from core.entities.enum.enums import AssetClass

# مدت زمان تسویه برای هر کلاس دارایی (به روز کاری)
ASSET_SETTLEMENT_DAYS = {
    AssetClass.STOCK: 2,
    AssetClass.ETF: 2,
    AssetClass.LEVERAGE_ETF: 2,
    AssetClass.CRYPTO: 0,
    AssetClass.COMMODITY: 1,
}

# ساعت معاملات برای هر کلاس دارایی
ASSET_TRADING_HOURS = {
    AssetClass.STOCK: ("09:00", "12:30"),
    AssetClass.ETF: ("09:00", "15:00"),
    AssetClass.LEVERAGE_ETF: ("09:00", "15:00"),
    AssetClass.CRYPTO: ("00:00", "23:59"),
    AssetClass.COMMODITY: ("10:00", "15:30"),
}
```


## 🗂️ Layer: Entities
📂 Path: `core/entities`


## 🗂️ Layer: Asset
📂 Path: `core/entities/asset`

- **File**: `asset.py`
  - 📍 Path: `core/entities/asset/asset.py`

```python
# core/entities/asset.py

from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime, time
from abc import ABC

from core.entities.enum.enums import AssetClass, Market
from core.config.market_rules import MARKET_PRICE_LIMITS
from core.config.asset_rules import ASSET_TRANSACTION_FEES


@dataclass
class AbstractAsset(ABC):
    name: str                            # نام کامل دارایی
    symbol: str                          # نماد (مثلاً BTC یا فولاد)
    isin: Optional[str]                  # شناسه ملی دارایی (برای سهام/ETF)
    asset_class: AssetClass              # نوع دارایی (سهام، کریپتو و ...)
    market: Market                       # بازار محل معامله
    last_price: float                    # آخرین قیمت معامله شده
    close_price: float                   # قیمت پایانی رسمی
    previous_price: float                # قیمت روز گذشته
    settlement_days: int                # مدت زمان تسویه (مثلاً 2 روز)
    trading_hours: Tuple[str, str]      # ساعت مجاز معامله به صورت ('09:00', '12:30')
    ask_price: Optional[float] = None   # کمترین قیمت فروش فعلی
    bid_price: Optional[float] = None   # بیشترین قیمت خرید فعلی

    def get_price_limit(self) -> float:
        """
        دامنه نوسان مجاز برای بازار دارایی (بر حسب درصد)
        """
        return MARKET_PRICE_LIMITS.get(self.market, 0.0)

    def get_transaction_fee(self) -> float:
        """
        کارمزد معامله دارایی (بر حسب درصد)
        """
        return ASSET_TRANSACTION_FEES.get(self.asset_class, 0.0)

    def is_trading_now(self, current_time: Optional[datetime] = None) -> bool:
        """
        بررسی فعال بودن بازار در لحظه فعلی
        """
        now = current_time or datetime.now()
        start_str, end_str = self.trading_hours
        start = time.fromisoformat(start_str)
        end = time.fromisoformat(end_str)
        return start <= now.time() <= end

    def has_price_limit_breach(self, current_price: float) -> bool:
        limit_percent = self.get_price_limit()
        if limit_percent == 0.0:
            return False  # برای کریپتو یا دارایی‌های بدون محدودیت
        upper_limit = self.close_price * (1 + limit_percent / 100)
        lower_limit = self.close_price * (1 - limit_percent / 100)
        return current_price > upper_limit or current_price < lower_limit


    def get_spread(self) -> Optional[float]:
        """
        اختلاف قیمت خرید و فروش (ask - bid)
        """
        if self.ask_price is not None and self.bid_price is not None:
            return self.ask_price - self.bid_price
        return None

    def is_valid(self) -> bool:
        """
        بررسی اعتبار اولیه دارایی
        """
        return self.last_price > 0 and self.close_price > 0
```

- **File**: `crypto_asset.py`
  - 📍 Path: `core/entities/asset/crypto_asset.py`

```python
# core/entities/crypto_asset.py

from core.entities.asset.asset import AbstractAsset
from core.entities.enum.enums import AssetClass, Market
from core.config.trading_rules import ASSET_SETTLEMENT_DAYS, ASSET_TRADING_HOURS


class CryptoAsset(AbstractAsset):
    def __init__(
        self,
        name: str,
        symbol: str,
        market: Market,
        last_price: float,
        close_price: float,
        previous_price: float,
        ask_price: float = None,
        bid_price: float = None
    ):
        asset_class = AssetClass.CRYPTO
        settlement_days = ASSET_SETTLEMENT_DAYS[asset_class]
        trading_hours = ASSET_TRADING_HOURS[asset_class]

        super().__init__(
            name=name,
            symbol=symbol,
            isin=None,
            asset_class=asset_class,
            market=market,
            last_price=last_price,
            close_price=close_price,
            previous_price=previous_price,
            settlement_days=settlement_days,
            trading_hours=trading_hours,
            ask_price=ask_price,
            bid_price=bid_price
        )
```

- **File**: `etf_asset.py`
  - 📍 Path: `core/entities/asset/etf_asset.py`

```python
from core.entities.asset.asset import AbstractAsset
from core.entities.enum.enums import AssetClass, Market
from core.config.trading_rules import ASSET_SETTLEMENT_DAYS, ASSET_TRADING_HOURS


class ETFAsset(AbstractAsset):
    def __init__(
        self,
        name: str,
        symbol: str,
        isin: str,
        market: Market,
        last_price: float,
        close_price: float,
        previous_price: float,
        ask_price: float = None,
        bid_price: float = None
    ):
        asset_class = AssetClass.ETF
        settlement_days = ASSET_SETTLEMENT_DAYS[asset_class]
        trading_hours = ASSET_TRADING_HOURS[asset_class]

        super().__init__(
            name=name,
            symbol=symbol,
            isin=isin,
            asset_class=asset_class,
            market=market,
            last_price=last_price,
            close_price=close_price,
            previous_price=previous_price,
            settlement_days=settlement_days,
            trading_hours=trading_hours,
            ask_price=ask_price,
            bid_price=bid_price
        )
```

- **File**: `__init__.py`
  - 📍 Path: `core/entities/asset/__init__.py`

```python
```

- **File**: `leverage_etf_asset.py`
  - 📍 Path: `core/entities/asset/leverage_etf_asset.py`

```python
# core/entities/leverage_etf_asset.py

from core.entities.asset.asset import AbstractAsset
from core.entities.enum.enums import AssetClass, Market
from core.config.trading_rules import ASSET_SETTLEMENT_DAYS, ASSET_TRADING_HOURS


class LeverageETFAsset(AbstractAsset):
    def __init__(
        self,
        name: str,
        symbol: str,
        isin: str,
        market: Market,
        last_price: float,
        close_price: float,
        previous_price: float,
        ask_price: float = None,
        bid_price: float = None,
        leverage_ratio: float = 2.0  # نسبت اهرم پیش‌فرض (مثلاً 2 برابر)
    ):
        asset_class = AssetClass.LEVERAGE_ETF
        settlement_days = ASSET_SETTLEMENT_DAYS[asset_class]
        trading_hours = ASSET_TRADING_HOURS[asset_class]

        super().__init__(
            name=name,
            symbol=symbol,
            isin=isin,
            asset_class=asset_class,
            market=market,
            last_price=last_price,
            close_price=close_price,
            previous_price=previous_price,
            settlement_days=settlement_days,
            trading_hours=trading_hours,
            ask_price=ask_price,
            bid_price=bid_price
        )
```

- **File**: `stock_asset.py`
  - 📍 Path: `core/entities/asset/stock_asset.py`

```python
# core/entities/stock_asset.py

from core.entities.asset.asset import AbstractAsset
from core.entities.enum.enums import AssetClass, Market
from core.config.trading_rules import ASSET_SETTLEMENT_DAYS, ASSET_TRADING_HOURS


class StockAsset(AbstractAsset):
    def __init__(
        self,
        name: str,
        symbol: str,
        isin: str,
        market: Market,
        last_price: float,
        close_price: float,
        previous_price: float,
        ask_price: float = None,
        bid_price: float = None
    ):
        asset_class = AssetClass.STOCK
        settlement_days = ASSET_SETTLEMENT_DAYS[asset_class]
        trading_hours = ASSET_TRADING_HOURS[asset_class]

        super().__init__(
            name=name,
            symbol=symbol,
            isin=isin,
            asset_class=asset_class,
            market=market,
            last_price=last_price,
            close_price=close_price,
            previous_price=previous_price,
            settlement_days=settlement_days,
            trading_hours=trading_hours,
            ask_price=ask_price,
            bid_price=bid_price
        )
```


## 🗂️ Layer: Enum
📂 Path: `core/entities/enum`

- **File**: `enums.py`
  - 📍 Path: `core/entities/enum/enums.py`

```python
# core/entities/enums.py

from enum import Enum


class AssetClass(str, Enum):
    STOCK = "Stock"
    ETF = "ETF"
    LEVERAGE_ETF = "Leveraged ETF"
    CRYPTO = "Crypto"
    COMMODITY = "Commodity"


class Market(str, Enum):
    #
    # بورس اوراق بهادار تهران (TSE)
    #
    TSE_FIRST = "بورس - بازار اول"
    TSE_SECOND = "بورس - بازار دوم"
    #
    # فرابورس ایران (IFB)
    #
    IFB_FIRST = "فرابورس - بازار اول"
    IFB_SECOND = "فرابورس - بازار دوم"
    IFB_THIRD = "فرابورس - بازار سوم"
    IFB_INNOVATION = "فرابورس - ابزارهای نوین مالی"

    #
    # بازار پایه فرابورس
    #

    IFB_BASE_YELLOW = "بازار پایه - زرد"
    IFB_BASE_ORANGE = "بازار پایه - نارنجی"
    IFB_BASE_RED = "بازار پایه - قرمز"

    #
    # سایر بازارهای رسمی ایران
    #

    ENERGY = "بورس انرژی"
    COMMODITY = "بورس کالا"
    
    #
    # بازار جهانی
    #
    
    GLOBAL = "بازار جهانی (کریپتو / خارجی)"
    
class ContractStatus(str, Enum):
    IN_THE_MONEY = "In the money"
    OUT_OF_THE_MONEY = "Out of the money"
    AT_THE_MONEY = "At the money"
    
class OptionType(Enum):
    CALL = "Call"
    PUT = "Put"```

- **File**: `__init__.py`
  - 📍 Path: `core/entities/enum/__init__.py`

```python
```

- **File**: `__init__.py`
  - 📍 Path: `core/entities/__init__.py`

```python
```


## 🗂️ Layer: Option
📂 Path: `core/entities/option`


## 🗂️ Layer: Calculators
📂 Path: `core/entities/option/calculators`


## 🗂️ Layer: Greeks
📂 Path: `core/entities/option/calculators/greeks`

- **File**: `base.py`
  - 📍 Path: `core/entities/option/calculators/greeks/base.py`

```python
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
```

- **File**: `black_scholes.py`
  - 📍 Path: `core/entities/option/calculators/greeks/black_scholes.py`

```python
from math import exp, log, sqrt
from scipy.stats import norm
from core.entities.enum.enums import OptionType
from core.entities.option.value_objects.greeks import OptionGreeks
from core.entities.option.calculators.greeks.base import BaseGreekCalculator

class BlackScholesGreekCalculator(BaseGreekCalculator):
    def calculate(self, option_type, spot, strike, time_to_expiry, risk_free_rate, volatility) -> OptionGreeks:
        d1 = (log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (volatility * sqrt(time_to_expiry))
        d2 = d1 - volatility * sqrt(time_to_expiry)

        if option_type == OptionType.CALL:
            delta = norm.cdf(d1)
            theta = (-spot * norm.pdf(d1) * volatility / (2 * sqrt(time_to_expiry))
                     - risk_free_rate * strike * exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
            rho = strike * time_to_expiry * exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
        else:
            delta = -norm.cdf(-d1)
            theta = (-spot * norm.pdf(d1) * volatility / (2 * sqrt(time_to_expiry))
                     + risk_free_rate * strike * exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2))
            rho = -strike * time_to_expiry * exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)

        gamma = norm.pdf(d1) / (spot * volatility * sqrt(time_to_expiry))
        vega = spot * norm.pdf(d1) * sqrt(time_to_expiry)

        return OptionGreeks(
            delta=delta,
            gamma=gamma,
            theta=theta / 365,  # تبدیل به روز
            vega=vega / 100,
            rho=rho / 100
        )
```

- **File**: `etf_option.py`
  - 📍 Path: `core/entities/option/etf_option.py`

```python
# core/entities/option/etf_option.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.entities.option.option import AbstractOption
from core.entities.asset.etf_asset import ETFAsset
from core.entities.enum.enums import OptionType


@dataclass
class ETFOption(AbstractOption):
    underlying_asset: ETFAsset
    benchmark_index: Optional[str] = None  # مثلاً "S&P 500", "شاخص هم‌وزن"
    nav_deviation: Optional[float] = None  # اختلاف قیمت بازار با NAV

    def calculate_raw_payoff(self, spot_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0.0, spot_price - self.strike_price)
        return max(0.0, self.strike_price - spot_price)

    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        spot = spot_price or self.spot_price
        raw_payoff_per_unit = self.calculate_raw_payoff(spot)

        # ✅ هزینه‌ها برای یک واحد
        fee_per_unit = (self.transaction_fee / 100 * spot) if self.transaction_fee else 0
        settle_per_unit = (self.settlement_cost / 100 * spot) if self.settlement_cost else 0



        total_cost_per_unit = self.premium + fee_per_unit + settle_per_unit
        return (raw_payoff_per_unit - total_cost_per_unit) * self.contract_size

    def get_break_even_price(self) -> float:
        fee = (self.transaction_fee / 100 * self.strike_price) if self.transaction_fee else 0
        settle = (self.settlement_cost / 100 * self.strike_price) if self.settlement_cost else 0
        return self.strike_price + self.premium + fee + settle


    def is_liquid(self) -> bool:
        """
        بررسی نقدشوندگی: اگر اسپرد خیلی زیاد باشد، نقدشوندگی پایین است.
        """
        spread = self.underlying_asset.get_spread()
        if spread is None:
            return False
        return spread / self.underlying_asset.last_price < 0.02  # کمتر از ۲٪

    def has_nav_deviation(self, nav_price: float) -> bool:
        """
        بررسی انحراف قیمت نسبت به NAV
        """
        deviation = abs(self.spot_price - nav_price) / nav_price
        self.nav_deviation = deviation
        return deviation > 0.03  # بیشتر از ۳٪
```

- **File**: `__init__.py`
  - 📍 Path: `core/entities/option/__init__.py`

```python
```

- **File**: `leverage_etf_option.py`
  - 📍 Path: `core/entities/option/leverage_etf_option.py`

```python
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
```

- **File**: `option.py`
  - 📍 Path: `core/entities/option/option.py`

```python
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
```

- **File**: `stock_option.py`
  - 📍 Path: `core/entities/option/stock_option.py`

```python
# core/entities/option/stock_option.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.entities.option.option import AbstractOption
from core.entities.asset.stock_asset import StockAsset
from core.entities.enum.enums import OptionType


@dataclass
class StockOption(AbstractOption):
    underlying_asset: StockAsset

    def calculate_raw_payoff(self, spot_price: float) -> float:
        if self.option_type == OptionType.CALL:
            return max(0.0, spot_price - self.strike_price)
        return max(0.0, self.strike_price - spot_price)

    def get_payoff(self, spot_price: Optional[float] = None) -> float:
        spot = spot_price or self.spot_price
        raw_payoff_per_unit = self.calculate_raw_payoff(spot)

        # ✅ هزینه‌ها برای یک واحد
        fee_per_unit = (self.transaction_fee / 100 * spot) if self.transaction_fee else 0
        settle_per_unit = (self.settlement_cost / 100 * spot) if self.settlement_cost else 0



        total_cost_per_unit = self.premium + fee_per_unit + settle_per_unit
        return (raw_payoff_per_unit - total_cost_per_unit) * self.contract_size

    def get_break_even_price(self) -> float:
        fee = (self.transaction_fee / 100 * self.strike_price) if self.transaction_fee else 0
        settle = (self.settlement_cost / 100 * self.strike_price) if self.settlement_cost else 0
        return self.strike_price + self.premium + fee + settle
```


## 🗂️ Layer: Value Objects
📂 Path: `core/entities/option/value_objects`

- **File**: `greeks.py`
  - 📍 Path: `core/entities/option/value_objects/greeks.py`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class OptionGreeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

    def __str__(self):
        return f"Δ: {self.delta:.4f}, Γ: {self.gamma:.4f}, Θ: {self.theta:.4f}, 𝜈: {self.vega:.4f}, ρ: {self.rho:.4f}"
```

- **File**: `__init__.py`
  - 📍 Path: `core/__init__.py`

```python
```


## 🗂️ Layer: Infrastructure
📂 Path: `infrastructure`


## 🗂️ Layer: Data Providers
📂 Path: `infrastructure/data_providers`

- **File**: `__init__.py`
  - 📍 Path: `infrastructure/data_providers/__init__.py`

```python
```


## 🗂️ Layer: Db
📂 Path: `infrastructure/db`

- **File**: `__init__.py`
  - 📍 Path: `infrastructure/db/__init__.py`

```python
```

- **File**: `__init__.py`
  - 📍 Path: `infrastructure/__init__.py`

```python
```


## 🗂️ Layer: Notifiers
📂 Path: `infrastructure/notifiers`

- **File**: `__init__.py`
  - 📍 Path: `infrastructure/notifiers/__init__.py`

```python
```

- **File**: `__init__.py`
  - 📍 Path: `__init__.py`

```python
```


## 🗂️ Layer: Interfaces
📂 Path: `interfaces`


## 🗂️ Layer: Api
📂 Path: `interfaces/api`

- **File**: `__init__.py`
  - 📍 Path: `interfaces/api/__init__.py`

```python
```


## 🗂️ Layer: Cli
📂 Path: `interfaces/cli`

- **File**: `__init__.py`
  - 📍 Path: `interfaces/cli/__init__.py`

```python
```

- **File**: `__init__.py`
  - 📍 Path: `interfaces/__init__.py`

```python
```


## 🗂️ Layer: Scheduler
📂 Path: `interfaces/scheduler`

- **File**: `__init__.py`
  - 📍 Path: `interfaces/scheduler/__init__.py`

```python
```

- **File**: `main.py`
  - 📍 Path: `main.py`

```python
```


## 🗂️ Layer: Notebooks
📂 Path: `notebooks`


## 🗂️ Layer: Entities
📂 Path: `notebooks/entities`

- **File**: `asset.ipynb`
  - 📍 Path: `notebooks/entities/asset.ipynb`

```python
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "f73bf675",
   "metadata": {},
   "source": [
    "# Call Packages"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "1d52dacd",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "os.chdir('/home/sajad/All Project/Clean Architecture Python/Project/src/crypto_option_arbitrage')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6f69984b",
   "metadata": {},
   "outputs": [],
   "source": [
    "from core.entities.enum.enums import Market\n",
    "# Stock Crypto Etf\n",
    "from core.entities.asset.stock_asset import StockAsset\n",
    "from core.entities.asset.crypto_asset import CryptoAsset\n",
    "from core.entities.asset.etf_asset import ETFAsset\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2551f2bc",
   "metadata": {},
   "source": [
    "# Strock Asset Class\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7d8401bf",
   "metadata": {},
   "source": [
    "## Create Instance"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "6244327e",
   "metadata": {},
   "outputs": [],
   "source": [
    "StockInstanse = StockAsset(\n",
    "        name=\"فولاد مبارکه\",\n",
    "        symbol=\"فولاد\",\n",
    "        isin=\"IRO1FOLD0001\",\n",
    "        market=Market.TSE_FIRST,\n",
    "        last_price=5000,\n",
    "        close_price=5100,\n",
    "        previous_price=4950,\n",
    "        ask_price=5150,\n",
    "        bid_price=5050\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4c4ba6f4",
   "metadata": {},
   "source": [
    "## Call Variable and Methods"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "0d2dadea",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " Info name     :فولاد مبارکه\n",
      " Market        :بورس - بازار اول\n",
      " Asset Class   :Stock\n",
      " Market time   :('09:00', '12:30')\n",
      " Range Price   :5.0\n",
      " TC            :1.5\n",
      " is open ?     :False\n"
     ]
    }
   ],
   "source": [
    "print(rf' Info name     :{StockInstanse.name}')\n",
    "print(rf' Market        :{StockInstanse.market}')\n",
    "print(rf' Asset Class   :{StockInstanse.asset_class}')\n",
    "\n",
    "print(rf' Market time   :{StockInstanse.trading_hours}')\n",
    "print(rf' Range Price   :{StockInstanse.get_price_limit()}')\n",
    "print(rf' TC            :{StockInstanse.get_transaction_fee()}')\n",
    "print(rf' is open ?     :{StockInstanse.is_trading_now()}')\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "71797f2f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'name': 'فولاد مبارکه',\n",
       " 'symbol': 'فولاد',\n",
       " 'isin': 'IRO1FOLD0001',\n",
       " 'asset_class': <AssetClass.STOCK: 'Stock'>,\n",
       " 'market': <Market.TSE_FIRST: 'بورس - بازار اول'>,\n",
       " 'last_price': 5000,\n",
       " 'close_price': 5100,\n",
       " 'previous_price': 4950,\n",
       " 'settlement_days': 2,\n",
       " 'trading_hours': ('09:00', '12:30'),\n",
       " 'ask_price': 5150,\n",
       " 'bid_price': 5050}"
      ]
     },
     "execution_count": 5,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "StockInstanse.__dict__"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "65193fe8",
   "metadata": {},
   "source": [
    "## Method resolution order (MRO)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "f38c52af",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Help on StockAsset in module core.entities.asset.stock_asset object:\n",
      "\n",
      "class StockAsset(core.entities.asset.asset.AbstractAsset)\n",
      " |  StockAsset(name: str, symbol: str, isin: str, market: core.entities.enum.enums.Market, last_price: float, close_price: float, previous_price: float, ask_price: float = None, bid_price: float = None)\n",
      " |  \n",
      " |  Method resolution order:\n",
      " |      StockAsset\n",
      " |      core.entities.asset.asset.AbstractAsset\n",
      " |      abc.ABC\n",
      " |      builtins.object\n",
      " |  \n",
      " |  Methods defined here:\n",
      " |  \n",
      " |  __init__(self, name: str, symbol: str, isin: str, market: core.entities.enum.enums.Market, last_price: float, close_price: float, previous_price: float, ask_price: float = None, bid_price: float = None)\n",
      " |      Initialize self.  See help(type(self)) for accurate signature.\n",
      " |  \n",
      " |  ----------------------------------------------------------------------\n",
      " |  Data and other attributes defined here:\n",
      " |  \n",
      " |  __abstractmethods__ = frozenset()\n",
      " |  \n",
      " |  __annotations__ = {}\n",
      " |  \n",
      " |  ----------------------------------------------------------------------\n",
      " |  Methods inherited from core.entities.asset.asset.AbstractAsset:\n",
      " |  \n",
      " |  __eq__(self, other)\n",
      " |      Return self==value.\n",
      " |  \n",
      " |  __repr__(self)\n",
      " |      Return repr(self).\n",
      " |  \n",
      " |  get_price_limit(self) -> float\n",
      " |      دامنه نوسان مجاز برای بازار دارایی (بر حسب درصد)\n",
      " |  \n",
      " |  get_spread(self) -> Optional[float]\n",
      " |      اختلاف قیمت خرید و فروش (ask - bid)\n",
      " |  \n",
      " |  get_transaction_fee(self) -> float\n",
      " |      کارمزد معامله دارایی (بر حسب درصد)\n",
      " |  \n",
      " |  has_price_limit_breach(self, current_price: float) -> bool\n",
      " |  \n",
      " |  is_trading_now(self, current_time: Optional[datetime.datetime] = None) -> bool\n",
      " |      بررسی فعال بودن بازار در لحظه فعلی\n",
      " |  \n",
      " |  is_valid(self) -> bool\n",
      " |      بررسی اعتبار اولیه دارایی\n",
      " |  \n",
      " |  ----------------------------------------------------------------------\n",
      " |  Data descriptors inherited from core.entities.asset.asset.AbstractAsset:\n",
      " |  \n",
      " |  __dict__\n",
      " |      dictionary for instance variables (if defined)\n",
      " |  \n",
      " |  __weakref__\n",
      " |      list of weak references to the object (if defined)\n",
      " |  \n",
      " |  ----------------------------------------------------------------------\n",
      " |  Data and other attributes inherited from core.entities.asset.asset.AbstractAsset:\n",
      " |  \n",
      " |  __dataclass_fields__ = {'ask_price': Field(name='ask_price',type=typin...\n",
      " |  \n",
      " |  __dataclass_params__ = _DataclassParams(init=True,repr=True,eq=True,or...\n",
      " |  \n",
      " |  __hash__ = None\n",
      " |  \n",
      " |  __match_args__ = ('name', 'symbol', 'isin', 'asset_class', 'market', '...\n",
      " |  \n",
      " |  ask_price = None\n",
      " |  \n",
      " |  bid_price = None\n",
      "\n"
     ]
    }
   ],
   "source": [
    "help(StockInstanse)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8962c998",
   "metadata": {},
   "source": [
    "# Crypto"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "10444e33",
   "metadata": {},
   "source": [
    "## Create Instance"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "369b59c0",
   "metadata": {},
   "outputs": [],
   "source": [
    "btc = CryptoAsset(\n",
    "    name=\"Bitcoin\",\n",
    "    symbol=\"BTC\",\n",
    "    market=Market.GLOBAL,\n",
    "    last_price=58320,\n",
    "    close_price=58000,\n",
    "    previous_price=57000,\n",
    "    ask_price=58350,\n",
    "    bid_price=58250\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "f03abf77",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ CryptoAsset ساخته شد: CryptoAsset(name='Bitcoin', symbol='BTC', isin=None, asset_class=<AssetClass.CRYPTO: 'Crypto'>, market=<Market.GLOBAL: 'بازار جهانی (کریپتو / خارجی)'>, last_price=58320, close_price=58000, previous_price=57000, settlement_days=0, trading_hours=('00:00', '23:59'), ask_price=58350, bid_price=58250)\n",
      "✅ دامنه نوسان: 0.0\n",
      "✅ کارمزد معامله: 0.2\n",
      "✅ اختلاف قیمت: 100\n",
      "✅ اعتبار قیمت‌ها: True\n",
      "✅ فعال بودن بازار اکنون: True\n",
      "✅ ساعت باز بودن بازار : ('00:00', '23:59')\n"
     ]
    }
   ],
   "source": [
    "print(\"✅ CryptoAsset ساخته شد:\", btc)\n",
    "\n",
    "# Cell 4: بررسی متدهای مربوط به CryptoAsset\n",
    "print(\"✅ دامنه نوسان:\", btc.get_price_limit())\n",
    "print(\"✅ کارمزد معامله:\", btc.get_transaction_fee())\n",
    "print(\"✅ اختلاف قیمت:\", btc.get_spread())\n",
    "print(\"✅ اعتبار قیمت‌ها:\", btc.is_valid())\n",
    "print(\"✅ فعال بودن بازار اکنون:\", btc.is_trading_now())\n",
    "print(\"✅ ساعت باز بودن بازار :\", btc.trading_hours)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "770ab0e5",
   "metadata": {},
   "outputs": [],
   "source": [
    "etf = ETFAsset(\n",
    "    name=\"صندوق شاخصی کارآفرین\",\n",
    "    symbol=\"کارآفرین\",\n",
    "    isin=\"IR1234567890\",\n",
    "    market=Market.IFB_THIRD,\n",
    "    last_price=21500,\n",
    "    close_price=21200,\n",
    "    previous_price=21000,\n",
    "    ask_price=21600,\n",
    "    bid_price=21400\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "376cb174",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "✅ ETFAsset ساخته شد: ETFAsset(name='صندوق شاخصی کارآفرین', symbol='کارآفرین', isin='IR1234567890', asset_class=<AssetClass.ETF: 'ETF'>, market=<Market.IFB_THIRD: 'فرابورس - بازار سوم'>, last_price=21500, close_price=21200, previous_price=21000, settlement_days=2, trading_hours=('09:00', '15:00'), ask_price=21600, bid_price=21400)\n",
      "✅ دامنه نوسان: 5.0\n",
      "✅ کارمزد معامله: 0.5\n",
      "✅ اختلاف قیمت: 200\n",
      "✅ اعتبار قیمت‌ها: True\n",
      "✅ فعال بودن بازار اکنون: False\n",
      "✅ ساعت باز بودن بازار : ('09:00', '15:00')\n"
     ]
    }
   ],
   "source": [
    "print(\"\\n✅ ETFAsset ساخته شد:\", etf)\n",
    "\n",
    "# Cell 6: بررسی متدهای مربوط به ETFAsset\n",
    "print(\"✅ دامنه نوسان:\", etf.get_price_limit())\n",
    "print(\"✅ کارمزد معامله:\", etf.get_transaction_fee())\n",
    "print(\"✅ اختلاف قیمت:\", etf.get_spread())\n",
    "print(\"✅ اعتبار قیمت‌ها:\", etf.is_valid())\n",
    "print(\"✅ فعال بودن بازار اکنون:\", etf.is_trading_now())\n",
    "print(\"✅ ساعت باز بودن بازار :\", etf.trading_hours)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c648b862",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

- **File**: `option.ipynb`
  - 📍 Path: `notebooks/entities/option.ipynb`

```python
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "63c1d4ed",
   "metadata": {},
   "source": [
    "# Option"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1fb6f81c",
   "metadata": {},
   "source": [
    "## Import Packages"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "88a89624",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "os.chdir('/home/sajad/All Project/Clean Architecture Python/Project/src/crypto_option_arbitrage')\n",
    "from datetime import datetime, timedelta\n",
    "from core.entities.enum.enums import Market, OptionType, ContractStatus\n",
    "from core.config.market_rules import RISK_FREE_RATE\n",
    "from core.entities.option.value_objects.greeks import OptionGreeks\n",
    "from core.entities.option.calculators.greeks.black_scholes import BlackScholesGreekCalculator\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4296dcc8",
   "metadata": {},
   "source": [
    "## Stock Option"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "aba6b064",
   "metadata": {},
   "outputs": [],
   "source": [
    "from core.entities.asset.stock_asset import StockAsset\n",
    "from core.entities.option.stock_option import StockOption"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "9f4b9ff6",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Cell 3: ساخت دارایی پایه\n",
    "stock = StockAsset(\n",
    "    name=\"فولاد مبارکه\",\n",
    "    symbol=\"FOLD\",\n",
    "    isin=\"IR1234567890\",\n",
    "    market=Market.TSE_FIRST,\n",
    "    last_price=1100,\n",
    "    close_price=1000,\n",
    "    previous_price=990,\n",
    "    ask_price=1110,\n",
    "    bid_price=1090,\n",
    ")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "9c9c8fab",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Cell 4: ساخت آپشن کال\n",
    "stock_option = StockOption(\n",
    "    contract_name=\"FOLD_C_1000\",\n",
    "    option_type=OptionType.CALL,\n",
    "    strike_price=1000,\n",
    "    premium=50,\n",
    "    expiry=datetime.utcnow() + timedelta(days=10),\n",
    "    underlying_asset=stock,\n",
    "    ask=55,\n",
    "    bid=45,\n",
    "    transaction_fee=2.0,\n",
    "    settlement_cost=1.0\n",
    ")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "85da6bf4",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Spot Price: 1100\n",
      "Time to Expiry: 10\n",
      "Break Even: 1080.0\n",
      "Payoff: 65500.0\n",
      "Contract Status: ContractStatus.IN_THE_MONEY\n",
      "\n",
      "📘 Greekهای StockOption:\n",
      "Δ: 0.9800, Γ: 0.0009, Θ: -0.6647, 𝜈: 0.0880, ρ: 0.2663\n"
     ]
    }
   ],
   "source": [
    "# Cell 5: بررسی عملکردها\n",
    "print(\"Spot Price:\", stock_option.spot_price)\n",
    "print(\"Time to Expiry:\", stock_option.time_to_expiry_days)\n",
    "print(\"Break Even:\", stock_option.get_break_even_price())\n",
    "print(\"Payoff:\", stock_option.get_payoff(spot_price=1150))\n",
    "print(\"Contract Status:\", stock_option.contract_status)\n",
    "\n",
    "# انتخاب مدل محاسبه اعداد یونانی ماژولار است\n",
    "calculator = BlackScholesGreekCalculator()\n",
    "print(\"\\n📘 Greekهای StockOption:\")\n",
    "print(stock_option.get_greeks(calculator=calculator))\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "30aa63ce",
   "metadata": {},
   "source": [
    "## ETF"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "c83189c1",
   "metadata": {},
   "outputs": [],
   "source": [
    "from core.entities.asset.etf_asset import ETFAsset\n",
    "from core.entities.option.etf_option import ETFOption"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "ede6a2be",
   "metadata": {},
   "outputs": [],
   "source": [
    "etf = ETFAsset(\n",
    "    name=\"صندوق شاخصی\",\n",
    "    symbol=\"صندوق\",\n",
    "    isin=\"IR1234567890\",\n",
    "    market=Market.IFB_THIRD,\n",
    "    last_price=10200,\n",
    "    close_price=10100,\n",
    "    previous_price=10000,\n",
    "    ask_price=10250,\n",
    "    bid_price=10150\n",
    ")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "ebb31759",
   "metadata": {},
   "outputs": [],
   "source": [
    "etf_option = ETFOption(\n",
    "    contract_name=\"ETF_CALL_10500\",\n",
    "    option_type=OptionType.CALL,\n",
    "    strike_price=10500,\n",
    "    premium=200,\n",
    "    expiry=datetime.utcnow() + timedelta(days=10),\n",
    "    underlying_asset=etf,\n",
    "    ask=210,\n",
    "    bid=190,\n",
    "    transaction_fee=0.5,\n",
    "    settlement_cost=1.0,\n",
    "    benchmark_index=\"S&P 500\"\n",
    ")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7d8c1e97",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "📈 Spot Price: 10200\n",
      "🕒 Time to Expiry: 10\n",
      "📊 Break Even Price: 10857.5\n",
      "💰 Payoff at 11000: 135000.0\n",
      "📉 Contract Status: OUT_OF_THE_MONEY\n",
      "🔁 Is Liquid: True\n",
      "📉 NAV Deviation? True\n",
      "📉 Deviation Value: 0.04081632653061224\n",
      "\n",
      "📘 Greekهای StockOption:\n",
      "Δ: 0.3269, Γ: 0.0007, Θ: -10.9050, 𝜈: 6.0907, ρ: 0.8845\n"
     ]
    }
   ],
   "source": [
    "\n",
    "print(\"📈 Spot Price:\", etf_option.spot_price)\n",
    "print(\"🕒 Time to Expiry:\", etf_option.time_to_expiry_days)\n",
    "print(\"📊 Break Even Price:\", etf_option.get_break_even_price())\n",
    "print(\"💰 Payoff at 11000:\", etf_option.get_payoff(11000))\n",
    "print(\"📉 Contract Status:\", etf_option.contract_status.name)\n",
    "print(\"🔁 Is Liquid:\", etf_option.is_liquid())\n",
    "print(\"📉 NAV Deviation?\", etf_option.has_nav_deviation(9800))\n",
    "print(\"📉 Deviation Value:\", etf_option.nav_deviation)\n",
    "# انتخاب مدل محاسبه اعداد یونانی ماژولار است\n",
    "calculator = BlackScholesGreekCalculator()\n",
    "print(\"\\n📘 Greekهای etf_option:\")\n",
    "print(etf_option.get_greeks(calculator=calculator))\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4c664b33",
   "metadata": {},
   "source": [
    "## Leverage ETF"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "16ab23cd",
   "metadata": {},
   "outputs": [],
   "source": [
    "from core.entities.asset.leverage_etf_asset import LeverageETFAsset\n",
    "from core.entities.option.leverage_etf_option import LeverageETFOption"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "9f24451f",
   "metadata": {},
   "outputs": [],
   "source": [
    "etf_asset = LeverageETFAsset(\n",
    "    name=\"نمونه اهرمی\",\n",
    "    symbol=\"LETF\",\n",
    "    isin=\"IR000000LETF\",\n",
    "    market=Market.IFB_SECOND,\n",
    "    last_price=9100,\n",
    "    close_price=9000,\n",
    "    previous_price=8800,\n",
    "    ask_price=9150,\n",
    "    bid_price=9050,\n",
    "    leverage_ratio=2.0\n",
    ")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "690b1d25",
   "metadata": {},
   "outputs": [],
   "source": [
    "lev_etf_option = LeverageETFOption(\n",
    "    contract_name=\"LETF_CALL_8800\",\n",
    "    option_type=OptionType.CALL,\n",
    "    strike_price=8800,\n",
    "    premium=250,\n",
    "    expiry=datetime.utcnow() + timedelta(days=20),\n",
    "    underlying_asset=etf_asset,\n",
    "    ask=260,\n",
    "    bid=240,\n",
    "    contract_size=1000,\n",
    "    transaction_fee=0.5,     # 0.5 درصد\n",
    "    settlement_cost=1.0      # 1 درصد\n",
    ")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "28198a74",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "📘 Contract Info\n",
      "نام: LETF_CALL_8800\n",
      "نوع: OptionType.CALL\n",
      "قیمت اعمال: 8800\n",
      "پریمیوم: 250\n",
      "----------------------------------------\n",
      "⏳ زمان تا سررسید: 20 روز\n",
      "📊 وضعیت قرارداد: IN_THE_MONEY\n",
      "💰 قیمت سر به سر (Break-even): 9182.0\n",
      "💸 Payoff در spot=9000: 15000.0\n",
      "💸 Payoff در spot=8500: -377500.0\n",
      "📉 حداکثر زیان: 386500.0\n",
      "📈 حداکثر سود در max_spot=9500: 1013500.0\n",
      "\n",
      "📘 Greekهای lev_etf_option:\n",
      "Δ: 0.7481, Γ: 0.0005, Θ: -8.5558, 𝜈: 6.7963, ρ: 3.4587\n"
     ]
    }
   ],
   "source": [
    "\n",
    "# 3️⃣ چاپ اطلاعات اولیه\n",
    "print(\"📘 Contract Info\")\n",
    "print(\"نام:\", lev_etf_option.contract_name)\n",
    "print(\"نوع:\", lev_etf_option.option_type)\n",
    "print(\"قیمت اعمال:\", lev_etf_option.strike_price)\n",
    "print(\"پریمیوم:\", lev_etf_option.premium)\n",
    "print(\"-\" * 40)\n",
    "\n",
    "# 4️⃣ زمان تا سررسید\n",
    "print(\"⏳ زمان تا سررسید:\", lev_etf_option.time_to_expiry_days, \"روز\")\n",
    "\n",
    "# 5️⃣ وضعیت قرارداد\n",
    "print(\"📊 وضعیت قرارداد:\", lev_etf_option.contract_status.name)\n",
    "\n",
    "# 6️⃣ محاسبه Break-even\n",
    "print(\"💰 قیمت سر به سر (Break-even):\", lev_etf_option.get_break_even_price())\n",
    "\n",
    "# 7️⃣ محاسبه Payoff برای قیمت اسپات مختلف\n",
    "print(\"💸 Payoff در spot=9000:\", lev_etf_option.get_payoff(spot_price=9000))\n",
    "print(\"💸 Payoff در spot=8500:\", lev_etf_option.get_payoff(spot_price=8500))\n",
    "\n",
    "# 8️⃣ حداکثر زیان\n",
    "print(\"📉 حداکثر زیان:\", lev_etf_option.get_max_loss())\n",
    "\n",
    "# 9️⃣ حداکثر سود در سقف فرضی 9500\n",
    "print(\"📈 حداکثر سود در max_spot=9500:\", lev_etf_option.get_max_gain(max_spot=9500))\n",
    "\n",
    "# انتخاب مدل محاسبه اعداد یونانی ماژولار است\n",
    "calculator = BlackScholesGreekCalculator()\n",
    "print(\"\\n📘 Greekهای lev_etf_option:\")\n",
    "print(lev_etf_option.get_greeks(calculator=calculator))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b6ba15aa",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

- **File**: `project_structure_documentation.md`
  - 📍 Path: `project_structure_documentation.md`

```python
```


## 🗂️ Layer: Tests
📂 Path: `tests`


## 🗂️ Layer: Core
📂 Path: `tests/core`


## 🗂️ Layer: Entities
📂 Path: `tests/core/entities`


## 🗂️ Layer: Asset
📂 Path: `tests/core/entities/asset`

- **File**: `test_crypto_asset.py`
  - 📍 Path: `tests/core/entities/asset/test_crypto_asset.py`

```python
# tests/core/entities/test_crypto_asset.py

import pytest
from datetime import datetime
from core.entities.asset.crypto_asset import CryptoAsset
from core.entities.enum.enums import Market

@pytest.fixture
def crypto_asset():
    return CryptoAsset(
        name="Bitcoin",
        symbol="BTC",
        market=Market.GLOBAL,
        last_price=30000.0,
        close_price=29500.0,
        previous_price=29000.0,
        ask_price=30100.0,
        bid_price=29900.0
    )

def test_is_valid(crypto_asset):
    assert crypto_asset.is_valid() is True

def test_price_limit(crypto_asset):
    assert crypto_asset.get_price_limit() == 0.0  # کریپتو دامنه ندارد

def test_transaction_fee(crypto_asset):
    fee = crypto_asset.get_transaction_fee()
    assert fee >= 0.0

def test_spread(crypto_asset):
    assert crypto_asset.get_spread() == 30100.0 - 29900.0

def test_price_limit_breach_upper(crypto_asset):
    assert crypto_asset.has_price_limit_breach(35000.0) is False

def test_price_limit_breach_lower(crypto_asset):
    assert crypto_asset.has_price_limit_breach(25000.0) is False

def test_is_trading_now(crypto_asset):
    assert crypto_asset.is_trading_now(datetime(2025, 1, 1, 4, 0)) is True  # ساعت ۴ صبح
    assert crypto_asset.is_trading_now(datetime(2025, 1, 1, 22, 0)) is True  # ساعت ۲۲ شب
```

- **File**: `test_etf_asset.py`
  - 📍 Path: `tests/core/entities/asset/test_etf_asset.py`

```python
import pytest
from core.entities.enum.enums import AssetClass, Market
from core.entities.asset.etf_asset import ETFAsset
from core.config.market_rules import MARKET_PRICE_LIMITS
from core.config.asset_rules import ASSET_TRANSACTION_FEES


def test_etf_asset_basic_behavior():
    asset = ETFAsset(
        name="دارا یکم",
        symbol="دارا",
        isin="IR00DARAYK01",
        market=Market.TSE_FIRST,
        last_price=12300,
        close_price=12200,
        previous_price=12000,
        ask_price=12400,
        bid_price=12100
    )

    assert asset.asset_class == AssetClass.ETF
    assert asset.symbol == "دارا"
    assert asset.get_transaction_fee() == ASSET_TRANSACTION_FEES[AssetClass.ETF]
    assert asset.get_price_limit() == MARKET_PRICE_LIMITS[Market.TSE_FIRST]
    assert asset.get_spread() == 300


def test_etf_asset_validity():
    asset = ETFAsset(
        name="دارا یکم",
        symbol="دارا",
        isin="IR00DARAYK01",
        market=Market.TSE_FIRST,
        last_price=12300,
        close_price=12200,
        previous_price=12000
    )

    assert asset.is_valid() is True
```

- **File**: `test_leverage_etf_asset.py`
  - 📍 Path: `tests/core/entities/asset/test_leverage_etf_asset.py`

```python
# test_leverage_etf_asset.py
import pytest
from core.entities.asset.leverage_etf_asset import LeverageETFAsset
from core.entities.enum.enums import AssetClass, Market

@pytest.fixture
def leverage_etf_asset():
    return LeverageETFAsset(
        name="Leveraged Fund X",
        symbol="LEFX",
        isin="IR1234567890",
        market=Market.TSE_SECOND,  # بازار فرعی بورس
        last_price=10800.0,
        close_price=11000.0,
        previous_price=11200.0,
        ask_price=10900.0,
        bid_price=10750.0
    )

def test_basic_properties(leverage_etf_asset):
    assert leverage_etf_asset.asset_class == AssetClass.LEVERAGE_ETF
    assert leverage_etf_asset.symbol == "LEFX"
    assert leverage_etf_asset.market.name.startswith("TSE")

def test_transaction_fee(leverage_etf_asset):
    fee = leverage_etf_asset.get_transaction_fee()
    assert isinstance(fee, float)
    assert fee > 0

def test_settlement_days(leverage_etf_asset):
    assert leverage_etf_asset.settlement_days == 2  # از روی config گرفته می‌شود

def test_trading_hours(leverage_etf_asset):
    start, end = leverage_etf_asset.trading_hours
    assert start < end

def test_price_limit(leverage_etf_asset):
    limit = leverage_etf_asset.get_price_limit()
    assert limit > 0

def test_price_limit_breach_upper(leverage_etf_asset):
    # بررسی عبور از سقف مجاز
    current_price = 13000.0
    assert leverage_etf_asset.has_price_limit_breach(current_price) is True

def test_price_limit_breach_lower(leverage_etf_asset):
    # بررسی عبور از کف مجاز
    current_price = 8000.0
    assert leverage_etf_asset.has_price_limit_breach(current_price) is True

def test_spread(leverage_etf_asset):
    spread = leverage_etf_asset.get_spread()
    assert spread == 10900.0 - 10750.0
```

- **File**: `test_stock_asset.py`
  - 📍 Path: `tests/core/entities/asset/test_stock_asset.py`

```python
import pytest
from core.entities.enum.enums import AssetClass, Market
from core.entities.asset.stock_asset import StockAsset
from core.config.market_rules import MARKET_PRICE_LIMITS
from core.config.asset_rules import ASSET_TRANSACTION_FEES


def test_stock_asset_properties():
    asset = StockAsset(
        name="فولاد مبارکه",
        symbol="فولاد",
        isin="IRO1FOLD0001",
        market=Market.TSE_FIRST,
        last_price=5000,
        close_price=5100,
        previous_price=4950,
        ask_price=5150,
        bid_price=5050
    )

    assert asset.asset_class == AssetClass.STOCK
    assert asset.symbol == "فولاد"
    assert asset.isin == "IRO1FOLD0001"
    assert asset.get_transaction_fee() == ASSET_TRANSACTION_FEES[AssetClass.STOCK]
    assert asset.get_price_limit() == MARKET_PRICE_LIMITS[Market.TSE_FIRST]
    assert asset.get_spread() == 100


def test_stock_asset_trading_status():
    asset = StockAsset(
        name="فولاد مبارکه",
        symbol="فولاد",
        isin="IRO1FOLD0001",
        market=Market.TSE_FIRST,
        last_price=5000,
        close_price=5100,
        previous_price=4950
    )
    assert asset.is_valid() is True
```


## 🗂️ Layer: Option
📂 Path: `tests/core/entities/option`

- **File**: `test_etf_option.py`
  - 📍 Path: `tests/core/entities/option/test_etf_option.py`

```python
# tests/core/entities/option/test_etf_option.py

import pytest
from datetime import datetime, timedelta

from core.entities.asset.etf_asset import ETFAsset
from core.entities.option.etf_option import ETFOption
from core.entities.enum.enums import OptionType, Market, ContractStatus
from core.entities.asset.asset import AbstractAsset


# --------------------
# Fixtures
# --------------------

@pytest.fixture
def etf_asset():
    return ETFAsset(
        name="ETF نمونه",
        symbol="ETF1",
        isin="IR1234567890",
        market=Market.IFB_FIRST,
        last_price=11000.0,  # spot price
        close_price=10800.0,
        previous_price=10700.0,
        ask_price=11050.0,
        bid_price=10950.0
    )


@pytest.fixture
def etf_option(etf_asset):
    return ETFOption(
        contract_name="ETF_CALL_10500",
        option_type=OptionType.CALL,
        strike_price=10500.0,
        premium=200.0,
        expiry=datetime.utcnow() + timedelta(days=10),
        underlying_asset=etf_asset,
        ask=210.0,
        bid=190.0,
        contract_size=1000,
        transaction_fee=0.5,  # 0.5 درصد
        settlement_cost=1.0,  # 1 درصد
        benchmark_index="S&P 500"
    )


# --------------------
# Tests
# --------------------

def test_underlying_is_etf(etf_option):
    assert isinstance(etf_option.underlying_asset, AbstractAsset)
    assert isinstance(etf_option.underlying_asset, ETFAsset)

def test_valid_option(etf_option):
    assert etf_option.is_valid() is True

def test_time_to_expiry(etf_option):
    assert 9 <= etf_option.time_to_expiry_days <= 10

def test_contract_status(etf_option):
    assert etf_option.contract_status == ContractStatus.IN_THE_MONEY

def test_break_even_price(etf_option):
    # strike = 10500
    # premium = 200
    # fee = 0.5% * 10500 = 52.5
    # settle = 1% * 10500 = 105.0
    # total = 200 + 52.5 + 105 = 357.5
    expected = 10500 + 357.5
    assert etf_option.get_break_even_price() == pytest.approx(expected, 0.1)

def test_payoff_itm(etf_option):
    # spot = 11000 → raw = 500/unit
    # total cost/unit = 200 + (0.5% * 11000) + (1% * 11000) = 200 + 55 + 110 = 365
    # payoff = (500 - 365) * 1000 = 135000
    expected = (500 - 365) * 1000
    assert etf_option.get_payoff(spot_price=11000) == pytest.approx(expected, 1)

def test_payoff_otm(etf_option):
    # spot = 10000 → raw = 0
    # cost = 200 + (0.5% * 10000) + (1% * 10000) = 200 + 50 + 100 = 350
    # payoff = -350 * 1000 = -350000
    expected = -350000
    assert etf_option.get_payoff(spot_price=10000) == pytest.approx(expected, 1)

def test_is_liquid(etf_option):
    # spread = 11050 - 10950 = 100 → 100 / 11000 = 0.009 → < 2%
    assert etf_option.is_liquid() is True

def test_nav_deviation_check(etf_option):
    nav_price = 10600  # spot = 11000 → deviation = ~3.77%
    assert etf_option.has_nav_deviation(nav_price) is True
    assert etf_option.nav_deviation > 0.03
```

- **File**: `test_leverage_etf_option.py`
  - 📍 Path: `tests/core/entities/option/test_leverage_etf_option.py`

```python
import pytest
from datetime import datetime, timedelta

from core.entities.asset.leverage_etf_asset import LeverageETFAsset
from core.entities.option.leverage_etf_option import LeverageETFOption
from core.entities.enum.enums import OptionType, Market, ContractStatus
from core.entities.asset.asset import AbstractAsset


# --------------------
# Fixtures
# --------------------

@pytest.fixture
def leverage_etf_asset():
    return LeverageETFAsset(
        name="LETF نمونه",
        symbol="LETF1",
        isin="IRLEVERAGE1234",
        market=Market.IFB_SECOND,
        last_price=9000.0,
        close_price=8800.0,
        previous_price=8700.0,
        ask_price=9050.0,
        bid_price=8950.0,
        leverage_ratio=2.0
    )


@pytest.fixture
def leverage_etf_option(leverage_etf_asset):
    return LeverageETFOption(
        contract_name="LETF_CALL_8500",
        option_type=OptionType.CALL,
        strike_price=8500.0,
        premium=300.0,
        expiry=datetime.utcnow() + timedelta(days=15),
        underlying_asset=leverage_etf_asset,
        ask=310.0,
        bid=290.0,
        contract_size=1000,
        transaction_fee=0.5,  # درصد
        settlement_cost=1.0,  # درصد
        leverage_ratio=2.0
    )


# --------------------
# Tests
# --------------------

def test_underlying_type(leverage_etf_option):
    assert isinstance(leverage_etf_option.underlying_asset, AbstractAsset)
    assert isinstance(leverage_etf_option.underlying_asset, LeverageETFAsset)

def test_valid_option(leverage_etf_option):
    assert leverage_etf_option.is_valid() is True

def test_time_to_expiry(leverage_etf_option):
    assert 14 <= leverage_etf_option.time_to_expiry_days <= 15

def test_contract_status(leverage_etf_option):
    assert leverage_etf_option.contract_status == ContractStatus.IN_THE_MONEY

def test_break_even_price(leverage_etf_option):
    # strike = 8500
    # premium = 300
    # fee = 0.5% * 8500 = 42.5
    # settle = 1% * 8500 = 85.0
    expected = 8500 + 300 + 42.5 + 85.0  # = 8927.5
    assert leverage_etf_option.get_break_even_price() == pytest.approx(expected, 0.1)

def test_payoff_itm(leverage_etf_option):
    # spot = 9000 → raw = (9000 - 8500) * 2 = 1000/unit
    # cost = 300 + 0.5%*9000 + 1%*9000 = 300 + 45 + 90 = 435/unit
    # total = (1000 - 435) * 1000 = 565000
    expected = (1000 - 435) * 1000
    assert leverage_etf_option.get_payoff(spot_price=9000) == pytest.approx(expected, 1)

def test_payoff_otm(leverage_etf_option):
    # spot = 8000 → raw = 0
    # cost = 300 + 40 + 80 = 420
    expected = -420 * 1000
    assert leverage_etf_option.get_payoff(spot_price=8000) == pytest.approx(expected, 1)

def test_max_loss(leverage_etf_option):
    # spot = 9000 → total cost = 300 + 45 + 90 = 435 → max loss = 435 * 1000 = 435000
    assert leverage_etf_option.get_max_loss() == pytest.approx(435000, 1)

def test_max_gain(leverage_etf_option):
    # فرض: max_spot = 9500
    # raw = (9500 - 8500) * 2 = 2000 → total = 2,000,000 - max_loss
    expected = (2000 * 1000) - 435000
    assert leverage_etf_option.get_max_gain(max_spot=9500) == pytest.approx(expected, 1)
```

- **File**: `test_stock_option.py`
  - 📍 Path: `tests/core/entities/option/test_stock_option.py`

```python
import pytest
from datetime import datetime, timedelta

from core.entities.asset.stock_asset import StockAsset
from core.entities.option.stock_option import StockOption
from core.entities.enum.enums import OptionType, Market
from core.entities.asset.asset import AbstractAsset  # برای بررسی دقیق

# ---------------------
# Fixtures
# ---------------------

@pytest.fixture
def stock_asset():
    return StockAsset(
        name="فولاد مبارکه",
        symbol="فولاد",
        isin="IRO1FOLD0001",
        market=Market.TSE_FIRST,
        last_price=150.0,
        close_price=148.0,
        previous_price=147.0,
        ask_price=151.0,
        bid_price=149.0
    )

@pytest.fixture
def stock_option_call(stock_asset):
    return StockOption(
        contract_name="EXMPL_CALL_160",
        option_type=OptionType.CALL,
        strike_price=160.0,
        premium=5.0,
        expiry=datetime.utcnow() + timedelta(days=30),
        underlying_asset=stock_asset,
        ask=6.0,
        bid=4.0,
        contract_size=1000,
        transaction_fee=5.0,  # %
        settlement_cost=1.0  # ثابت
    )

@pytest.fixture
def expired_option(stock_asset):
    return StockOption(
        contract_name="EXPIRED_CALL",
        option_type=OptionType.CALL,
        strike_price=160.0,
        premium=5.0,
        expiry=datetime.utcnow() - timedelta(days=1),
        underlying_asset=stock_asset,
        contract_size=1000
    )

# ---------------------
# Tests
# ---------------------

def test_underlying_type(stock_option_call):
    assert isinstance(stock_option_call.underlying_asset, AbstractAsset)

def test_valid_option(stock_option_call):
    assert stock_option_call.is_valid() is True

def test_time_to_expiry(stock_option_call):
    assert 28 <= stock_option_call.time_to_expiry_days <= 31

def test_expired_status(expired_option, stock_option_call):
    assert stock_option_call.has_expired() is False
    assert expired_option.has_expired() is True

def test_break_even_price(stock_option_call):
    # strike = 160, premium = 5, fee = 0.8, settle = 1 → break_even = 166.8
    assert stock_option_call.get_break_even_price() == pytest.approx(166.8, 0.1)

def test_payoff_itm(stock_option_call):
    # spot = 170 → raw = 10/unit
    # fee = 8.5, settle = 1.7 → total cost = 15.2/unit
    expected = (10.0 - 15.2) * 1000  # = -5200
    assert stock_option_call.get_payoff(170.0) == pytest.approx(expected, 1)


def test_payoff_otm(stock_option_call):
    # spot = 150 → raw = 0
    # fee = 7.5, settle = 1.5 → total cost = 14.0/unit
    expected = -14.0 * 1000  # = -14000
    assert stock_option_call.get_payoff(150.0) == pytest.approx(expected, 1)


def test_contract_status(stock_option_call):
    # spot = 150 < strike = 160 → OTM
    assert stock_option_call.contract_status.name == "OUT_OF_THE_MONEY"
```

- **File**: `__init__.py`
  - 📍 Path: `tests/__init__.py`

```python
```


## 🗂️ Layer: Use Cases
📂 Path: `use_cases`

- **File**: `__init__.py`
  - 📍 Path: `use_cases/__init__.py`

```python
```

