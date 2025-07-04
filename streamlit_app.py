import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import os


# Import the Backend class from backend_logic.py
from backend_logic import Backend

# Import your page content functions
import Body_Metrics
import Dashboard
import Diet_Planner
import Exercise_Library
import Progress_Tracker
import Workout_Planner # Assume Workout_Planner.py exists or will be created


# --- App Configuration ---
st.set_page_config(
    page_title="💪 Ultimate Fitness Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Backend in session state (only once per session) ---
# This makes the AI client and calculation functions available to all dashboards.
if "backend" not in st.session_state:
    st.session_state.backend = Backend()

# --- Helper Functions for CSS/Images ---
def get_base64_image(image_file):
    """Reads an image file and returns its base64 encoded string."""
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        return base64.b64encode(img_data).decode()
    except FileNotFoundError:
        print(f"Error: Background image '{image_file}' not found.")
        return None
    except Exception as e:
        print(f"Error loading image '{image_file}': {e}")
        return None

def load_css(b64_encoded_image=None, css_file_name="template/basic.html"):
    """Apply enhanced custom styling by loading from basic.html and adding dynamic background."""
    
    # Read static CSS from basic.html
    static_css_content = ""

    # Define primary color hex for dynamic use in CSS (e.g., for rgba colors)
    primary_hex = "4A90E2" # This should match the --primary in basic.html
    r = int(primary_hex[0:2], 16)
    g = int(primary_hex[2:4], 16)
    b = int(primary_hex[4:6], 16)
    primary_rgb = f"{r}, {g}, {b}"

    try:
        current_dir = os.path.dirname(__file__)
        css_file_path = os.path.join(current_dir, css_file_name)
        
        # ✅ FIX: Specify UTF-8 encoding explicitly
        with open(css_file_path, "r", encoding="utf-8") as f:
            static_css_content = f.read()
            # Extract just the <style> content if the file is a full HTML document
            if "<style>" in static_css_content and "</style>" in static_css_content:
                start = static_css_content.find("<style>") + len("<style>")
                end = static_css_content.find("</style>")
                static_css_content = static_css_content[start:end]

    except FileNotFoundError:
        st.error(f"CSS file '{css_file_name}' not found. Make sure it's in the '{os.path.dirname(css_file_path)}' directory.")
        static_css_content = "" # Fallback to empty if file not found
    except UnicodeDecodeError as e:
        st.error(f"Encoding error reading CSS file '{css_file_name}': {e}")
        st.info("Try saving the CSS file as UTF-8 encoding.")
        static_css_content = ""
    except Exception as e:
        st.error(f"Error reading CSS file '{css_file_name}': {e}")
        static_css_content = ""
        
    background_style = ""
    if b64_encoded_image:
        background_style = f"""
            .stApp {{
                background-image: 
                    linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.4)),
                    url(data:image/jpeg;base64,{b64_encoded_image});
                background-size: cover;
                background-position: center center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                min-height: 100vh;
            }}
            
            /* Add a subtle overlay pattern for texture */
            .stApp::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 2px, transparent 2px),
                    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
                background-size: 50px 50px;
                pointer-events: none;
                z-index: -1;
            }}
        """
    else:
        background_style = """
            .stApp {
                background: linear-gradient(135deg, var(--primary-light), var(--primary-dark));
                background-attachment: fixed;
                min-height: 100vh;
            }
        """

    # Combine static and dynamic CSS
    full_css = f"""
    <style>
        {background_style}
        {static_css_content}
    </style>
    """
    
    # Add primary_rgb to the CSS variables for use in rgba colors
    full_css = f"""
    <style>
        :root {{
            --primary-rgb: {primary_rgb};
        }}
        {background_style}
        {static_css_content}
    </style>
    """
    
    st.markdown(full_css, unsafe_allow_html=True)


# --- Inject Font Awesome CSS (Crucial for icons from basic.html and other pages) ---
st.markdown(
    """
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

# --- Check if image file exists before processing and apply CSS ---
# Ensure these paths are correct relative to your project or are absolute.
# For local development, absolute paths like this work. For deployment, consider relative paths or Streamlit's file uploader.
background_image_path = "E:/GEN AI/fitness_testing/fitness_bg.jpg" # Update if path changes
fitness_icon_path = "E:/GEN AI/fitness_testing/fitness_icon.png" # Update if path changes

b64_image = None
if os.path.exists(background_image_path):
    b64_image = get_base64_image(background_image_path)
else:
    print(f"Background image not found at: {background_image_path}")

# Apply CSS - pass the base64 image and the HTML file name
# Make sure 'template' folder exists in the same directory as this script, and basic.html is inside it.
load_css(b64_encoded_image=b64_image, css_file_name="template/basic.html")


# --- Initialize session state for current page ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# --- Sidebar Content ---
with st.sidebar:
    if os.path.exists(fitness_icon_path):
        st.image(fitness_icon_path, width=80)
    else:
        st.markdown("### 💪") # Fallback icon

    st.title("Fitness Navigation")

    # User Information Input - These are now shared directly with pages that need them
    if 'user_name' not in st.session_state:
        st.session_state.user_name = st.text_input("Your Name", "Fitness Enthusiast")

    if 'user_email' not in st.session_state:
        st.session_state.user_email = st.text_input("Email (optional)", "")

    st.markdown("---")

    # Page Navigation Buttons
    page_buttons = [
        {"label": "Home", "icon": "🏠", "key": "Home"},
        {"label": "Dashboard", "icon": "📊", "key": "Dashboard"},
        {"label": "Body Metrics", "icon": "📏", "key": "Body_Metrics"},
        {"label": "Diet Planner", "icon": "🥦", "key": "Diet_Planner"},
        {"label": "Workout Planner", "icon": "🗓️", "key": "Workout_Planner"},
        {"label": "Exercise Library", "icon": "📚", "key": "Exercise_Library"},
        {"label": "Progress Tracker", "icon": "📈", "key": "Progress_Tracker"},
    ]

    for btn in page_buttons:
        # Highlight active button visually (requires CSS in basic.html for .stButton > button[aria-pressed="true"])
        is_active = (st.session_state.current_page == btn['key'])
        button_style = "active" if is_active else ""
        
        # Streamlit's button doesn't directly support adding custom classes to the button element itself easily,
        # but the [aria-pressed="true"] selector in basic.html will handle the active state highlight
        if st.button(f"{btn['icon']} {btn['label']}", key=f"nav_btn_{btn['key']}",
                     use_container_width=True,
                     help=f"Go to {btn['label']} Page"):
            st.session_state.current_page = btn['key']
            st.rerun()

    # Get today's tip from the backend instance
    st.markdown("---")
    st.markdown("### 💡 Today's Tip")
    if st.session_state.backend:
        st.info(st.session_state.backend.get_todays_tip())
    else:
        st.info("Ensure your AI backend is configured to get daily tips!")

# --- Main Header Section ---
st.markdown(f"""
<div style="text-align: center;" class="fade-in">
    <h1>🏋️‍♂️ ULTIMATE FITNESS PLANNER</h1>
    <p style="font-size: 1.2rem; margin-bottom: 30px; color: #2c3e50; font-weight: 500;">Your AI-powered personal fitness companion</p>
</div>
""", unsafe_allow_html=True)


# --- Main Content Area - Page Routing ---
if st.session_state.current_page == "Home":
    st.header(f"Welcome, {st.session_state.user_name}!")
    st.markdown("""
    <div class="fade-in">
        <p style="font-size: 1.1rem; color: #2c3e50;">
            This is your central hub for managing your fitness journey.
            Use the sidebar to navigate through various sections of the app.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Your Fitness Overview")
    st.info("Start by exploring the Dashboard or planning your next workout!")

    col1, col2 = st.columns(2)
    with col1:
        st.slider("Daily Water Intake (liters)", 0.0, 5.0, 2.0)
    with col2:
        st.selectbox("Fitness Goal", ["Lose Weight", "Gain Muscle", "Improve Endurance", "Maintain Fitness"])

elif st.session_state.current_page == "Body_Metrics":
    try:
        Body_Metrics.app()
    except Exception as e:
        st.error(f"Could not load Body Metrics page. Error: {e}")
        st.warning("Please ensure 'Body_Metrics.py' is in the same directory and has an 'app()' function.")

elif st.session_state.current_page == "Dashboard":
    try:
        Dashboard.app()
    except Exception as e:
        st.error(f"Could not load Dashboard page. Error: {e}")
        st.warning("Please ensure 'Dashboard.py' exists with an 'app()' function.")

elif st.session_state.current_page == "Diet_Planner":
    try:
        Diet_Planner.app()
    except Exception as e:
        st.error(f"Could not load Diet Planner page. Error: {e}")
        st.warning("Please ensure 'Diet_Planner.py' exists with an 'app()' function.")

elif st.session_state.current_page == "Exercise_Library":
    try:
        Exercise_Library.app()
    except Exception as e:
        st.error(f"Could not load Exercise Library page. Error: {e}")
        st.warning("Please ensure 'Exercise_Library.py' exists with an 'app()' function.")

elif st.session_state.current_page == "Progress_Tracker":
    try:
        Progress_Tracker.app()
    except Exception as e:
        st.error(f"Could not load Progress Tracker page. Error: {e}")
        st.warning("Please ensure 'Progress_Tracker.py' exists with an 'app()' function.")

elif st.session_state.current_page == "Workout_Planner":
    try:
        Workout_Planner.app()
    except Exception as e:
        st.error(f"Could not load Workout Planner page. Error: {e}")
        st.warning("Please ensure 'Workout_Planner.py' exists with an 'app()' function.")

