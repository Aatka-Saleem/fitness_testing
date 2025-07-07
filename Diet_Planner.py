import streamlit as st
import time
import asyncio

def app():
    backend = st.session_state.backend 

    st.header("🍎 AI-Powered Diet Planner")
    st.write("Leverage AI to create personalized meal plans based on your goals, dietary preferences, and allergies.")

    # --- Retrieve User Metrics ---
    weight_kg = st.session_state.get('weight_kg', 70.0)
    height_cm = st.session_state.get('height_cm', 175.0)
    age = st.session_state.get('age', 30)
    gender = st.session_state.get('gender', "Male")
    activity_level = st.session_state.get('activity_level', "Moderately Active")
    fitness_goal = st.session_state.get('fitness_goal', "Maintain Fitness")

    bmi = backend.calculate_bmi(weight_kg, height_cm)
    bmr = backend.calculate_bmr(weight_kg, height_cm, age, gender)

    def calculate_tdee_local(bmr_val, activity_lvl):
        multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Extremely Active": 1.9
        }
        return bmr_val * multipliers.get(activity_lvl, 1.55)

    def calculate_protein_needs_local(weight_val, goal):
        multipliers = {
            "Lose Weight": 1.6,
            "Gain Muscle": 2.2,
            "Maintain Fitness": 1.2,
            "Improve Endurance": 1.4,
            "General Health": 1.0
        }
        if goal == "Maintain Weight":
            goal_for_protein = "Maintain Fitness"
        else:
            goal_for_protein = goal

        return weight_val * multipliers.get(goal_for_protein, 1.2)

    tdee = calculate_tdee_local(bmr, activity_level)
    protein_need = calculate_protein_needs_local(weight_kg, fitness_goal)

    if 'diet_goal' not in st.session_state:
        st.session_state.diet_goal = fitness_goal
    if 'diet_prefs' not in st.session_state:
        st.session_state.diet_prefs = []
    if 'diet_allergies' not in st.session_state:
        st.session_state.diet_allergies = ""

    if 'daily_calorie_target' not in st.session_state or st.session_state.daily_calorie_target == 2000:
        if fitness_goal == "Lose Weight":
            st.session_state.daily_calorie_target = int(tdee * 0.8)
        elif fitness_goal == "Gain Muscle":
            st.session_state.daily_calorie_target = int(tdee * 1.1)
        else:
            st.session_state.daily_calorie_target = int(tdee)

    # --- Profile Display ---
    st.subheader("Your Dietary Profile")
    col_goal, col_cal = st.columns(2)
    diet_goal_options = ["Lose Weight", "Gain Muscle", "Maintain Weight"]

    index = 0
    if st.session_state.diet_goal in diet_goal_options:
        index = diet_goal_options.index(st.session_state.diet_goal)
    elif st.session_state.diet_goal == "Maintain Fitness":
        index = diet_goal_options.index("Maintain Weight")

    st.session_state.diet_goal = col_goal.selectbox("🎯 Your Diet Goal", diet_goal_options, index=index)

    st.session_state.daily_calorie_target = col_cal.number_input(
        "🔥 Daily Calorie Target (kcal)", 
        min_value=1000, 
        max_value=5000, 
        value=st.session_state.daily_calorie_target, 
        step=50
    )

    st.session_state.diet_prefs = st.multiselect(
        "🥗 Dietary Preferences", 
        ["Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean", "Gluten-Free", "Dairy-Free", "Low-Carb", "High-Protein"],
        default=st.session_state.diet_prefs
    )

    st.session_state.diet_allergies = st.text_input(
        "🚫 Allergies (e.g., Peanuts, Shellfish, Lactose)", 
        value=st.session_state.diet_allergies
    )

    # --- Meal Plan Generator ---
    st.subheader("Generate Meal Plan with AI")
    prompt = st.text_area("Describe your needs:", height=150, key="diet_plan_ai_prompt")

    if st.button("✨ Generate Meal Plan", key="generate_meal_plan_btn"):
        if not prompt:
            st.warning("Please provide a prompt.")
        else:
            system_prompt = f"""
            You are an AI meal planner. User details:
            - Weight: {weight_kg}kg
            - Height: {height_cm}cm
            - Age: {age}
            - Gender: {gender}
            - Activity Level: {activity_level}
            - Fitness Goal: {fitness_goal}
            - Diet Goal: {st.session_state.diet_goal}
            - BMR: {bmr:.0f} kcal
            - TDEE: {tdee:.0f} kcal
            - Calorie Target: {st.session_state.daily_calorie_target} kcal
            - Protein Need: {protein_need:.0f}g
            - Preferences: {', '.join(st.session_state.diet_prefs) or 'None'}
            - Allergies: {st.session_state.diet_allergies or 'None'}
            """

            with st.spinner("Generating meal plan..."):
                result = asyncio.run(backend.get_ai_response(system_prompt, prompt))
                if result:
                    st.session_state.last_generated_meal_plan = result
                    st.session_state.protein_goal = int(protein_need)
                    remaining_cal = st.session_state.daily_calorie_target - (st.session_state.protein_goal * 4)
                    st.session_state.fats_goal = int(remaining_cal * 0.3 / 9)
                    st.session_state.carbs_goal = int(remaining_cal * 0.7 / 4)
                    st.success("Meal plan generated and goals updated!")

    if 'last_generated_meal_plan' in st.session_state:
        st.subheader("Your Generated Meal Plan")
        st.markdown(st.session_state.last_generated_meal_plan)

    # --- Recipe Generator ---
    st.markdown("---")
    st.subheader("✨ Recipe Creator & Ingredient Swapper")

    mode = st.radio("Choose:", ["Create Recipe", "Suggest Swaps"], key="recipe_mode")

    if mode == "Create Recipe":
        ingredients = st.text_area("List ingredients:", height=100)
        style = st.text_input("Preferred cuisine/style (optional):")

        if st.button("✨ Generate Recipe"):
            if not ingredients:
                st.warning("Please enter ingredients.")
            else:
                system_prompt = f"""
                You are an AI chef. Generate a healthy recipe using:
                - Ingredients: {ingredients}
                - Style: {style or 'Any'}
                - Calorie Target: {st.session_state.daily_calorie_target}
                - Protein Need: {protein_need:.0f}g
                - Preferences: {', '.join(st.session_state.diet_prefs) or 'None'}
                - Allergies: {st.session_state.diet_allergies or 'None'}
                """
                with st.spinner("Creating recipe..."):
                    recipe = asyncio.run(backend.get_ai_response(system_prompt, "Create a recipe"))
                    if recipe:
                        st.markdown(recipe)

    else:
        recipe_input = st.text_area("Enter recipe or ingredient:")
        goal = st.text_input("Swap goal (e.g. lower carbs):")

        if st.button("✨ Suggest Swaps"):
            if not recipe_input:
                st.warning("Please enter something.")
            else:
                system_prompt = f"""
                Suggest healthy swaps for: {recipe_input}
                Goal: {goal or 'Improve health'}
                Preferences: {', '.join(st.session_state.diet_prefs) or 'None'}
                Allergies: {st.session_state.diet_allergies or 'None'}
                """
                with st.spinner("Finding swaps..."):
                    swap_result = asyncio.run(backend.get_ai_response(system_prompt, "Suggest healthy swaps"))
                    if swap_result:
                        st.markdown(swap_result)

