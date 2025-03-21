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
    "Tour fare with class differential": "NYC DL X/ATL QR X/DOH EK DXB M/IT USD350.00 BKK TG HKT 100.00 NUC 450.00 END ROE1.0",
    "Pattern with class differential": "LON BA NYC D25.00 AF PAR F50.00 LH FRA 75.00 NUC 150.00 END ROE0.8",
    "Round trip with stopover": "NYC DL X/ATL O DL MIA 150.00 DL X/ATL DL NYC 150.00 NUC 300.00 END ROE1.0",
    "International with I- prefix": "I-FRA LH NYC 400.00 BA LON 200.00 NUC 600.00 END ROE0.85",
    "Pattern with multiple currencies": "NYC UA LON 250.00USD100.00 BA PAR EUR200.00 AF NYC 175.00 NUC 725.00 END ROE1.0",
    "Mileage fares with Q surcharge": "SIN SQ BKK M250.00 Q30.00 TG HKG M300.00 CX TPE M200.00 Q25.00 NUC 805.00 END ROE1.0",
    "Complex pattern with multiple side trips": "NYC AA CHI 100.00 (UA DEN UA LAS 50.00) UA LAX 150.00 (AS SEA AS PDX 75.00) AS NYC 200.00 NUC 575.00 END ROE1.0"
}

# Display examples in three columns
col1, col2, col3 = st.columns(3)

# Calculate items per column (round up to handle uneven distribution)
total_examples = len(example_patterns)
items_per_column = (total_examples + 2) // 3  # Using integer division with ceiling

# Get list of items
example_items = list(example_patterns.items())

# First column
with col1:
    for i, (description, pattern) in enumerate(example_items[:items_per_column]):
        if st.button(f"Example {i+1}: {description}", key=f"example_{i+1}"):
            st.session_state.pattern_input = pattern
            st.experimental_rerun()

# Second column
with col2:
    for i, (description, pattern) in enumerate(example_items[items_per_column:2*items_per_column]):
        idx = i + items_per_column + 1
        if st.button(f"Example {idx}: {description}", key=f"example_{idx}"):
            st.session_state.pattern_input = pattern
            st.experimental_rerun()

# Third column
with col3:
    for i, (description, pattern) in enumerate(example_items[2*items_per_column:]):
        idx = i + 2*items_per_column + 1
        if st.button(f"Example {idx}: {description}", key=f"example_{idx}"):
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
    
    **Pattern with class differential**
    - Uses letters like D, C, or F to indicate premium cabins (e.g., D for business, F for first class)
    - Class differential amounts represent the price difference from economy class
    
    **Round trip with stopover**
    - Uses O indicator to mark a stopover point
    - Contains return segments with journey fare for both outbound and return
    - Full round trip pricing structure
    
    **International with I- prefix**
    - Begins with I- prefix indicating an international fare calculation
    - Used primarily for international journeys with special fare rules
    
    **Pattern with multiple currencies**
    - Contains fare amounts in different currencies (e.g., USD, EUR)
    - Requires currency conversion to NUC (Neutral Units of Construction)
    
    **Mileage fares with Q surcharge**
    - Combines mileage-based fares (M prefix) with Q surcharges
    - Shows how different fare components can be combined
    
    **Complex pattern with multiple side trips**
    - Contains multiple parenthesized segments representing different side trips
    - Demonstrates complex fare construction with various deviations from the main route
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