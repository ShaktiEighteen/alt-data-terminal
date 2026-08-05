import streamlit as st
import pandas as pd

# Initialize Terminal UI
st.set_page_config(page_title="Alt Data Terminal", layout="wide")

# Inject custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #2E231F; 
        color: #F4ECD8; 
        font-family: 'Georgia', serif;
    }
    div[data-testid="stMetricValue"] {
        color: #D4AF37; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("📜 Alternative Data Investment Terminal")
st.markdown("### Real-Time Pricing & Arbitrage Engine")

try:
    df = pd.read_csv('prices.csv')
    
    # --- PANDAS DATA FORMATTING ---
    # 1. Extract the clean product name from the raw Amazon URL
    if 'product_page_url' in df.columns:
        df['Asset_Name'] = df['product_page_url'].str.extract(r'amazon\.in/([^/]+)/dp/')[0]
        # Clean up the hyphens into spaces
        df['Asset_Name'] = df['Asset_Name'].str.replace('-', ' ')
    
    # 2. Keep only the useful columns and drop empty rows
    df_clean = df[['Asset_Name', 'product_page_url']].dropna()
    
    # --- UI DISPLAY ---
    total_assets = len(df_clean)
    st.metric(label="Total Assets Tracked (INR Market)", value=total_assets)
    
    st.write("#### Live Asset Ledger")
    st.dataframe(df_clean, use_container_width=True)
    
    # Fire the animation effect when data successfully loads
    st.balloons()
    
except FileNotFoundError:
    st.error("Data pipeline empty. Please execute scraper.py to initialize the data feed.")