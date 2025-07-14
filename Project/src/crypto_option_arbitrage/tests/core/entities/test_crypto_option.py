import pytest
from datetime import datetime, timedelta
from crypto_option_arbitrage.core.entities.crypto_option import CryptoOption
from crypto_option_arbitrage.core.entities.option import OptionType


@pytest.fixture
def sample_call_option():
    return CryptoOption(
        contract_name="BTC-20JUL25-30000-C",
        option_type=OptionType.CALL,
        strike_price=30000,
        expiry=datetime.utcnow() + timedelta(days=3),
        premium=500,
        underlying_symbol="BTC"
    )


def test_is_in_the_money(sample_call_option):
    assert sample_call_option.is_in_the_money(spot_price=32500) is True
    assert sample_call_option.is_in_the_money(spot_price=29000) is False


def test_get_payoff(sample_call_option):
    assert sample_call_option.get_payoff(spot_price=32500) == 2500
    assert sample_call_option.get_payoff(spot_price=29500) == 0


def test_get_break_even_price(sample_call_option):
    assert sample_call_option.get_break_even_price() == 30500


def test_expiry_check(sample_call_option):
    assert sample_call_option.has_expired(reference_time=datetime.utcnow()) is False


def test_validity(sample_call_option):
    assert sample_call_option.is_valid() is True
