import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="NSE Pre-Open Market Viewer", layout="wide")

st.title("NSE Pre-Open Market Viewer")

URL = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

@st.cache_data(ttl=60)
def fetch_preopen_data():
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"Error fetching data. Status code: {response.status_code}")
            return None

        try:
            data = response.json()
        except ValueError:
            st.error("Failed to fetch data from NSE. Empty or invalid JSON.")
            return None

        return data

    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

data = fetch_preopen_data()

if data and "data" in data:
    records = data["data"]
    df = pd.DataFrame(records)

    if not df.empty:
        df = df[["metadata", "lastPrice", "priceBand", "finalQuantity", "iep"]]
        df["symbol"] = df["metadata"].apply(lambda x: x.get("symbol") if isinstance(x, dict) else None)
        df = df[["symbol", "lastPrice", "iep", "finalQuantity", "priceBand"]]
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Data fetched, but it's empty.")
else:
    st.warning("No data available to display.")
