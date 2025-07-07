import streamlit as st
import asyncio

# No need for Lottie helper functions if not used.

def app():
    backend = st.session_state.backend # Get the backend instance

    st.header("🗓️ AI-Powered Workout Planner")
    st.write("Generate custom workout plans tailored to your fitness level, goals, and available equipment.")

    st.subheader("Your Workout Preferences")

    # Retrieve user name from session state
    user_name = st.session_state.get('user_name', 'Fitness Enthusiast')

    # --- Retrieve User Metrics from Body_Metrics via Session State ---
    # These values should be set and updated by the Body_Metrics.py page
    weight_kg = st.session_state.get('weight_kg', 70.0)
    height_cm = st.session_state.get('height_cm', 175.0)
    age = st.session_state.get('age', 30)
    gender = st.session_state.get('gender', "Male")
    activity_level = st.session_state.get('activity_level', "Moderately Active")
    fitness_goal_overall = st.session_state.get('fitness_goal', "Maintain Fitness") # Renamed to avoid clash with workout_goal

    # Calculated metrics from Body_Metrics (or recalculated here if needed, but safer to assume Body_Metrics sets them)
    bmi = st.session_state.get('bmi', backend.calculate_bmi(weight_kg, height_cm))
    bmr = st.session_state.get('bmr', backend.calculate_bmr(weight_kg, height_cm, age, gender))
    tdee = st.session_state.get('tdee', bmr * 1.55) # Placeholder if TDEE isn't consistently passed

    col1, col2 = st.columns(2)
    fitness_level = col1.selectbox("Your Current Fitness Level", 
                                   ["Beginner", "Intermediate", "Advanced"], 
                                   key="fitness_level")
    # Default workout_goal to the overall fitness_goal if available and matches options
    default_workout_goal_index = 0 # Default to "Strength"
    workout_goal_options = ["Strength", "Endurance", "Weight Loss", "Muscle Gain", "Flexibility & Mobility"]
    if fitness_goal_overall in workout_goal_options:
        default_workout_goal_index = workout_goal_options.index(fitness_goal_overall)
    elif fitness_goal_overall == "Maintain Fitness": # Specific mapping
        default_workout_goal_index = workout_goal_options.index("Endurance") # or "Strength", depends on interpretation
    elif fitness_goal_overall == "General Health":
        default_workout_goal_index = workout_goal_options.index("Endurance") # or "Strength"
    
    workout_goal = col2.selectbox("Primary Workout Goal", 
                                 workout_goal_options, 
                                 index=default_workout_goal_index, # Use determined index
                                 key="workout_goal")

    available_equipment = st.multiselect("Available Equipment", 
                                         ["None (Bodyweight)", "Dumbbells", "Barbell", "Resistance Bands", 
                                          "Kettlebell", "Gym Access (Full Equipment)"],
                                         key="available_equipment")

    workout_duration = st.slider("Preferred Workout Duration (minutes)", 
                                  min_value=15, max_value=120, value=45, step=5, 
                                  key="workout_duration")
    
    days_per_week = st.slider("Workout Days Per Week", 
                              min_value=1, max_value=7, value=3, step=1, 
                              key="days_per_week")

    st.subheader("Generate Custom Workout Plan")

    ai_workout_prompt = st.text_area(
        f"Tell AI more about your workout needs, {user_name} (e.g., 'A 3-day split focusing on upper/lower body', 'Full-body routine for home without equipment', 'Help me structure my warm-up and cool-down'):",
        height=150,
        key="ai_workout_prompt_text_area" # Unique key
    )

    if st.button("✨ Generate Workout Plan", key="generate_workout_plan_btn"):
        if not ai_workout_prompt:
            st.warning("Please provide a prompt for your workout plan.")
        else:
            # --- Construct a comprehensive system prompt for the AI with ALL relevant data ---
            system_prompt_workout = f"""
            You are an AI personal trainer specializing in creating workout plans.
            Generate a detailed workout plan based on the user's complete profile and specific request.

            User Profile:
            - Name: {user_name}
            - Current Weight: {weight_kg} kg
            - Current Height: {height_cm} cm
            - Age: {age} years
            - Gender: {gender}
            - Activity Level: {activity_level}
            - Overall Fitness Goal: {fitness_goal_overall}
            - Current BMI: {bmi:.1f}
            - Current BMR: {bmr:.0f} calories/day
            - Current TDEE: {tdee:.0f} calories/day
            - User's Stated Fitness Level: {fitness_level}
            - Primary Workout Goal: {workout_goal}
            - Available Equipment: {', '.join(available_equipment) if available_equipment else 'None'}
            - Preferred Duration Per Session: {workout_duration} minutes
            - Desired Workout Days Per Week: {days_per_week}

            Consider all the above context, especially the user's physical stats, fitness level, goals,
            available equipment, and preferred duration/frequency.
            
            Structure the workout plan clearly, e.g., by day (Monday: Upper Body, Tuesday: Rest, etc.) or by workout type (Workout A, Workout B, Workout C).
            For each workout session, include:
            - **Warm-up:** (e.g., 5-10 minutes light cardio and dynamic stretches)
            - **Main Exercises:**
                - For each exercise, specify: Exercise Name, Sets and Reps (e.g., 3 sets of 8-12 reps) or Duration (for cardio/flexibility).
                - Add brief instructions for proper form or focus (e.g., "focus on controlled eccentric", "engage core").
                - Suggest progressive overload strategies (e.g., "aim to increase weight next week", "add 5 minutes to cardio").
            - **Cool-down:** (e.g., 5-10 minutes static stretches)
            
            Provide a realistic, actionable, and safe plan. If the user asks for a specific workout split (e.g., 3-day full body, 4-day upper/lower), adhere to that.
            """
            
            with st.spinner("Generating your personalized workout plan..."):
                generated_plan = asyncio.run(backend.get_ai_response(system_prompt_workout, ai_workout_prompt))
                # generated_plan = backend.get_ai_response(system_prompt_workout, ai_workout_prompt)
                
                if generated_plan:
                    st.session_state.last_generated_workout_plan = generated_plan
                    # Store a summary for Dashboard to display
                    st.session_state.generated_workout_plan_summary = \
                        f"{days_per_week} days/week, {workout_duration} min/session. Goal: {workout_goal}." \
                        f" Equipment: {', '.join(available_equipment) if available_equipment else 'None'}."
                    st.success("Workout plan generated successfully!")

    # Display the last generated workout plan
    if 'last_generated_workout_plan' in st.session_state and st.session_state.last_generated_workout_plan:
        st.subheader("Your Generated Workout Plan")
        st.markdown(st.session_state.last_generated_workout_plan)
    else:
        st.info("Your personalized workout plan will appear here once generated.")
