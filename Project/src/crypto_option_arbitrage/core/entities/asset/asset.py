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
