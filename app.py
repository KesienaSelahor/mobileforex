import streamlit as st
import datetime, pytz, time
import yfinance as yf
import google.generativeai as genai
import plotly.graph_objects as go

st.set_page_config("Forex Quant Terminal","🦅",layout="wide")
st.set_option("client.showErrorDetails", False)

# ---------------- STATE ----------------
state = st.session_state
state.setdefault("connected", False)
state.setdefault("analysis", None)

# ---------------- HEADER ----------------
st.markdown("## 🦅 FX-CORE QUANT TERMINAL")
st.caption(datetime.datetime.now(
    pytz.timezone("Africa/Lagos")).strftime("Lagos %H:%M"))

# ---------------- DATA ENGINE ----------------
@st.cache_data(ttl=900)
def get_dxy():
    d = yf.Ticker("DX-Y.NYB").history(period="2d")
    return d.Close.iloc[-1], ((d.Close.iloc[-1]-d.Open.iloc[-1])/d.Open.iloc[-1])*100

# ---------------- CONNECT ----------------
if not state.connected:
    if st.button("🔌 INITIALIZE SYSTEM"):
        with st.spinner("Booting systems..."):
            state.dxy, state.usd_strength = get_dxy()
            state.connected = True
else:
    col1, col2 = st.columns([1,2])
    with col1:
        st.metric("DXY", f"{state.dxy:.2f}")
        pair = st.selectbox("Asset",["EURUSD","GBPUSD","XAUUSD"])

    with col2:
        api_key = st.text_input("Gemini API Key", type="password")
        if st.button("⚡ RUN AI ANALYSIS"):
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                with st.spinner("AI thinking..."):
                    r = model.generate_content(
                        f"Analyze {pair}. USD strength {state.usd_strength}. "
                        "Return JSON score/action."
                    )
                    state.analysis = r.text

    if state.analysis:
        st.success("AI RESPONSE")
        st.code(state.analysis)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=70,
            gauge={"axis":{"range":[0,100]}}
        ))
        st.plotly_chart(fig,use_container_width=True)
