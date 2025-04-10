import streamlit as st
from db import *
from server import run_playwright
import traceback

st.set_page_config(page_title="Auto Tweet Bot 🤖", layout="centered")

# Page Title
st.markdown("<h1 style='text-align: center;'>🤖 Auto Tweet Bot</h1>", unsafe_allow_html=True)

# Info Section
with st.expander("📘 How to Use This Bot", expanded=True):
    st.markdown("""
    ### 🧰 Setup Instructions
    1. Open **File Explorer** and paste the following command into the address bar (you can modify the path if Chrome is installed elsewhere):
    ```bash
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\ChromeProfile" https://x.com/home
    ```
    2. This will open a special Chrome window in debug mode. **Log into X (Twitter)** there.
    3. Come back here and start tweeting!

    🔐 **Need a News API Key?** Get one from [https://newsapi.org](https://newsapi.org)
    """)

st.divider()

# Session state initialization
if 'newses' not in st.session_state:
    st.session_state.newses = {}

# Configuration Sidebar
with st.container():
    st.subheader("⚙️ Configuration")

    st.session_state.api_key = st.text_input("🔑 Enter your News API Key", type="password", placeholder="Paste your NewsAPI key here")
    st.session_state.niche = st.text_input("🧠 Enter a News Topic", value="crypto", placeholder="e.g. crypto, tech, politics")
    st.session_state.page_size = st.slider("📰 Number of News Articles", 1, 10, 5)

    st.session_state.cdp_url = "http://localhost:9222"
    st.caption(f"🧩 CDP Debugger URL in use: `{st.session_state.cdp_url}`")

# Fetch News Button
st.markdown("---")
if st.button("📡 Fetch News & Prepare Tweets"):
    with st.spinner("Fetching the latest news headlines..."):
        try:
            newses = get_news(
                niche=st.session_state.niche,
                pageSize=st.session_state.page_size,
                NEWS_API_KEY=st.session_state.api_key
            )
            st.session_state.newses = newses
            st.success(f"✅ {len(newses)} articles fetched and prepared!")
        except Exception as e:
            st.error("❌ Failed to fetch news. Please check your API key and internet.")
            st.text(str(e))

# Tweets to Post
if st.session_state.newses:
    st.markdown("---")
    st.subheader("🚀 Tweets Ready to Post")

    for i, news in list(st.session_state.newses.items()):
        with st.container(border=True):
            st.write(f"**📰 Tweet #{i + 1}:**")
            st.markdown(f"> {news[:250]}...")
            if st.button(f"📤 Post Tweet #{i+1}"):
                with st.spinner("Sending tweet via Playwright..."):
                    try:
                        run_playwright(news, st.session_state.cdp_url)
                        st.session_state["last_tweet_status"] = "✅ Tweet posted successfully!"
                    except Exception as e:
                        st.session_state["last_tweet_status"] = f"❌ Error: {e}"
                
                # Display result
                if st.session_state.last_tweet_status.startswith("✅"):
                    st.toast(st.session_state["last_tweet_status"], icon="✅")
                    del st.session_state.newses[i]
                    st.rerun()
                else:
                    st.toast(st.session_state["last_tweet_status"], icon="❌")

    if not st.session_state.newses:
        st.success("✅ All tweets have been posted!")

