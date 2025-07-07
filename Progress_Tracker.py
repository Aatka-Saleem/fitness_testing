import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import asyncio
# import pandas as pd # This import is duplicated, removed in final output

def app():
    """
    The main function for the Progress Tracker page.
    Handles loading, displaying, and saving user progress data to Firestore.
    """
    st.header("📈 Your Fitness Progress")
    st.write("Track your weight, body measurements, and performance over time.")

    # --- 1. Check for Login and Backend ---
    if 'backend' not in st.session_state or 'user_info' not in st.session_state:
        st.error("Please log in to view your progress.")
        return
    
    backend = st.session_state.backend
    user_info = st.session_state.user_info
    user_id = user_info['uid']
    org_id = user_info['org_id']

    # --- 2. Load Data from Firestore ---
    # Use a unique key for the dataframe to prevent conflicts
    if 'progress_data_df' not in st.session_state:
        with st.spinner("Loading your progress history..."):
            logs = asyncio.run(backend.get_daily_logs(org_id, user_id))
            if logs:
                st.session_state.progress_data_df = pd.DataFrame(logs)
                # Ensure date column is in datetime format for charting
                # Localize to None to handle potential timezone issues from Firestore Timestamps
                st.session_state.progress_data_df['date'] = pd.to_datetime(st.session_state.progress_data_df['date']).dt.tz_localize(None)
                # Sort by date for proper time-series plotting
                st.session_state.progress_data_df = st.session_state.progress_data_df.sort_values('date').reset_index(drop=True)
            else:
                st.session_state.progress_data_df = pd.DataFrame(columns=['date', 'weight_kg', 'bmi', 'body_fat_percent', 'workout_duration_min', 'calories_burned'])

    progress_df = st.session_state.progress_data_df

    # --- 3. Log New Entry Form ---
    st.subheader("Log New Entry")
    with st.expander("Add New Progress Entry", expanded=True):
        with st.form("new_entry_form"):
            entry_date = st.date_input("Date", datetime.now())
            # --- MODIFIED: Set min_value and value to 0.0, add format="%.2f" ---
            entry_weight = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
            # -----------------------------------------------------------------
            entry_workout_duration = st.number_input("Workout Duration (min)", min_value=0, value=0)
            entry_calories_burned = st.number_input("Calories Burned (kcal)", min_value=0, value=0)
            
            submitted = st.form_submit_button("Add Entry")

    # Handle form submission outside the form block for reliability
    if submitted:
        # Basic validation for weight input
        if entry_weight <= 0:
            st.error("Weight must be a positive value to calculate metrics.")
        else:
            with st.spinner("Saving your entry..."):
                profile = asyncio.run(backend.get_user_profile(user_id, org_id))
                if profile:
                    metrics = profile.get('body_metrics', {})
                    height = metrics.get('height_cm', 175.0)
                    age = metrics.get('age', 30)
                    gender = metrics.get('gender', 'Male')

                    # Ensure height is positive before calculating BMI to avoid division by zero
                    if height <= 0:
                        st.error("Please set your height in the 'Body Metrics' section before logging entries.")
                        return

                    calculated_bmi = backend.calculate_bmi(entry_weight, height)
                    calculated_body_fat = backend.calculate_body_fat(calculated_bmi, age, gender)

                    new_log = {
                        'date': pd.to_datetime(entry_date),
                        'weight_kg': entry_weight,
                        'bmi': calculated_bmi,
                        'body_fat_percent': calculated_body_fat,
                        'workout_duration_min': entry_workout_duration,
                        'calories_burned': entry_calories_burned
                    }
                    
                    success = asyncio.run(backend.save_daily_log(user_id, org_id, new_log))

                    if success:
                        st.success("Entry saved!")
                        # Manually update the dataframe in session state for instant UI refresh
                        new_log_df = pd.DataFrame([new_log])
                        # Use concat and sort to add new data and maintain order
                        st.session_state.progress_data_df = pd.concat([st.session_state.progress_data_df, new_log_df], ignore_index=True)
                        st.session_state.progress_data_df = st.session_state.progress_data_df.sort_values('date').reset_index(drop=True)
                        st.rerun() # Rerun to update charts and table
                    else:
                        st.error("Failed to save entry.")
                else:
                    st.error("Could not load user profile to save entry.")

    # --- 4. Display Charts and Data ---
    st.subheader("Your Progress History")
    if progress_df.empty:
        st.info("No progress data yet. Add your first entry to see your progress charts!")
    else:
        display_df = progress_df.sort_values('date', ascending=False)
        st.dataframe(display_df, use_container_width=True)
        
        st.subheader("Progress Charts")
        # Ensure there's enough data to plot (at least two points for a line chart to show change)
        if len(progress_df) > 0:
            fig_weight = px.line(progress_df, x='date', y='weight_kg', title='Weight Over Time', markers=True)
            st.plotly_chart(fig_weight, use_container_width=True)

            # Add more charts for other metrics if desired
            fig_bmi = px.line(progress_df, x='date', y='bmi', title='BMI Over Time', markers=True, color_discrete_sequence=['orange'])
            st.plotly_chart(fig_bmi, use_container_width=True)

            fig_body_fat = px.line(progress_df, x='date', y='body_fat_percent', title='Body Fat Percentage Over Time', markers=True, color_discrete_sequence=['purple'])
            st.plotly_chart(fig_body_fat, use_container_width=True)

            fig_workout = px.bar(progress_df, x='date', y='workout_duration_min', title='Workout Duration Over Time', color_discrete_sequence=['green'])
            st.plotly_chart(fig_workout, use_container_width=True)

            fig_calories = px.bar(progress_df, x='date', y='calories_burned', title='Calories Burned Over Time', color_discrete_sequence=['red'])
            st.plotly_chart(fig_calories, use_container_width=True)

        else:
            st.info("Add more entries to see detailed progress charts.")

    # --- 5. AI Analysis of Progress ---
    st.subheader("AI Analysis of Your Progress")
    if st.button("Get AI Progress Analysis"):
        if progress_df.empty:
            st.warning("No progress data to analyze.")
        else:
            summary = progress_df.to_markdown(index=False)
            profile = asyncio.run(backend.get_user_profile(user_id, org_id))
            
            # Get current body metrics for more precise AI analysis
            current_metrics = profile.get('body_metrics', {})
            current_weight = current_metrics.get('weight_kg', 'N/A')
            current_height = current_metrics.get('height_cm', 'N/A')
            current_age = current_metrics.get('age', 'N/A')
            current_gender = current_metrics.get('gender', 'N/A')

            system_prompt = f"""You are an AI fitness progress analyst. Here is the user's logged fitness data:
{summary}

User's current body metrics:
- Weight: {current_weight} kg
- Height: {current_height} cm
- Age: {current_age} years
- Gender: {current_gender}

The user's fitness goal is {profile.get('fitness_goal', 'not set')}.
Analyze the data to identify trends, strengths, and areas for improvement. Provide actionable advice. Be encouraging and insightful.
If there's very little data, mention that more data is needed for a comprehensive analysis."""
            user_prompt = "Analyze my progress and give me some advice."
            
            with st.spinner("Analyzing your progress..."):
                response = asyncio.run(backend.get_ai_response(system_prompt, user_prompt))
                st.markdown(response)