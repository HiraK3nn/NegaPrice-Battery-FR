import requests
import pandas as pd

def get_prices(zone, start, end):
    url = "https://api.energy-charts.info/price"
    params = {"bzn": zone, "start": start, "end": end}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def to_series(data, tz="Europe/Paris"):
    dates = pd.to_datetime(data["unix_seconds"], unit="s", utc=True).tz_convert(tz)
    return pd.Series(data["price"], index=dates, name="da_price")

