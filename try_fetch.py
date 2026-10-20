from energycharts import get_prices, to_series

data = get_prices("FR", "2025-01-01", "2025-01-07")
s = to_series(data)
print(s.head())
print(len(s), "valeurs, min", s.min(), "max", s.max())