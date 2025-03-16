import re
import pandas as pd
from data_generator import AIRPORT_CODES, AIRLINE_CODES

# Add NYC as a valid airport code if not already in the list
if "NYC" not in AIRPORT_CODES:
    AIRPORT_CODES.append("NYC")

# Add WY as a valid airline code if not already in the list
if "WY" not in AIRLINE_CODES:
    AIRLINE_CODES.append("WY")

def is_valid_token(token):
    """Check if a token is a valid airport code, airline code, or numeric value"""
    # Check if it's a valid airport code
    if token in AIRPORT_CODES:
        return True, "AIRPORT"
    
    # Check if it's a valid airline code
    if token in AIRLINE_CODES:
        return True, "AIRLINE"
    
    # Check if it's a numeric value (fare amount)
    if re.match(r'^\d+\.\d{2}$', token):
        return True, "FARE"
    
    # Check if it's one of the special tokens
    if token in ['NUC', 'END']:
        return True, "SPECIAL"
    
    return False, "INVALID"

def find_potential_airport_code(token):
    """Check if a token might be part of an airport code"""
    for code in AIRPORT_CODES:
        if code.startswith(token) or token.startswith(code):
            return True
    return False

def find_potential_airline_code(token):
    """Check if a token might be part of an airline code"""
    for code in AIRLINE_CODES:
        if code.startswith(token) or token.startswith(code):
            return True
    return False

def is_potential_split_token(token1, token2):
    """Check if two tokens might be parts of a split token"""
    combined = token1 + token2
    
    # Check if the combined token is a valid airport or airline code
    if combined in AIRPORT_CODES or combined in AIRLINE_CODES:
        return True, combined
    
    # Check for partial matches (e.g., "BO" + "M" -> "BOM")
    for code in AIRPORT_CODES:
        if code.startswith(combined) or (token1 in code and code.endswith(token2)):
            return True, code
    
    for code in AIRLINE_CODES:
        if code.startswith(combined) or (token1 in code and code.endswith(token2)):
            return True, code
    
    return False, None

def remove_garbage_values(pattern):
    """Remove garbage values from an FCA pattern"""
    tokens = pattern.split()
    cleaned_tokens = []
    
    for token in tokens:
        is_valid, token_type = is_valid_token(token)
        if is_valid:
            cleaned_tokens.append(token)
    
    return ' '.join(cleaned_tokens)

def fix_spacing_issues(pattern):
    """Fix spacing issues in an FCA pattern"""
    tokens = pattern.split()
    fixed_tokens = []
    i = 0
    
    while i < len(tokens):
        current_token = tokens[i]
        
        # Check if we're not at the last token
        if i < len(tokens) - 1:
            next_token = tokens[i + 1]
            
            # Check if these two tokens might be parts of a split token
            is_split, combined = is_potential_split_token(current_token, next_token)
            if is_split:
                fixed_tokens.append(combined)
                i += 2  # Skip the next token
                continue
        
        # If we couldn't combine with the next token, check if this token is valid
        is_valid, token_type = is_valid_token(current_token)
        if is_valid:
            fixed_tokens.append(current_token)
        
        i += 1
    
    return ' '.join(fixed_tokens)

def reconstruct_valid_pattern(tokens):
    """Attempt to reconstruct a valid pattern from tokens"""
    # Ensure we have the minimum required tokens
    if len(tokens) < 5:
        return ' '.join(tokens)  # Not enough tokens to reconstruct
    
    # Make sure the pattern ends with "NUC X.XX END"
    if tokens[-1] != "END" or tokens[-3] != "NUC":
        # Try to fix the ending if possible
        if "NUC" in tokens and "END" in tokens:
            nuc_index = tokens.index("NUC")
            end_index = tokens.index("END")
            
            if nuc_index < end_index - 1 and nuc_index > 0:
                # Ensure there's a fare amount before NUC
                fare_before_nuc = tokens[nuc_index - 1]
                if re.match(r'^\d+\.\d{2}$', fare_before_nuc):
                    # Use the same fare amount after NUC
                    reconstructed = tokens[:nuc_index] + [fare_before_nuc, "NUC", fare_before_nuc, "END"]
                    return ' '.join(reconstructed)
    
    # If the ending is already correct, focus on the route part
    route_tokens = tokens[:-4]  # Exclude the fare part
    
    # First token should be an airport code
    if route_tokens and route_tokens[0] not in AIRPORT_CODES:
        # Try to find a valid airport code to start with
        for i, token in enumerate(route_tokens):
            if token in AIRPORT_CODES:
                route_tokens = route_tokens[i:]
                break
    
    # Ensure alternating airport and airline codes
    valid_route = []
    if route_tokens:
        valid_route.append(route_tokens[0])  # Start with the first token (should be an airport)
        
        i = 1
        while i < len(route_tokens):
            current = route_tokens[i]
            is_valid, token_type = is_valid_token(current)
            
            # Check if we need to add an airline code
            if len(valid_route) % 2 == 1:  # Need an airline
                if token_type == "AIRLINE":
                    valid_route.append(current)
                elif i + 1 < len(route_tokens) and route_tokens[i+1] in AIRPORT_CODES:
                    # If next token is an airport, insert a default airline
                    valid_route.append("XX")  # Placeholder airline
                    continue  # Don't increment i
            else:  # Need an airport
                if token_type == "AIRPORT":
                    valid_route.append(current)
                elif i + 1 < len(route_tokens) and route_tokens[i+1] in AIRLINE_CODES:
                    # If next token is an airline, insert a default airport
                    valid_route.append("XXX")  # Placeholder airport
                    continue  # Don't increment i
            
            i += 1
    
    # Combine the route with the fare part
    reconstructed = valid_route + tokens[-4:]
    return ' '.join(reconstructed)

def clean_fca_pattern(pattern):
    """Clean an FCA pattern by removing garbage and fixing spacing issues"""
    # First, remove any garbage values
    cleaned = remove_garbage_values(pattern)
    
    # Then fix any spacing issues
    fixed = fix_spacing_issues(cleaned)
    
    # If the pattern is still invalid, try to reconstruct it
    tokens = fixed.split()
    is_valid, _ = validate_pattern_structure(fixed)
    
    if not is_valid:
        # Try to reconstruct a valid pattern
        reconstructed = reconstruct_valid_pattern(tokens)
        return reconstructed
    
    return fixed

def validate_pattern_structure(pattern):
    """Validate the structure of an FCA pattern"""
    tokens = pattern.split()
    
    # Basic structure check
    if len(tokens) < 5:
        return False, "Pattern too short"
    
    # Check if the pattern ends with "NUC X.XX END"
    if tokens[-1] != "END" or tokens[-3] != "NUC":
        return False, "Invalid ending structure"
    
    # Check if the fare amounts match
    try:
        fare1 = float(tokens[-4])
        fare2 = float(tokens[-2])
        if fare1 != fare2:
            return False, "Fare amounts don't match"
    except (ValueError, IndexError):
        return False, "Invalid fare amounts"
    
    # Check alternating airport and airline codes
    # First token should be an airport code
    if tokens[0] not in AIRPORT_CODES:
        return False, "First token is not a valid airport code"
    
    # Check the rest of the pattern (excluding the fare part)
    i = 1
    while i < len(tokens) - 4:  # Stop before the fare part
        # Even positions should be airline codes
        if i % 2 == 1 and tokens[i] not in AIRLINE_CODES:
            return False, f"Expected airline code at position {i}"
        
        # Odd positions should be airport codes
        if i % 2 == 0 and tokens[i] not in AIRPORT_CODES:
            return False, f"Expected airport code at position {i}"
        
        i += 1
    
    return True, "Valid pattern"

def process_fca_patterns(input_file, output_file):
    """Process a file of FCA patterns and save the cleaned results"""
    try:
        df = pd.read_csv(input_file)
    except:
        # If file doesn't exist or isn't a CSV, create a new DataFrame
        df = pd.DataFrame(columns=['original'])
    
    if 'original' not in df.columns:
        print("Input file must have an 'original' column")
        return
    
    # Clean each pattern
    df['cleaned'] = df['original'].apply(clean_fca_pattern)
    
    # Validate each pattern
    validations = df['cleaned'].apply(validate_pattern_structure)
    df['is_valid'] = [v[0] for v in validations]
    df['validation_message'] = [v[1] for v in validations]
    
    # Save the results
    df.to_csv(output_file, index=False)
    print(f"Processed {len(df)} patterns and saved to {output_file}")
    
    # Print some statistics
    valid_count = df['is_valid'].sum()
    print(f"Valid patterns: {valid_count} ({valid_count/len(df)*100:.2f}%)")
    print(f"Invalid patterns: {len(df) - valid_count} ({(len(df) - valid_count)/len(df)*100:.2f}%)")

if __name__ == "__main__":
    # Test with the examples from the prompt
    example1 = "BOM WY LON BA PAR OPDQ7LP AI NYC 1000.00 NUC 1000.00 END"
    example2 = "DEL AI BO M BA LON 1000.00 NUC 1000.00 END"
    
    print(f"Original: {example1}")
    cleaned1 = clean_fca_pattern(example1)
    print(f"Cleaned: {cleaned1}")
    valid1, msg1 = validate_pattern_structure(cleaned1)
    print(f"Valid: {valid1}, Message: {msg1}")
    
    print(f"\nOriginal: {example2}")
    cleaned2 = clean_fca_pattern(example2)
    print(f"Cleaned: {cleaned2}")
    valid2, msg2 = validate_pattern_structure(cleaned2)
    print(f"Valid: {valid2}, Message: {msg2}") 