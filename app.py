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

# Initialize session state for pattern_input if it doesn't exist
if 'pattern_input' not in st.session_state:
    st.session_state.pattern_input = ""
if 'last_pattern' not in st.session_state:
    st.session_state.last_pattern = ""

# Example patterns section
st.subheader("Example Patterns")
st.markdown("Click on any example to try it out:")

example_patterns = {
    "Multi-segment journey with Q surcharges": "NYC AA X/ORD UA X/DEN AS SEA 250.00 // YVR AC X/YYZ Q25.00 BA LON Q50.00 AF X/CDG LH FRA 500.00 NUC 750.00 END ROE 1.25",
    "Pattern with plus up": "LON BA NYC 80.00 P LONNYC 20.00 NUC 100.00 END ROE1.25",
    "Pattern with mileage fares": "LON BA BKK TG SIN M1000.00 SQ JKT GA SYD M1800.00 P LONSIN 100.00 NUC 2900.00 END",
    "Pattern with side trip": "BRU LH FRA 150.00 (LH AMS LH BRU 100.00) BA LON 200.00 NUC 450.00 END ROE1.0",
    "One-way side trip with surface": "LON BA FRA 150.00 (/-AMS KL BRU 75.00) LH MUC 120.00 NUC 345.00 END ROE0.9",
    "Complex pattern with stopovers": "JFK AA X/DFW AS X/SEA BA LON M500.00 AF X/PAR LH X/FRA TK IST M750.00 EK X/DXB SQ SIN M900.00 NUC 2150.00 END ROE1.0",
    "Tour fare with class differential": "NYC DL X/ATL QR X/DOH EK DXB M/IT USD350.00 BKK TG HKT 100.00 NUC 450.00 END ROE1.0",
    "Pattern with class differential": "LON BA NYC D LONNYC 25.00 AF PAR F 50.00 LH FRA 75.00 NUC 150.00 END ROE0.8",
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

# Second column
with col2:
    for i, (description, pattern) in enumerate(example_items[items_per_column:2*items_per_column]):
        idx = i + items_per_column + 1
        if st.button(f"Example {idx}: {description}", key=f"example_{idx}"):
            st.session_state.pattern_input = pattern

# Third column
with col3:
    for i, (description, pattern) in enumerate(example_items[2*items_per_column:]):
        idx = i + 2*items_per_column + 1
        if st.button(f"Example {idx}: {description}", key=f"example_{idx}"):
            st.session_state.pattern_input = pattern

# Display status message when example is selected
if st.session_state.pattern_input != st.session_state.last_pattern and st.session_state.pattern_input != "":
    st.success("Example pattern selected! Scroll down to analyze it or modify it in the text area below.")
    st.session_state.last_pattern = st.session_state.pattern_input

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
    - Contains a segment enclosed in parentheses, representing a round-trip deviation from the main journey
    - Format: `Origin Airline Stopover Fare (Airline SideTrip Airline Origin SideTrip_Fare) Airline Destination MainFare`
    - Example: `BRU LH FRA 150.00 (LH AMS LH BRU 100.00) BA LON 200.00`
    - Side trips are priced separately and added to the total fare
    
    **One-way side trip with surface transportation**
    - Includes surface transportation marker (/-) indicating non-flight segment
    - Format: `Origin Airline Destination Fare (/-SurfaceOrigin Airline SurfaceDestination SideTrip_Fare)`
    - Example: `LON BA FRA 150.00 (/-AMS KL BRU 75.00)`
    - Combines flight and surface segments in a cohesive fare calculation
    
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