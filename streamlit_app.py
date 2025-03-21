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

# Example patterns section
st.subheader("Example Patterns")
st.markdown("Click on any example to try it out:")

example_patterns = {
    "Multi-segment journey with Q surcharges": "NYC AA X/ORD UA X/DEN AS SEA 250.00 // YVR AC X/YYZ Q25.00 BA LON Q50.00 AF X/CDG LH FRA 500.00 NUC 750.00 END ROE 1.25",
    "Pattern with plus up": "LON BA NYC 80.00 P LONNYC 20.00 NUC 100.00 END ROE1.25",
    "Pattern with mileage fares": "LON BA BKK TG SIN M1000.00 SQ JKT GA SYD M1800.00 P LONSIN 100.00 NUC 2900.00 END",
    "Pattern with side trip": "LON BA NYC 80.00 (BA AMS) AF MAD 5.00 P LON NYC 5.00 NUC 90.00 END ROE1.25",
    "Complex pattern with stopovers": "JFK AA X/DFW AS X/SEA BA LON M500.00 AF X/PAR LH X/FRA TK IST M750.00 EK X/DXB SQ SIN M900.00 NUC 2150.00 END ROE1.0",
    "Tour fare with class differential": "NYC DL X/ATL QR X/DOH EK DXB M/IT USD350.00 BKK TG HKT 100.00 NUC 450.00 END ROE1.0"
}

col1, col2 = st.columns(2)
with col1:
    for i, (description, pattern) in enumerate(list(example_patterns.items())[:3]):
        if st.button(f"Example {i+1}: {description}", key=f"example_{i+1}"):
            st.session_state.pattern_input = pattern
            st.experimental_rerun()

with col2:
    for i, (description, pattern) in enumerate(list(example_patterns.items())[3:]):
        if st.button(f"Example {i+4}: {description}", key=f"example_{i+4}"):
            st.session_state.pattern_input = pattern
            st.experimental_rerun()

# Explanation of pattern types
with st.expander("Learn more about pattern types"):
    st.markdown("""
    ### Fare Calculation Pattern Components
    
    **Multi-segment journey with Q surcharges**
    - Contains multiple flight segments with different carriers
    - Includes Q surcharges (fees added to the base fare)
    - Uses X/ to indicate connection points
    
    **Pattern with plus up**
    - Contains a plus up component (P) which adds an amount to the journey fare
    - Format: `P CITYCITY amount` or `P CITY CITY amount`
    
    **Pattern with mileage fares**
    - Contains fares with M prefix (e.g., M1000.00) indicating mileage-based pricing
    - Often used for complex international routings
    
    **Pattern with side trip**
    - Contains a segment enclosed in parentheses, indicating a deviation from the main journey
    - Side trips are priced separately and added to the total fare
    
    **Complex pattern with stopovers**
    - Contains multiple X/ connection points and multiple carriers
    - Includes mileage fares for different segments
    
    **Tour fare with class differential**
    - Contains M/IT or M/BT indicators for inclusive or bulk tours
    - May include class differential pricing for different cabin classes
    """)

# Input form
with st.form("pattern_form"):
    pattern_input = st.text_area(
        "Enter fare calculation pattern:",
        height=100,
        value=st.session_state.get("pattern_input", ""),
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