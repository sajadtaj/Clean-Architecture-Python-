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
