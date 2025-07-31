import numpy as np
import matplotlib.pyplot as plt

# Parameters
num_buyers = 100
num_sellers = 100
num_steps = 50

# Initialize agents
buyers = np.random.uniform(80, 120, size=num_buyers)  # Willingness to pay
sellers = np.random.uniform(80, 120, size=num_sellers)  # Minimum prices

market_prices = []

for step in range(num_steps):
    trades = []
    # Shuffle for random matching
    np.random.shuffle(buyers)
    np.random.shuffle(sellers)
    for b, s in zip(buyers, sellers):
        if b >= s:
            price = (b + s) / 2
            trades.append(price)
    if trades:
        avg_price = np.mean(trades)
        market_prices.append(avg_price)
        # Sellers slightly increase min prices if many trades (high demand)
        sellers += 0.05 * (avg_price - sellers)
        # Buyers decrease WTP if prices go down
        buyers -= 0.05 * (buyers - avg_price)
    else:
        # No trades: stagnation or mismatch
        market_prices.append(market_prices[-1] if market_prices else 100)

# Plot the results
plt.plot(market_prices, label="Market Price")
plt.title("Simulated Market Price Over Time")
plt.xlabel("Time Step")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()
