# tests/core/entities/option/test_etf_option.py

import pytest
from datetime import datetime, timedelta

from core.entities.asset.etf_asset import ETFAsset
from core.entities.option.etf_option import ETFOption
from core.entities.enum.enums import OptionType, Market, ContractStatus
from core.entities.asset.asset import AbstractAsset


# --------------------
# Fixtures
# --------------------

@pytest.fixture
def etf_asset():
    return ETFAsset(
        name="ETF نمونه",
        symbol="ETF1",
        isin="IR1234567890",
        market=Market.IFB_FIRST,
        last_price=11000.0,  # spot price
        close_price=10800.0,
        previous_price=10700.0,
        ask_price=11050.0,
        bid_price=10950.0
    )


@pytest.fixture
def etf_option(etf_asset):
    return ETFOption(
        contract_name="ETF_CALL_10500",
        option_type=OptionType.CALL,
        strike_price=10500.0,
        premium=200.0,
        expiry=datetime.utcnow() + timedelta(days=10),
        underlying_asset=etf_asset,
        ask=210.0,
        bid=190.0,
        contract_size=1000,
        transaction_fee=0.5,  # 0.5 درصد
        settlement_cost=1.0,  # 1 درصد
        benchmark_index="S&P 500"
    )


# --------------------
# Tests
# --------------------

def test_underlying_is_etf(etf_option):
    assert isinstance(etf_option.underlying_asset, AbstractAsset)
    assert isinstance(etf_option.underlying_asset, ETFAsset)

def test_valid_option(etf_option):
    assert etf_option.is_valid() is True

def test_time_to_expiry(etf_option):
    assert 9 <= etf_option.time_to_expiry_days <= 10

def test_contract_status(etf_option):
    assert etf_option.contract_status == ContractStatus.IN_THE_MONEY

def test_break_even_price(etf_option):
    # strike = 10500
    # premium = 200
    # fee = 0.5% * 10500 = 52.5
    # settle = 1% * 10500 = 105.0
    # total = 200 + 52.5 + 105 = 357.5
    expected = 10500 + 357.5
    assert etf_option.get_break_even_price() == pytest.approx(expected, 0.1)

def test_payoff_itm(etf_option):
    # spot = 11000 → raw = 500/unit
    # total cost/unit = 200 + (0.5% * 11000) + (1% * 11000) = 200 + 55 + 110 = 365
    # payoff = (500 - 365) * 1000 = 135000
    expected = (500 - 365) * 1000
    assert etf_option.get_payoff(spot_price=11000) == pytest.approx(expected, 1)

def test_payoff_otm(etf_option):
    # spot = 10000 → raw = 0
    # cost = 200 + (0.5% * 10000) + (1% * 10000) = 200 + 50 + 100 = 350
    # payoff = -350 * 1000 = -350000
    expected = -350000
    assert etf_option.get_payoff(spot_price=10000) == pytest.approx(expected, 1)

def test_is_liquid(etf_option):
    # spread = 11050 - 10950 = 100 → 100 / 11000 = 0.009 → < 2%
    assert etf_option.is_liquid() is True

def test_nav_deviation_check(etf_option):
    nav_price = 10600  # spot = 11000 → deviation = ~3.77%
    assert etf_option.has_nav_deviation(nav_price) is True
    assert etf_option.nav_deviation > 0.03
