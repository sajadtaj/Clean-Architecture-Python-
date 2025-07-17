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
        bid_price: float = None
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
    # بورس اوراق بهادار تهران (TSE)
    TSE_FIRST = "بورس - بازار اول"
    TSE_SECOND = "بورس - بازار دوم"

    # فرابورس ایران (IFB)
    IFB_FIRST = "فرابورس - بازار اول"
    IFB_SECOND = "فرابورس - بازار دوم"
    IFB_THIRD = "فرابورس - بازار سوم"
    IFB_INNOVATION = "فرابورس - ابزارهای نوین مالی"

    # بازار پایه فرابورس
    IFB_BASE_YELLOW = "بازار پایه - زرد"
    IFB_BASE_ORANGE = "بازار پایه - نارنجی"
    IFB_BASE_RED = "بازار پایه - قرمز"

    # سایر بازارهای رسمی ایران
    ENERGY = "بورس انرژی"
    COMMODITY = "بورس کالا"

    # بازار جهانی
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

- **File**: `__init__.py`
  - 📍 Path: `core/entities/option/__init__.py`

```python
```

- **File**: `option.py`
  - 📍 Path: `core/entities/option/option.py`

```python
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
   "execution_count": 2,
   "id": "6f69984b",
   "metadata": {},
   "outputs": [],
   "source": [
    "from core.entities.asset.stock_asset import StockAsset\n",
    "from core.entities.enum.enums import Market\n",
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
    "os.chdir('/home/sajad/All Project/Clean Architecture Python/Project/src/crypto_option_arbitrage')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "06ea2588",
   "metadata": {},
   "outputs": [],
   "source": [
    "from datetime import datetime, timedelta\n",
    "\n",
    "from core.entities.asset.stock_asset import StockAsset\n",
    "from core.entities.enum.enums import Market, OptionType, ContractStatus\n",
    "from core.entities.option.stock_option import StockOption"
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
   "execution_count": 4,
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
   "execution_count": 5,
   "id": "9c9c8fab",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Cell 4: ساخت آپشن کال\n",
    "call_option = StockOption(\n",
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
   "execution_count": 6,
   "id": "85da6bf4",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Spot Price: 1100\n",
      "Time to Expiry: 9\n",
      "Break Even: 1053.0\n",
      "Payoff: 97000.0\n",
      "Contract Status: ContractStatus.IN_THE_MONEY\n"
     ]
    }
   ],
   "source": [
    "# Cell 5: بررسی عملکردها\n",
    "print(\"Spot Price:\", call_option.spot_price)\n",
    "print(\"Time to Expiry:\", call_option.time_to_expiry_days)\n",
    "print(\"Break Even:\", call_option.get_break_even_price())\n",
    "print(\"Payoff:\", call_option.get_payoff(spot_price=1150))\n",
    "print(\"Contract Status:\", call_option.contract_status)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "45cd3a53",
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

- **File**: `test_stock_option.py`
  - 📍 Path: `tests/core/entities/option/test_stock_option.py`

```python
import pytest
from datetime import datetime, timedelta

from core.entities.asset.stock_asset import StockAsset
from core.entities.option.stock_option import StockOption
from core.entities.enum.enums import OptionType, Market, AssetClass, ContractStatus


@pytest.fixture
def stock_asset():
    return StockAsset(
        name="ExampleStock",
        symbol="EXMPL",
        isin="IR1234567890",
        market=Market.TSE_SECOND,
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
        transaction_fee=0.5,
        settlement_cost=1.0
    )


def test_valid_option(stock_option_call):
    assert stock_option_call.is_valid() is True


def test_time_to_expiry(stock_option_call):
    assert stock_option_call.time_to_expiry_days == 30


def test_spot_price(stock_option_call):
    assert stock_option_call.spot_price == 150.0


def test_contract_status(stock_option_call):
    # Since spot = 150 < strike = 160 → CALL is out-of-the-money
    assert stock_option_call.contract_status == ContractStatus.OUT_OF_THE_MONEY


def test_expired_status(stock_option_call):
    future_date = datetime.utcnow() + timedelta(days=1)
    assert stock_option_call.has_expired(now=future_date) is False

    past_date = datetime.utcnow() - timedelta(days=1)
    assert stock_option_call.has_expired(now=past_date) is True


def test_break_even_price(stock_option_call):
    # For CALL: break_even = strike_price + premium
    assert stock_option_call.get_break_even_price() == 165.0


def test_payoff_itm(stock_option_call):
    # spot = 170 > strike = 160 → CALL payoff = 10
    assert stock_option_call.get_payoff(170.0) == 10.0


def test_payoff_otm(stock_option_call):
    # spot = 150 < strike = 160 → CALL payoff = 0
    assert stock_option_call.get_payoff(150.0) == 0.0


def test_contract_size_default(stock_option_call):
    assert stock_option_call.contract_size == 1000
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

