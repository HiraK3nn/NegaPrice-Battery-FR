from energycharts import get_prices, to_series

data = get_prices("FR", "2015-01-01", "2015-01-07")
s = to_series(data)
print(len(s), "valeurs")