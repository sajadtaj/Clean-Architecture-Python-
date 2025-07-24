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
