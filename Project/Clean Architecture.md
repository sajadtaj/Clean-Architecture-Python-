<div dir='rtl'>

## ✅ جایگاه اجزای پروژه در معماری Clean Architecture

| نوع مؤلفه / کلاس                                                             | جایگاه                           | توضیح                                                                    |
| ---------------------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------ |
| 📦 **مدل‌های دامنه (مانند Option، Order، ArbitrageOpportunity)**             | `core/entities/`                 | فقط شامل داده و قوانین درونی، فاقد وابستگی به بیرون                      |
| 🔢 **اشیاء ارزش‌محور (Value Objects)** مانند `Price`, `Greeks`, `Volatility` | `core/value_objects/`            | اشیائی با مقایسه بر اساس مقدار، نه شناسه                                 |
| 🔍 **منطق کشف آربیتراژ، اجرای استراتژی‌ها، محاسبه سود و زیان**               | `use_cases/`                     | شامل سرویس‌های کاربردی، با استفاده از موجودیت‌ها                         |
| 🌐 **APIهای خارجی، FastAPI، CLI، Scheduler**                                 | `interfaces/`                    | دریافت ورودی از بیرون، ارتباط با use case از طریق adapter                |
| 📡 **ماژول‌های اتصال به اکسچنج‌ها (Deribit, Binance)**                       | `infrastructure/data_providers/` | ارتباط با APIها، وب‌سوکت‌ها، یا REST، بدون منطق تجاری                    |
| 🗃️ **پایگاه داده، ارتباط با PostgreSQL یا Redis**                           | `infrastructure/db/`             | شامل driverها، Repository Adapterها، Migration‌ها                        |
| 🔔 **سیستم اعلان‌ها (ایمیل، Slack، SMS)**                                    | `infrastructure/notifiers/`      | پیاده‌سازی ارسال هشدار بدون منطق دامنه‌ای                                |
| ⚙️ **تنظیمات، فایل‌های `.env`، بارگذاری کانفیگ‌ها**                          | `config/`                        | تنظیمات وابسته به محیط                                                   |
| 🧪 **تست‌های واحد، یکپارچه، و شبیه‌سازی (Mock)**                             | `tests/`                         | مطابق ساختار پروژه، هر فایل تست مطابق لایه هدف                           |
| 🚀 **نقطه شروع برنامه و اجرای کلی**                                          | `main.py`                        | اجرای اپلیکیشن، فراخوانی use case اصلی، وابسته به interface و زیرساخت‌ها |

---

## 📘 مثال از جایگاه کلاس‌ها و فایل‌ها

| نام کلاس یا فایل                      | قرار می‌گیرد در                                   |
| ------------------------------------- | ------------------------------------------------- |
| `Option`                              | `core/entities/option.py`                         |
| `Price`, `Greeks`                     | `core/value_objects/price.py`                     |
| `DetectArbitrageService`              | `use_cases/detect_arbitrage.py`                   |
| `arbitrage_router` (FastAPI endpoint) | `interfaces/api/arbitrage_router.py`              |
| `deribit_client.py`                   | `infrastructure/data_providers/deribit_client.py` |
| `postgres_repository.py`              | `infrastructure/db/postgres_repository.py`        |
| `slack_notifier.py`                   | `infrastructure/notifiers/slack_notifier.py`      |
| `settings.py`                         | `config/settings.py`                              |
| `test_arbitrage_detection.py`         | `tests/use_cases/test_arbitrage_detection.py`     |
| `main.py`                             | `main.py` در ریشه پروژه                           |

---

این تقسیم‌بندی به‌شکلی طراحی شده که **وابستگی‌ها همیشه از بیرون به درون باشند (outside → inside)** و منطق دامنه‌ای (مثل موجودیت Option یا آربیتراژ) هرگز وابسته به تکنولوژی یا ابزار خاصی نباشد.

