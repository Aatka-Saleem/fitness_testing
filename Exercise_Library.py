import streamlit as st
# No need for Lottie helper functions if not used.

def app():
    backend = st.session_state.backend # Get the backend instance

    st.header("📚 AI-Enhanced Exercise Library")
    st.write("Browse a comprehensive library of exercises with detailed instructions, and get AI recommendations.")

    # --- Manual Exercise Library (Existing) ---
    st.subheader("Explore Exercises by Muscle Group")

    muscle_groups = ["Chest", "Back", "Legs", "Shoulders", "Arms", "Core", "Cardio", "Full Body"]
    selected_group = st.selectbox("Select a Muscle Group", muscle_groups, key="muscle_group_select")

    # Display content based on selection (can be expanded with more details/videos)
    exercise_details = {
        "Chest": {
            "description": "Exercises for pectoral muscles.",
            "exercises": [
                {"name": "Bench Press", "desc": "Great for overall chest development. Can be done with barbell or dumbbells.", "video_url": "https://www.youtube.com/watch?v=SCVCLChPQFY"},
                {"name": "Push-ups", "desc": "Classic bodyweight exercise, targets chest, shoulders, triceps. Modify for difficulty.", "video_url": "https://www.youtube.com/watch?v=IODxDxX7yrg"},
                {"name": "Dumbbell Flyes", "desc": "Isolates chest muscles, focuses on stretch.", "video_url": "https://www.youtube.com/watch?v=Z5rnE8f_H2k"},
            ]
        },
        "Back": {
            "description": "Exercises for lats, rhomboids, trapezius, and lower back.",
            "exercises": [
                {"name": "Pull-ups", "desc": "Excellent for upper back and lats. Great bodyweight strength builder.", "video_url": "https://www.youtube.com/watch?v=eGo4dqzLg3A"},
                {"name": "Bent Over Rows", "desc": "Builds thickness and strength in the mid-back.", "video_url": "https://www.youtube.com/watch?v=Zp801D352h8"},
                {"name": "Lat Pulldowns", "desc": "Targets the lats, good for building a V-taper.", "video_url": "https://www.youtube.com/watch?v=0YGQ5bY6V2w"},
            ]
        },
        "Legs": {
            "description": "Exercises for quadriceps, hamstrings, glutes, and calves.",
            "exercises": [
                {"name": "Squats", "desc": "Fundamental exercise for lower body strength and mass. Many variations.", "video_url": "https://www.youtube.com/watch?v=ultWZbKWUjg"},
                {"name": "Deadlifts", "desc": "Full-body strength exercise, excellent for hamstrings, glutes, and back.", "video_url": "https://www.youtube.com/watch?v=ytQyNlO2vN8"},
                {"name": "Lunges", "desc": "Unilateral exercise, improves balance and targets individual leg muscles.", "video_url": "https://www.youtube.com/watch?v=QO2z-bS2C8E"},
            ]
        },
        "Shoulders": {
            "description": "Exercises for deltoids (front, side, rear) and trapezius.",
            "exercises": [
                {"name": "Overhead Press", "desc": "Builds strong shoulders and triceps.", "video_url": "https://www.youtube.com/watch?v=SCVCLChPQFY"},
                {"name": "Lateral Raises", "desc": "Isolates the side deltoids for wider shoulders.", "video_url": "https://www.youtube.com/watch?v=3VcKaXYSadg"},
            ]
        },
        "Arms": {
            "description": "Exercises for biceps, triceps, and forearms.",
            "exercises": [
                {"name": "Bicep Curls", "desc": "Classic bicep builder.", "video_url": "https://www.youtube.com/watch?v=kwG2ipFRgfo"},
                {"name": "Tricep Pushdowns", "desc": "Targets the triceps, good for elbow extension.", "video_url": "https://www.youtube.com/watch?v=F54_GqjJ-Xg"},
            ]
        },
        "Core": {
            "description": "Exercises for abdominal muscles, obliques, and lower back stabilization.",
            "exercises": [
                {"name": "Plank", "desc": "Excellent for core stability and endurance.", "video_url": "https://www.youtube.com/watch?v=ASdvN_X32Lg"},
                {"name": "Crunches", "desc": "Targets the rectus abdominis.", "video_url": "https://www.youtube.com/watch?v=MkQv5K6iV_E"},
            ]
        },
        "Cardio": {
            "description": "Exercises for cardiovascular health and endurance.",
            "exercises": [
                {"name": "Running", "desc": "Classic cardio, improves endurance and burns calories.", "video_url": "https://www.youtube.com/watch?v=kD3Fp4oE6m4"},
                {"name": "Cycling", "desc": "Low-impact cardio, great for leg endurance.", "video_url": "https://www.youtube.com/watch?v=r_37Yl8B_0M"},
            ]
        },
        "Full Body": {
            "description": "Exercises that work multiple muscle groups simultaneously.",
            "exercises": [
                {"name": "Burpees", "desc": "High-intensity full-body exercise.", "video_url": "https://www.youtube.com/watch?v=dZgVxmf6C28"},
                {"name": "Kettlebell Swings", "desc": "Explosive full-body exercise, great for power and conditioning.", "video_url": "https://www.youtube.com/watch?v=uC06yJd124o"},
            ]
        },
    }

    if selected_group in exercise_details:
        st.info(exercise_details[selected_group]["description"])
        for exercise in exercise_details[selected_group]["exercises"]:
            st.markdown(f"### {exercise['name']}")
            st.write(exercise['desc'])
            if exercise['video_url']:
                st.video(exercise['video_url'])
            st.markdown("---")
    else:
        st.info(f"Details for {selected_group} exercises coming soon!")

    # --- AI-Powered Exercise Recommendations ---
    st.subheader("AI-Powered Exercise Finder")

    # Retrieve user metrics for AI context
    weight_kg = st.session_state.get('weight_kg', 70.0)
    height_cm = st.session_state.get('height_cm', 175.0)
    age = st.session_state.get('age', 30)
    gender = st.session_state.get('gender', "Male")
    activity_level = st.session_state.get('activity_level', "Moderately Active")
    fitness_goal_overall = st.session_state.get('fitness_goal', "Maintain Fitness")

    # From Workout_Planner, if set, otherwise default
    fitness_level_from_planner = st.session_state.get('fitness_level', "Beginner")
    workout_goal_from_planner = st.session_state.get('workout_goal', "Strength")
    available_equipment_from_planner = st.session_state.get('available_equipment', ["None (Bodyweight)"])


    ai_exercise_query = st.text_area(
        "Ask AI for exercise suggestions based on your specific needs (e.g., 'bodyweight exercises for core strength', 'dumbbell exercises for beginners', 'exercises to improve posture'):",
        height=100,
        key="ai_exercise_query_text_area" # Unique key
    )
    if st.button("Get AI Exercise Suggestions", key="ai_exercise_suggestions_btn"):
        if ai_exercise_query:
            # --- Construct a comprehensive system prompt for the AI with ALL relevant data ---
            system_prompt_exercise = f"""
            You are an AI exercise specialist and physical therapist. Provide detailed exercise suggestions based on the user's query and their comprehensive profile.
            
            User Profile:
            - Name: {st.session_state.get('user_name', 'User')}
            - Current Weight: {weight_kg} kg
            - Current Height: {height_cm} cm
            - Age: {age} years
            - Gender: {gender}
            - Activity Level: {activity_level}
            - Overall Fitness Goal: {fitness_goal_overall}
            - Stated Fitness Level (from Workout Planner): {fitness_level_from_planner}
            - Primary Workout Goal (from Workout Planner): {workout_goal_from_planner}
            - Available Equipment (from Workout Planner): {', '.join(available_equipment_from_planner) if available_equipment_from_planner else 'None'}

            Given the user's request and their profile, for each exercise, include:
            - **Exercise Name**
            - **Brief Description:** What does it do?
            - **Target Muscle Group(s)**
            - **Equipment Needed:** (e.g., "Dumbbells", "Bodyweight", "Gym machine")
            - **Tips for Proper Form:** A crucial tip or common mistake to avoid.
            - **Modification/Progression:** How can it be made easier or harder, if applicable.
            
            Suggest 3-5 relevant exercises unless the query specifically asks for more or fewer.
            Format your response clearly using bullet points or a numbered list.
            Ensure safety and effectiveness are prioritized based on their fitness level and available equipment.
            """
            with st.spinner("Finding personalized exercise suggestions..."):
                backend.get_ai_response(system_prompt_exercise, ai_exercise_query)
        else:
            st.warning("Please enter a query for AI exercise suggestions.")
