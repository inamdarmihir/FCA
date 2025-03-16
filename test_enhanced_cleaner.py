#!/usr/bin/env python
"""
Test script to verify that the enhanced cleaner works correctly with the updated code lists
and without the @Web marker.
"""

from enhanced_fca_cleaner import analyze_pattern
import traceback

def test_airline_codes():
    """Test recognition of airline codes"""
    print("=== Testing Airline Code Recognition ===\n")
    
    try:
        # Test with various airline codes
        airlines_to_test = ["AA", "BA", "LH", "AF", "KL", "EK", "QR", "SQ", "CX", "AS"]
        
        for airline in airlines_to_test:
            pattern = f"NYC {airline} LON 250.00 NUC 250.00 END ROE 1.25"
            print(f"Testing airline code: {airline}")
            result = analyze_pattern(pattern)
            
            # Check if the pattern is valid
            if result['is_valid']:
                print(f"✓ Airline code {airline} recognized successfully")
            else:
                print(f"✗ Airline code {airline} not recognized")
            
            # Check if the airline code is in the cleaned pattern
            if airline in result['cleaned_pattern']:
                print(f"✓ Airline code {airline} preserved in cleaned pattern")
            else:
                print(f"✗ Airline code {airline} not preserved in cleaned pattern")
            
            print()
    except Exception as e:
        print(f"Error in test_airline_codes: {e}")
        traceback.print_exc()

def test_airport_codes():
    """Test recognition of airport codes"""
    print("=== Testing Airport Code Recognition ===\n")
    
    try:
        # Test with various airport codes
        airports_to_test = ["NYC", "LON", "PAR", "FRA", "AMS", "DXB", "SIN", "HKG", "SYD", "JNB"]
        
        for airport in airports_to_test:
            pattern = f"{airport} AA LON 250.00 NUC 250.00 END ROE 1.25"
            print(f"Testing airport code: {airport}")
            result = analyze_pattern(pattern)
            
            # Check if the pattern is valid
            if result['is_valid']:
                print(f"✓ Airport code {airport} recognized successfully")
            else:
                print(f"✗ Airport code {airport} not recognized")
            
            # Check if the airport code is in the cleaned pattern
            if airport in result['cleaned_pattern']:
                print(f"✓ Airport code {airport} preserved in cleaned pattern")
            else:
                print(f"✗ Airport code {airport} not preserved in cleaned pattern")
            
            print()
    except Exception as e:
        print(f"Error in test_airport_codes: {e}")
        traceback.print_exc()

def test_currency_codes():
    """Test recognition of currency codes"""
    print("=== Testing Currency Code Recognition ===\n")
    
    try:
        # Test with various currency codes
        currencies_to_test = ["NUC", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY"]
        
        for currency in currencies_to_test:
            pattern = f"NYC AA LON 250.00 {currency} 250.00 END ROE 1.25"
            print(f"Testing currency code: {currency}")
            result = analyze_pattern(pattern)
            
            # Check if the pattern is valid
            if result['is_valid']:
                print(f"✓ Currency code {currency} recognized successfully")
            else:
                print(f"✗ Currency code {currency} not recognized")
            
            # Check if the currency code is in the cleaned pattern
            if currency in result['cleaned_pattern']:
                print(f"✓ Currency code {currency} preserved in cleaned pattern")
            else:
                print(f"✗ Currency code {currency} not preserved in cleaned pattern")
            
            print()
    except Exception as e:
        print(f"Error in test_currency_codes: {e}")
        traceback.print_exc()

def test_web_marker_removal():
    """Test removal of @Web marker"""
    print("=== Testing @Web Marker Removal ===\n")
    
    try:
        # Test with @Web marker
        pattern_with_web = "@Web NYC AA LON 250.00 NUC 250.00 END ROE 1.25"
        print(f"Original pattern with @Web: {pattern_with_web}")
        result = analyze_pattern(pattern_with_web)
        
        # Check if the @Web marker is removed
        if "@Web" not in result['cleaned_pattern']:
            print("✓ @Web marker successfully removed from cleaned pattern")
        else:
            print("✗ @Web marker not removed from cleaned pattern")
        
        # Check if the pattern is valid
        if result['is_valid']:
            print("✓ Pattern with @Web marker is valid after processing")
        else:
            print("✗ Pattern with @Web marker is not valid after processing")
        
        print(f"Cleaned pattern: {result['cleaned_pattern']}")
        print()
    except Exception as e:
        print(f"Error in test_web_marker_removal: {e}")
        traceback.print_exc()

def test_i_prefix_preservation():
    """Test I- prefix preservation"""
    print("=== Testing I- Prefix Preservation ===\n")
    
    try:
        # Test with I- prefix
        pattern_with_i = "I- NYC AA LON 250.00 NUC 250.00 END ROE 1.25"
        print(f"Original pattern with I-: {pattern_with_i}")
        result = analyze_pattern(pattern_with_i)
        
        # Check if the I- prefix is preserved
        if result['cleaned_pattern'].startswith("I-"):
            print("✓ I- prefix preserved in cleaned pattern")
        else:
            print("✗ I- prefix not preserved in cleaned pattern")
        
        # Test without I- prefix
        pattern_without_i = "NYC AA LON 250.00 NUC 250.00 END ROE 1.25"
        print(f"\nOriginal pattern without I-: {pattern_without_i}")
        result = analyze_pattern(pattern_without_i)
        
        # Check if the I- prefix is added
        if result['cleaned_pattern'].startswith("I-"):
            print("✓ I- prefix added to cleaned pattern")
        else:
            print("✗ I- prefix not added to cleaned pattern")
        
        print(f"Cleaned pattern: {result['cleaned_pattern']}")
        print()
    except Exception as e:
        print(f"Error in test_i_prefix_preservation: {e}")
        traceback.print_exc()

def test_q_surcharge_inclusion():
    """Test Q surcharge inclusion in total fare"""
    print("=== Testing Q Surcharge Inclusion ===\n")
    
    try:
        # Test with Q surcharges and incorrect total
        pattern = "NYC AA LON 250.00 Q25.00 NUC 250.00 END ROE 1.25"
        print(f"Pattern with Q surcharges and incorrect total: {pattern}")
        result = analyze_pattern(pattern)
        
        # Check if Q surcharges are included in the total fare
        if result['fare_calculation']['q_surcharge'] > 0:
            print(f"✓ Q surcharge detected: {result['fare_calculation']['q_surcharge']}")
        else:
            print("✗ Q surcharge not detected")
        
        # Check if the fare total is auto-corrected
        if result['fare_calculation']['expected_fare'] == result['fare_calculation']['calculated_fare_total']:
            print(f"✓ Fare total auto-corrected to include Q surcharges: {result['fare_calculation']['expected_fare']}")
        else:
            print(f"✗ Fare total not auto-corrected. Expected: {result['fare_calculation']['calculated_fare_total']}, Got: {result['fare_calculation']['expected_fare']}")
        
        print(f"Cleaned pattern: {result['cleaned_pattern']}")
        print()
    except Exception as e:
        print(f"Error in test_q_surcharge_inclusion: {e}")
        traceback.print_exc()

def test_complex_pattern():
    """Test a complex pattern with multiple features"""
    print("=== Testing Complex Pattern ===\n")
    
    try:
        # Complex pattern with @Web marker, missing I- prefix, and Q surcharges
        pattern = "@Web NYC AA X/ORD UA X/DEN AS SEA 250.00 // YVR AC X/YYZ Q25.00 BA LON Q50.00 AF X/CDG LH FRA 500.00 NUC 750.00 END ROE 1.25"
        print(f"Original complex pattern: {pattern}")
        
        # Analyze the pattern
        result = analyze_pattern(pattern)
        
        # Print the results
        print(f"Is valid: {result['is_valid']}")
        print(f"Original pattern starts with I-: {result['original_pattern'].startswith('I-')}")
        print(f"Cleaned pattern starts with I-: {result['cleaned_pattern'].startswith('I-')}")
        print(f"@Web marker removed: {'@Web' not in result['cleaned_pattern']}")
        print(f"Journey fares: {result['fare_calculation']['journey_fares']}")
        print(f"Q surcharge: {result['fare_calculation']['q_surcharge']}")
        print(f"Total journey fare: {result['fare_calculation']['total_journey_fare']}")
        print(f"Expected fare: {result['fare_calculation']['expected_fare']}")
        print(f"Cleaned pattern: {result['cleaned_pattern']}")
        
    except Exception as e:
        print(f"Error in test_complex_pattern: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting tests...\n")
    test_airline_codes()
    test_airport_codes()
    test_currency_codes()
    test_web_marker_removal()
    test_i_prefix_preservation()
    test_q_surcharge_inclusion()
    test_complex_pattern()
    print("All tests completed.") 