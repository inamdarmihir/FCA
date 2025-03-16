import random
import string
import pandas as pd
import re

# Define valid airport codes and airline codes
AIRPORT_CODES = [
    "DEL", "BOM", "CCU", "MAA", "BLR", "HYD", "COK", "AMD", "PNQ", "GOI",  # India
    "JFK", "LAX", "ORD", "ATL", "DFW", "DEN", "SFO", "SEA", "MIA", "BOS",  # USA
    "LHR", "CDG", "FRA", "AMS", "MAD", "FCO", "IST", "ZRH", "MUC", "BCN",  # Europe
    "DXB", "DOH", "AUH", "SIN", "BKK", "HKG", "NRT", "ICN", "PEK", "SYD",  # Others
    "YYZ", "YVR", "MEX", "GRU", "EZE", "JNB", "CAI", "TLV", "MEL", "AKL",  # More
    "NYC", "LON", "PAR", "ROM", "BER", "TOK", "BRU", "VIE", "OSL", "CPH"   # Common city codes
]

AIRLINE_CODES = [
    "AI", "UK", "IX", "SG", "6E",  # India
    "AA", "UA", "DL", "WN", "B6",  # USA
    "BA", "AF", "LH", "KL", "IB",  # Europe
    "EK", "QR", "EY", "SQ", "TG",  # Others
    "CX", "NH", "OZ", "CA", "QF",  # More
    "AC", "WS", "AM", "JJ", "AR",  # Americas
    "SA", "MS", "LY", "VA", "NZ",  # Others
    "WY", "LX", "OS", "SK", "AY"   # Additional airlines
]

# Define common garbage values
GARBAGE_PATTERNS = [
    r'[A-Z0-9]{7,}',  # Random alphanumeric strings like OPDQ7LP
    r'X[A-Z0-9]{2,5}',  # X followed by 2-5 alphanumeric chars
    r'[0-9]{4,6}[A-Z]',  # 4-6 digits followed by a letter
    r'[A-Z]{2}[0-9]{2,4}',  # 2 letters followed by 2-4 digits
    r'[A-Z][0-9][A-Z][0-9]',  # Alternating letters and numbers
    r'[A-Z]{3}[0-9]{3}',  # 3 letters followed by 3 numbers
    r'[0-9]{3}[A-Z]{3}',  # 3 numbers followed by 3 letters
]

def generate_random_garbage():
    """Generate a random garbage value"""
    pattern = random.choice(GARBAGE_PATTERNS)
    if pattern == r'[A-Z0-9]{7,}':
        length = random.randint(7, 10)
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    elif pattern == r'X[A-Z0-9]{2,5}':
        length = random.randint(2, 5)
        return 'X' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    elif pattern == r'[0-9]{4,6}[A-Z]':
        length = random.randint(4, 6)
        return ''.join(random.choices(string.digits, k=length)) + random.choice(string.ascii_uppercase)
    elif pattern == r'[A-Z]{2}[0-9]{2,4}':
        length = random.randint(2, 4)
        return ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=length))
    elif pattern == r'[A-Z][0-9][A-Z][0-9]':
        return random.choice(string.ascii_uppercase) + random.choice(string.digits) + \
               random.choice(string.ascii_uppercase) + random.choice(string.digits)
    elif pattern == r'[A-Z]{3}[0-9]{3}':
        return ''.join(random.choices(string.ascii_uppercase, k=3)) + ''.join(random.choices(string.digits, k=3))
    elif pattern == r'[0-9]{3}[A-Z]{3}':
        return ''.join(random.choices(string.digits, k=3)) + ''.join(random.choices(string.ascii_uppercase, k=3))
    else:
        # Default fallback
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def generate_valid_fca_pattern():
    """Generate a valid FCA pattern"""
    num_segments = random.randint(2, 5)
    segments = []
    
    # First segment always starts with an airport
    current_airport = random.choice(AIRPORT_CODES)
    
    for _ in range(num_segments):
        airline = random.choice(AIRLINE_CODES)
        next_airport = random.choice([a for a in AIRPORT_CODES if a != current_airport])
        segments.append(f"{airline} {next_airport}")
        current_airport = next_airport
    
    # Add fare information
    fare_amount = round(random.uniform(100, 5000), 2)
    
    # Construct the full pattern
    pattern = f"{random.choice(AIRPORT_CODES)} {' '.join(segments)} {fare_amount:.2f} NUC {fare_amount:.2f} END"
    return pattern

def add_garbage_to_pattern(pattern, num_garbage=None):
    """Add garbage values to a valid pattern"""
    tokens = pattern.split()
    
    # Number of garbage values to add (1-3)
    if num_garbage is None:
        num_garbage = random.randint(1, 3)
    
    for _ in range(num_garbage):
        # Choose a position to insert garbage (not at the beginning or end)
        pos = random.randint(1, len(tokens) - 2)
        
        # Generate and insert garbage
        garbage = generate_random_garbage()
        tokens.insert(pos, garbage)
    
    return ' '.join(tokens)

def add_spacing_issues(pattern, num_issues=None):
    """Add spacing issues to a valid pattern"""
    tokens = pattern.split()
    
    # Number of spacing issues to add (1-2)
    if num_issues is None:
        num_issues = random.randint(1, 2)
    
    # Keep track of positions where we've added spacing issues
    modified_positions = set()
    
    for _ in range(num_issues):
        # Try to find a suitable token to split
        attempts = 0
        while attempts < 10:  # Limit attempts to avoid infinite loops
            # Choose a position (not at the beginning or end)
            pos = random.randint(1, len(tokens) - 2)
            
            # Skip if we've already modified this position
            if pos in modified_positions:
                attempts += 1
                continue
            
            token = tokens[pos]
            if len(token) >= 3:  # Only split if token is long enough
                split_point = random.randint(1, len(token) - 1)
                part1 = token[:split_point]
                part2 = token[split_point:]
                
                # Replace the token with the split parts
                tokens[pos] = part1
                tokens.insert(pos + 1, part2)
                
                # Mark this position as modified
                modified_positions.add(pos)
                modified_positions.add(pos + 1)
                break
            
            attempts += 1
    
    return ' '.join(tokens)

def add_both_issues(pattern):
    """Add both garbage values and spacing issues to a pattern"""
    # First add garbage
    with_garbage = add_garbage_to_pattern(pattern, num_garbage=random.randint(1, 2))
    
    # Then add spacing issues
    with_both = add_spacing_issues(with_garbage, num_issues=1)
    
    return with_both

def generate_edge_cases():
    """Generate specific edge cases for testing"""
    edge_cases = []
    
    # Case 1: Pattern with multiple garbage values
    base_pattern = "BOM WY LON BA PAR AI NYC 1000.00 NUC 1000.00 END"
    edge_cases.append({
        'original': add_garbage_to_pattern(base_pattern, num_garbage=3),
        'clean': base_pattern,
        'has_garbage': True,
        'has_spacing_issues': False,
        'description': "Multiple garbage values"
    })
    
    # Case 2: Pattern with multiple spacing issues
    base_pattern = "DEL AI BOM BA LON 1000.00 NUC 1000.00 END"
    edge_cases.append({
        'original': add_spacing_issues(base_pattern, num_issues=2),
        'clean': base_pattern,
        'has_garbage': False,
        'has_spacing_issues': True,
        'description': "Multiple spacing issues"
    })
    
    # Case 3: Pattern with both garbage and spacing issues
    base_pattern = "JFK AA LHR BA CDG 500.00 NUC 500.00 END"
    edge_cases.append({
        'original': add_both_issues(base_pattern),
        'clean': base_pattern,
        'has_garbage': True,
        'has_spacing_issues': True,
        'description': "Both garbage and spacing issues"
    })
    
    # Case 4: Pattern with garbage in the middle of a valid token
    base_pattern = "SFO UA LHR BA CDG 750.50 NUC 750.50 END"
    tokens = base_pattern.split()
    tokens[2] = "L" + generate_random_garbage() + "R"  # Replace LHR with L{garbage}R
    edge_cases.append({
        'original': ' '.join(tokens),
        'clean': base_pattern,
        'has_garbage': True,
        'has_spacing_issues': False,
        'description': "Garbage in the middle of a valid token"
    })
    
    # Case 5: Pattern with a missing token
    base_pattern = "NYC DL AMS KL PAR 800.00 NUC 800.00 END"
    tokens = base_pattern.split()
    tokens.pop(random.randint(1, len(tokens) - 5))  # Remove a random token (not the first or last 4)
    edge_cases.append({
        'original': ' '.join(tokens),
        'clean': base_pattern,
        'has_garbage': False,
        'has_spacing_issues': False,
        'description': "Missing token"
    })
    
    # Case 6: Pattern with incorrect fare amounts
    base_pattern = "LAX AA LON BA PAR 900.00 NUC 900.00 END"
    tokens = base_pattern.split()
    tokens[-2] = "950.00"  # Different fare amount after NUC
    edge_cases.append({
        'original': ' '.join(tokens),
        'clean': base_pattern,
        'has_garbage': False,
        'has_spacing_issues': False,
        'description': "Incorrect fare amounts"
    })
    
    # Case 7: Pattern with extra spaces
    base_pattern = "DXB EK SIN SQ HKG 1200.00 NUC 1200.00 END"
    with_extra_spaces = base_pattern.replace(" ", "  ")  # Double all spaces
    edge_cases.append({
        'original': with_extra_spaces,
        'clean': base_pattern,
        'has_garbage': False,
        'has_spacing_issues': False,
        'description': "Extra spaces"
    })
    
    # Case 8: Pattern with lowercase letters
    base_pattern = "AMS KL CDG AF FCO 600.00 NUC 600.00 END"
    with_lowercase = base_pattern.lower()
    edge_cases.append({
        'original': with_lowercase,
        'clean': base_pattern,
        'has_garbage': False,
        'has_spacing_issues': False,
        'description': "Lowercase letters"
    })
    
    # Case 9: Pattern with specific examples from the prompt
    edge_cases.append({
        'original': "BOM WY LON BA PAR OPDQ7LP AI NYC 1000.00 NUC 1000.00 END",
        'clean': "BOM WY LON BA PAR AI NYC 1000.00 NUC 1000.00 END",
        'has_garbage': True,
        'has_spacing_issues': False,
        'description': "Example from prompt with garbage"
    })
    
    edge_cases.append({
        'original': "DEL AI BO M BA LON 1000.00 NUC 1000.00 END",
        'clean': "DEL AI BOM BA LON 1000.00 NUC 1000.00 END",
        'has_garbage': False,
        'has_spacing_issues': True,
        'description': "Example from prompt with spacing issue"
    })
    
    return edge_cases

def generate_synthetic_dataset(num_samples=1000, include_edge_cases=True):
    """Generate a synthetic dataset of FCA patterns"""
    data = []
    
    # Generate clean patterns
    clean_patterns = [generate_valid_fca_pattern() for _ in range(num_samples)]
    
    # Create patterns with issues
    for pattern in clean_patterns:
        # 25% clean, 25% with garbage, 25% with spacing issues, 25% with both
        issue_type = random.randint(0, 3)
        
        if issue_type == 0:
            # Clean pattern
            data.append({
                'original': pattern,
                'clean': pattern,
                'has_garbage': False,
                'has_spacing_issues': False,
                'description': "Clean pattern"
            })
        elif issue_type == 1:
            # Pattern with garbage
            pattern_with_garbage = add_garbage_to_pattern(pattern)
            data.append({
                'original': pattern_with_garbage,
                'clean': pattern,
                'has_garbage': True,
                'has_spacing_issues': False,
                'description': "Pattern with garbage"
            })
        elif issue_type == 2:
            # Pattern with spacing issues
            pattern_with_spacing = add_spacing_issues(pattern)
            data.append({
                'original': pattern_with_spacing,
                'clean': pattern,
                'has_garbage': False,
                'has_spacing_issues': True,
                'description': "Pattern with spacing issues"
            })
        else:
            # Pattern with both issues
            pattern_with_both = add_both_issues(pattern)
            data.append({
                'original': pattern_with_both,
                'clean': pattern,
                'has_garbage': True,
                'has_spacing_issues': True,
                'description': "Pattern with both issues"
            })
    
    # Add edge cases if requested
    if include_edge_cases:
        edge_cases = generate_edge_cases()
        data.extend(edge_cases)
    
    return pd.DataFrame(data)

def save_dataset(filename='fca_patterns.csv', num_samples=1000, include_edge_cases=True):
    """Generate and save a synthetic dataset"""
    df = generate_synthetic_dataset(num_samples, include_edge_cases)
    df.to_csv(filename, index=False)
    print(f"Generated {len(df)} samples and saved to {filename}")
    
    # Print some examples
    print("\nExamples:")
    for i in range(min(5, len(df))):
        print(f"Original: {df.iloc[i]['original']}")
        print(f"Clean:    {df.iloc[i]['clean']}")
        print(f"Description: {df.iloc[i]['description']}")
        print(f"Has garbage: {df.iloc[i]['has_garbage']}, Has spacing issues: {df.iloc[i]['has_spacing_issues']}")
        print()

if __name__ == "__main__":
    save_dataset(num_samples=1000, include_edge_cases=True) 