# Definitions:
S_0 : Underlying price
K : Strike Price
r : risk-free rate
T : Time to maturity (Year)
C : Call Price C_1, C_2
P : Put Price P_1, P_2

## Formular: Formular should be Tru, or arbitrage opportunity exist.
# Single Option
* Call: max{S_0 - Ke^(-rT), 0} < C_1 < S_0
* Put: max{Ke^(-rT) - S_0, 0} < P_1 < Ke^(-rT)

# Two Options: Strike Spread
* Call: (K_1 - K_2) * e^(-r * (T_2 - T_1)) < C_2 - C_1 < 0
* Put: (K_1 - K_2) * e^(-r * (T_2 - T_1)) < P_1 - P_2 < 0

# Two Options: Calendar Spread
* Call: C_2 - C_1 > (K_1 - K_2) * e^(-r * (T_2 - T_1))
* Put: P_1 - P_2 > (K_1 - K_2) * e^(-r * (T_2 - T_1))

# Three Options: Butterfly Spread
* Call: C_1 - 2C_2 + C_3 > 0
* Put: P_1 - 2P_2 + P_3 > 0