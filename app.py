import streamlit as st
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
from enhanced_fca_cleaner import analyze_pattern

# Set page configuration
st.set_page_config(
    page_title="Fare Calculation Analyzer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1 {
        color: #2c3e50;
    }
    .highlight {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
    }
    .warning {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
    }
    .error {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("✈️ Fare Calculation Analyzer")
st.markdown("""
This tool analyzes fare calculation patterns used in the airline industry. 
It validates patterns, cleans them, and provides detailed analysis of fare components.
""")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    The Fare Calculation Analyzer (FCA) is designed to parse, validate, and clean fare calculation patterns.
    It provides detailed analysis of fare components, including journey fares, Q surcharges, and total fare calculations.
    """)
    
    st.header("Features")
    st.markdown("""
    - Pattern validation
    - Pattern cleaning
    - Fare calculation analysis
    - Automatic I- prefix handling
    - Q surcharge inclusion
    """)
    
    st.header("Instructions")
    st.markdown("""
    1. Enter a fare calculation pattern in the text area
    2. Click "Analyze Pattern"
    3. View the analysis results
    """)

# Main content
st.header("Pattern Analysis")

# Input form
with st.form("pattern_form"):
    pattern_input = st.text_area(
        "Enter fare calculation pattern:",
        height=100,
        placeholder="Example: NYC AA X/ORD UA X/DEN AS SEA 250.00 // YVR AC X/YYZ Q25.00 BA LON Q50.00 AF X/CDG LH FRA 500.00 NUC 750.00 END ROE 1.25"
    )
    
    analyze_button = st.form_submit_button("Analyze Pattern")

# Process the pattern when the button is clicked
if analyze_button and pattern_input:
    with st.spinner("Analyzing pattern..."):
        # Analyze the pattern
        result = analyze_pattern(pattern_input)
        
        # Display results
        st.subheader("Analysis Results")
        
        # Pattern validity
        if result['is_valid']:
            st.markdown('<div class="highlight">✅ Pattern is valid</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error">❌ Pattern is invalid</div>', unsafe_allow_html=True)
        
        # Original and cleaned patterns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Pattern:**")
            st.code(result['original_pattern'])
        
        with col2:
            st.markdown("**Cleaned Pattern:**")
            st.code(result['cleaned_pattern'])
        
        # Fare calculation details
        st.subheader("Fare Calculation Details")
        
        # Create a DataFrame for fare details
        fare_data = {
            "Component": ["Journey Fares", "Q Surcharge", "Class Differential", "Plus Up", "Tour Indicators", "Side Trips", "Total Journey Fare", "Expected Fare", "Calculated Fare Total"],
            "Value": [
                ", ".join([f"{fare:.2f}" for fare in result['fare_calculation']['journey_fares']]),
                f"{result['fare_calculation']['q_surcharge']:.2f}",
                f"{result['fare_calculation'].get('class_differential', 0.00):.2f}",
                f"{result['fare_calculation'].get('plus_up', 0.00):.2f}",
                ", ".join(result['fare_calculation'].get('tour_indicators', [])) or "None",
                ", ".join(result['fare_calculation'].get('side_trips', [])) or "None",
                f"{result['fare_calculation']['total_journey_fare']:.2f}",
                f"{result['fare_calculation']['expected_fare']:.2f}" if result['fare_calculation']['expected_fare'] is not None else "N/A for Tour Fares",
                f"{result['fare_calculation']['calculated_fare_total']:.2f}"
            ]
        }
        
        fare_df = pd.DataFrame(fare_data)
        st.table(fare_df)
        
        # Display garbage tokens if any
        if result.get('garbage_tokens'):
            st.subheader("Garbage Tokens")
            st.markdown('<div class="warning">The following tokens were removed from the pattern:</div>', unsafe_allow_html=True)
            st.code(", ".join(result['garbage_tokens']))
        
        # Display spacing issues if any
        if result.get('spacing_issues'):
            st.subheader("Spacing Issues")
            st.markdown('<div class="warning">The following spacing issues were fixed:</div>', unsafe_allow_html=True)
            for issue in result['spacing_issues']:
                st.markdown(f"- {issue}")

        # Visualization of fare components
        st.subheader("Fare Components Visualization")
        
        # Create a pie chart of fare components
        fig, ax = plt.subplots(figsize=(10, 6))
        components = ['Journey Fares', 'Q Surcharges', 'Class Differentials', 'Plus Up']
        values = [
            result['fare_calculation']['total_journey_fare'], 
            result['fare_calculation']['q_surcharge'],
            result['fare_calculation'].get('class_differential', 0.00),
            result['fare_calculation'].get('plus_up', 0.00)
        ]
        colors = ['#4CAF50', '#FFC107', '#2196F3', '#9C27B0']
        
        # Add explanation for tour fares if present
        if result['fare_calculation'].get('tour_indicators', []):
            tour_indicators = result['fare_calculation'].get('tour_indicators', [])
            tour_description = ", ".join(tour_indicators)
            st.markdown(f'<div class="highlight">🛫 Tour fare indicators present: {tour_description}</div>', unsafe_allow_html=True)
            
            # Add more detailed explanations for tour indicators
            st.markdown("""
            **About Tour Indicators:**
            
            Tour indicators in fare calculations identify special tour fares that have different pricing and validation rules:
            
            - **M/BT (Bulk Tour)**: 
              - Used for contracted bulk tour fares with specific negotiated rates
              - May not include explicit fare amounts in segments
              - Often has special validation exemptions
            
            - **M/IT (Inclusive Tour)**: 
              - Used for inclusive tour packages that combine airfare with accommodations or other services
              - Requires specific validation through tour codes or endorsements
              - Often has special ticketing time limits
              
            When these indicators are present, the fare validation may be more lenient as they follow different fare rules.
            """)
            
            # Add side trip explanation after the tour indicators explanation
            if result['fare_calculation'].get('side_trips', []):
                side_trips = result['fare_calculation'].get('side_trips', [])
                side_trip_description = ", ".join(side_trips)
                st.markdown(f'<div class="highlight">🛫 Side trips present: {side_trip_description}</div>', unsafe_allow_html=True)
                
                # Add more detailed explanations for side trips
                st.markdown("""
                **About Side Trips:**
                
                Side trips in fare calculations represent deviations from the main route:
                
                - **One-way with first segment as surface transportation**: 
                  - Format: `BRU(/-AMS 6X BRU53.20)`
                  - Surface transport to first city, then flight back to origin
                
                - **One-way with second segment as surface transportation**:
                  - Format: `BRU(6X AMS53.20/-BRU)`
                  - Flight to destination, then surface transport back to origin
                
                - **Round trip side trips**:
                  - Format: `BRU(6X AMS 6X BRU106.40)`
                  - Complete round trip by air from the main route point
                
                Side trips are priced separately from the main journey and are enclosed in parentheses.
                """)
            
        # Filter out zero values
        non_zero_components = []
        non_zero_values = []
        non_zero_colors = []
        for i, value in enumerate(values):
            if value > 0:
                non_zero_components.append(components[i])
                non_zero_values.append(value)
                non_zero_colors.append(colors[i])
        
        if non_zero_values:
            plt.pie(non_zero_values, labels=non_zero_components, colors=non_zero_colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            st.pyplot(fig)
        else:
            st.write("No fare components to display")
        plt.close()

elif analyze_button and not pattern_input:
    st.error("Please enter a fare calculation pattern.")

# Footer
st.markdown("---")
st.markdown("© 2025 Fare Calculation Analyzer | Built with Streamlit") 