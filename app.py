import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="NSE Pre-Market Dashboard", layout="wide")

@st.cache_data(ttl=300)
def fetch_nse_preopen():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market"
    }
    session = requests.Session()

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        response = session.get(url, headers=headers, timeout=10)
        data = response.json()
    except Exception as e:
        st.error(f"Failed to fetch data from NSE. Error: {e}")
        return pd.DataFrame()

    records = data.get('data', [])
    if not records:
        st.warning("No data found in the response.")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    if "metadata" not in df.columns:
        st.warning("Unexpected data format from NSE.")
        return pd.DataFrame()

    df = df[["metadata", "lastPrice", "pChange", "quantityTraded", "totalTradedValue"]]
    df["Symbol"] = df["metadata"].apply(lambda x: x.get("symbol", "") if isinstance(x, dict) else "")
    df["Name"] = df["metadata"].apply(lambda x: x.get("name", "") if isinstance(x, dict) else "")
    df = df.drop(columns=["metadata"])
    df.columns = ["Price", "% Change", "Volume", "Traded Value", "Symbol", "Name"]
    df["% Change"] = pd.to_numeric(df["% Change"], errors='coerce')
    df = df.dropna(subset=["% Change"])
    return df

# Load data
df = fetch_nse_preopen()

if not df.empty:
    st.title("NSE Pre-Market Dashboard")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top Gainers")
        st.dataframe(df.sort_values("% Change", ascending=False).head(10), use_container_width=True)

    with col2:
        st.subheader("Top Losers")
        st.dataframe(df.sort_values("% Change", ascending=True).head(10), use_container_width=True)

    with col3:
        st.subheader("Highest Volume")
        st.dataframe(df.sort_values("Volume", ascending=False).head(10), use_container_width=True)
else:
    st.error("No data available to display.")
