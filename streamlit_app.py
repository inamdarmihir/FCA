import streamlit as st
import pandas as pd
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
        
        # Check for fare mismatch warning
        if 'fare_mismatch_warning' in result:
            st.markdown(f'<div class="warning">⚠️ {result["fare_mismatch_warning"]}</div>', unsafe_allow_html=True)
        
        # Create a DataFrame for fare details
        fare_data = {
            "Component": ["Journey Fares", "Q Surcharge", "Plus Up", "Total Journey Fare", "Expected Fare", "Calculated Fare Total"],
            "Value": [
                ", ".join([f"{fare:.2f}" for fare in result['fare_calculation']['journey_fares']]),
                f"{result['fare_calculation']['q_surcharge']:.2f}",
                f"{result['fare_calculation'].get('plus_up', 0.00):.2f}",
                f"{result['fare_calculation']['total_journey_fare']:.2f}",
                f"{result['fare_calculation']['expected_fare']:.2f}" if result['fare_calculation']['expected_fare'] is not None else "N/A",
                f"{result['fare_calculation']['calculated_fare_total']:.2f}"
            ]
        }
        
        fare_df = pd.DataFrame(fare_data)
        st.table(fare_df)
        
        # Display garbage tokens if any
        if result['garbage_tokens']:
            st.subheader("Garbage Tokens")
            st.markdown('<div class="warning">The following tokens were removed from the pattern:</div>', unsafe_allow_html=True)
            st.code(", ".join(result['garbage_tokens']))
        
        # Display spacing issues if any
        if result['spacing_issues']:
            st.subheader("Spacing Issues")
            st.markdown('<div class="warning">The following spacing issues were fixed:</div>', unsafe_allow_html=True)
            for issue in result['spacing_issues']:
                st.markdown(f"- {issue}")

elif analyze_button and not pattern_input:
    st.error("Please enter a fare calculation pattern.")

# Footer
st.markdown("---")
st.markdown("© 2025 Fare Calculation Analyzer | Powered by Streamlit") 