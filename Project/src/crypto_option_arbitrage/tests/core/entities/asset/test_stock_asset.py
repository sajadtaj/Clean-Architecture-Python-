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
