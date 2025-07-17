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
