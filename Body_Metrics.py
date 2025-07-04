import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

def app():
    """Main Body Metrics application focused on current metrics and analysis"""
    # Retrieve the backend instance from session state
    backend = st.session_state.backend 

    st.header("📏 Body Metrics & Health Analytics")
    
    # Create tabs for body metrics functionality
    tab1, tab2, tab3 = st.tabs(["📊 Current Metrics", "📈 Health Analysis", "🔍 Body Composition"])
    
    with tab1:
        display_current_metrics(backend)
    
    with tab2:
        display_health_analysis(backend)
    
    with tab3:
        display_body_composition_analysis(backend)

def display_current_metrics(backend):
    """Display current body metrics input and basic calculations"""
    
    st.subheader("Current Body Metrics Input")
    
    # Initialize session state variables with defaults
    metrics_keys = ['weight_kg', 'height_cm', 'age', 'gender']
    defaults = [70.0, 175.0, 30, "Male"]
    
    for key, default in zip(metrics_keys, defaults):
        if key not in st.session_state:
            st.session_state[key] = default

    # Input fields in organized layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.weight_kg = st.number_input(
            "⚖️ Weight (kg)", 
            min_value=20.0, max_value=300.0, 
            value=st.session_state.weight_kg, 
            step=0.1, 
            help="Enter your current weight in kilograms"
        )
        
    with col2:
        st.session_state.height_cm = st.number_input(
            "📏 Height (cm)", 
            min_value=50.0, max_value=250.0, 
            value=st.session_state.height_cm, 
            step=0.1, 
            help="Enter your height in centimeters"
        )
        
    with col3:
        st.session_state.age = st.number_input(
            "🎂 Age (years)", 
            min_value=10, max_value=100, 
            value=st.session_state.age, 
            step=1, 
            help="Enter your age in years"
        )
        
    with col4:
        st.session_state.gender = st.selectbox(
            "👥 Gender",
            ["Male", "Female"],
            index=0 if st.session_state.gender == "Male" else 1
        )
    
    # Calculate core metrics using backend
    bmi = backend.calculate_bmi(st.session_state.weight_kg, st.session_state.height_cm)
    body_fat = backend.calculate_body_fat(bmi, st.session_state.age, st.session_state.gender)
    bmr = backend.calculate_bmr(st.session_state.weight_kg, st.session_state.height_cm, st.session_state.age, st.session_state.gender)
    
    # Calculate additional basic metrics
    ideal_weight = calculate_ideal_weight(st.session_state.height_cm, st.session_state.gender)
    bmi_category, bmi_color = get_bmi_category(bmi)
    bf_category = get_body_fat_category(body_fat, st.session_state.gender)
    
    # Display results
    st.divider()
    st.subheader("📊 Your Current Health Metrics")
    
    # Primary metrics display
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

def display_health_analysis(backend):
    """Display health analysis and risk assessment"""
    
    st.subheader("Health Status Analysis")
    
    # Get current metrics
    bmi = backend.calculate_bmi(st.session_state.weight_kg, st.session_state.height_cm)
    body_fat = backend.calculate_body_fat(bmi, st.session_state.age, st.session_state.gender)
    bmr = backend.calculate_bmr(st.session_state.weight_kg, st.session_state.height_cm, st.session_state.age, st.session_state.gender)
    
    # Health status indicators
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Health Status Summary")
        
        # BMI Analysis
        bmi_category, bmi_color = get_bmi_category(bmi)
        st.markdown(f"**BMI Status:** <span style='color:{bmi_color}'>{bmi_category}</span>", 
                   unsafe_allow_html=True)
        
        # Body Fat Analysis
        bf_category = get_body_fat_category(body_fat, st.session_state.gender)
        st.markdown(f"**Body Fat Category:** {bf_category}")
        
        # Age-related considerations
        age_considerations = get_age_health_considerations(st.session_state.age)
        st.markdown(f"**Age Considerations:** {age_considerations}")
        
        # Basic health recommendations
        st.markdown("#### 💡 Key Recommendations")
        recommendations = get_basic_recommendations(bmi, body_fat, st.session_state.age, st.session_state.gender)
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    with col2:
        st.markdown("#### ⚠️ Health Risk Indicators")
        
        # Risk assessment based on metrics
        risks = assess_basic_health_risks(bmi, body_fat, st.session_state.age)
        
        if not risks:
            st.success("✅ No major risk indicators identified based on current metrics.")
        else:
            for risk in risks:
                st.warning(f"⚠️ {risk}")
        
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
    
    # Get current metrics
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
    if gender == "Male":
        tbw = 2.447 - (0.09156 * age) + (0.1074 * 175) + (0.3362 * weight_kg)  # Using average height
    else:
        tbw = -2.097 + (0.1069 * 160) + (0.2466 * weight_kg)  # Using average height
    
    return (tbw / weight_kg) * 100

def create_bmi_bodyfat_comparison(bmi, body_fat, gender):
    """Create BMI vs Body Fat comparison chart"""
    # Create ranges for comparison
    bmi_ranges = ["Underweight", "Normal", "Overweight", "Obese"]
    bmi_values = [17, 22, 27.5, 35]
    
    if gender == "Male":
        bf_ranges = ["Athletic", "Fitness", "Acceptable", "High"]
        bf_values = [12, 16, 22, 30]
    else:
        bf_ranges = ["Athletic", "Fitness", "Acceptable", "High"]
        bf_values = [18, 23, 28, 35]
    
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
    fat_bmr = fat_mass * 4.5     # ~4.5 cal/kg for fat mass
    other_bmr = bmr - muscle_bmr - fat_bmr  # Organs, brain, etc.
    
    bmr_breakdown = pd.DataFrame({
        'Component': ['Lean Mass', 'Fat Mass', 'Organs & Other'],
        'BMR Contribution': [muscle_bmr, fat_bmr, max(0, other_bmr)],
        'Weight (kg)': [lean_mass, fat_mass, 0]
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
        st.markdown("**BMR Facts:**")
        st.markdown(f"• Total BMR: **{bmr:.0f} calories/day**")
        st.markdown(f"• Lean mass burns ~{muscle_bmr:.0f} cal/day")
        st.markdown(f"• Fat mass burns ~{fat_bmr:.0f} cal/day")
        st.markdown("• Muscle tissue burns 3x more calories than fat")
        st.markdown("• Building muscle increases metabolic rate")