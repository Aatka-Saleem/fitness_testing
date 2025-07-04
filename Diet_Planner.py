import streamlit as st
import time # Needed for st.spinner

def app():
    # Retrieve the backend instance from session state
    backend = st.session_state.backend 

    st.header("🍎 AI-Powered Diet Planner")
    st.write("Leverage AI to create personalized meal plans based on your goals, dietary preferences, and allergies.")

    # --- Retrieve User Metrics from Body_Metrics via Session State ---
    # These values should be set and updated by the Body_Metrics.py page
    weight_kg = st.session_state.get('weight_kg', 70.0)
    height_cm = st.session_state.get('height_cm', 175.0)
    age = st.session_state.get('age', 30)
    gender = st.session_state.get('gender', "Male")
    activity_level = st.session_state.get('activity_level', "Moderately Active")
    fitness_goal = st.session_state.get('fitness_goal', "Maintain Fitness")

    # Calculate current BMI, BMR, TDEE, Protein Needs using the backend and session state data
    bmi = backend.calculate_bmi(weight_kg, height_cm)
    bmr = backend.calculate_bmr(weight_kg, height_cm, age, gender)
    
    # Re-calculate TDEE and protein needs here to ensure they are up-to-date with current inputs
    # Need to import or define these helper functions if they are not in backend_logic.py
    # For now, let's assume they are either in backend or we'll define them locally again.
    # From previous files, these were helper functions, so let's put them here too.
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
            "General Health": 1.0 # Added general health, assuming it maps
        }
        # Map Diet_Planner goals to Protein Needs multipliers, assuming Diet_Planner uses subset of Fitness_Goal
        # If Diet_Planner's goals are different, this mapping needs adjustment.
        # For now, mapping Diet_Planner's "Lose Weight", "Gain Muscle", "Maintain Weight" to a general "Lose Weight", "Gain Muscle", "Maintain Fitness"
        # If the goal is "Maintain Weight" in Diet Planner, map it to "Maintain Fitness" for protein needs.
        if goal == "Maintain Weight":
            goal_for_protein = "Maintain Fitness"
        else:
            goal_for_protein = goal # Directly use "Lose Weight" or "Gain Muscle"
        
        return weight_val * multipliers.get(goal_for_protein, 1.2) # Default multiplier 1.2g/kg

    tdee = calculate_tdee_local(bmr, activity_level)
    protein_need = calculate_protein_needs_local(weight_kg, fitness_goal) # Use fitness_goal from Body Metrics

    # --- User Dietary Preferences (from session state or new input) ---
    if 'diet_goal' not in st.session_state:
        st.session_state.diet_goal = fitness_goal # Default to overall fitness goal
    if 'diet_prefs' not in st.session_state:
        st.session_state.diet_prefs = []
    if 'diet_allergies' not in st.session_state:
        st.session_state.diet_allergies = ""
    
    # Use calculated TDEE as the initial daily calorie target if not explicitly set by user before
    if 'daily_calorie_target' not in st.session_state or st.session_state.daily_calorie_target == 2000: # Check if it's the default placeholder
         if fitness_goal == "Lose Weight":
             st.session_state.daily_calorie_target = int(tdee * 0.8) # 20% deficit
         elif fitness_goal == "Gain Muscle":
             st.session_state.daily_calorie_target = int(tdee * 1.1) # 10% surplus
         else:
             st.session_state.daily_calorie_target = int(tdee)


    st.subheader("Your Dietary Profile")
    
    col_goal, col_cal = st.columns(2)

    # Define the actual options for the selectbox
    diet_goal_options = ["Lose Weight", "Gain Muscle", "Maintain Weight"]
    
    # Determine the initial index for the selectbox to prevent ValueError
    initial_diet_goal_index = 0 # Default to "Lose Weight"
    if st.session_state.diet_goal in diet_goal_options:
        initial_diet_goal_index = diet_goal_options.index(st.session_state.diet_goal)
    elif st.session_state.diet_goal == "Maintain Fitness": # Handle specific mapping
        initial_diet_goal_index = diet_goal_options.index("Maintain Weight")
    # For any other unexpected value, it will remain at default_index (0)

    st.session_state.diet_goal = col_goal.selectbox(
        "🎯 Your Diet Goal", 
        diet_goal_options,
        index=initial_diet_goal_index # Use the safely determined index
    )
    # Calorie target can be adjusted by the user, but starts with a smart default
    st.session_state.daily_calorie_target = col_cal.number_input(
        "🔥 Daily Calorie Target (kcal)", 
        min_value=1000, 
        max_value=5000, 
        value=st.session_state.daily_calorie_target, 
        step=50,
        help=f"Recommended starting point based on your TDEE ({int(tdee)} kcal) and goal: {st.session_state.daily_calorie_target} kcal"
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

    # AI interaction for meal planning
    st.subheader("Generate Meal Plan with AI")

    prompt = st.text_area(
        "Tell me more about your meal plan needs (e.g., 'A 7-day vegetarian meal plan for 2000 calories with easy-to-find ingredients'):", 
        height=150,
        key="diet_plan_ai_prompt" # Unique key for this text area
    )

    if st.button("✨ Generate Meal Plan", key="generate_meal_plan_btn"):
        if not prompt:
            st.warning("Please provide a prompt for your meal plan.")
        else:
            # --- Construct a comprehensive system prompt for the AI with ALL relevant data ---
            system_prompt_diet = f"""
            You are an AI-powered fitness and nutrition expert specializing in meal planning.
            Your task is to create a detailed, actionable, and personalized meal plan.

            Here's the user's complete profile and requirements:
            - User Name: {st.session_state.get('user_name', 'User')}
            - Current Weight: {weight_kg} kg
            - Current Height: {height_cm} cm
            - Age: {age} years
            - Gender: {gender}
            - Activity Level: {activity_level}
            - Primary Fitness Goal (Overall): {fitness_goal}
            - Specific Diet Goal (for this plan): {st.session_state.diet_goal}
            - Calculated BMR (Basal Metabolic Rate): {bmr} kcal/day
            - Calculated TDEE (Total Daily Energy Expenditure): {tdee:.0f} kcal/day
            - Daily Calorie Target for Plan: {st.session_state.daily_calorie_target} kcal
            - Estimated Protein Needs: {protein_need:.0f}g/day (approx.)
            - Dietary Preferences: {', '.join(st.session_state.diet_prefs) if st.session_state.diet_prefs else 'None specified'}
            - Allergies: {st.session_state.diet_allergies if st.session_state.diet_allergies else 'None'}

            Consider all the above context, especially the calorie target, preferences, and allergies.
            Structure the meal plan clearly. For example:
            - **Day 1: [Day Name]**
                - **Breakfast:** [Meal Name] ([Approx. Calories], [Key Macros]) - [Brief Description]
                - **Lunch:** ...
                - **Dinner:** ...
                - **Snacks:** ...
            Include portion sizes or calorie estimates per meal if possible.
            Suggest diverse, balanced, and appealing meals.
            If the user asks for a specific duration (e.g., "7-day plan"), adhere to that.
            """
            
            with st.spinner("Generating your personalized meal plan... This may take a moment."):
                generated_plan = backend.get_ai_response(system_prompt_diet, prompt)
                # Store the generated plan and its key nutritional targets in session state
                if generated_plan:
                    st.session_state.last_generated_meal_plan = generated_plan
                    
                    # Attempt to extract macro goals from the generated plan (this is an advanced step)
                    # For simplicity, let's just store the overall calorie target and protein need from calculations
                    st.session_state.protein_goal = int(protein_need)
                    # Assume approximate carbs/fats for display on dashboard
                    remaining_calories = st.session_state.daily_calorie_target - (st.session_state.protein_goal * 4) # Protein 4 cal/g
                    st.session_state.fats_goal = int(remaining_calories * 0.3 / 9) # Assume 30% from fats (9 cal/g)
                    st.session_state.carbs_goal = int(remaining_calories * 0.7 / 4) # Remaining from carbs (4 cal/g)
                    st.success("Meal plan generated and goals updated!")

    # Display the last generated meal plan
    if 'last_generated_meal_plan' in st.session_state and st.session_state.last_generated_meal_plan:
        st.subheader("Your Generated Meal Plan")
        st.markdown(st.session_state.last_generated_meal_plan)
    else:
        st.info("Your personalized meal plan will appear here once generated.")

    st.markdown("---")
    st.subheader("✨ Recipe Creator & Ingredient Swapper")
    st.write("Let AI help you with recipes or suggest healthy swaps!")

    # New AI Feature: Recipe Creator / Ingredient Swapper
    recipe_mode = st.radio(
        "What would you like to do?",
        ["Create a Recipe from Ingredients", "Suggest Healthy Swaps for a Recipe/Ingredient"],
        key="recipe_mode_selection"
    )

    if recipe_mode == "Create a Recipe from Ingredients":
        ingredients_input = st.text_area(
            "List your available ingredients (e.g., 'chicken breast, broccoli, rice, soy sauce'):",
            height=100,
            key="ingredients_input"
        )
        recipe_style_prompt = st.text_input(
            "Any specific cuisine or style? (e.g., 'quick stir-fry', 'Italian pasta dish', 'low-carb dinner'):",
            key="recipe_style_prompt"
        )
        if st.button("✨ Generate Recipe", key="generate_from_ingredients_btn"):
            if not ingredients_input:
                st.warning("Please list some ingredients to generate a recipe.")
            else:
                system_prompt_recipe_creator = f"""
                You are an AI chef and nutritionist. Based on the user's available ingredients, 
                generate a delicious and healthy recipe. Consider their general dietary preferences:
                - Preferences: {', '.join(st.session_state.diet_prefs) if st.session_state.diet_prefs else 'None'}
                - Allergies: {st.session_state.diet_allergies if st.session_state.diet_allergies else 'None'}
                - Daily Calorie Target: {st.session_state.daily_calorie_target} kcal (try to keep the recipe sensible for a meal portion)
                - Estimated Protein Needs: {protein_need:.0f}g/day

                Available Ingredients: {ingredients_input}
                Recipe Style/Request: {recipe_style_prompt if recipe_style_prompt else 'None specified (make it a balanced meal)'}

                Provide the recipe with:
                - Recipe Name
                - Brief Description
                - Ingredients List (with quantities)
                - Step-by-Step Instructions
                - Estimated Prep & Cook Time
                - Rough Nutritional Information (Calories, Protein, Carbs, Fats per serving, if possible).
                """
                user_prompt_recipe_creator = "Generate a recipe using the provided ingredients and style."
                with st.spinner("Whipping up a recipe..."):
                    backend.get_ai_response(system_prompt_recipe_creator, user_prompt_recipe_creator)

    elif recipe_mode == "Suggest Healthy Swaps for a Recipe/Ingredient":
        swap_input = st.text_area(
            "Enter a recipe or a specific ingredient you want to swap (e.g., 'lasagna recipe' or 'white rice'):",
            height=100,
            key="swap_input"
        )
        swap_reason_prompt = st.text_input(
            "What's your goal for the swap? (e.g., 'lower carbs', 'gluten-free', 'more protein', 'healthier alternative'):",
            key="swap_reason_prompt"
        )
        if st.button("✨ Suggest Swaps", key="suggest_swaps_btn"):
            if not swap_input:
                st.warning("Please enter a recipe or ingredient to suggest swaps for.")
            else:
                system_prompt_ingredient_swapper = f"""
                You are an AI nutritionist and culinary expert. Based on the user's input, 
                suggest healthy and suitable ingredient swaps or modifications for a recipe.
                Consider their dietary preferences and allergies:
                - Preferences: {', '.join(st.session_state.diet_prefs) if st.session_state.diet_prefs else 'None'}
                - Allergies: {st.session_state.diet_allergies if st.session_state.diet_allergies else 'None'}
                - Daily Calorie Target: {st.session_state.daily_calorie_target} kcal

                User wants to modify: {swap_input}
                Goal for swap: {swap_reason_prompt if swap_reason_prompt else 'Make it healthier'}

                Provide:
                - A clear explanation of why the swap is beneficial.
                - The original ingredient/component and the suggested swap(s).
                - How the swap might affect taste or texture (briefly).
                - Any adjustments needed in cooking method or other ingredients.
                If it's a recipe, suggest a few key swaps. If it's a single ingredient, provide multiple alternatives.
                """
                user_prompt_ingredient_swapper = "Suggest healthy swaps for the provided recipe/ingredient based on my goals."
                with st.spinner("Finding healthy alternatives..."):
                    backend.get_ai_response(system_prompt_ingredient_swapper, user_prompt_ingredient_swapper)

