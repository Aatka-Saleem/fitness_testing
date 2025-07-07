import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import asyncio

def app():
    """Main Body Metrics application focused on current metrics and analysis"""
    backend = st.session_state.backend 

    st.header("📏 Body Metrics & Health Analytics")
    
    # Initialize/Load User Profile and Metrics
    if "user_profile_loaded" not in st.session_state:
        if 'user_info' in st.session_state and st.session_state.user_info:
            user_uid = st.session_state.user_info.get('uid')
            org_id = st.session_state.user_info.get('org_id')
            
            if user_uid and org_id:
                user_profile = asyncio.run(backend.get_user_profile(user_uid, org_id))
                
                if user_profile:
                    st.session_state.user_profile = user_profile
                    st.session_state.body_metrics_data = user_profile.get('body_metrics', {})
                    
                    st.session_state.needs_metrics_input = not bool(st.session_state.body_metrics_data)
                    
                    if st.session_state.needs_metrics_input:
                        st.session_state.weight_kg = 0.0
                        st.session_state.height_cm = 0.0
                        st.session_state.age = 0
                        st.session_state.gender = "Male"
                    else:
                        st.session_state.weight_kg = float(st.session_state.body_metrics_data.get('weight_kg', 70.0))
                        st.session_state.height_cm = float(st.session_state.body_metrics_data.get('height_cm', 175.0))
                        st.session_state.age = int(st.session_state.body_metrics_data.get('age', 30))
                        st.session_state.gender = st.session_state.body_metrics_data.get('gender', "Male")
                else:
                    st.error("Could not load user profile. Please try logging in again.")
                    st.session_state.needs_metrics_input = True 
                    st.session_state.weight_kg = 0.0
                    st.session_state.height_cm = 0.0
                    st.session_state.age = 0
                    st.session_state.gender = "Male"
            else:
                st.warning("User UID or Organization ID not found in session. Please log in.")
                st.session_state.needs_metrics_input = True 
                st.session_state.weight_kg = 0.0
                st.session_state.height_cm = 0.0
                st.session_state.age = 0
                st.session_state.gender = "Male"
        else:
            st.warning("User information not available. Please log in.")
            st.session_state.needs_metrics_input = True 
            st.session_state.weight_kg = 0.0
            st.session_state.height_cm = 0.0
            st.session_state.age = 0
            st.session_state.gender = "Male"

        st.session_state.user_profile_loaded = True

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Current Metrics", "📈 Health Analysis", "🔍 Body Composition"])
    
    with tab1:
        display_current_metrics(backend)
    
    with tab2:
        if not st.session_state.needs_metrics_input:
            display_health_analysis(backend)
        else:
            st.info("Please enter your current metrics in the 'Current Metrics' tab and click 'Save My Metrics' to see your health analysis.")
    
    with tab3:
        if not st.session_state.needs_metrics_input:
            display_body_composition_analysis(backend)
        else:
            st.info("Please enter your current metrics in the 'Current Metrics' tab and click 'Save My Metrics' to see your body composition analysis.")

def display_current_metrics(backend):
    """Display current body metrics input and basic calculations"""
    st.subheader("Current Body Metrics Input")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        new_weight = st.number_input(
            "⚖ Weight (kg)", 
            min_value=0.0,
            max_value=300.0, 
            value=float(st.session_state.weight_kg),
            step=0.1,
            format="%.2f",
            key="input_weight_kg"
        )
        
    with col2:
        new_height = st.number_input(
            "📏 Height (cm)", 
            min_value=0.0,
            max_value=250.0, 
            value=float(st.session_state.height_cm),
            step=0.1,
            format="%.2f",
            key="input_height_cm"
        )
        
    with col3:
        new_age = st.number_input(
            "🎂 Age (years)", 
            min_value=0,
            max_value=100, 
            value=int(st.session_state.age),
            step=1,
            key="input_age"
        )
        
    with col4:
        new_gender = st.selectbox(
            "👥 Gender",
            ["Male", "Female"],
            index=0 if st.session_state.gender == "Male" else 1,
            key="input_gender"
        )
    
    st.session_state.weight_kg = new_weight
    st.session_state.height_cm = new_height
    st.session_state.age = new_age
    st.session_state.gender = new_gender

    if st.button("Save My Metrics", key="save_metrics_button"):
        user_uid = st.session_state.user_info.get('uid')
        org_id = st.session_state.user_info.get('org_id')

        if st.session_state.weight_kg <= 0 or st.session_state.height_cm <= 0 or st.session_state.age <= 0:
            st.warning("Please enter valid positive values for Weight, Height, and Age.")
        elif user_uid and org_id:
            metrics_to_save = {
                'weight_kg': st.session_state.weight_kg,
                'height_cm': st.session_state.height_cm,
                'age': st.session_state.age,
                'gender': st.session_state.gender
            }
            success = asyncio.run(backend.update_user_profile(user_uid, org_id, {'body_metrics': metrics_to_save}))
            if success:
                st.success("Your body metrics have been saved successfully!")
                st.session_state.body_metrics_data = metrics_to_save
                st.session_state.needs_metrics_input = False
                st.rerun()
            else:
                st.error("Failed to save your body metrics. Please try again.")
        else:
            st.error("User information is missing. Please log in again to save metrics.")
    
    st.divider()
    
    if not st.session_state.needs_metrics_input:
        st.subheader("📊 Your Current Health Metrics")
        
        bmi = backend.calculate_bmi(st.session_state.weight_kg, st.session_state.height_cm)
        body_fat = backend.calculate_body_fat(bmi, st.session_state.age, st.session_state.gender)
        bmr = backend.calculate_bmr(st.session_state.weight_kg, st.session_state.height_cm, st.session_state.age, st.session_state.gender)
        
        ideal_weight = calculate_ideal_weight(st.session_state.height_cm, st.session_state.gender)
        bmi_category, bmi_color = get_bmi_category(bmi)
        bf_category = get_body_fat_category(body_fat, st.session_state.gender)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("BMI", f"{bmi:.1f}", help="Body Mass Index")
            st.markdown(f"<p style='color:{bmi_color}; font-weight:bold; font-size:0.9em;'>{bmi_category}</p>", 
                       unsafe_allow_html=True)
            
        with col2:
            st.metric("Body Fat", f"{body_fat:.1f}%", help="Estimated body fat percentage")
            st.markdown(f"<p style='font-weight:bold; font-size:0.9em;'>{bf_category}</p>", 
                       unsafe_allow_html=True)
            
        with col3:
            st.metric("BMR", f"{int(bmr):,}", help="Basal Metabolic Rate (calories/day)")
            st.markdown("<p style='font-size:0.8em; color:gray;'>Calories burned at rest</p>", 
                       unsafe_allow_html=True)
            
        with col4:
            weight_diff = st.session_state.weight_kg - ideal_weight
            st.metric("Ideal Weight", f"{ideal_weight:.1f} kg", f"{weight_diff:+.1f} kg")
            st.markdown("<p style='font-size:0.8em; color:gray;'>Based on Devine formula</p>", 
                       unsafe_allow_html=True)
    else:
        st.info("Please enter your body metrics above and click 'Save My Metrics' to view your health statistics.")


def display_health_analysis(backend):
    """Display health analysis and risk assessment"""
    
    st.subheader("Health Status Analysis")
    
    # Get current metrics from session state
    bmi = backend.calculate_bmi(st.session_state.weight_kg, st.session_state.height_cm)
    body_fat = backend.calculate_body_fat(bmi, st.session_state.age, st.session_state.gender)
    bmr = backend.calculate_bmr(st.session_state.weight_kg, st.session_state.height_cm, st.session_state.age, st.session_state.gender)
    
    # Health status indicators
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Health Status Summary")
        
        # BMI Analysis
        bmi_category, bmi_color = get_bmi_category(bmi)
        st.markdown(f"*BMI Status:* <span style='color:{bmi_color}'>{bmi_category}</span>", 
                    unsafe_allow_html=True)
        
        # Body Fat Analysis
        bf_category = get_body_fat_category(body_fat, st.session_state.gender)
        st.markdown(f"*Body Fat Category:* {bf_category}")
        
        # Age-related considerations
        age_considerations = get_age_health_considerations(st.session_state.age)
        st.markdown(f"*Age Considerations:* {age_considerations}")
        
        # Basic health recommendations
        st.markdown("#### 💡 Key Recommendations")
        recommendations = get_basic_recommendations(bmi, body_fat, st.session_state.age, st.session_state.gender)
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    with col2:
        st.markdown("#### ⚠ Health Risk Indicators")
        
        # Risk assessment based on metrics
        risks = assess_basic_health_risks(bmi, body_fat, st.session_state.age)
        
        if not risks:
            st.success("✅ No major risk indicators identified based on current metrics.")
        else:
            for risk in risks:
                st.warning(f"⚠ {risk}")
        
        # Health score calculation
        health_score = calculate_health_score(bmi, body_fat, st.session_state.age)
        st.markdown("#### 🎯 Overall Health Score")
        
        # Health score gauge
        score_color = get_score_color(health_score)
        st.markdown(f"<h2 style='color:{score_color}; text-align:center;'>{health_score}/100</h2>", 
                    unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:{score_color};'>{get_score_category(health_score)}</p>", 
                    unsafe_allow_html=True)

def display_body_composition_analysis(backend):
    """Display detailed body composition analysis with visualizations"""
    
    st.subheader("Body Composition Analysis")
    
    # Get current metrics from session state
    bmi = backend.calculate_bmi(st.session_state.weight_kg, st.session_state.height_cm)
    body_fat = backend.calculate_body_fat(bmi, st.session_state.age, st.session_state.gender)
    bmr = backend.calculate_bmr(st.session_state.weight_kg, st.session_state.height_cm, st.session_state.age, st.session_state.gender)
    
    # Body composition breakdown
    fat_mass = (body_fat / 100) * st.session_state.weight_kg
    lean_mass = st.session_state.weight_kg - fat_mass
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Body composition pie chart
        composition_data = pd.DataFrame({
            'Component': ['Lean Mass', 'Fat Mass'],
            'Weight (kg)': [lean_mass, fat_mass],
            'Percentage': [100 - body_fat, body_fat]
        })
        
        fig_composition = px.pie(composition_data, 
                                 values='Weight (kg)', 
                                 names='Component',
                                 title='Body Composition Breakdown',
                                 color_discrete_sequence=['#2E86AB', '#A23B72'])
        fig_composition.update_traces(textposition='inside', 
                                     textinfo='percent+label',
                                     textfont_size=14)
        fig_composition.update_layout(height=400, title_x=0.5)
        st.plotly_chart(fig_composition, use_container_width=True)
        
    with col2:
        # BMI vs Body Fat comparison
        create_bmi_bodyfat_comparison(bmi, body_fat, st.session_state.gender)
    
    # Detailed composition metrics
    st.divider()
    st.markdown("### 📊 Detailed Body Composition Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fat Mass", f"{fat_mass:.1f} kg", help="Total body fat weight")
        
    with col2:
        st.metric("Lean Mass", f"{lean_mass:.1f} kg", help="Muscle, bones, organs, water")
        
    with col3:
        muscle_mass = estimate_muscle_mass(lean_mass, st.session_state.gender)
        st.metric("Est. Muscle Mass", f"{muscle_mass:.1f} kg", help="Estimated skeletal muscle mass")
        
    with col4:
        water_content = estimate_body_water(st.session_state.weight_kg, st.session_state.age, st.session_state.gender)
        st.metric("Body Water", f"{water_content:.1f}%", help="Estimated total body water percentage")
    
    # BMR breakdown
    st.markdown("### 🔥 Metabolic Analysis")
    create_bmr_breakdown(bmr, st.session_state.weight_kg, lean_mass, fat_mass)

# Helper Functions

def calculate_ideal_weight(height_cm, gender):
    """Calculate ideal weight using Devine formula"""
    height_inches = height_cm / 2.54
    if gender == "Male":
        return 50 + 2.3 * (height_inches - 60)
    else:
        return 45.5 + 2.3 * (height_inches - 60)

def get_bmi_category(bmi):
    """Get BMI category and color"""
    if bmi < 18.5:
        return "Underweight", "#FF9800"
    elif 18.5 <= bmi < 25:
        return "Normal Weight", "#4CAF50"
    elif 25 <= bmi < 30:
        return "Overweight", "#FF5722"
    else:
        return "Obese", "#F44336"

def get_body_fat_category(body_fat, gender):
    """Get body fat category based on gender"""
    if gender == "Male":
        if body_fat < 6:
            return "Essential Fat"
        elif body_fat < 14:
            return "Athletic"
        elif body_fat < 18:
            return "Fitness"
        elif body_fat < 25:
            return "Acceptable"
        else:
            return "High"
    else:  # Female
        if body_fat < 14:
            return "Essential Fat"
        elif body_fat < 21:
            return "Athletic"
        elif body_fat < 25:
            return "Fitness"
        elif body_fat < 32:
            return "Acceptable"
        else:
            return "High"

def get_age_health_considerations(age):
    """Get age-related health considerations"""
    if age < 18:
        return "Growth and development phase"
    elif age < 30:
        return "Peak physical condition years"
    elif age < 50:
        return "Metabolism begins to slow"
    elif age < 65:
        return "Increased focus on muscle preservation"
    else:
        return "Emphasis on mobility and strength"

def get_basic_recommendations(bmi, body_fat, age, gender):
    """Get basic health recommendations"""
    recommendations = []
    
    # BMI-based recommendations
    if bmi < 18.5:
        recommendations.append("Consider gaining weight through balanced nutrition and strength training")
    elif bmi >= 25:
        recommendations.append("Focus on weight management through diet and exercise")
    
    # Body fat recommendations
    bf_category = get_body_fat_category(body_fat, gender)
    if bf_category == "High":
        recommendations.append("Prioritize reducing body fat through cardio and strength training")
    elif bf_category == "Essential Fat":
        recommendations.append("Ensure adequate fat intake for hormonal health")
    
    # Age-based recommendations
    if age >= 40:
        recommendations.append("Include strength training to preserve muscle mass")
    if age >= 50:
        recommendations.append("Focus on bone health with weight-bearing exercises")
    
    # General recommendations
    recommendations.extend([
        "Maintain regular physical activity",
        "Follow a balanced, nutritious diet",
        "Ensure adequate sleep (7-9 hours)",
        "Stay hydrated throughout the day"
    ])
    
    return recommendations[:5]  # Limit to top 5 recommendations

def assess_basic_health_risks(bmi, body_fat, age):
    """Assess basic health risks based on metrics"""
    risks = []
    
    if bmi >= 30:
        risks.append("Obesity increases risk of cardiovascular disease and diabetes")
    elif bmi >= 25:
        risks.append("Overweight status may increase health risks")
    elif bmi < 18.5:
        risks.append("Underweight status may indicate nutritional deficiencies")
    
    if body_fat > 32 and age > 40:
        risks.append("High body fat with age increases metabolic risk")
    
    return risks

def calculate_health_score(bmi, body_fat, age):
    """Calculate a simple health score out of 100"""
    score = 100
    
    # BMI penalty
    if bmi < 18.5 or bmi >= 30:
        score -= 30
    elif bmi >= 25:
        score -= 15
    
    # Body fat penalty (simplified)
    if body_fat > 35:
        score -= 25
    elif body_fat > 25:
        score -= 10
    
    # Age adjustment (slight penalty for older age)
    if age > 50:
        score -= 5
    elif age > 65:
        score -= 10
    
    return max(0, min(100, score))

def get_score_color(score):
    """Get color based on health score"""
    if score >= 80:
        return "#4CAF50"  # Green
    elif score >= 60:
        return "#FF9800"  # Orange
    else:
        return "#F44336"  # Red

def get_score_category(score):
    """Get category based on health score"""
    if score >= 80:
        return "Excellent Health"
    elif score >= 60:
        return "Good Health"
    elif score >= 40:
        return "Fair Health"
    else:
        return "Needs Improvement"

def estimate_muscle_mass(lean_mass, gender):
    """Estimate skeletal muscle mass from lean mass"""
    # Rough estimation: skeletal muscle is about 40-45% of lean mass
    multiplier = 0.45 if gender == "Male" else 0.40
    return lean_mass * multiplier

def estimate_body_water(weight_kg, age, gender):
    """Estimate total body water percentage"""
    # Watson formula approximation
    # Note: The original code used fixed heights (175, 160) which might not be accurate.
    # For a more precise calculation, height_cm should be used here.
    # Assuming height_cm is available from session state.
    height_cm = st.session_state.get('height_cm', 175.0) # Fallback to default if not found

    if gender == "Male":
        tbw = 2.447 - (0.09156 * age) + (0.1074 * height_cm) + (0.3362 * weight_kg)
    else:
        tbw = -2.097 + (0.1069 * height_cm) + (0.2466 * weight_kg)
    
    # Ensure weight_kg is not zero to avoid division by zero
    if weight_kg > 0:
        return (tbw / weight_kg) * 100
    return 0.0

def create_bmi_bodyfat_comparison(bmi, body_fat, gender):
    """Create BMI vs Body Fat comparison chart"""
    # Create ranges for comparison
    bmi_ranges = ["Underweight", "Normal", "Overweight", "Obese"]
    bmi_values = [17, 22, 27.5, 35] # Representative BMI values for categories
    
    if gender == "Male":
        bf_ranges = ["Athletic", "Fitness", "Acceptable", "High"]
        bf_values = [12, 16, 22, 30] # Representative BF values for male categories
    else:
        bf_ranges = ["Athletic", "Fitness", "Acceptable", "High"]
        bf_values = [18, 23, 28, 35] # Representative BF values for female categories
    
    fig = go.Figure()
    
    # Add BMI reference bars
    fig.add_trace(go.Bar(
        name='BMI Reference',
        x=bmi_ranges,
        y=bmi_values,
        marker_color='lightblue',
        opacity=0.6
    ))
    
    # Add current BMI point
    current_category, _ = get_bmi_category(bmi)
    fig.add_trace(go.Scatter(
        name='Your BMI',
        x=[current_category],
        y=[bmi],
        mode='markers',
        marker=dict(size=15, color='red', symbol='diamond')
    ))
    
    fig.update_layout(
        title='BMI Category Comparison',
        xaxis_title='Category',
        yaxis_title='BMI Value',
        height=300,
        title_x=0.5
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_bmr_breakdown(bmr, total_weight, lean_mass, fat_mass):
    """Create BMR breakdown visualization"""
    # Rough estimates of BMR contribution by tissue type
    # Muscle tissue burns more calories than fat tissue
    muscle_bmr = lean_mass * 13  # ~13 cal/kg for lean mass
    fat_bmr = fat_mass * 4.5    # ~4.5 cal/kg for fat mass
    
    # Ensure other_bmr is not negative
    other_bmr = max(0, bmr - muscle_bmr - fat_bmr) # Organs, brain, etc.
    
    bmr_breakdown = pd.DataFrame({
        'Component': ['Lean Mass', 'Fat Mass', 'Organs & Other'],
        'BMR Contribution': [muscle_bmr, fat_bmr, other_bmr],
        'Weight (kg)': [lean_mass, fat_mass, 0] # Weight for 'Organs & Other' is not directly applicable here
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BMR breakdown pie chart
        fig_bmr = px.pie(bmr_breakdown, 
                         values='BMR Contribution', 
                         names='Component',
                         title='BMR Breakdown by Tissue Type',
                         color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
        fig_bmr.update_traces(textposition='inside', textinfo='percent+label')
        fig_bmr.update_layout(height=300, title_x=0.5)
        st.plotly_chart(fig_bmr, use_container_width=True)
    
    with col2:
        st.markdown("*BMR Facts:*")
        st.markdown(f"• Total BMR: *{bmr:.0f} calories/day*")
        st.markdown(f"• Lean mass burns ~{muscle_bmr:.0f} cal/day")
        st.markdown(f"• Fat mass burns ~{fat_bmr:.0f} cal/day")
        st.markdown("• Muscle tissue burns 3x more calories than fat")
        st.markdown("• Building muscle increases metabolic rate")