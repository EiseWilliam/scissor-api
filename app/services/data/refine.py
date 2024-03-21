from datetime import UTC, datetime
from typing import Literal


import pandas as pd


def process_timeline(data: list, interval: Literal["h","d"] = "h") -> dict:
    data.append({'timestamp': datetime.now(UTC).isoformat(), 'count': 0})
    df = pd.DataFrame(data)
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df.set_index('timestamp', inplace=True)

        # Resample with hourly frequency, filling missing values with 0
        df = df.fillna(0).resample(interval).sum()

        df.index = df.index.to_series().apply(lambda x: x.isoformat()) # type: ignore
    
    
    # df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # # Set the 'date' column as the index for time series operations
    # df.set_index("date", inplace=True)

    # # Handle missing data (if needed)
    # df.fillna(0, inplace=True)  # Replace missing 'count' values with 0

    # Resample to a desired interval (optional)
    # df = df.resample('D').sum()  # Resample to daily counts

    # df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return df.to_dict()


def process_location(data_list: list) -> tuple:
    countries = {}
    country_codes = {}
    cities = {}
    for data in data_list:
        country_name = data["country"]
        country_code = data["country_code"]
        city_name = data["city"]
        count = data["count"]

        # Update the counts for the country and city
        countries[country_name] = countries.get(country_name, 0) + count
        cities[city_name] = cities.get(city_name, 0) + count
        country_codes[country_code] = country_codes.get(country_name, 0) + count

    return country_codes, countries, cities