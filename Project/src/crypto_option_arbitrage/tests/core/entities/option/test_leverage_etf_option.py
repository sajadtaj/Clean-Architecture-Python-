import pytest
from datetime import datetime, timedelta

from core.entities.asset.leverage_etf_asset import LeverageETFAsset
from core.entities.option.leverage_etf_option import LeverageETFOption
from core.entities.enum.enums import OptionType, Market, ContractStatus
from core.entities.asset.asset import AbstractAsset


# --------------------
# Fixtures
# --------------------

@pytest.fixture
def leverage_etf_asset():
    return LeverageETFAsset(
        name="LETF نمونه",
        symbol="LETF1",
        isin="IRLEVERAGE1234",
        market=Market.IFB_SECOND,
        last_price=9000.0,
        close_price=8800.0,
        previous_price=8700.0,
        ask_price=9050.0,
        bid_price=8950.0,
        leverage_ratio=2.0
    )


@pytest.fixture
def leverage_etf_option(leverage_etf_asset):
    return LeverageETFOption(
        contract_name="LETF_CALL_8500",
        option_type=OptionType.CALL,
        strike_price=8500.0,
        premium=300.0,
        expiry=datetime.utcnow() + timedelta(days=15),
        underlying_asset=leverage_etf_asset,
        ask=310.0,
        bid=290.0,
        contract_size=1000,
        transaction_fee=0.5,  # درصد
        settlement_cost=1.0,  # درصد
        leverage_ratio=2.0
    )


# --------------------
# Tests
# --------------------

def test_underlying_type(leverage_etf_option):
    assert isinstance(leverage_etf_option.underlying_asset, AbstractAsset)
    assert isinstance(leverage_etf_option.underlying_asset, LeverageETFAsset)

def test_valid_option(leverage_etf_option):
    assert leverage_etf_option.is_valid() is True

def test_time_to_expiry(leverage_etf_option):
    assert 14 <= leverage_etf_option.time_to_expiry_days <= 15

def test_contract_status(leverage_etf_option):
    assert leverage_etf_option.contract_status == ContractStatus.IN_THE_MONEY

def test_break_even_price(leverage_etf_option):
    # strike = 8500
    # premium = 300
    # fee = 0.5% * 8500 = 42.5
    # settle = 1% * 8500 = 85.0
    expected = 8500 + 300 + 42.5 + 85.0  # = 8927.5
    assert leverage_etf_option.get_break_even_price() == pytest.approx(expected, 0.1)

def test_payoff_itm(leverage_etf_option):
    # spot = 9000 → raw = (9000 - 8500) * 2 = 1000/unit
    # cost = 300 + 0.5%*9000 + 1%*9000 = 300 + 45 + 90 = 435/unit
    # total = (1000 - 435) * 1000 = 565000
    expected = (1000 - 435) * 1000
    assert leverage_etf_option.get_payoff(spot_price=9000) == pytest.approx(expected, 1)

def test_payoff_otm(leverage_etf_option):
    # spot = 8000 → raw = 0
    # cost = 300 + 40 + 80 = 420
    expected = -420 * 1000
    assert leverage_etf_option.get_payoff(spot_price=8000) == pytest.approx(expected, 1)

def test_max_loss(leverage_etf_option):
    # spot = 9000 → total cost = 300 + 45 + 90 = 435 → max loss = 435 * 1000 = 435000
    assert leverage_etf_option.get_max_loss() == pytest.approx(435000, 1)

def test_max_gain(leverage_etf_option):
    # فرض: max_spot = 9500
    # raw = (9500 - 8500) * 2 = 2000 → total = 2,000,000 - max_loss
    expected = (2000 * 1000) - 435000
    assert leverage_etf_option.get_max_gain(max_spot=9500) == pytest.approx(expected, 1)
