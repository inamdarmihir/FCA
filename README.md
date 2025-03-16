# Fare Calculation Analyzer (FCA)

A comprehensive tool for analyzing and validating fare calculation patterns used in the airline industry.

## Overview

The Fare Calculation Analyzer (FCA) is designed to parse, validate, and clean fare calculation patterns. It provides detailed analysis of fare components, including journey fares, Q surcharges, and total fare calculations.

## Key Features

- **Pattern Validation**: Validates fare calculation patterns against industry standards
- **Pattern Cleaning**: Normalizes patterns for consistent formatting
- **Fare Calculation**: Analyzes fare components and validates total fare calculations
- **Automatic Corrections**:
  - Adds "I-" prefix to patterns when missing
  - Corrects fare totals to include Q surcharges
- **Comprehensive Code Lists**:
  - Airline codes (IATA 2-letter codes)
  - Airport codes (IATA 3-letter codes)
  - Currency codes (ISO 4217)

## Recent Enhancements

- Removed dependency on the "@Web" marker
- Added automatic "I-" prefix handling
- Expanded code lists for airlines, airports, and currencies
- Improved fare calculation with automatic Q surcharge inclusion
- Fixed indentation issues in the codebase
- Added comprehensive test suite

## Usage

### Basic Usage

```python
from enhanced_fca_cleaner import analyze_pattern

# Analyze a fare calculation pattern
pattern = "NYC AA LON 250.00 NUC 250.00 END ROE 1.25"
result = analyze_pattern(pattern)

# Check if the pattern is valid
if result['is_valid']:
    print("Pattern is valid")
    print(f"Cleaned pattern: {result['cleaned_pattern']}")
    print(f"Fare calculation: {result['fare_calculation']}")
else:
    print("Pattern is invalid")
    print(f"Garbage tokens: {result['garbage_tokens']}")
```

### Complex Pattern Analysis

```python
# Analyze a complex pattern with Q surcharges
pattern = "NYC AA X/ORD UA X/DEN AS SEA 250.00 // YVR AC X/YYZ Q25.00 BA LON Q50.00 AF X/CDG LH FRA 500.00 NUC 750.00 END ROE 1.25"
result = analyze_pattern(pattern)

# The analyzer will automatically correct the fare total to include Q surcharges
print(f"Journey fares: {result['fare_calculation']['journey_fares']}")
print(f"Q surcharge: {result['fare_calculation']['q_surcharge']}")
print(f"Total journey fare: {result['fare_calculation']['total_journey_fare']}")
print(f"Expected fare: {result['fare_calculation']['expected_fare']}")
print(f"Calculated fare total: {result['fare_calculation']['calculated_fare_total']}")
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fca.git
   cd fca
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Deployment

### Local Deployment

To run the Streamlit app locally:

```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Deploy the app using `streamlit_app.py` as the main file

### Troubleshooting Deployment Issues

If you encounter issues with missing dependencies during deployment:

1. Ensure all required packages are listed in `requirements.txt`
2. Run the deployment script to check for missing dependencies:
   ```bash
   python deployment.py
   ```
3. Check the logs for any error messages
4. Make sure the Python version specified in `runtime.txt` is supported by your deployment platform

## Testing

Run the test suite to verify functionality:

```
python test_enhanced_cleaner.py
python test_real_world.py
```

## Dependencies

- Python 3.6+
- Required packages are listed in `requirements.txt`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- International Air Transport Association (IATA) for standardized airline and airport codes
- International Organization for Standardization (ISO) for currency codes 