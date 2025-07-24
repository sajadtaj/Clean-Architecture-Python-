from dataclasses import dataclass

@dataclass(frozen=True)
class OptionGreeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

    def __str__(self):
        return f"Δ: {self.delta:.4f}, Γ: {self.gamma:.4f}, Θ: {self.theta:.4f}, 𝜈: {self.vega:.4f}, ρ: {self.rho:.4f}"
