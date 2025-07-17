from core.entities.enum.enums import AssetClass

# کارمزد معاملات به درصد
ASSET_TRANSACTION_FEES = {
    AssetClass.STOCK: 1.5,
    AssetClass.ETF: 0.5,
    AssetClass.LEVERAGE_ETF: 1.0,
    AssetClass.CRYPTO: 0.2,
    AssetClass.COMMODITY: 0.8,
}
