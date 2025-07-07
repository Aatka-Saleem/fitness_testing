import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import plotly.graph_objects as go

def app():
    """
    The main function for the Dashboard page.
    It loads and displays all user-specific wellness data.
    """
    st.header("📊 Your Wellness Dashboard")

    # --- 1. Check for Login and Backend ---
    if 'backend' not in st.session_state or 'user_info' not in st.session_state:
        st.error("Please log in to view your dashboard.")
        return

    backend = st.session_state.backend
    user_info = st.session_state.user_info
    user_id = user_info['uid']
    org_id = user_info['org_id']

    st.markdown(f"## Welcome back, **{user_info.get('name', 'User')}**! 👋")

    # --- 2. Asynchronous Data Loading ---
    async def load_dashboard_data():
        profile_task = backend.get_user_profile(user_id, org_id)
        logs_task = backend.get_daily_logs(org_id, user_id)
        notifications_task = backend.get_notifications(org_id, user_id)
        # Run database calls concurrently for speed
        results = await asyncio.gather(profile_task, logs_task, notifications_task)
        return results

    with st.spinner("Loading your dashboard data..."):
        user_profile, daily_logs, notifications = asyncio.run(load_dashboard_data())

    if not user_profile:
        st.error("Could not load your user profile. Please try again.")
        return

    # --- Display Agent Notifications ---
    st.subheader("💡 Proactive Wellness Nudges")
    if not notifications:
        st.info("No new nudges from your AI agent. Keep up the great work!")
    else:
        for i, nudge in enumerate(notifications):
            nudge_id = nudge.get('id')
            col1, col2 = st.columns([4, 1])
            with col1:
                st.success(f"**AI Coach:** {nudge.get('message')}")
            with col2:
                # --- FIX: Only show the dismiss button if the nudge has an ID ---
                if nudge_id:
                    if st.button("Dismiss", key=f"dismiss_{nudge_id}_{i}", use_container_width=True):
                        success = asyncio.run(backend.mark_notification_as_read(org_id, user_id, nudge_id))
                        if success:
                            st.rerun() # Refresh the page to make the notification disappear
                        else:
                            st.error("Could not dismiss notification.")
                else:
                    # If there's no ID, we can't dismiss it, so don't show the button.
                    st.caption("Old notification")
    
    st.markdown("---")

    # --- 3. Key Metrics Display ---
    st.subheader("Key Metrics")
    metrics = user_profile.get('body_metrics', {})
    col1, col2, col3 = st.columns(3)
    # --- Cleaned display for Key Metrics ---
    default_weight = 70
    default_height = 175

    current_weight_kg = metrics.get('weight_kg', 0)
    current_height_cm = metrics.get('height_cm', 0)
    current_age = metrics.get('age', 0)
    current_gender = metrics.get('gender', 'Male')

    col1, col2, col3 = st.columns(3)

    if (
        current_weight_kg == default_weight and
        current_height_cm == default_height and
        current_age == 30
    ):
        # New user with default profile — show placeholders
        col1.metric("Weight", "—")
        col2.metric("BMI", "—")
        col3.metric("BMR", "—")
        st.warning("Please update your body metrics to personalize your dashboard.")
    else:
        col1.metric("Weight", f"{current_weight_kg} kg")
        col2.metric("BMI", f"{backend.calculate_bmi(current_weight_kg, current_height_cm):.1f}")
        col3.metric("BMR", f"{backend.calculate_bmr(current_weight_kg, current_height_cm, current_age, current_gender)} kcal")


    # --- 4. Weekly Activity Summary Chart ---
    st.subheader("Weekly Activity Summary")
    if not daily_logs:
        st.info("Log some progress in the 'Progress Tracker' to see your weekly activity summary!")
    else:
        df = pd.DataFrame(daily_logs)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            if df['date'].dt.tz is not None:
                df['date'] = df['date'].dt.tz_localize(None)
            df['date'] = df['date'].dt.date
            
            all_7_days = [(datetime.now().date() - timedelta(days=i)) for i in range(7)]
            df_full_week = pd.DataFrame({'date': all_7_days})
            
            df_merged = df_full_week.merge(df, on='date', how='left').fillna(0)
            df_merged = df_merged.sort_values('date')
            df_merged['Day'] = pd.to_datetime(df_merged['date']).dt.strftime('%a')

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_merged['Day'], y=df_merged['calories_burned'], name='Calories Burned', marker_color='#3498db'))
            fig.add_trace(go.Scatter(x=df_merged['Day'], y=df_merged['workout_duration_min'], name='Duration (min)', yaxis='y2', line=dict(color='#2ecc71', width=4)))
            
            fig.update_layout(
                yaxis=dict(title='Calories Burned'),
                yaxis2=dict(title='Duration (min)', overlaying="y", side="right"),
                title_text='Weekly Workout Performance',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)')
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- 5. AI Insights on Weekly Summary ---
    st.subheader("AI Insights on Your Performance")
    if st.button("Get AI Weekly Analysis"):
        if not daily_logs:
            st.warning("Not enough data to analyze. Log some progress first!")
        else:
            summary = pd.DataFrame(daily_logs).to_markdown(index=False)
            system_prompt = f"Analyze this user's weekly fitness data and provide 2-3 concise, actionable insights. The user's goal is {user_profile.get('fitness_goal', 'not set')}. Data:\n{summary}"
            user_prompt = "What are the key trends and what should I focus on next week?"
            
            with st.spinner("Analyzing your performance..."):
                response = asyncio.run(backend.get_ai_response(system_prompt, user_prompt))
                st.markdown(response)

    # --- 6. Quick Actions ---
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("🏃‍♂️ Start Workout", use_container_width=True):
        st.session_state.current_page = "Workout_Planner"; st.rerun()
    if col2.button("🍎 Log Meal", use_container_width=True):
        st.session_state.current_page = "Diet_Planner"; st.rerun()
    if col3.button("⚖️ Update Metrics", use_container_width=True):
        st.session_state.current_page = "Body_Metrics"; st.rerun()
    if col4.button("📈 Log Progress", use_container_width=True):
        st.session_state.current_page = "Progress_Tracker"; st.rerun()
