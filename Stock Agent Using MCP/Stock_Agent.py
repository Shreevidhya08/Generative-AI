import os
import requests
import yfinance as yf
import streamlit as st
from langchain_groq import ChatGroq

st.set_page_config(page_title="Currency & Stock Agent", layout="centered")

st.title("🌍 Country Currency & Stock Market Agent")

# 🔐 Get API keys from Streamlit Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
EXCHANGE_API_KEY = st.secrets["EXCHANGE_API_KEY"]

# Initialize LLM (only to satisfy assignment requirement)
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

country = st.text_input(
    "Enter Country Name (Japan, India, USA, UK, China, South Korea)"
)

# Country Mapping
country_data = {
    "Japan": {
        "currency": "JPY",
        "indices": {"Nikkei 225": "^N225"},
        "exchange_name": "Tokyo Stock Exchange",
        "maps_query": "Tokyo Stock Exchange HQ"
    },
    "India": {
        "currency": "INR",
        "indices": {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"},
        "exchange_name": "Bombay Stock Exchange",
        "maps_query": "Bombay Stock Exchange HQ"
    },
    "USA": {
        "currency": "USD",
        "indices": {"S&P 500": "^GSPC", "Dow Jones": "^DJI"},
        "exchange_name": "New York Stock Exchange",
        "maps_query": "New York Stock Exchange HQ"
    },
    "UK": {
        "currency": "GBP",
        "indices": {"FTSE 100": "^FTSE"},
        "exchange_name": "London Stock Exchange",
        "maps_query": "London Stock Exchange HQ"
    },
    "China": {
        "currency": "CNY",
        "indices": {"Shanghai Composite": "000001.SS"},
        "exchange_name": "Shanghai Stock Exchange",
        "maps_query": "Shanghai Stock Exchange HQ"
    },
    "South Korea": {
        "currency": "KRW",
        "indices": {"KOSPI": "^KS11"},
        "exchange_name": "Korea Exchange",
        "maps_query": "Korea Exchange HQ"
    }
}

if st.button("Get Details"):

    if country not in country_data:
        st.error("Country not supported in demo version.")
    else:
        try:
            data = country_data[country]
            currency = data["currency"]

            # 1️⃣ Official Currency
            st.subheader(f"Official Currency of {country}")
            st.write(currency)

            # 2️⃣ Exchange Rates
            url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{currency}"
            response = requests.get(url).json()

            st.subheader("Exchange Rates (1 Unit)")
            targets = ["USD", "INR", "GBP", "EUR"]

            for t in targets:
                rate = response["conversion_rates"].get(t, "N/A")
                st.write(f"1 {currency} → {t}: {rate}")

            # 3️⃣ Stock Indices
            st.subheader("Major Stock Indices")

            for name, ticker in data["indices"].items():
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")

                if not hist.empty:
                    price = hist["Close"].iloc[-1]
                    st.write(f"{name}: {round(price, 2)}")
                else:
                    st.write(f"{name}: Data unavailable")

            # 4️⃣ Google Maps Location
            st.subheader("Stock Exchange HQ Location")
            maps_url = f"https://www.google.com/maps?q={data['maps_query']}&output=embed"
            st.components.v1.iframe(maps_url, height=400)

        except Exception as e:
            st.error("Error fetching data. Check API keys in Streamlit Secrets.")
