import os
import streamlit as st
from datetime import datetime, timedelta
import base64
import asyncio
import nest_asyncio
import pandas as pd
import pytz

# Apply the patch for nested event loops, required for Streamlit
nest_asyncio.apply()

# Import your page modules
from backend_logic import Backend
import Login
import Admin_Panel
import Body_Metrics
import Dashboard
import Diet_Planner
import Exercise_Library
import Progress_Tracker
import Workout_Planner
from wellness_nudge_agent import get_nudge_from_agent

# --- App Configuration ---
st.set_page_config(
    page_title="💪 Enterprise Wellness Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Backend ---
if "backend" not in st.session_state:
    st.session_state.backend = Backend()

# --- Helper Functions for Styling ---
def get_base64_image(image_file):
    try:
        with open(image_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            css = f.read()
            if "<style>" in css:
                css = css.split("<style>")[1].split("</style>")[0]
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except: pass

# --- Apply Styling ---
b64_image = get_base64_image("fitness_bg.jpg")
if b64_image:
    st.markdown(f"""<style>.stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.6)), url(data:image/jpeg;base64,{b64_image});
        background-size: cover; background-position: center; background-attachment: fixed;
    }}</style>""", unsafe_allow_html=True)
load_css("template/basic.html")


# --- Main Application Logic ---
if not st.session_state.get("logged_in", False):
    Login.app()
else:
    # --- Sidebar ---
    with st.sidebar:
        user_info = st.session_state.get('user_info', {})
        st.image("fitness_icon.png", width=80)
        st.title("Navigation")
        st.write(f"Welcome, **{user_info.get('name', '')}**!")
        st.markdown("---")
        
        page_buttons = [
            {"label": "Home", "icon": "🏠", "key": "Home"},
            {"label": "Dashboard", "icon": "📊", "key": "Dashboard"},
            {"label": "Body Metrics", "icon": "📏", "key": "Body_Metrics"},
            {"label": "Diet Planner", "icon": "🥦", "key": "Diet_Planner"},
            {"label": "Workout Planner", "icon": "🗓️", "key": "Workout_Planner"},
            {"label": "Exercise Library", "icon": "📚", "key": "Exercise_Library"},
            {"label": "Progress Tracker", "icon": "📈", "key": "Progress_Tracker"},
        ]
        
        if user_info.get('is_admin', False):
            page_buttons.append({"label": "Admin Panel", "icon": "🏢", "key": "Admin_Panel"})

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"

        for btn in page_buttons:
            if st.button(f"{btn['icon']} {btn['label']}", key=f"nav_btn_{btn['key']}", use_container_width=True):
                st.session_state.current_page = btn['key']
                st.rerun()

        st.markdown("---")
        st.info(st.session_state.backend.get_todays_tip())

    # --- Page Routing ---
    page = st.session_state.current_page
    
    if page == "Home":
        user_info = st.session_state.user_info
        st.header(f"Welcome back, {user_info.get('name', 'User')}! 👋")
        
        st.markdown("---")
        st.subheader("Your Fitness Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Daily Water Intake (liters)", 0.0, 5.0, 2.5)
        with col2:
            st.selectbox("Main Fitness Goal", ["Lose Weight", "Gain Muscle", "Improve Endurance", "Maintain Fitness"])

        st.markdown("---")
        st.subheader("🧠 Manual Wellness Nudge")
        with st.form("nudge_form"):
            nudge_input = st.text_area("Describe how you're feeling or what you need help with:", height=100)
            submitted = st.form_submit_button("Get a Nudge")

        if submitted and nudge_input:
            with st.spinner("Thinking of a motivational nudge..."):
                profile = asyncio.run(st.session_state.backend.get_user_profile(user_info['uid'], user_info['org_id']))
                if profile:
                    response = get_nudge_from_agent(nudge_input, profile, st.session_state.backend)

                    # Prevent duplicate nudge if Groq returns the same message twice
                    if "Here's your personalized nudge:" in response:
                        response = response.split("Here's your personalized nudge:")[-1].strip()

                    # Remove duplicate lines
                    unique_lines = []
                    for line in response.splitlines():
                        line = line.strip()
                        if line and line.lower() not in [l.lower() for l in unique_lines]:
                            unique_lines.append(line)

                    cleaned_response = "\n".join(unique_lines)

                    st.success("Here's your personalized nudge:")
                    st.markdown(f"> {cleaned_response}")

                else:
                    st.error("Could not retrieve user profile.")
        
        # --- Proactive Agent Check (Manual Trigger) ---
        st.markdown("---")
        st.subheader("🤖 Proactive Agent Check")
        if st.button("Have I been inactive?"):
            with st.spinner("Checking your recent activity..."):
                backend = st.session_state.backend
                uid = user_info["uid"]
                org_id = user_info["org_id"]

                recent_logs = asyncio.run(backend.get_daily_logs(org_id, uid))
                
                has_worked_out = False
                if recent_logs:
                    df_logs = pd.DataFrame(recent_logs)
                    df_logs['date'] = pd.to_datetime(df_logs['date'])
                    if df_logs['date'].dt.tz is not None:
                        df_logs['date'] = df_logs['date'].dt.tz_localize(None)
                    
                    three_days_ago = datetime.now() - timedelta(days=3)
                    recent_workouts = df_logs[df_logs['date'] > three_days_ago]
                    if not recent_workouts.empty:
                        has_worked_out = True

                if not has_worked_out:
                    st.warning("It looks like you haven't logged a workout in the last 3 days. Here's a little nudge!")
                    profile = asyncio.run(backend.get_user_profile(uid, org_id))
                    if profile:
                        message = get_nudge_from_agent(
                            "I haven't worked out in a few days and need some motivation.", profile, backend
                        )
                        asyncio.run(backend.save_notification(org_id, uid, message))
                        st.success("A motivational nudge has been sent to your dashboard!")
                        st.markdown(f"> {message}")
                else:
                    st.success("✅ You're on track! You've logged a workout recently. Keep up the great work!")

    # --- Other Page Renders ---
    elif page == "Dashboard": Dashboard.app()
    elif page == "Body_Metrics": Body_Metrics.app()
    elif page == "Diet_Planner": Diet_Planner.app()
    elif page == "Workout_Planner": Workout_Planner.app()
    elif page == "Exercise_Library": Exercise_Library.app()
    elif page == "Progress_Tracker": Progress_Tracker.app()
    elif page == "Admin_Panel": Admin_Panel.app()
