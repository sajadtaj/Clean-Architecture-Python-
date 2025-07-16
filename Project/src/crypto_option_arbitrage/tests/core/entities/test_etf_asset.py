import pytest
from core.entities.enums import AssetClass, Market
from core.entities.etf_asset import ETFAsset
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
