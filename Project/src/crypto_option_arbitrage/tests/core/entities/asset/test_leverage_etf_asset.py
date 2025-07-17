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
