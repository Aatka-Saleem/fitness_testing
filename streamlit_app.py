import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# --- Streamlit App ---
st.set_page_config(page_title="💪 Ultimate Fitness Planner", layout="wide")
st.title("🏋️‍♂️ Ultimate Fitness Planner")

# --- BMI & Body Fat Calculator ---
st.header("📏 Body Metrics Calculator")
col1, col2, col3 = st.columns(3)
weight = col1.number_input("Weight (kg)", min_value=20.0, value=60.0)  # Added min_value
height = col2.number_input("Height (cm)", min_value=50.0, value=170.0)  # Added min_value
age = col3.number_input("Age (years)", min_value=10, value=25)  # Added min_value
gender = st.selectbox("Gender", ["Male", "Female"])

bmi = weight / (height / 100) ** 2
st.metric("Your BMI", f"{bmi:.2f}")

# Rough body fat estimate (YMCA method)
if gender == "Male":
    body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
else:
    body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
st.metric("Estimated Body Fat %", f"{body_fat:.1f}%")

# --- Fitness Goal & AI Plan ---
st.header("🤖 AI-Generated Diet & Workout Plan")
goal = st.text_input("Fitness Goal (e.g., muscle gain, fat loss):", "muscle gain")

if st.button("Generate Plan"):
    with st.spinner("Generating your personalized plan..."):
        prompt = (
            f"Generate a **detailed 3-day diet and workout plan** for {gender}, "
            f"{age} years old, weighing {weight} kg, height {height} cm, aiming for {goal}. "
            "Include daily **nutritional breakdown**: protein, calcium, fiber, carbs, fats (amounts in grams or mg). "
            "Include **Day 1 (Core + Chest + Biceps), Day 2 (Legs + Triceps), Day 3 (Shoulders + Back + Core)** workouts. "
            "Present both plans in clear tables."
        )
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1500,
            top_p=1,
            stream=True,
        )
        response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            response += content
        st.success("Here’s your personalized plan!")
        st.markdown(response)

# --- Alternative Meal Suggestions ---
st.header("🥗 Alternative Meal Suggestions")
meal_type = st.selectbox("Choose alternative meal type", ["Vegetarian", "Vegan", "High-Protein"])
if st.button("Suggest Alternative Meals"):
    with st.spinner("Fetching alternative meals..."):
        alt_prompt = f"Suggest a **{meal_type}** version of the above diet plan, keeping nutritional balance."
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": alt_prompt}],
            temperature=1,
            max_completion_tokens=1000,
            top_p=1,
            stream=True,
        )
        alt_response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            alt_response += content
        st.markdown(alt_response)

# --- Progress Tracker ---
st.header("📈 Fitness Progress Tracker")
st.write("Input your progress data below:")
progress_data = {
    "Week": [1, 2, 3, 4],
    "Weight (kg)": [weight, weight - 0.5, weight - 1.0, weight - 1.5],
    "Waist (cm)": [80, 79, 78, 77]
}
df = pd.DataFrame(progress_data)
st.line_chart(df.set_index("Week"))

# --- Download Plan ---
st.header("💾 Download Your Plan")
dummy_text = "Your fitness plan goes here..."  # Replace with real content if needed
st.download_button("Download Plan as TXT", dummy_text.encode(), "fitness_plan.txt", "text/plain")
st.download_button("Download Progress as CSV", df.to_csv().encode(), "progress.csv", "text/csv")
