import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="NSE Pre-Market Dashboard", layout="wide")

@st.cache_data(ttl=300)
def fetch_nse_preopen():
    url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/pre_open/fo.json"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www1.nseindia.com/live_market/dynaContent/live_watch/pre_open/pre_open_market.htm"
    }

    session = requests.Session()
    try:
        response = session.get(url, headers=headers, timeout=10)
        data = response.json()
    except Exception as e:
        st.error(f"Failed to fetch data from NSE. Error: {e}")
        return pd.DataFrame()

    rows = data.get("data", [])
    df = pd.DataFrame(rows)
    df = df[["symbol", "finalPrice", "perChange", "iVol_traded", "iValue"]]
    df.columns = ["Symbol", "Price", "% Change", "Volume", "Traded Value"]
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
