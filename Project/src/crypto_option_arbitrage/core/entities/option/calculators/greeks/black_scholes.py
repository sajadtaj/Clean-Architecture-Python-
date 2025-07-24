from math import exp, log, sqrt
from scipy.stats import norm
from core.entities.enum.enums import OptionType
from core.entities.option.value_objects.greeks import OptionGreeks
from core.entities.option.calculators.greeks.base import BaseGreekCalculator

class BlackScholesGreekCalculator(BaseGreekCalculator):
    def calculate(self, option_type, spot, strike, time_to_expiry, risk_free_rate, volatility) -> OptionGreeks:
        d1 = (log(spot / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (volatility * sqrt(time_to_expiry))
        d2 = d1 - volatility * sqrt(time_to_expiry)

        if option_type == OptionType.CALL:
            delta = norm.cdf(d1)
            theta = (-spot * norm.pdf(d1) * volatility / (2 * sqrt(time_to_expiry))
                     - risk_free_rate * strike * exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
            rho = strike * time_to_expiry * exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
        else:
            delta = -norm.cdf(-d1)
            theta = (-spot * norm.pdf(d1) * volatility / (2 * sqrt(time_to_expiry))
                     + risk_free_rate * strike * exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2))
            rho = -strike * time_to_expiry * exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)

        gamma = norm.pdf(d1) / (spot * volatility * sqrt(time_to_expiry))
        vega = spot * norm.pdf(d1) * sqrt(time_to_expiry)

        return OptionGreeks(
            delta=delta,
            gamma=gamma,
            theta=theta / 365,  # تبدیل به روز
            vega=vega / 100,
            rho=rho / 100
        )
