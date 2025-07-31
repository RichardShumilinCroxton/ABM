import random
import numpy as np
import mesa
from mesa import Model, Agent
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt

# -------------------------------
# Buyer Agent
# -------------------------------
class BuyerAgent(Agent):
    def __init__(self, model, unique_id):
        super().__init__(model)
        self.unique_id = unique_id
        self.budget = random.uniform(80, 120)
        self.wtp = random.uniform(80, 120)
        self.last_bid = None

    def step(self):
        # Generate a bid near WTP
        self.last_bid = random.uniform(self.wtp - 5, self.wtp + 5)


# -------------------------------
# Seller Agent
# -------------------------------
class SellerAgent(Agent):
    def __init__(self, model, unique_id):
        super().__init__(model)
        self.unique_id = unique_id
        self.inventory = 1
        self.price = random.uniform(80, 120)
        self.sales = 0

    def step(self):
        # Adaptive pricing
        if self.sales > 0:
            self.price *= 1.02  # Increase price if sold
        else:
            self.price *= 0.98  # Decrease price if unsold
        self.sales = 0  # Reset for next round


# -------------------------------
# Market Model
# -------------------------------
class MarketModel(Model):
    def __init__(self, num_buyers=50, num_sellers=50, seed=None):
        super().__init__(seed=seed)

        self.num_buyers = num_buyers
        self.num_sellers = num_sellers
        self.avg_price = 100.0  # Start with default average price

        # Create agents — Mesa auto-registers them
        for i in range(num_buyers):
            BuyerAgent(self, f"buyer_{i}")
        for j in range(num_sellers):
            SellerAgent(self, f"seller_{j}")

        # Track average price over time
        self.datacollector = DataCollector(
            model_reporters={"Average_Price": lambda m: m.avg_price}
        )

    def step(self):
        # Step 1: Buyers generate bids
        self.agents.select(lambda a: isinstance(a, BuyerAgent)).do("step")

        # Step 2: Sellers adapt prices
        self.agents.select(lambda a: isinstance(a, SellerAgent)).do("step")

        # Step 3: Match and trade
        buyers = self.agents.select(lambda a: isinstance(a, BuyerAgent)).shuffle()
        sellers = self.agents.select(lambda a: isinstance(a, SellerAgent)).shuffle()

        trades = []

        for b, s in zip(buyers, sellers):
            if b.budget <= 0 or s.inventory <= 0:
                continue

            bid = b.last_bid
            ask = s.price

            if bid >= ask:
                trade_price = (bid + ask) / 2
                b.budget -= trade_price
                s.inventory -= 1
                s.sales += 1
                trades.append(trade_price)

        if trades:
            self.avg_price = float(np.mean(trades))

        # Step 4: Collect model-level data
        self.datacollector.collect(self)


# -------------------------------
# Run the Model and Plot
# -------------------------------
if __name__ == "__main__":
    model = MarketModel(num_buyers=100, num_sellers=100, seed=42)

    for _ in range(100):
        model.step()

    # Plot results
    df = model.datacollector.get_model_vars_dataframe()
    df.plot(y="Average_Price", legend=False)
    plt.title("Market Price Over Time (Mesa 3.x)")
    plt.xlabel("Step")
    plt.ylabel("Average Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
