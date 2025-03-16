import streamlit as st
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
from fca_cleaner import clean_fca_pattern, validate_pattern_structure
from test_patterns import load_models, predict_issues
# Import the new model improvements module
from model_improvements import (
    enhanced_clean_fca_pattern, 
    enhanced_validate_pattern_structure,
    analyze_pattern_issues,
    generate_correction_suggestions
)
# Import the enhanced FCA cleaner
from enhanced_fca_cleaner import (
    enhanced_clean_fca_pattern as enhanced_cleaner,
    analyze_pattern,
    validate_pattern_structure as enhanced_validate
)
import re

# Set page configuration
st.set_page_config(
    page_title="FCA Pattern Cleaner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .success {
        color: #0f5132;
        background-color: #d1e7dd;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #badbcc;
    }
    .error {
        color: #842029;
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #f5c2c7;
    }
    .warning {
        color: #664d03;
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffecb5;
    }
    .info {
        color: #055160;
        background-color: #cff4fc;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #b6effb;
    }
    .highlight {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
    }
    .token {
        display: inline-block;
        padding: 2px 6px;
        margin: 2px;
        border-radius: 3px;
        color: #000000;
        font-weight: 500;
    }
    .airport {
        background-color: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
    }
    .airline {
        background-color: #cff4fc;
        color: #055160;
        border: 1px solid #b6effb;
    }
    .fare {
        background-color: #fff3cd;
        color: #664d03;
        border: 1px solid #ffecb5;
    }
    .special {
        background-color: #f8d7da;
        color: #842029;
        border: 1px solid #f5c2c7;
    }
    .surface {
        background-color: #e2e3e5;
        color: #41464b;
        border: 1px solid #d3d6d8;
        font-weight: bold;
    }
    .transit {
        background-color: #6c757d;
        color: #ffffff;
        border: 1px solid #495057;
        font-weight: bold;
    }
    .garbage {
        background-color: #f8d7da;
        color: #842029;
        text-decoration: line-through;
        border: 1px solid #f5c2c7;
    }
</style>
""", unsafe_allow_html=True)

# Load models
@st.cache_resource
def get_models():
    return load_models()

# Function to display tokens with highlighting
def display_tokens(pattern, is_original=True):
    from enhanced_fca_cleaner import is_valid_token
    
    tokens = pattern.split()
    html = []
    
    for token in tokens:
        is_valid, token_type = is_valid_token(token)
        
        if is_valid:
            if token_type == "AIRPORT":
                html.append(f'<span class="token airport">{token}</span>')
            elif token_type == "AIRLINE":
                html.append(f'<span class="token airline">{token}</span>')
            elif token_type == "FARE":
                html.append(f'<span class="token fare">{token}</span>')
            elif token_type == "SURFACE":
                html.append(f'<span class="token surface">{token}</span>')
            elif token_type == "TRANSIT":
                html.append(f'<span class="token transit">{token}</span>')
            elif token_type == "SPECIAL" or token_type == "NUMERIC" or token_type == "Q_SURCHARGE" or token_type == "ROE_VALUE":
                html.append(f'<span class="token special">{token}</span>')
        else:
            if is_original:
                html.append(f'<span class="token garbage">{token}</span>')
            else:
                html.append(f'<span class="token">{token}</span>')
    
    return " ".join(html)

# Sidebar
st.sidebar.title("FCA Pattern Cleaner")
st.sidebar.image("https://img.icons8.com/fluency/96/airplane-mode-on.png", width=80)

def journey_validator():
    """Journey validation page"""
    st.title("Journey Validator")
    st.write("Validate if a journey string matches the route part of an FCA pattern and identify missing segments.")
    
    # Input for pattern and journey
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("FCA Pattern")
        pattern = st.text_area("Enter FCA Pattern", 
                              value="LON BA PAR WY DOH 800.00 NUC 800.00 END", 
                              height=100)
    
    with col2:
        st.subheader("Journey String")
        journey = st.text_area("Enter Journey String", 
                              value="LON BA PAR WY DOH", 
                              height=100)
    
    # Example buttons
    st.subheader("Examples")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Complete Match"):
            st.session_state.pattern = "LON BA PAR WY DOH 800.00 NUC 800.00 END"
            st.session_state.journey = "LON BA PAR WY DOH"
            st.experimental_rerun()
    
    with col2:
        if st.button("Missing Beginning"):
            st.session_state.pattern = "LON BA PAR WY DOH 800.00 NUC 800.00 END"
            st.session_state.journey = "PAR WY DOH"
            st.experimental_rerun()
    
    with col3:
        if st.button("Missing Middle"):
            st.session_state.pattern = "LON BA PAR WY DOH 800.00 NUC 800.00 END"
            st.session_state.journey = "LON BA DOH"
            st.experimental_rerun()
    
    with col4:
        if st.button("Missing End"):
            st.session_state.pattern = "LON BA PAR WY DOH 800.00 NUC 800.00 END"
            st.session_state.journey = "LON BA PAR"
            st.experimental_rerun()
    
    # Add example with Q surcharge
    col1, col2 = st.columns(2)
    with col1:
        if st.button("With Q Surcharge"):
            st.session_state.pattern = "LON BA PAR WY DOH 500.00 Q300.00 NUC 800.00 END"
            st.session_state.journey = "LON BA PAR WY DOH"
            st.experimental_rerun()
    
    with col2:
        if st.button("Multiple Journey Fares"):
            st.session_state.pattern = "LON BA PAR 300.00 WY DOH 500.00 NUC 800.00 END"
            st.session_state.journey = "LON BA PAR WY DOH"
            st.experimental_rerun()
    
    # Use session state if available
    if hasattr(st.session_state, 'pattern'):
        pattern = st.session_state.pattern
    if hasattr(st.session_state, 'journey'):
        journey = st.session_state.journey
    
    # Validate button
    if st.button("Validate Journey"):
        if not pattern or not journey:
            st.error("Please enter both a pattern and a journey string.")
        else:
            with st.spinner("Validating journey..."):
                # Analyze the pattern with journey validation
                analysis = analyze_pattern_with_journey(pattern, journey)
                
                # Display results
                st.markdown("### Results")
                
                # Pattern analysis
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Pattern Analysis")
                    st.write(f"Original Pattern: {pattern}")
                    st.write(f"Cleaned Pattern: {analysis.get('cleaned_pattern', analysis.get('cleaned', ''))}")
                    st.write(f"Journey String: {journey}")
                    
                    if analysis['is_valid']:
                        st.success(f"✅ Valid pattern: {analysis['message']}")
                    else:
                        st.error(f"❌ Invalid pattern: {analysis['message']}")
                
                with col2:
                    st.subheader("Journey Analysis")
                    st.write(f"Original Journey: {journey}")
                    st.write(f"Cleaned Journey: {analysis['journey_validation']['cleaned_journey']}")
                    
                    if analysis['journey_validation']['is_match']:
                        st.success("✅ Journey matches the pattern route")
                    else:
                        st.error("❌ Journey does not match the pattern route")
                
                # Journey validation details
                if not analysis['journey_validation']['is_match']:
                    st.subheader("Missing Segments")
                    
                    for segment in analysis['journey_validation']['missing_segments']:
                        st.warning(f"Missing: {segment}")
                    
                    st.subheader("Detailed Analysis")
                    st.info(analysis['missing_journey_parts'])
                
                # Fare Calculation
                if 'fare_calculation' in analysis:
                    st.subheader("Fare Calculation")
                    
                    # Journey fares
                    if analysis['fare_calculation']['journey_fares']:
                        st.markdown("**Journey Fares**")
                        for segment, fare in analysis['fare_calculation']['journey_fares'].items():
                            st.write(f"{segment}: {fare:.2f}")
                    
                    # Q surcharge
                    q_surcharge = analysis['fare_calculation']['q_surcharge']
                    if q_surcharge > 0:
                        st.write(f"**Q Surcharge**: {q_surcharge:.2f}")
                    
                    # Total calculation
                    st.markdown("**Fare Calculation**")
                    total_journey_fare = analysis['fare_calculation']['total_journey_fare']
                    calculated_nuc = analysis['fare_calculation']['calculated_nuc_total']
                    pattern_nuc = analysis['fare_calculation']['pattern_nuc_total']
                    
                    st.write(f"Total Journey Fare: {total_journey_fare:.2f}")
                    if q_surcharge > 0:
                        st.write(f"Journey Fare ({total_journey_fare:.2f}) + Q Surcharge ({q_surcharge:.2f}) = NUC Total ({calculated_nuc:.2f})")
                    else:
                        st.write(f"Journey Fare = NUC Total ({calculated_nuc:.2f})")
                    
                    # Check if calculated NUC matches pattern NUC
                    if analysis['fare_calculation']['is_nuc_match']:
                        st.success(f"✅ Calculated NUC ({calculated_nuc:.2f}) matches pattern NUC ({pattern_nuc:.2f})")
                    else:
                        st.error(f"❌ Calculated NUC ({calculated_nuc:.2f}) does not match pattern NUC ({pattern_nuc:.2f})")
                
                # Visual comparison
                st.subheader("Visual Comparison")
                
                # Extract route tokens from pattern
                pattern_tokens = analysis.get('cleaned_pattern', analysis.get('cleaned', '')).split()
                route_tokens = []
                for token in pattern_tokens:
                    if re.match(r'^\d+\.\d{2}$', token):
                        break
                    route_tokens.append(token)
                
                # Journey tokens
                journey_tokens = analysis['journey_validation']['cleaned_journey'].split()
                
                # Create HTML for highlighting
                pattern_html = []
                journey_html = []
                
                # Highlight pattern tokens
                for token in route_tokens:
                    if token in journey_tokens:
                        pattern_html.append(f'<span style="background-color: #d1e7dd; padding: 2px 4px; border-radius: 3px;">{token}</span>')
                    else:
                        pattern_html.append(f'<span style="background-color: #f8d7da; padding: 2px 4px; border-radius: 3px;">{token}</span>')
                
                # Highlight journey tokens
                for token in journey_tokens:
                    if token in route_tokens:
                        journey_html.append(f'<span style="background-color: #d1e7dd; padding: 2px 4px; border-radius: 3px;">{token}</span>')
                    else:
                        journey_html.append(f'<span style="background-color: #f8d7da; padding: 2px 4px; border-radius: 3px;">{token}</span>')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Pattern Route**")
                    st.markdown(' '.join(pattern_html), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Journey**")
                    st.markdown(' '.join(journey_html), unsafe_allow_html=True)
                
                # Legend
                st.markdown("**Legend**")
                st.markdown('<span style="background-color: #d1e7dd; padding: 2px 4px; border-radius: 3px;">Matching tokens</span> <span style="background-color: #f8d7da; padding: 2px 4px; border-radius: 3px;">Missing/extra tokens</span>', unsafe_allow_html=True)

# Navigation
page = st.sidebar.radio("Navigation", ["Single Pattern Cleaner", "Batch Processing", "Journey Validator", "Edge Case Handler", "Model Performance", "About"])

# Load models if available
models_loaded = False
try:
    garbage_model, spacing_model, vectorizer, scaler = get_models()
    if all([garbage_model, spacing_model, vectorizer, scaler]):
        models_loaded = True
        st.sidebar.success("Models loaded successfully!")
    else:
        st.sidebar.warning("Models not fully loaded. Some features may be limited.")
except Exception as e:
    st.sidebar.error(f"Error loading models: {str(e)}")

# Single Pattern Cleaner
if page == "Single Pattern Cleaner":
    st.title("FCA Pattern Cleaner")
    st.markdown("Clean and validate Fare Construction Analysis (FCA) patterns by removing garbage values and fixing spacing issues.")
    
    # Input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pattern = st.text_area("Enter FCA Pattern", 
                              value="SIN SQ LO N AA NYC OPD7LP AC YYZ 1000.00 NUC 1000.00 END", 
                              height=100)
    
    with col2:
        st.markdown("### Examples")
        example1 = "BOM WY LON BA PAR OPDQ7LP AI NYC 1000.00 NUC 1000.00 END"
        example2 = "DEL AI BO M BA LON 1000.00 NUC 1000.00 END"
        example3 = "JFK AA LHR BA CDG AF FCO 500.00 NUC 500.00 END"
        example4 = "SIN SQ LO N AA NYC OPD7LP AC YYZ 1000.00 NUC 1000.00 END"
        
        if st.button("Example 1 (Garbage)"):
            pattern = example1
            st.experimental_rerun()
        
        if st.button("Example 2 (Spacing)"):
            pattern = example2
            st.experimental_rerun()
        
        if st.button("Example 3 (Valid)"):
            pattern = example3
            st.experimental_rerun()
            
        if st.button("Example 4 (Problematic)"):
            pattern = example4
            st.experimental_rerun()
    
    # Process button
    if st.button("Clean Pattern"):
        if not pattern:
            st.error("Please enter a pattern to clean.")
        else:
            with st.spinner("Cleaning pattern..."):
                # Use the enhanced cleaner for better handling of spacing issues and valid tokens
                analysis = analyze_pattern(pattern)
                enhanced_cleaned = analysis.get('cleaned_pattern', analysis.get('cleaned', ''))
                enhanced_valid = analysis['is_valid']
                enhanced_message = analysis.get('message', '')
                has_spacing_issues = analysis.get('has_spacing_issues', False)
                spacing_fixes = analysis.get('spacing_issues', analysis.get('spacing_fixes', []))
                garbage_tokens = analysis['garbage_tokens']
                
                # Model predictions if models are loaded
                if models_loaded:
                    has_garbage, has_spacing, garbage_prob, spacing_prob = predict_issues(
                        pattern, garbage_model, spacing_model, vectorizer, scaler
                    )
                
                # Display results
                st.markdown("### Results")
                
                # Original pattern with highlighting
                st.markdown("#### Original Pattern")
                st.markdown(f'<div class="highlight">{display_tokens(pattern)}</div>', unsafe_allow_html=True)
                
                # Cleaned pattern with highlighting
                st.markdown("#### Cleaned Pattern")
                st.markdown(f'<div class="highlight">{display_tokens(enhanced_cleaned, is_original=False)}</div>', unsafe_allow_html=True)
                
                # Validation result
                if enhanced_valid:
                    st.markdown(f'<div class="success">✅ Valid pattern: {enhanced_message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error">❌ Invalid pattern: {enhanced_message}</div>', unsafe_allow_html=True)
                
                # Model predictions
                if models_loaded:
                    st.markdown("#### Model Predictions")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Garbage Detection**")
                        if has_garbage:
                            st.markdown(f'<div class="warning">Pattern contains garbage values (Probability: {garbage_prob:.4f})</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="info">No garbage values detected (Probability: {garbage_prob:.4f})</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Spacing Issues**")
                        if has_spacing:
                            st.markdown(f'<div class="warning">Pattern has spacing issues (Probability: {spacing_prob:.4f})</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="info">No spacing issues detected (Probability: {spacing_prob:.4f})</div>', unsafe_allow_html=True)
                
                # Explanation
                st.markdown("#### Explanation")
                changes = []
                
                # Add spacing fixes to changes
                if has_spacing_issues and spacing_fixes:
                    spacing_changes = []
                    for tokens, fixed in spacing_fixes:
                        spacing_changes.append(f"'{' '.join(tokens)}' → '{fixed}'")
                    changes.append(f"Fixed spacing issues: {', '.join(spacing_changes)}")
                
                # Add garbage tokens to changes
                if garbage_tokens:
                    changes.append(f"Removed garbage values: {', '.join(garbage_tokens)}")
                
                if changes:
                    st.markdown(f"Changes made: {'; '.join(changes)}")
                else:
                    st.markdown("No changes were needed; the pattern was already valid.")

# Batch Processing
elif page == "Batch Processing":
    st.title("Batch Processing")
    st.markdown("Clean and validate multiple FCA patterns at once.")
    
    # File upload
    uploaded_file = st.file_uploader("Upload a CSV or TXT file with patterns", type=["csv", "txt"])
    
    if uploaded_file is not None:
        # Process the file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                if 'pattern' not in df.columns and 'original' not in df.columns:
                    st.error("CSV file must have a 'pattern' or 'original' column.")
                else:
                    pattern_col = 'pattern' if 'pattern' in df.columns else 'original'
                    patterns = df[pattern_col].tolist()
            else:  # txt file
                content = uploaded_file.read().decode()
                patterns = [line.strip() for line in content.split('\n') if line.strip()]
            
            if not patterns:
                st.error("No patterns found in the file.")
            else:
                st.success(f"Found {len(patterns)} patterns in the file.")
                
                # Process button
                if st.button("Process All Patterns"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process each pattern
                    results = []
                    for i, pattern in enumerate(patterns):
                        status_text.text(f"Processing pattern {i+1}/{len(patterns)}")
                        progress_bar.progress((i + 1) / len(patterns))
                        
                        # Use the enhanced cleaner for better handling
                        analysis = analyze_pattern(pattern)
                        enhanced_cleaned = analysis.get('cleaned_pattern', analysis.get('cleaned', ''))
                        enhanced_valid = analysis['is_valid']
                        enhanced_message = analysis.get('message', '')
                        has_spacing_issues = analysis.get('has_spacing_issues', False)
                        spacing_fixes = analysis.get('spacing_issues', analysis.get('spacing_fixes', []))
                        garbage_tokens = analysis['garbage_tokens']
                        
                        # Model predictions if models are loaded
                        has_garbage, has_spacing = False, False
                        garbage_prob, spacing_prob = None, None
                        
                        if models_loaded:
                            has_garbage, has_spacing, garbage_prob, spacing_prob = predict_issues(
                                pattern, garbage_model, spacing_model, vectorizer, scaler
                            )
                        
                        results.append({
                            'original': pattern,
                            'cleaned': enhanced_cleaned,
                            'is_valid': enhanced_valid,
                            'message': enhanced_message,
                            'has_spacing_issues': has_spacing_issues,
                            'has_garbage': has_garbage if models_loaded else None,
                            'has_spacing': has_spacing if models_loaded else None,
                            'garbage_prob': garbage_prob if models_loaded else None,
                            'spacing_prob': spacing_prob if models_loaded else None,
                            'spacing_fixes': '; '.join([f"'{' '.join(tokens)}' → '{fixed}'" for tokens, fixed in spacing_fixes]) if spacing_fixes else "",
                            'garbage_tokens': '; '.join(garbage_tokens) if garbage_tokens else ""
                        })
                    
                    # Create results DataFrame
                    results_df = pd.DataFrame(results)
                    
                    # Display results
                    st.markdown("### Results")
                    
                    # Summary statistics
                    st.markdown("#### Summary")
                    valid_count = results_df['is_valid'].sum()
                    st.markdown(f"Successfully cleaned {valid_count} out of {len(patterns)} patterns ({valid_count/len(patterns)*100:.2f}%)")
                    
                    spacing_issues_count = results_df['has_spacing_issues'].sum()
                    st.markdown(f"Patterns with spacing issues: {spacing_issues_count} ({spacing_issues_count/len(patterns)*100:.2f}%)")
                    
                    garbage_patterns_count = results_df[results_df['garbage_tokens'] != ""].shape[0]
                    st.markdown(f"Patterns with garbage tokens: {garbage_patterns_count} ({garbage_patterns_count/len(patterns)*100:.2f}%)")
                    
                    if models_loaded:
                        garbage_count = results_df['has_garbage'].sum()
                        spacing_count = results_df['has_spacing'].sum()
                        st.markdown(f"Model predictions - Garbage: {garbage_count} ({garbage_count/len(patterns)*100:.2f}%); Spacing: {spacing_count} ({spacing_count/len(patterns)*100:.2f}%)")
                    
                    # Display the results table
                    st.markdown("#### Detailed Results")
                    display_cols = ['original', 'cleaned', 'is_valid', 'message', 'spacing_fixes', 'garbage_tokens']
                    if models_loaded:
                        display_cols.extend(['garbage_prob', 'spacing_prob'])
                    st.dataframe(results_df[display_cols])
                    
                    # Download link
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="cleaned_patterns.csv",
                        mime="text/csv"
                    )
                    
                    # Visualizations
                    if len(patterns) > 1:
                        st.markdown("#### Visualizations")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pie chart of valid vs invalid patterns
                            fig, ax = plt.subplots(figsize=(8, 6))
                            valid_counts = results_df['is_valid'].value_counts()
                            ax.pie(valid_counts, labels=['Valid', 'Invalid'] if len(valid_counts) > 1 else ['Valid'], 
                                  autopct='%1.1f%%', startangle=90, colors=['#d1e7dd', '#f8d7da'])
                            ax.set_title('Validation Results')
                            st.pyplot(fig)
                        
                        with col2:
                            # Bar chart of issue types
                            fig, ax = plt.subplots(figsize=(8, 6))
                            issue_data = {
                                'Spacing Issues': spacing_issues_count,
                                'Garbage Tokens': garbage_patterns_count,
                                'Both': sum((results_df['has_spacing_issues']) & (results_df['garbage_tokens'] != "")),
                                'None': sum((~results_df['has_spacing_issues']) & (results_df['garbage_tokens'] == ""))
                            }
                            ax.bar(issue_data.keys(), issue_data.values(), color=['#cff4fc', '#f8d7da', '#fff3cd', '#d1e7dd'])
                            ax.set_title('Issue Types')
                            ax.set_ylabel('Number of Patterns')
                            st.pyplot(fig)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Edge Case Handler
elif page == "Edge Case Handler":
    st.title("Edge Case Handler")
    st.markdown("Handle difficult edge cases with enhanced pattern cleaning and validation.")
    
    # Input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pattern = st.text_area("Enter FCA Pattern", 
                              value="SIN SQ LO N AA NYC OPD7LP AC YYZ 1000.00 NUC 1000.00 END", 
                              height=100)
    
    with col2:
        st.markdown("### Edge Case Examples")
        example1 = "bom wy lon ba par ai nyc 1000.00 nuc 1000.00 end"  # lowercase
        example2 = "BOM WY LON BA PAR AI NYC 1000.00 NUC 1200.00 END"  # mismatched fares
        example3 = "BOM WY LON BA PAR AI NYC 1000.00 NUC 1000.00"      # missing END
        example4 = "BOM WY LON BA PAR AI NYC 1000.00 1000.00 END"      # missing NUC
        example5 = "BOM WY LON BA PAR AI NYC 1000.00 NUC 1000.00 END #$%^&*" # special chars
        example6 = "SIN SQ LO N AA NYC OPD7LP AC YYZ 1000.00 NUC 1000.00 END" # problematic pattern
        
        if st.button("Lowercase"):
            pattern = example1
            st.experimental_rerun()
        
        if st.button("Mismatched Fares"):
            pattern = example2
            st.experimental_rerun()
        
        if st.button("Missing END"):
            pattern = example3
            st.experimental_rerun()
            
        if st.button("Missing NUC"):
            pattern = example4
            st.experimental_rerun()
            
        if st.button("Special Chars"):
            pattern = example5
            st.experimental_rerun()
            
        if st.button("Problematic"):
            pattern = example6
            st.experimental_rerun()
    
    # Process button
    if st.button("Analyze Pattern"):
        if not pattern:
            st.error("Please enter a pattern to analyze.")
        else:
            with st.spinner("Analyzing pattern..."):
                # Standard cleaning
                standard_cleaned = clean_fca_pattern(pattern)
                standard_valid, standard_message = validate_pattern_structure(standard_cleaned)
                
                # Enhanced cleaning using our new enhanced cleaner
                analysis = analyze_pattern(pattern)
                enhanced_cleaned = analysis.get('cleaned_pattern', analysis.get('cleaned', ''))
                enhanced_valid = analysis['is_valid']
                enhanced_message = analysis.get('message', '')
                has_spacing_issues = analysis.get('has_spacing_issues', False)
                spacing_fixes = analysis.get('spacing_fixes', [])
                garbage_tokens = analysis['garbage_tokens']
                
                # Original model improvements for comparison
                model_enhanced_cleaned = enhanced_clean_fca_pattern(pattern)
                model_enhanced_valid, model_enhanced_message = enhanced_validate_pattern_structure(model_enhanced_cleaned)
                
                # Analyze issues with original model improvements
                issues = analyze_pattern_issues(pattern)
                
                # Generate suggestions with original model improvements
                suggestions = generate_correction_suggestions(pattern, model_enhanced_cleaned, issues)
                
                # Model predictions if models are loaded
                if models_loaded:
                    has_garbage, has_spacing, garbage_prob, spacing_prob = predict_issues(
                        pattern, garbage_model, spacing_model, vectorizer, scaler
                    )
                
                # Display results
                st.markdown("### Results")
                
                # Original pattern with highlighting
                st.markdown("#### Original Pattern")
                st.markdown(f'<div class="highlight">{display_tokens(pattern)}</div>', unsafe_allow_html=True)
                
                # Comparison of standard vs enhanced cleaning
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### Standard Cleaning")
                    st.markdown(f'<div class="highlight">{display_tokens(standard_cleaned, is_original=False)}</div>', unsafe_allow_html=True)
                    
                    if standard_valid:
                        st.markdown(f'<div class="success">✅ Valid pattern: {standard_message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error">❌ Invalid pattern: {standard_message}</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### Model Improvements")
                    st.markdown(f'<div class="highlight">{display_tokens(model_enhanced_cleaned, is_original=False)}</div>', unsafe_allow_html=True)
                    
                    if model_enhanced_valid:
                        st.markdown(f'<div class="success">✅ Valid pattern: {model_enhanced_message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error">❌ Invalid pattern: {model_enhanced_message}</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown("#### Enhanced Cleaning")
                    st.markdown(f'<div class="highlight">{display_tokens(enhanced_cleaned, is_original=False)}</div>', unsafe_allow_html=True)
                    
                    if enhanced_valid:
                        st.markdown(f'<div class="success">✅ Valid pattern: {enhanced_message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error">❌ Invalid pattern: {enhanced_message}</div>', unsafe_allow_html=True)
                
                # Issue analysis
                st.markdown("#### Issue Analysis")
                
                # Original model improvements issues
                st.markdown("**Original Model Improvements Analysis:**")
                issue_cols = st.columns(5)
                
                with issue_cols[0]:
                    if issues["has_lowercase"]:
                        st.markdown(f'<div class="warning">Lowercase</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info">No lowercase</div>', unsafe_allow_html=True)
                
                with issue_cols[1]:
                    if issues["has_special_chars"]:
                        st.markdown(f'<div class="warning">Special chars</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info">No special chars</div>', unsafe_allow_html=True)
                
                with issue_cols[2]:
                    if issues["has_missing_end"]:
                        st.markdown(f'<div class="warning">Missing END</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info">Has END</div>', unsafe_allow_html=True)
                
                with issue_cols[3]:
                    if issues["has_missing_nuc"]:
                        st.markdown(f'<div class="warning">Missing NUC</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info">Has NUC</div>', unsafe_allow_html=True)
                
                with issue_cols[4]:
                    if issues["has_mismatched_fares"]:
                        st.markdown(f'<div class="warning">Mismatched fares</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info">Matching fares</div>', unsafe_allow_html=True)
                
                # Enhanced cleaner analysis
                st.markdown("**Enhanced Cleaner Analysis:**")
                
                # Spacing issues
                if has_spacing_issues and spacing_fixes:
                    st.markdown("**Spacing Issues:**")
                    for tokens, fixed in spacing_fixes:
                        st.markdown(f'<div class="warning">"{" ".join(tokens)}" → "{fixed}"</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info">No spacing issues detected</div>', unsafe_allow_html=True)
                
                # Garbage tokens
                if garbage_tokens:
                    st.markdown("**Garbage Tokens:**")
                    for token in garbage_tokens:
                        st.markdown(f'<div class="warning">"{token}"</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="info">No garbage tokens detected</div>', unsafe_allow_html=True)
                
                # Correction suggestions
                if suggestions:
                    st.markdown("#### Correction Suggestions")
                    for i, suggestion in enumerate(suggestions):
                        st.markdown(f"{i+1}. {suggestion}")
                
                # Model predictions
                if models_loaded:
                    st.markdown("#### Model Predictions")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Garbage Detection**")
                        if has_garbage:
                            st.markdown(f'<div class="warning">Pattern contains garbage values (Probability: {garbage_prob:.4f})</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="info">No garbage values detected (Probability: {garbage_prob:.4f})</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Spacing Issues**")
                        if has_spacing:
                            st.markdown(f'<div class="warning">Pattern has spacing issues (Probability: {spacing_prob:.4f})</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="info">No spacing issues detected (Probability: {spacing_prob:.4f})</div>', unsafe_allow_html=True)

# Model Performance
elif page == "Model Performance":
    st.title("Model Performance")
    
    if not models_loaded:
        st.warning("Models are not loaded. Please train models first.")
    else:
        st.markdown("### Model Accuracy")
        
        # Display model performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Garbage Detection Model")
            if hasattr(garbage_model, 'feature_importances_'):
                # Feature importance
                st.markdown("Top 10 Features:")
                feature_cols = []
                try:
                    with open('models/feature_columns.pkl', 'rb') as f:
                        import pickle
                        feature_cols = pickle.load(f)
                except:
                    feature_cols = [f"Feature {i}" for i in range(len(garbage_model.feature_importances_))]
                
                top_features = sorted(zip(feature_cols, garbage_model.feature_importances_), 
                                     key=lambda x: x[1], reverse=True)[:10]
                
                # Create a bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                feature_names = [f[0] for f in top_features]
                feature_importances = [f[1] for f in top_features]
                
                # Shorten feature names if they're too long
                feature_names = [name[:20] + '...' if len(name) > 20 else name for name in feature_names]
                
                ax.barh(feature_names, feature_importances, color='skyblue')
                ax.set_xlabel('Importance')
                ax.set_title('Top 10 Features for Garbage Detection')
                plt.tight_layout()
                st.pyplot(fig)
        
        with col2:
            st.markdown("#### Spacing Issues Model")
            if hasattr(spacing_model, 'feature_importances_'):
                # Feature importance
                st.markdown("Top 10 Features:")
                feature_cols = []
                try:
                    with open('models/feature_columns.pkl', 'rb') as f:
                        import pickle
                        feature_cols = pickle.load(f)
                except:
                    feature_cols = [f"Feature {i}" for i in range(len(spacing_model.feature_importances_))]
                
                top_features = sorted(zip(feature_cols, spacing_model.feature_importances_), 
                                     key=lambda x: x[1], reverse=True)[:10]
                
                # Create a bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                feature_names = [f[0] for f in top_features]
                feature_importances = [f[1] for f in top_features]
                
                # Shorten feature names if they're too long
                feature_names = [name[:20] + '...' if len(name) > 20 else name for name in feature_names]
                
                ax.barh(feature_names, feature_importances, color='lightgreen')
                ax.set_xlabel('Importance')
                ax.set_title('Top 10 Features for Spacing Issues Detection')
                plt.tight_layout()
                st.pyplot(fig)
        
        # Test on examples from the prompt
        st.markdown("### Test on Examples")
        
        examples = [
            "BOM WY LON BA PAR OPDQ7LP AI NYC 1000.00 NUC 1000.00 END",  # Has garbage
            "DEL AI BO M BA LON 1000.00 NUC 1000.00 END",  # Has spacing issues
            "JFK AA LHR BA CDG AF FCO 500.00 NUC 500.00 END",  # Valid pattern
            "SFO UA LHR QX123Z BA CDG 750.50 NUC 750.50 END",  # Has garbage
            "NYC DL A MS TER DAM 800.00 NUC 800.00 END",  # Has spacing issues
            "LAX AA L ON BA PAR 123ABC AF ROM 900.00 NUC 900.00 END",  # Has both issues
        ]
        
        results = []
        for example in examples:
            # Clean and validate
            cleaned = clean_fca_pattern(example)
            is_valid, message = validate_pattern_structure(cleaned)
            
            # Model predictions
            has_garbage, has_spacing, garbage_prob, spacing_prob = predict_issues(
                example, garbage_model, spacing_model, vectorizer, scaler
            )
            
            results.append({
                'original': example,
                'cleaned': cleaned,
                'is_valid': is_valid,
                'message': message,
                'has_garbage': has_garbage,
                'has_spacing': has_spacing,
                'garbage_prob': garbage_prob,
                'spacing_prob': spacing_prob
            })
        
        # Display results
        for i, result in enumerate(results):
            with st.expander(f"Example {i+1}: {result['original']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Original Pattern**")
                    st.markdown(f'<div class="highlight">{display_tokens(result["original"])}</div>', unsafe_allow_html=True)
                    
                    st.markdown("**Model Predictions**")
                    st.markdown(f"Has garbage: {'Yes' if result['has_garbage'] else 'No'} (Probability: {result['garbage_prob']:.4f})")
                    st.markdown(f"Has spacing issues: {'Yes' if result['has_spacing'] else 'No'} (Probability: {result['spacing_prob']:.4f})")
                
                with col2:
                    st.markdown("**Cleaned Pattern**")
                    st.markdown(f'<div class="highlight">{display_tokens(result["cleaned"], is_original=False)}</div>', unsafe_allow_html=True)
                    
                    st.markdown("**Validation**")
                    if result['is_valid']:
                        st.markdown(f'<div class="success">✅ Valid pattern: {result["message"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error">❌ Invalid pattern: {result["message"]}</div>', unsafe_allow_html=True)

# Journey Validator
elif page == "Journey Validator":
    journey_validator()

# About
else:
    st.title("About FCA Pattern Cleaner")
    
    st.markdown("""
    ## Overview

    This application provides a comprehensive solution for cleaning and validating Fare Construction Analysis (FCA) patterns. It can identify and remove garbage values, fix spacing issues, and ensure the patterns follow the correct structure.

    ## Key Features

    1. **Garbage Value Detection**: Identifies and removes random alphanumeric strings that don't belong in FCA patterns.
    2. **Spacing Issue Correction**: Fixes patterns where valid tokens have been incorrectly split (e.g., "BO M" → "BOM").
    3. **Pattern Validation**: Ensures patterns follow the correct structure with alternating airport and airline codes.
    4. **Machine Learning Models**: Uses trained models to detect patterns with issues.
    5. **Synthetic Data Generation**: Creates a diverse dataset for training with various edge cases.

    ## How It Works

    The application uses a combination of rule-based cleaning and machine learning models:

    1. **Rule-based Cleaning**:
       - Removes tokens that are not valid airport codes, airline codes, fare amounts, or special tokens
       - Fixes spacing issues by combining split tokens
       - Reconstructs valid patterns when possible

    2. **Machine Learning Models**:
       - Garbage Detection: Identifies patterns with random alphanumeric strings
       - Spacing Issues Detection: Identifies patterns with incorrectly split tokens

    ## Color Legend

    - <span class="token airport">Airport Codes</span>
    - <span class="token airline">Airline Codes</span>
    - <span class="token fare">Fare Amounts</span>
    - <span class="token special">Special Tokens</span>
    - <span class="token garbage">Garbage Values</span>
    """, unsafe_allow_html=True)

    st.markdown("## Project Team")
    st.markdown("Developed by the FCA Pattern Cleaner Team")
    
    st.markdown("## Version")
    st.markdown("1.0.0")

def display_pattern_analysis(pattern):
    """Display detailed analysis of a pattern"""
    analysis = analyze_pattern(pattern)
    
    st.subheader("Original Pattern")
    st.write(analysis.get('original_pattern', analysis.get('original', '')))
    
    st.subheader("Cleaned Pattern")
    st.write(analysis.get('cleaned_pattern', analysis.get('cleaned', '')))
    
    if analysis['is_valid']:
        st.success(f"✅ Valid pattern: {analysis.get('message', '')}")
    else:
        st.error(f"❌ Invalid pattern: {analysis.get('message', '')}")
    
    # Load models for prediction
    garbage_model = load_model("garbage_model.pkl")
    spacing_model = load_model("spacing_model.pkl")
    
    if garbage_model and spacing_model:
        st.subheader("Model Predictions")
        
        # Predict garbage
        garbage_prob = predict_garbage(garbage_model, pattern)
        st.write("Garbage Detection")
        if garbage_prob > 0.5:
            st.write(f"Pattern contains garbage values (Probability: {garbage_prob:.4f})")
        else:
            st.write(f"No garbage values detected (Probability: {garbage_prob:.4f})")
        
        # Predict spacing issues
        spacing_prob = predict_spacing_issues(spacing_model, pattern)
        st.write("Spacing Issues")
        if spacing_prob > 0.5:
            st.write(f"Pattern has spacing issues (Probability: {spacing_prob:.4f})")
        else:
            st.write(f"No spacing issues detected (Probability: {spacing_prob:.4f})")
    
    st.subheader("Explanation")
    
    # Explain changes made
    changes = []
    
    # Check for spacing issues
    if analysis['has_spacing_issues']:
        spacing_fixes = []
        
        # Regular spacing fixes
        for tokens, fixed in analysis['spacing_fixes']:
            spacing_fixes.append(f"'{' '.join(tokens)}' → '{fixed}'")
        
        # Concatenated token fixes
        if 'concatenated_fixes' in analysis:
            for token, split_tokens in analysis['concatenated_fixes']:
                spacing_fixes.append(f"'{token}' → '{' '.join(split_tokens)}'")
        
        if spacing_fixes:
            changes.append(f"Fixed spacing issues: {', '.join(spacing_fixes)}")
    
    # Check for garbage tokens
    if analysis['garbage_tokens']:
        garbage_list = [f"'{token}'" for token in analysis['garbage_tokens']]
        changes.append(f"Removed garbage values: {', '.join(garbage_list)}")
    
    if changes:
        st.write("Changes made: " + "; ".join(changes))
    else:
        st.write("No changes needed.")
    
    # Display token highlighting
    st.subheader("Token Highlighting")
    
    # Create columns for original and cleaned
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Original Pattern")
        display_highlighted_tokens(analysis.get('original_pattern', analysis.get('original', '')))
    
    with col2:
        st.write("Cleaned Pattern")
        display_highlighted_tokens(analysis.get('cleaned_pattern', analysis.get('cleaned', '')))

def display_highlighted_tokens(pattern):
    """Display tokens with color highlighting based on their type"""
    tokens = pattern.split()
    html = []
    
    for token in tokens:
        is_valid, token_type = is_valid_token(token)
        
        if not is_valid:
            # Check if it might be part of a concatenated token
            split_tokens = split_concatenated_tokens(token)
            if len(split_tokens) > 1:
                # This is a concatenated token
                html.append(f'<span style="background-color: #ffcc00; padding: 2px 4px; border-radius: 3px;" title="Concatenated tokens: {" ".join(split_tokens)}">{token}</span>')
                continue
            
            # It's a garbage token
            html.append(f'<span style="background-color: #ff6b6b; padding: 2px 4px; border-radius: 3px;" title="Garbage">{token}</span>')
        elif token_type == "AIRPORT":
            html.append(f'<span style="background-color: #4ecdc4; padding: 2px 4px; border-radius: 3px;" title="Airport">{token}</span>')
        elif token_type == "AIRLINE":
            html.append(f'<span style="background-color: #a9e34b; padding: 2px 4px; border-radius: 3px;" title="Airline">{token}</span>')
        elif token_type == "FARE":
            html.append(f'<span style="background-color: #f7fff7; padding: 2px 4px; border-radius: 3px;" title="Fare">{token}</span>')
        elif token_type == "SPECIAL":
            html.append(f'<span style="background-color: #ff9f1c; padding: 2px 4px; border-radius: 3px;" title="Special Token">{token}</span>')
    
    st.markdown(' '.join(html), unsafe_allow_html=True)

def edge_case_handler():
    """Handle edge cases in FCA patterns"""
    st.title("Edge Case Handler")
    st.write("This page helps you handle edge cases in FCA patterns that might be difficult to clean automatically.")
    
    # Example patterns
    st.subheader("Example Patterns")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Spacing Example"):
            st.session_state.edge_case_pattern = "SIN SQ LO N AA NYC AC YY Z 1000.00 NUC 1000.00 EN D"
    
    with col2:
        if st.button("Garbage Example"):
            st.session_state.edge_case_pattern = "SIN SQ LON AA NYC XYZ123 AC YYZ 1000.00 NUC 1000.00 END"
    
    with col3:
        if st.button("Concatenated Example"):
            st.session_state.edge_case_pattern = "SINSQLON AA NYC OPD7LP AC YYZ 1000.00 NUC 1000.00 END"
    
    with col4:
        if st.button("Problematic Example"):
            st.session_state.edge_case_pattern = "SINSQLONAA NYC ACYYZ 1000.00 NUC1000.00 END"
    
    # Input for pattern
    pattern = st.text_area("Enter FCA Pattern", value=st.session_state.get("edge_case_pattern", ""), height=100)
    
    if pattern:
        # Analyze the pattern
        analysis = analyze_pattern(pattern)
        
        # Display side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Pattern")
            st.write(pattern)
            display_highlighted_tokens(pattern)
            
            # Show detected issues
            if analysis['has_spacing_issues']:
                st.subheader("Detected Spacing Issues")
                
                # Regular spacing fixes
                for tokens, fixed in analysis['spacing_fixes']:
                    st.write(f"'{' '.join(tokens)}' → '{fixed}'")
                
                # Concatenated token fixes
                if 'concatenated_fixes' in analysis:
                    for token, split_tokens in analysis['concatenated_fixes']:
                        st.write(f"'{token}' → '{' '.join(split_tokens)}'")
            
            if analysis['garbage_tokens']:
                st.subheader("Detected Garbage Tokens")
                for token in analysis['garbage_tokens']:
                    st.write(f"'{token}'")
        
        with col2:
            st.subheader("Cleaned Pattern")
            st.write(analysis.get('cleaned_pattern', analysis.get('cleaned', '')))
            display_highlighted_tokens(analysis.get('cleaned_pattern', analysis.get('cleaned', '')))
            
            if analysis['is_valid']:
                st.success(f"✅ Valid pattern: {analysis['message']}")
            else:
                st.error(f"❌ Invalid pattern: {analysis['message']}")
        
        # Manual editing section
        st.subheader("Manual Editing")
        st.write("If the automatic cleaning didn't produce the expected result, you can manually edit the pattern below:")
        
        manual_pattern = st.text_area("Manual Edit", value=analysis.get('cleaned_pattern', analysis.get('cleaned', '')), height=100)
        
        if st.button("Validate Manual Edit"):
            is_valid, message = validate_pattern_structure(manual_pattern)
            
            if is_valid:
                st.success(f"✅ Valid pattern: {message}")
            else:
                st.error(f"❌ Invalid pattern: {message}")
            
            display_highlighted_tokens(manual_pattern) 