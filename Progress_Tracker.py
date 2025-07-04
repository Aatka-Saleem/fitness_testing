import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px # For charting progress

def app():
    backend = st.session_state.backend # Get the backend instance

    st.header("📈 Your Fitness Progress")
    st.write("Track your weight, body measurements, and performance over time.")

    # Initialize data if not in session state with standardized column names
    if 'progress_data' not in st.session_state:
        st.session_state.progress_data = pd.DataFrame(
            columns=['date', 'weight_kg', 'bmi', 'body_fat_percent', 'workout_duration_min', 'calories_burned']
        )
        # Add some initial dummy data if empty for better visualization on first run
        # Use values that align with the type (e.g., float for weight, int for duration/calories)
        if st.session_state.progress_data.empty:
            # Safely get default backend values, assuming they are available
            dummy_height = st.session_state.get('height_cm', 175.0)
            dummy_age = st.session_state.get('age', 30)
            dummy_gender = st.session_state.get('gender', 'Male')

            initial_data = {
                'date': [datetime(2023, 1, 1), datetime(2023, 1, 8), datetime(2023, 1, 15)],
                'weight_kg': [75.0, 74.5, 74.0],
                'bmi': [backend.calculate_bmi(75.0, dummy_height), backend.calculate_bmi(74.5, dummy_height), backend.calculate_bmi(74.0, dummy_height)],
                'body_fat_percent': [backend.calculate_body_fat(backend.calculate_bmi(75.0, dummy_height), dummy_age, dummy_gender), 
                                     backend.calculate_body_fat(backend.calculate_bmi(74.5, dummy_height), dummy_age, dummy_gender),
                                     backend.calculate_body_fat(backend.calculate_bmi(74.0, dummy_height), dummy_age, dummy_gender)],
                'workout_duration_min': [60, 75, 70],
                'calories_burned': [400, 500, 480]
            }
            st.session_state.progress_data = pd.DataFrame(initial_data)
            st.session_state.progress_data['date'] = pd.to_datetime(st.session_state.progress_data['date']) # Ensure datetime type


    st.subheader("Log New Entry")
    with st.expander("Add New Progress Entry"):
        col1, col2 = st.columns(2)
        entry_date = col1.date_input("Date", datetime.now(), key="progress_date")
        
        # Set default value for weight based on last entry or a reasonable default
        # Ensure default_weight is a float
        default_weight = float(st.session_state.progress_data['weight_kg'].iloc[-1]) if not st.session_state.progress_data.empty else 70.0
        entry_weight = col2.number_input("Weight (kg)", min_value=20.0, value=default_weight, key="progress_weight", step=0.1)
        
        col3, col4 = st.columns(2)
        
        # Use saved height, age, and gender from Body Metrics page or default if not set
        current_height_cm = st.session_state.get('height_cm', 170.0) 
        current_age = st.session_state.get('age', 30) 
        current_gender = st.session_state.get('gender', 'Male') # Use saved gender or default
        
        # Use backend for calculations
        calculated_bmi = backend.calculate_bmi(entry_weight, current_height_cm)
        calculated_body_fat = backend.calculate_body_fat(calculated_bmi, current_age, current_gender)

        entry_bmi = col3.number_input("BMI (calculated)", value=float(f"{calculated_bmi:.2f}"), disabled=True, key="progress_bmi")
        entry_body_fat = col4.number_input("Body Fat (%) (estimated)", value=float(f"{calculated_body_fat:.1f}"), disabled=True, key="progress_body_fat")
        
        # Optional workout/calorie data
        entry_workout_duration = st.number_input("Workout Duration (min)", min_value=0, value=0, key="progress_workout_duration")
        entry_calories_burned = st.number_input("Calories Burned (kcal)", min_value=0, value=0, key="progress_calories_burned")

        if st.button("Add Entry", key="add_progress_entry"):
            # Check for duplicate dates to prevent adding multiple entries for the same day
            # Convert entry_date to datetime for comparison with DataFrame 'date' column
            entry_date_dt = datetime(entry_date.year, entry_date.month, entry_date.day)
            
            if not st.session_state.progress_data.empty and \
               entry_date_dt.date() in st.session_state.progress_data['date'].dt.date.tolist():
                st.warning(f"An entry for {entry_date.strftime('%Y-%m-%d')} already exists. Please choose a different date or update the existing entry.")
            else:
                new_entry = {
                    'date': entry_date_dt, # Store as datetime object
                    'weight_kg': entry_weight,
                    'bmi': calculated_bmi,
                    'body_fat_percent': calculated_body_fat,
                    'workout_duration_min': entry_workout_duration,
                    'calories_burned': entry_calories_burned
                }
                # Convert to DataFrame row and append
                new_entry_df = pd.DataFrame([new_entry])
                st.session_state.progress_data = pd.concat([st.session_state.progress_data, new_entry_df], ignore_index=True)
                st.session_state.progress_data['date'] = pd.to_datetime(st.session_state.progress_data['date']) # Ensure Date is datetime type
                st.session_state.progress_data = st.session_state.progress_data.sort_values(by='date').reset_index(drop=True)
                st.success("Progress entry added!")
    
    st.subheader("Your Progress Data")
    if not st.session_state.progress_data.empty:
        st.dataframe(st.session_state.progress_data.style.format({
            'weight_kg': "{:.1f}", 
            'bmi': "{:.2f}", 
            'body_fat_percent': "{:.1f}%",
            'date': lambda x: x.strftime('%Y-%m-%d') # Format for display
        }), use_container_width=True)

        st.subheader("Progress Charts")
        
        # Weight Progress
        fig_weight = px.line(st.session_state.progress_data, x='date', y='weight_kg', 
                             title='Weight Over Time', markers=True, 
                             labels={'weight_kg': 'Weight (kg)', 'date': 'Date'})
        fig_weight.update_xaxes(dtick="M1", tickformat="%b\n%Y") # Monthly ticks
        fig_weight.update_traces(line_color="#3498db") # Changed to hardcoded primary color
        st.plotly_chart(fig_weight, use_container_width=True)

        # BMI Progress
        fig_bmi = px.line(st.session_state.progress_data, x='date', y='bmi', 
                          title='BMI Over Time', markers=True,
                          labels={'bmi': 'BMI', 'date': 'Date'})
        fig_bmi.update_xaxes(dtick="M1", tickformat="%b\n%Y")
        fig_bmi.update_traces(line_color="#E74C3C") # Using a specific color for contrast or theme
        st.plotly_chart(fig_bmi, use_container_width=True)

        # Body Fat Progress (New Chart)
        fig_body_fat = px.line(st.session_state.progress_data, x='date', y='body_fat_percent', 
                               title='Body Fat Percentage Over Time', markers=True,
                               labels={'body_fat_percent': 'Body Fat (%)', 'date': 'Date'})
        fig_body_fat.update_xaxes(dtick="M1", tickformat="%b\n%Y")
        fig_body_fat.update_traces(line_color="#8E44AD") # Purple color
        st.plotly_chart(fig_body_fat, use_container_width=True)


        # Workout Duration / Calories Burned
        if 'workout_duration_min' in st.session_state.progress_data.columns and \
           'calories_burned' in st.session_state.progress_data.columns:
            # Melt the DataFrame to plot multiple columns on the same y-axis for bar chart
            melted_df = st.session_state.progress_data.melt(id_vars=['date'], value_vars=['workout_duration_min', 'calories_burned'], var_name='Metric', value_name='Value')
            fig_workout_calories = px.bar(melted_df, x='date', y='Value', color='Metric', 
                                         title='Workout Performance Over Time',
                                         labels={'Value':'Value', 'Metric':'Metric', 'date': 'Date'},
                                         barmode='group', # Use group mode for clarity
                                         color_discrete_map={
                                             'workout_duration_min': '#2ecc71', # Green
                                             'calories_burned': '#f39c12' # Orange
                                         }) 
            fig_workout_calories.update_xaxes(dtick="M1", tickformat="%b\n%Y")
            st.plotly_chart(fig_workout_calories, use_container_width=True)

        # --- AI Insights on Progress ---
        st.markdown("---")
        st.subheader("AI Analysis of Your Progress")
        
        # Convert DataFrame to a string suitable for LLM input
        progress_summary = st.session_state.progress_data.to_markdown(index=False) # Use markdown for better LLM parsing
        
        ai_progress_query = st.text_area(
            "Ask AI to analyze your progress (e.g., 'What trends do you see in my weight?', 'How can I improve my calories burned?'):",
            "Analyze my weight and body fat trends over time. What insights do you have and what adjustments should I consider?",
            height=150,
            key="ai_progress_query_text_area" # Unique key
        )
        if st.button("Get AI Progress Analysis", key="ai_progress_analysis_btn"):
            if ai_progress_query:
                system_prompt_progress = f"""
                You are an AI fitness progress analyst.
                Here is the user's logged fitness progress data:
                {progress_summary}

                User's Overall Fitness Goal: {st.session_state.get('fitness_goal', 'Not set')}.
                User's Activity Level: {st.session_state.get('activity_level', 'Not set')}.
                User's Age: {st.session_state.get('age', 'Not set')} years.
                User's Gender: {st.session_state.get('gender', 'Not set')}.

                Analyze the provided data to identify trends, strengths, and areas for improvement.
                Provide actionable advice based on the user's specific question and their overall progress.
                Be encouraging and insightful.
                """
                with st.spinner("Analyzing your progress data..."):
                    backend.get_ai_response(system_prompt_progress, ai_progress_query)
            else:
                st.warning("Please enter a question for the AI about your progress.")

    else:
        st.info("No progress data yet. Add your first entry above to see your progress charts!")
