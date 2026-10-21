import os
import pandas as pd
import time
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

load_dotenv("clepai.env")
client = EntsoePandasClient(api_key=os.environ["ENTSOE_API_KEY"])

def get_prices(zone, start, end, retries=3):
    # ENTSO-E demande des dates avec fuseau, et la fin est exclue : on ajoute 1 jour
    t_start = pd.Timestamp(start, tz="Europe/Paris")
    t_end = pd.Timestamp(end, tz="Europe/Paris") + pd.Timedelta(days=1)
    
    # Mécanisme de relance (retry) en cas d'erreur ou de timeout
    for attempt in range(retries):
        try:
            return client.query_day_ahead_prices(zone, start=t_start, end=t_end)
            
        except Exception as e:
            if attempt == retries - 1:
                raise e
            print(f"Erreur de connexion. Nouvel essai {attempt + 1}/{retries}...")
            time.sleep(5)

def to_series(data, tz="Europe/Paris"):
    data.index = pd.to_datetime(data.index, utc=True).tz_convert(tz)
    return data.rename("da_price")

def to_hourly(series):
    return series.resample("1h").mean()

def make_chunks(start, end, chunk_days=30):
    first = pd.Timestamp(start)
    last = pd.Timestamp(end)
    chunks = []
    current = first
    while current <= last:
        chunk_end = min(current + pd.Timedelta(days=chunk_days - 1), last)
        chunks.append((current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        current = chunk_end + pd.Timedelta(days=1)
    return chunks

def fetch_chunk(zone, start, end):
    data = get_prices(zone, start, end)
    series = to_series(data)
    return to_hourly(series)

def fetch_range(zone, start, end, chunk_days=30, sleep_time=1.5):
    parts = []
    for chunk_start, chunk_end in make_chunks(start, end, chunk_days):
        part = fetch_chunk(zone, chunk_start, chunk_end)
        parts.append(part)
        print(chunk_start, "->", chunk_end, "ok")
        
        # Pause obligatoire entre chaque bloc pour ménager l'API
        time.sleep(sleep_time)
        
    series = pd.concat(parts)
    series = series[~series.index.duplicated(keep="last")]
    return series.sort_index()