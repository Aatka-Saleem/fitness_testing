import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st # Used for st.session_state to store the client
from datetime import datetime

# Load Environment Variables (ensure .env file with GROQ_API_KEY exists in your project root)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class Backend:
    """
    Manages all backend logic, including Groq API interactions and core calculations.
    """
    def __init__(self):
        # Initialize Groq client only if it's not already in session state
        # This prevents re-initialization on every rerun of the Streamlit app.
        if "groq_client" not in st.session_state:
            if not GROQ_API_KEY:
                st.error("GROQ_API_KEY not found in environment variables. Please set it up in a .env file.")
                st.session_state.groq_client = None # Set to None if API key is missing
            else:
                st.session_state.groq_client = Groq(api_key=GROQ_API_KEY)
        self.groq_client = st.session_state.groq_client

    def get_groq_client(self):
        """Returns the initialized Groq client."""
        return self.groq_client

    def get_ai_response(self, system_prompt, user_prompt, model="llama3-8b-8192", max_tokens=1500, temperature=0.7):
        """
        Sends a request to the Groq API and returns the AI's response.
        Handles streaming for better UX.
        """
        if not self.groq_client:
            st.error("Groq API client is not initialized. Please ensure your GROQ_API_KEY is set correctly.")
            return "AI service is unavailable."

        full_response = ""
        message_placeholder = st.empty()

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True, # Enable streaming for a better UX
            )

            for chunk in chat_completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # Show typing indicator
            message_placeholder.markdown(full_response) # Final message without typing indicator
            return full_response
        except Exception as e:
            st.error(f"Error communicating with Groq API: {e}")
            return "An error occurred while processing your request with AI."

    # --- Core Fitness Calculation Functions (Moved from Body_Metrics.py) ---
    def calculate_bmi(self, weight_kg, height_cm):
        """Calculates BMI."""
        if height_cm > 0:
            return round(weight_kg / ((height_cm / 100) ** 2), 2)
        return 0.0

    def calculate_body_fat(self, bmi, age, gender):
        """
        Calculates rough body fat estimate (YMCA method).
        gender: "Male" or "Female"
        """
        if gender == "Male":
            body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
        else:  # Female
            body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
        return round(body_fat, 1)

    def calculate_bmr(self, weight_kg, height_cm, age, gender):
        """
        Calculates Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation.
        gender: "Male" or "Female"
        """
        if gender == "Male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # Female
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return int(bmr) # BMR is typically an integer value

    # Add more shared utility functions here as needed
    def get_todays_tip(self):
        """Provides a rotating fitness tip for the day."""
        tips = [
            "Stay hydrated! Aim to drink at least 8 glasses of water daily.",
            "Rest is crucial for muscle growth. Ensure you get 7-8 hours of sleep.",
            "Consistency over intensity - regular moderate workouts beat occasional intense ones.",
            "Track your macros, not just calories, for optimal results.",
            "Incorporate strength training for overall health and metabolism boost.",
            "Listen to your body. Don't push through pain, rest if needed.",
            "Focus on whole, unprocessed foods for sustained energy.",
            "Set realistic goals and celebrate small victories.",
            "Warm-up before exercise and cool-down afterward to prevent injuries."
        ]
        return tips[datetime.now().day % len(tips)]
