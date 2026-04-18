import streamlit as st
import requests
import pickle
import numpy as np
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
load_dotenv()
API_KEY = os.getenv("CRICAPI_KEY") or st.secrets.get("CRICAPI_KEY", "")

st.set_page_config(page_title="IPL AI Predictor", layout="wide")

st.title("🏏 IPL LIVE MATCH AI PREDICTOR")

# ---------------- SIDEBAR ----------------
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Live Match", "Manual Input", "Demo Match"]
)

auto_refresh = st.sidebar.checkbox("Auto Refresh (5 sec)", value=True)

# ---------------- LOAD MODEL ----------------
MODEL_PATH = Path(__file__).resolve().parent / "live_model.pkl"
model = None
model_error = None

if MODEL_PATH.exists():
    try:
        with open(MODEL_PATH, "rb") as model_file:
            model = pickle.load(model_file)
    except (pickle.UnpicklingError, EOFError, OSError) as exc:
        model_error = f"Unable to load local model file: {exc}"
else:
    model_error = f"Model file not found at {MODEL_PATH}"

if model is None:
    uploaded_model = st.sidebar.file_uploader("Upload trained model (.pkl)", type=["pkl"])
    if uploaded_model is not None:
        try:
            model = pickle.load(uploaded_model)
            model_error = None
            st.sidebar.success("Model uploaded successfully")
        except (pickle.UnpicklingError, EOFError, OSError) as exc:
            model_error = f"Uploaded model could not be loaded: {exc}"

if model_error:
    st.sidebar.warning("No valid model loaded. Using fallback estimator.")
    st.sidebar.caption(model_error)


def get_win_probability(runs_left, balls_left, wickets):
    if balls_left <= 0:
        return 0.0 if runs_left > 0 else 1.0

    if model is not None:
        try:
            data = np.array([[runs_left, balls_left, wickets]])
            return float(model.predict_proba(data)[0][1])
        except Exception:
            pass

    # Heuristic fallback when a trained model is unavailable.
    required_rate = (runs_left * 6) / balls_left
    wicket_penalty = max(0, wickets - 2) * 0.18
    pressure = (required_rate - 8.0) * 0.9 + wicket_penalty
    prob = 1 / (1 + np.exp(pressure))
    return float(np.clip(prob, 0.01, 0.99))

# ---------------- FUNCTION: GET LIVE MATCH ----------------
def get_live_match():
    if not API_KEY:
        return None

    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    try:
        response = requests.get(url)
        data = response.json()

        for match in data.get('data', []):
            if "IPL" in match.get('series', ""):
                return match
    except:
        return None

    return None


# =========================================================
# 🟢 LIVE MATCH MODE
# =========================================================
if mode == "Live Match":

    if not API_KEY:
        st.info("Set CRICAPI_KEY as an environment variable or in Streamlit secrets to enable live match mode.")

    match = get_live_match()

    if match:
        st.subheader(f"📺 {match['name']}")

        score_data = match.get('score', [])

        if len(score_data) >= 2:

            team1 = score_data[0]
            team2 = score_data[1]

            col1, col2 = st.columns(2)

            with col1:
                st.metric(team1['inning'], f"{team1['r']}/{team1['w']}")
                st.write(f"Overs: {team1['o']}")

            with col2:
                st.metric(team2['inning'], f"{team2['r']}/{team2['w']}")
                st.write(f"Overs: {team2['o']}")

            # 🔥 Assume team2 chasing
            target = team1['r'] + 1
            runs = team2['r']
            wickets = team2['w']
            overs = float(team2['o'])

            balls = int(overs) * 6 + int((overs - int(overs)) * 10)

            runs_left = target - runs
            balls_left = 120 - balls

            if balls_left > 0 and runs_left > 0:

                st.markdown("### 🤖 AI Prediction")

                prob = get_win_probability(runs_left, balls_left, wickets)

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Win Probability", f"{prob*100:.2f}%")

                with col2:
                    st.metric("Lose Probability", f"{(1-prob)*100:.2f}%")

                st.progress(int(prob * 100))

            else:
                st.success("Match Finished 🎉")

        else:
            st.warning("Score data not available yet")

    else:
        st.warning("No live IPL match found ❌")

# =========================================================
# 🟡 MANUAL INPUT MODE
# =========================================================
elif mode == "Manual Input":

    st.subheader("✍️ Enter Match Situation")

    target = st.number_input("Target", 100, 300, 180)
    runs = st.number_input("Current Runs", 0, target, 120)
    overs = st.number_input("Overs", 0.0, 20.0, 15.0)
    wickets = st.number_input("Wickets Fallen", 0, 10, 4)

    balls = int(overs) * 6 + int((overs - int(overs)) * 10)

    runs_left = target - runs
    balls_left = 120 - balls

    if st.button("Predict"):

        prob = get_win_probability(runs_left, balls_left, wickets)

        st.success(f"Win Probability: {prob*100:.2f}%")
        st.info(f"Lose Probability: {(1-prob)*100:.2f}%")

# =========================================================
# 🔵 DEMO MODE (BEST FOR PRESENTATION)
# =========================================================
elif mode == "Demo Match":

    st.subheader("🎯 Demo IPL Scenario")

    # Fixed match example
    target = 180
    runs = 145
    overs = 17.2
    wickets = 5

    balls = int(overs) * 6 + int((overs - int(overs)) * 10)

    runs_left = target - runs
    balls_left = 120 - balls

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Score", f"{runs}/{wickets}")

    with col2:
        st.metric("Overs", overs)

    st.write(f"🎯 Target: {target}")

    prob = get_win_probability(runs_left, balls_left, wickets)

    st.markdown("### 🤖 AI Prediction")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Win Probability", f"{prob*100:.2f}%")

    with col2:
        st.metric("Lose Probability", f"{(1-prob)*100:.2f}%")

    st.progress(int(prob * 100))


# =========================================================
# 🔄 AUTO REFRESH
# =========================================================
if auto_refresh and mode == "Live Match":
    time.sleep(5)
    st.rerun()