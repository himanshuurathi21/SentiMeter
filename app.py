import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
from streamlit_lottie import st_lottie
from model_utils import load_sentiment_model, process_results

# 1. Page Configuration
st.set_page_config(page_title="SentimentMeter AI", page_icon="", layout="wide")
st.set_page_config(
    page_title="SentimentMeter AI", 
    page_icon="🧪", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Yeh niche wala CSS code icon aur fork button ko hide kar dega
st.markdown("""
    <style>
    /* GitHub icon aur Fork button hide karne ke liye */
    .stAppDeployButton {
        display: none;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# CSS for Animations and Layout
st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-title {
        animation: fadeIn 1.5s ease-out;
        text-align: center;
    }
    .stButton>button {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper function for Lottie
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

lottie_ai = load_lottieurl("https://lottie.host/82548486-4f40-424b-8534-793223381a1a/Y5m9e0f6P5.json")

# 2. Smooth Reveal Loader
if 'loaded' not in st.session_state:
    if lottie_ai:
        with st.empty():
            _, center_col, _ = st.columns([1,2,1])
            with center_col:
                st_lottie(lottie_ai, height=300, key="initial_loader")
                st.markdown("<h2 style='text-align:center;'>SentimentMeter AI is Waking Up...</h2>", unsafe_allow_html=True)
                time.sleep(2.2)
            st.empty()
    st.session_state.loaded = True

# Initialize Session States
if 'history' not in st.session_state: st.session_state.history = []
if 'user_text' not in st.session_state: st.session_state.user_text = ""

# 3. Sidebar (Interactive History)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("SentimentMeter Dashboard")
    st.markdown("---")
    st.subheader("📜 Analysis History")
    if not st.session_state.history:
        st.info("Your history will appear here.")
    else:
        for index, item in enumerate(reversed(st.session_state.history[-8:])):
            if st.button(f"{item['emoji']} {item['sentiment']}\n{item['text'][:25]}...", key=f"hist_{index}", use_container_width=True):
                st.session_state.user_text = item['text']
                st.rerun()
            st.divider()

# 4. Main UI
st.markdown('<div class="main-title"><h1> SentimentMeter: Sentiment Analysis Engine</h1><p style="font-size:18px; color:gray;">Measuring the Emotional Pulse of your Text</p></div>', unsafe_allow_html=True)

# Aligned Example Buttons (Positive -> Neutral -> Negative)
# Aligned Example Buttons (Positive -> Neutral -> Negative)
st.write("Quick Test:")
col_pos, col_neu, col_neg = st.columns(3)

with col_pos:
    if st.button("Happy News 📈", use_container_width=True): 
        # Update both states to ensure it shows up in the text area
        st.session_state.user_text = "I am incredibly happy with these results!"
        st.session_state.current_input = "I am incredibly happy with these results!"
        st.rerun()

with col_neu:
    if st.button("Fact (Neutral) 📖", use_container_width=True): 
        st.session_state.user_text = "The sky is blue today."
        st.session_state.current_input = "The sky is blue today."
        st.rerun()

with col_neg:
    if st.button("Sad News 📉", use_container_width=True): 
        st.session_state.user_text = "The service was extremely disappointing and rude."
        st.session_state.current_input = "The service was extremely disappointing and rude."
        st.rerun()
# --- BUG FIX: TEXT AREA SYNC ---
user_input = st.text_area("Input Text:", value=st.session_state.user_text, height=150, placeholder="Type how you feel...", key="current_input")

# 5. Analysis Logic
if st.button("Analyze Now", use_container_width=True):
    final_input = st.session_state.current_input # Fetch latest input directly
    
    if not final_input.strip():
        st.warning("Please enter some text first!")
    else:
        st.session_state.user_text = final_input # Update state for persistence
        
        with st.spinner("AI is decoding emotions..."):
            classifier = load_sentiment_model()
            raw_results = classifier(final_input)
            data = process_results(raw_results)
            
            if data:
                best = max(data, key=lambda x: x['Score'])
                
                # Logic for Gauge Meter
                if best['Label'] == "Positive":
                    emoji, color, val = "😊", "#2ecc71", 66 + (best['Score']/3)
                elif best['Label'] == "Negative":
                    emoji, color, val = "😡", "#e74c3c", (33 - (best['Score']/3))
                else:
                    emoji, color, val = "😐", "#f1c40f", 50

                # History Management
                if final_input not in [h['text'] for h in st.session_state.history]:
                    st.session_state.history.append({"text": final_input, "sentiment": best['Label'], "emoji": emoji})

                st.divider()
                
                # 6. Display Results
                res_left, res_right = st.columns([1, 1])
                
                with res_left:
                    # Needle Gauge Meter
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number", value = val,
                        title = {'text': f"{emoji} {best['Label']}", 'font': {'size': 24}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickvals': [15, 50, 85], 'ticktext': ['Negative', 'Neutral', 'Positive']},
                            'bar': {'color': "black"},
                            'steps': [
                                {'range': [0, 33], 'color': '#e74c3c'},
                                {'range': [33, 66], 'color': '#f1c40f'},
                                {'range': [66, 100], 'color': '#2ecc71'}
                            ],
                            'threshold': {'line': {'color': "black", 'width': 4}, 'value': val}
                        }
                    ))
                    fig_gauge.update_layout(height=350, margin=dict(t=50, b=0))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with res_right:
                    # Confidence Bar Chart
                    st.subheader("Confidence Levels")
                    df = pd.DataFrame(data)
                    fig_bar = px.bar(df, x='Label', y='Score', color='Label',
                                     color_discrete_map={'Positive':'#2ecc71', 'Neutral':'#f1c40f', 'Negative':'#e74c3c'})
                    fig_bar.update_layout(height=320, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)

# Final Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 14px;">
        Thankyou | Submit issue or feedback on 
        <a href="mailto:rathihimanshuu@gmail.com?subject=SentimentMeter%20App%20Feedback" style="color: #3498db; text-decoration: none; font-weight: bold;">
            rathihimanshuu@gmail.com
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)
