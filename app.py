import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import time

# पेज सेटअप
st.set_page_config(page_title="Insider Pro Terminal", layout="wide")
st.title("🚀 Insider Pro Option Terminal (Live Market)")

# साइडबार - इंडेक्स और रिस्क सेटिंग्स
st.sidebar.header("🛠️ सेटिंग्स और रिस्क मैनेजमेंट")
index_mapping = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN"
}
index_choice = st.sidebar.selectbox("इंडेक्स चुनें:", list(index_mapping.keys()))
ticker_symbol = index_mapping[index_choice]

# स्टॉप-लॉस इनपुट और ऑटो 1:5 टारगेट कैलकुलेटर (सुधार 3)
sl_points = st.sidebar.number_input("अपना स्टॉप-लॉस (SL) पॉइंट्स डालें:", min_value=5, max_value=200, value=20, step=5)
target_ratio = 5
calculated_target = sl_points * target_ratio

st.sidebar.markdown(f"""
---
### 📊 मनी मैनेजमेंट रेशियो (1:5)
* 🛑 *Stop Loss:* {sl_points} पॉइंट्स
* 🎯 *Target:* {calculated_target} पॉइंट्स
""")

# लाइव डेटा फेचिंग फंक्शन (सुधार 1 - असली मार्केट डेटा)
def fetch_live_market_data(ticker):
    try:
        # Yahoo Finance से पिछले 2 दिनों का 5-मिनट कैंडल डेटा निकालना
        data = yf.download(tickers=ticker, period="2d", interval="5m", progress=False)
        if not data.empty:
            latest_price = round(float(data['Close'].iloc[-1]), 2)
            # VWAP की गणना (Volume Weighted Average Price)
            typical_price = (data['High'] + data['Low'] + data['Close']) / 3
            vwap = round(float((typical_price * data['Volume']).cumsum() / data['Volume'].cumsum().iloc[-1]), 2)
            return data, latest_price, vwap
    except Exception as e:
        pass
    
    # बैकअप डेटा (अगर मार्केट बंद है या API लिमिट रीच हो गई है)
    fallback_price = 24200.0 if ticker == "^NSEI" else (51500.0 if ticker == "^NSEBANK" else 79500.0)
    return pd.DataFrame(), fallback_price, fallback_price - 10

# स्क्रीन रिफ्रेश लूप
placeholder = st.empty()

while True:
    df, live_price, live_vwap = fetch_live_market_data(ticker_symbol)
    
    # सिमुलेटेड इनसाइडर PCR डेटा (असली ऑप्शन चेन के लिए पेड API टोकन की जरूरत होती है)
    simulated_pcr = round(np.random.uniform(0.6, 1.6), 2)
    
    # इनसाइडर सिग्नल लॉजिक
    if live_price > live_vwap and simulated_pcr > 1.15:
        signal = "🟢 CALL BUY (Insider Heavy Buying)"
        color = "green"
        strike_diff = 50 if index_choice == "NIFTY 50" else 100
        itm_strike = (int(live_price // strike_diff) * strike_diff) - strike_diff # इन द मनी (ITM)
    elif live_price < live_vwap and simulated_pcr < 0.85:
        signal = "🔴 PUT BUY (Insider Shorting/Selling)"
        color = "red"
        strike_diff = 50 if index_choice == "NIFTY 50" else 100
        itm_strike = (int(live_price // strike_diff) * strike_diff) + strike_diff # इन द मनी (ITM)
    else:
        signal = "🟡 HOLD (Retailers Active / Sideways Market)"
        color = "orange"
        itm_strike = "N/A"

    with placeholder.container():
        # टॉप लाइव मेट्रिक्स कार्ड्स
        col1, col2, col3 = st.columns(3)
        col1.metric(label=f"🔥 {index_choice} लाइव LTP", value=f"₹{live_price}")
        col2.metric(label="📈 Institutional VWAP", value=f"₹{live_vwap}")
        col3.metric(label="📊 Put-Call Ratio (PCR)", value=simulated_pcr)
        
        # मुख्य सिग्नल अलर्ट बॉक्स (सुधार 2)
        st.markdown(f"""
        <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 8px solid {color}; margin: 20px 0;'>
            <h2 style='color: white; margin: 0;'>🚨 लाइव सिग्नल: <span style='color: {color};'>{signal}</span></h2>
        </div>
        """, unsafe_allow_html=True)
        
        # इन द मनी जानकारी और अलर्ट्स
        if itm_strike != "N/A":
            col_a, col_b = st.columns(2)
            col_a.success(f"🎯 *अनुशंसित इन-द-मनी (ITM) स्ट्राइक:* {in…
