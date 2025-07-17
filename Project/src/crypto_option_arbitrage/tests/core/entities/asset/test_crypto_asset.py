# tests/core/entities/test_crypto_asset.py

import pytest
from datetime import datetime
from core.entities.asset.crypto_asset import CryptoAsset
from core.entities.enum.enums import Market

@pytest.fixture
def crypto_asset():
    return CryptoAsset(
        name="Bitcoin",
        symbol="BTC",
        market=Market.GLOBAL,
        last_price=30000.0,
        close_price=29500.0,
        previous_price=29000.0,
        ask_price=30100.0,
        bid_price=29900.0
    )

def test_is_valid(crypto_asset):
    assert crypto_asset.is_valid() is True

def test_price_limit(crypto_asset):
    assert crypto_asset.get_price_limit() == 0.0  # کریپتو دامنه ندارد

def test_transaction_fee(crypto_asset):
    fee = crypto_asset.get_transaction_fee()
    assert fee >= 0.0

def test_spread(crypto_asset):
    assert crypto_asset.get_spread() == 30100.0 - 29900.0

def test_price_limit_breach_upper(crypto_asset):
    assert crypto_asset.has_price_limit_breach(35000.0) is False

def test_price_limit_breach_lower(crypto_asset):
    assert crypto_asset.has_price_limit_breach(25000.0) is False

def test_is_trading_now(crypto_asset):
    assert crypto_asset.is_trading_now(datetime(2025, 1, 1, 4, 0)) is True  # ساعت ۴ صبح
    assert crypto_asset.is_trading_now(datetime(2025, 1, 1, 22, 0)) is True  # ساعت ۲۲ شب
