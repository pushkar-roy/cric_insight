import numpy as np
import pandas as pd

match = pd.read_csv("matches.csv")
delivery = pd.read_csv("deliveries.csv")

print(match.describe())
print(delivery.describe())

