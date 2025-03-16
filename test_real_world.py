#!/usr/bin/env python
"""
Test script to verify that the enhanced cleaner works with a real-world example.
"""

from enhanced_fca_cleaner import analyze_pattern
import json

def test_real_world_example():
    """Test a real-world example with complex fare calculation pattern"""
    print("=== Testing Real-World Example ===\n")
    
    # Real-world example with complex fare calculation
    pattern = "NYC AA X/ORD UA X/DEN AS SEA 250.00 // YVR AC X/YYZ Q25.00 BA LON Q50.00 AF X/CDG LH FRA 500.00 NUC 750.00 END ROE 1.25"
    print(f"Original pattern: {pattern}")
    
    # Analyze the pattern
    result = analyze_pattern(pattern)
    
    # Print the results in a structured format
    print("\nAnalysis Results:")
    print(f"Is valid: {result['is_valid']}")
    print(f"Original pattern: {result['original_pattern']}")
    print(f"Cleaned pattern: {result['cleaned_pattern']}")
    
    print("\nFare Calculation Details:")
    print(f"Journey fares: {result['fare_calculation']['journey_fares']}")
    print(f"Q surcharge: {result['fare_calculation']['q_surcharge']}")
    print(f"Total journey fare: {result['fare_calculation']['total_journey_fare']}")
    print(f"Expected fare: {result['fare_calculation']['expected_fare']}")
    print(f"Calculated fare total: {result['fare_calculation']['calculated_fare_total']}")
    
    # Check if journey_segments exists in the result
    if 'journey_segments' in result:
        print("\nJourney Segments:")
        for i, segment in enumerate(result['journey_segments']):
            print(f"Segment {i+1}:")
            print(f"  Origin: {segment['origin']}")
            print(f"  Destination: {segment['destination']}")
            print(f"  Carrier: {segment['carrier']}")
            print(f"  Stopover: {segment['stopover']}")
    else:
        print("\nJourney Segments: Not available in the result")
    
    # Verify key aspects of the analysis
    print("\nVerification:")
    if result['is_valid']:
        print("✓ Pattern is valid")
    else:
        print("✗ Pattern is not valid")
    
    if result['cleaned_pattern'].startswith("I-"):
        print("✓ I- prefix added to cleaned pattern")
    else:
        print("✗ I- prefix not added to cleaned pattern")
    
    if result['fare_calculation']['expected_fare'] == result['fare_calculation']['calculated_fare_total']:
        print("✓ Fare total correctly includes Q surcharges")
    else:
        print("✗ Fare total does not include Q surcharges")
    
    # Save the results to a JSON file for reference
    with open('real_world_test_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\nResults saved to real_world_test_results.json")

if __name__ == "__main__":
    test_real_world_example()
    print("\nReal-world test completed.") 