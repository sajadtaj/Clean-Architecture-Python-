# core/entities/stock_asset.py

from core.entities.asset import AbstractAsset
from core.entities.enums import AssetClass, Market
from core.config.trading_rules import ASSET_SETTLEMENT_DAYS, ASSET_TRADING_HOURS


class StockAsset(AbstractAsset):
    def __init__(
        self,
        name: str,
        symbol: str,
        isin: str,
        market: Market,
        last_price: float,
        close_price: float,
        previous_price: float,
        ask_price: float = None,
        bid_price: float = None
    ):
        asset_class = AssetClass.STOCK
        settlement_days = ASSET_SETTLEMENT_DAYS[asset_class]
        trading_hours = ASSET_TRADING_HOURS[asset_class]

        super().__init__(
            name=name,
            symbol=symbol,
            isin=isin,
            asset_class=asset_class,
            market=market,
            last_price=last_price,
            close_price=close_price,
            previous_price=previous_price,
            settlement_days=settlement_days,
            trading_hours=trading_hours,
            ask_price=ask_price,
            bid_price=bid_price
        )
