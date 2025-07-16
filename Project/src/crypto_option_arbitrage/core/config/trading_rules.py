from core.entities.enums import AssetClass

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
