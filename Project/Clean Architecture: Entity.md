<div dir='rtl'>

# 🧾 مستند معماری لایه Entity

### پروژه: کشف فرصت آربیتراژ در آپشن دارایی‌ها (سهام، صندوق‌ها، کریپتو و ...)

---

## 🎯 هدف لایه Entity

لایه `entity` مسئول مدل‌سازی **موجودیت‌های دامنه اصلی مالی** (دارایی‌ها، آپشن‌ها، استراتژی‌ها) به شکل انتزاعی و مستقل از تکنولوژی است. این لایه:

* وابسته به هیچ دیتابیس، API، فایل یا سرویس خارجی نیست (pure domain logic)
* هسته تحلیلی پروژه را در خود جای داده است
* پایه‌گذار اصول Domain-Driven Design (DDD) است

---

## 🏗️ ساختار لایه `entity`

</div>

```
core/
└── entities/
    ├── asset.py                 ← کلاس پایه AbstractAsset
    ├── stock_asset.py          ← دارایی سهام
    ├── etf_asset.py            ← صندوق قابل معامله
    ├── leverage_etf_asset.py   ← صندوق اهرمی
    ├── crypto_asset.py         ← دارایی کریپتو
    ├── option.py               ← کلاس پایه AbstractOption
    └── enums.py                ← انواع (Enums) مثل OptionType, AssetClass, Market
```
<div dir='rtl'>

---

## 🧩 کلاس‌ها و وابستگی‌ها

### ✅ `AbstractAsset`

مدل انتزاعی همه دارایی‌ها، شامل:

* ویژگی‌های عمومی مثل `symbol`, `price`, `market`, `ask`, `bid`
* منطق‌های دامنه مثل:

  * `is_valid()`
  * `get_transaction_fee()`
  * `has_price_limit_breach()`
  * `is_trading_now()`

📌 وابستگی به `AssetClass`, `Market`, `config` برای قوانین بازار و دارایی.

---

### ✅ کلاس‌های فرزند:

| کلاس               | ارث‌بری از      | توضیحات                    |
| ------------------ | --------------- | -------------------------- |
| `StockAsset`       | `AbstractAsset` | سهام بورسی                 |
| `ETFAsset`         | `AbstractAsset` | صندوق‌های قابل معامله      |
| `LeverageETFAsset` | `AbstractAsset` | صندوق‌های اهرمی بورسی      |
| `CryptoAsset`      | `AbstractAsset` | رمزارزها با بازار ۲۴ ساعته |

📌 هر کلاس اطلاعاتی مثل `settlement_days`, `trading_hours`, `fee` را از فایل‌های کانفیگ مثل `ASSET_TRADING_HOURS` می‌گیرد، **نه hardcode**.

---

### ✅ `AbstractOption`

مدل انتزاعی یک قرارداد اختیار معامله با متدهای تحلیلی:

* `is_in_the_money()`
* `get_payoff()`
* `get_break_even_price()`
* `has_expired()`

📌 به هیچ API یا دیتابیس وابسته نیست. فقط منطق مالی خالص دارد.

---

## 🧠 چرا کلاس‌های دارایی مستقل داریم؟

سؤالات مهم:

> چرا `StockAsset`, `CryptoAsset` و ... جدا تعریف شدند؟ چرا فقط از `AbstractAsset` استفاده نشد؟

### ✅ پاسخ مفصل و حرفه‌ای:

| اصل                  | دلیل                                                                                                                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **OCP**              | هر کلاس در آینده رفتار خاصی خواهد داشت. مثلاً `CryptoAsset.get_transaction_fee()` می‌تواند به API متصل شود، ولی `StockAsset` به مقدار ثابت. این قابلیت بدون تغییر کلاس والد انجام می‌شود. |
| **LSP**              | هر کلاس می‌تواند جایگزین کلاس والد شود، بدون اینکه منطق آن شکسته شود.                                                                                                                     |
| **ISP**              | اگر ETF نیاز به محاسبه NAV داشته باشد، به راحتی در `ETFAsset` اضافه می‌شود بدون اینکه `StockAsset` آلوده شود.                                                                             |
| **DDD**              | هر نوع دارایی یک *مفهوم دامنه* متفاوت است (Bounded Context). پس مدل جداگانه می‌خواهد.                                                                                                     |
| **پرهیز از if-else** | به‌جای بررسی نوع دارایی در هر تابع با `if asset_class == ...`، رفتار از طریق کلاس مجزا تعیین می‌شود.                                                                                      |

---

## 🧾 متدهای کلیدی

| متد                        | در کدام کلاس     | توضیح                               |
| -------------------------- | ---------------- | ----------------------------------- |
| `is_valid()`               | `AbstractAsset`  | بررسی اعتبار دارایی بر اساس قیمت‌ها |
| `get_price_limit()`        | `AbstractAsset`  | دامنه نوسان از فایل کانفیگ          |
| `get_transaction_fee()`    | `AbstractAsset`  | درصد کارمزد از کانفیگ               |
| `is_trading_now()`         | `AbstractAsset`  | بررسی فعال بودن بازار               |
| `has_price_limit_breach()` | `AbstractAsset`  | بررسی عبور از دامنه نوسان           |
| `get_spread()`             | `AbstractAsset`  | اختلاف ask و bid                    |
| `has_expired()`            | `AbstractOption` | انقضای قرارداد آپشن                 |
| `get_payoff()`             | `AbstractOption` | محاسبه سود یا زیان آپشن             |

---

## 📚 Enumها

```python
class AssetClass(Enum):
    STOCK = "stock"
    ETF = "etf"
    LEVERAGE_ETF = "leverage_etf"
    CRYPTO = "crypto"
    ...

class Market(Enum):
    TSE_FIRST = ...
    IFB_SECOND = ...
    COMMODITY = ...
    ENERGY = ...
    BASE_YELLOW = ...
    ...

class OptionType(Enum):
    CALL = "call"
    PUT = "put"
```

---

## 🧾 منابع اطلاعاتی (config)

### 📁 `core/config/asset_rules.py`

```python
ASSET_TRANSACTION_FEES = {
    AssetClass.STOCK: 1.5,
    AssetClass.CRYPTO: 0.3,
    ...
}
```

### 📁 `core/config/trading_rules.py`

```python
ASSET_TRADING_HOURS = {
    AssetClass.STOCK: ("09:00", "12:30"),
    AssetClass.CRYPTO: ("00:00", "23:59"),
    ...
}

ASSET_SETTLEMENT_DAYS = {
    AssetClass.STOCK: 2,
    AssetClass.CRYPTO: 0,
    ...
}
```

### 📁 `core/config/market_rules.py`

```python
MARKET_PRICE_LIMITS = {
    Market.TSE_FIRST: 5.0,
    Market.BASE_YELLOW: 3.0,
    ...
}
```

---

## ✅ نتیجه‌گیری

* لایه `entity` قلب دامنه پروژه است.
* تمام رفتارها و ساختارها با اصول معماری تمیز طراحی شده‌اند.
* از هرگونه hardcode، وابستگی به تکنولوژی یا API اجتناب شده است.
* طراحی برای توسعه آینده (مثلاً اضافه شدن کالای فیزیکی، energy asset و...) آماده است.
