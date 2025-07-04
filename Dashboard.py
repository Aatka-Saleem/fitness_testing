import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd 

def app():
    backend = st.session_state.backend # Get the backend instance

    st.markdown(f"""
    <div style="animation: fadeIn 1s;">
        <h2>Welcome back, {st.session_state.user_name}! 👋</h2>
        <p>Today is {datetime.now().strftime('%A, %B %d, %Y')}. Let's crush your fitness goals!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Dynamic Dashboard Metrics ---
    # Fetch latest metrics from session state, which are updated by Body_Metrics.py and Progress_Tracker.py
    current_weight = st.session_state.get('weight_kg', 70.0)
    current_bmi = st.session_state.get('bmi', backend.calculate_bmi(current_weight, st.session_state.get('height_cm', 175.0)))
    
    # Placeholder for daily calories and water intake.
    # These would typically come from a meal logging or water tracking feature.
    # For now, let's use sensible defaults from Diet_Planner or calculated values.
    daily_calorie_target = st.session_state.get('daily_calorie_target', 2000) 
    
    tracked_calories_today = 0
    tracked_water_today = 0 # Placeholder for water tracking, needs dedicated logging if desired
    
    if 'progress_data' in st.session_state and not st.session_state.progress_data.empty:
        today_str = datetime.now().strftime('%Y-%m-%d')
        # Ensure 'date' column is datetime and then convert to date string for comparison
        st.session_state.progress_data['date'] = pd.to_datetime(st.session_state.progress_data['date'])
        today_entry = st.session_state.progress_data[
            st.session_state.progress_data['date'].dt.strftime('%Y-%m-%d') == today_str
        ]
        
        if not today_entry.empty:
            # IMPORTANT: Use the standardized column names from progress_tracker.py
            if 'calories_burned' in today_entry.columns:
                tracked_calories_today = today_entry['calories_burned'].sum() 
            # If you add 'water_intake_liters' to progress_data or a separate log
            # if 'water_intake_liters' in today_entry.columns:
            #     tracked_water_today = today_entry['water_intake_liters'].sum()
    
    # Target water intake can be calculated using a helper if not stored
    recommended_water_intake = st.session_state.get('water_intake', 3.0) # From Body_Metrics

    # Calculate weekly workout count from progress_data
    weekly_workouts = 0
    target_weekly_workouts = st.session_state.get('days_per_week', 3) # From Workout_Planner if set, else default

    if 'progress_data' in st.session_state and not st.session_state.progress_data.empty:
        # Get data for the last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        st.session_state.progress_data['date'] = pd.to_datetime(st.session_state.progress_data['date']) # Ensure datetime
        recent_progress = st.session_state.progress_data[st.session_state.progress_data['date'] >= seven_days_ago].copy()
        
        # Ensure 'workout_duration_min' and 'calories_burned' columns exist before trying to access
        if 'workout_duration_min' in recent_progress.columns and 'calories_burned' in recent_progress.columns:
            # Count unique dates where workout duration or calories burned were greater than 0
            weekly_workouts = recent_progress[
                (recent_progress['workout_duration_min'] > 0) | 
                (recent_progress['calories_burned'] > 0)
            ]['date'].dt.date.nunique()
    
    weekly_workout_percentage = (weekly_workouts / target_weekly_workouts * 100) if target_weekly_workouts > 0 else 0
    # Explicitly cast to float for delta to ensure compatibility
    weekly_workout_delta = float(weekly_workout_percentage) 

    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Pass the formatted string to the value, and the numerical delta
        st.metric("Weekly Workouts", f"{weekly_workouts}/{target_weekly_workouts}", delta=weekly_workout_delta, delta_color="normal")
    with col2:
        # Explicitly cast to int for delta
        calories_delta = int(tracked_calories_today - daily_calorie_target)
        st.metric("Calories Today", f"{tracked_calories_today}/{int(daily_calorie_target)}", delta=calories_delta)
    with col3:
        # Calculate water delta percentage and cast to float or format as string
        water_delta_percent = (tracked_water_today / recommended_water_intake * 100) if recommended_water_intake > 0 else 0
        st.metric("Water Intake", f"{tracked_water_today:.1f}/{recommended_water_intake:.1f}L", delta=f"{water_delta_percent:+.0f}%" if recommended_water_intake > 0 else "0%", delta_color="normal")
    
    # --- Dynamic Weekly Activity Summary with Plotly ---
    st.subheader("Weekly Activity Summary")
    
    if 'progress_data' in st.session_state and not st.session_state.progress_data.empty:
        df_progress = st.session_state.progress_data.copy()
        df_progress['date_only'] = df_progress['date'].dt.date # For grouping by day
        
        # Ensure required columns for plotting exist
        required_cols = ['calories_burned', 'workout_duration_min'] # Use standardized names
        for col in required_cols:
            if col not in df_progress.columns:
                df_progress[col] = 0 # Add missing columns with default 0

        # Aggregate data by day for the last 7 days
        all_last_7_days = [datetime.now().date() - timedelta(days=i) for i in range(7)][::-1] # Ascending order
        
        recent_activity_agg = df_progress[df_progress['date_only'].isin(all_last_7_days)].groupby('date_only').agg(
            {'calories_burned': 'sum', 'workout_duration_min': 'sum'} # Use standardized names
        ).reset_index()
        
        # Merge with all_last_7_days to ensure all days are represented, even if no activity
        full_week_df = pd.DataFrame({'date_only': all_last_7_days})
        recent_activity = pd.merge(full_week_df, recent_activity_agg, on='date_only', how='left').fillna(0)
        
        recent_activity['Day'] = recent_activity['date_only'].apply(lambda x: x.strftime('%a')) # Abbreviated day names
        
        # Create the figure with two y-axes
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=recent_activity['Day'],
            y=recent_activity['calories_burned'], # Use standardized name
            name='Calories Burned',
            marker_color='#3498db'
        ))
        
        fig.add_trace(go.Scatter(
            x=recent_activity['Day'],
            y=recent_activity['workout_duration_min'], # Use standardized name
            name='Duration (min)',
            marker_color='#2ecc71',
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title={
                'text': 'Weekly Workout Performance',
                'font': {'size': 20, 'color': '#2c3e50', 'family': 'Montserrat'}
            },
            xaxis_tickfont_size=14,
            yaxis=dict(
                title=dict(
                    text='Calories Burned',
                    font=dict(size=16, color='#2c3e50')
                ),
                tickfont=dict(size=14, color='#7f8c8d'),
            ),
            yaxis2=dict(
                title=dict(
                    text='Duration (min)',
                    font=dict(size=16, color='#2c3e50')
                ),
                tickfont=dict(size=14, color='#7f8c8d'),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255, 255, 255, 0.7)',
                bordercolor='rgba(0, 0, 0, 0.1)',
                font=dict(color='#2c3e50')
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log some progress entries to see your weekly activity summary!")

    # --- AI Insights on Weekly Summary ---
    st.subheader("AI Insights on Your Weekly Performance")
    
    ai_analysis_placeholder = st.empty()
    
    if st.button("Get AI Weekly Analysis", key="ai_analysis_dashboard_btn"):
        if 'progress_data' in st.session_state and not st.session_state.progress_data.empty:
            df_progress = st.session_state.progress_data.copy()
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_progress_for_ai = df_progress[df_progress['date'] >= seven_days_ago].copy() # Ensure copy to avoid SettingWithCopyWarning
            
            # Ensure columns exist before passing to AI
            if 'workout_duration_min' not in recent_progress_for_ai.columns:
                recent_progress_for_ai['workout_duration_min'] = 0
            if 'calories_burned' not in recent_progress_for_ai.columns:
                recent_progress_for_ai['calories_burned'] = 0

            if not recent_progress_for_ai.empty:
                # Use standardized column names in the summary for LLM
                weekly_data_summary = recent_progress_for_ai[['date', 'weight_kg', 'workout_duration_min', 'calories_burned']].to_markdown(index=False)
                
                system_prompt_dashboard = f"""
                You are an AI fitness coach specializing in performance analysis.
                Here is the user's recent activity data (last 7 days):
                {weekly_data_summary}
                
                The user's current fitness goal is: {st.session_state.get('fitness_goal', 'Not set')}.
                Their typical activity level is: {st.session_state.get('activity_level', 'Not set')}.

                Analyze the provided data to identify trends, consistency, and areas for improvement.
                Provide concise, actionable insights and recommendations for the upcoming week.
                Consider rest days (0 calories/duration) in your analysis.
                For example, if workout duration is low, suggest increasing it; if calories burned are inconsistent, suggest finding a routine.
                """
                user_prompt = "Analyze my recent weekly activity and performance, then suggest concrete steps for improvement or areas to focus on for the upcoming week based on my data and goal."
                
                with st.spinner("Analyzing your weekly performance..."):
                    backend.get_ai_response(system_prompt_dashboard, user_prompt)
            else:
                st.info("No recent progress data (last 7 days) to analyze. Please log some entries in the 'Progress Tracker' tab first.")
        else:
            st.info("No progress data available to analyze. Please log some entries in the 'Progress Tracker' tab first.")

    # --- Dynamic "Today's Plan" ---
    st.subheader("Today's Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Attempt to fetch dynamic workout plan summary from Workout_Planner state
        workout_plan_summary = "No workout planned. Generate one in 'Workout Planner'."
        if 'last_generated_workout_plan' in st.session_state and st.session_state.last_generated_workout_plan:
            workout_plan_display = f"Workout: {st.session_state.get('workout_goal', 'N/A')} Focus<br>" \
                                   f"Duration: {st.session_state.get('workout_duration', 'N/A')} mins<br>" \
                                   f"Days/week: {st.session_state.get('days_per_week', 'N/A')}"
        else:
            workout_plan_display = "No workout planned. Generate one in 'Workout Planner'."

        st.markdown(f"""
        <div class="calendar-day active">
            <h4><i class="fas fa-dumbbell"></i> Workout Plan</h4>
            <p>{workout_plan_display}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Attempt to fetch dynamic nutrition goals from Diet_Planner state
        protein_goal = st.session_state.get('protein_goal', 'N/A')
        carbs_goal = st.session_state.get('carbs_goal', 'N/A')
        fats_goal = st.session_state.get('fats_goal', 'N/A')
        daily_calorie_target_display = st.session_state.get('daily_calorie_target', 'N/A')
        
        st.markdown(f"""
        <div class="calendar-day">
            <h4><i class="fas fa-utensils"></i> Nutrition Goals</h4>
            <p><i class="fas fa-fire"></i> Calories: {daily_calorie_target_display} kcal</p>
            <p><i class="fas fa-apple-alt"></i> Protein: {protein_goal}g</p>
            <p><i class="fas fa-bread-slice"></i> Carbs: {carbs_goal}g</p>
            <p><i class="fas fa-oil-can"></i> Fats: {fats_goal}g</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- Quick Actions (using Streamlit buttons for proper navigation) ---
    st.subheader("Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏃‍♂️ Start Workout", key="start_workout_btn", use_container_width=True):
            st.session_state.current_page = "Workout_Planner" 
            st.rerun()
        
    with col2:
        if st.button("🍎 Log Meal", key="log_meal_btn", use_container_width=True):
            st.session_state.current_page = "Diet_Planner" 
            st.rerun()

    with col3:
        if st.button("⚖️ Update Metrics", key="update_metrics_btn", use_container_width=True):
            st.session_state.current_page = "Body_Metrics" 
            st.rerun()
        
    with col4:
        if st.button("📈 Log Progress", key="log_progress_btn", use_container_width=True):
            st.session_state.current_page = "Progress_Tracker" 
            st.rerun()
