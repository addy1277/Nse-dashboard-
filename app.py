
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="NSE Pre-Market Dashboard", layout="wide")

def fetch_nse_preopen():
    url = "https://www.nseindia.com/api/market-data-pre-open?key=NIFTY"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market"
    }
    session = requests.Session()
    response = session.get("https://www.nseindia.com", headers=headers)
    cookies = session.cookies.get_dict()
    response = session.get(url, headers=headers, cookies=cookies)
    data = response.json()
    records = data.get('data', [])

    df = pd.DataFrame(records)
    df = df[["metadata", "lastPrice", "pChange", "quantityTraded", "totalTradedValue"]]
    df["Symbol"] = df["metadata"].apply(lambda x: x.get("symbol", ""))
    df["Name"] = df["metadata"].apply(lambda x: x.get("name", ""))
    df = df.drop(columns=["metadata"])
    df.columns = ["Price", "% Change", "Volume", "Traded Value", "Symbol", "Name"]

    df["% Change"] = pd.to_numeric(df["% Change"], errors='coerce')
    df = df.dropna(subset=["% Change"])
    return df

st.title("NSE Pre-Market Dashboard")
st.markdown("View **Top Gainers**, **Top Losers**, and **Highest Volume Stocks** in Pre-Market Session.")

df = fetch_nse_preopen()
df_filtered = df[df["% Change"].abs() > 2]

search = st.text_input("Search Stock (Symbol or Name)").upper()
if search:
    df_filtered = df_filtered[df_filtered["Symbol"].str.contains(search) | df_filtered["Name"].str.upper().str.contains(search)]

st.dataframe(df_filtered.sort_values(by="% Change", ascending=False), use_container_width=True)
