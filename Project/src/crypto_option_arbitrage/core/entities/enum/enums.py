# core/entities/enums.py

from enum import Enum


class AssetClass(str, Enum):
    STOCK = "Stock"
    ETF = "ETF"
    LEVERAGE_ETF = "Leveraged ETF"
    CRYPTO = "Crypto"
    COMMODITY = "Commodity"


class Market(str, Enum):
    #
    # بورس اوراق بهادار تهران (TSE)
    #
    TSE_FIRST = "بورس - بازار اول"
    TSE_SECOND = "بورس - بازار دوم"
    #
    # فرابورس ایران (IFB)
    #
    IFB_FIRST = "فرابورس - بازار اول"
    IFB_SECOND = "فرابورس - بازار دوم"
    IFB_THIRD = "فرابورس - بازار سوم"
    IFB_INNOVATION = "فرابورس - ابزارهای نوین مالی"

    #
    # بازار پایه فرابورس
    #

    IFB_BASE_YELLOW = "بازار پایه - زرد"
    IFB_BASE_ORANGE = "بازار پایه - نارنجی"
    IFB_BASE_RED = "بازار پایه - قرمز"

    #
    # سایر بازارهای رسمی ایران
    #

    ENERGY = "بورس انرژی"
    COMMODITY = "بورس کالا"
    
    #
    # بازار جهانی
    #
    
    GLOBAL = "بازار جهانی (کریپتو / خارجی)"
    
class ContractStatus(str, Enum):
    IN_THE_MONEY = "In the money"
    OUT_OF_THE_MONEY = "Out of the money"
    AT_THE_MONEY = "At the money"
    
class OptionType(Enum):
    CALL = "Call"
    PUT = "Put"