"""
Enhanced FCA Pattern Cleaner

This module provides improved functions for cleaning and validating FCA patterns,
with special focus on handling spacing issues and correctly identifying valid tokens.
"""

import re
import pandas as pd
from data_generator import AIRPORT_CODES, AIRLINE_CODES

# Ensure common codes are in our lists
COMMON_AIRPORTS = [
    "LON", "NYC", "PAR", "SIN", "BOM", "DEL", "JFK", "LAX", "SFO", "YYZ", "HOU",
    "ATL", "ORD", "DFW", "DEN", "LHR", "CDG", "AMS", "FRA", "MAD", "FCO", "ZRH",
    "IST", "DXB", "DOH", "SYD", "MEL", "HKG", "PEK", "PVG", "NRT", "HND", "ICN",
    "BKK", "KUL", "SIN", "CGK", "MNL", "JNB", "CPT", "CAI", "LOS", "GRU", "EZE",
    "SCL", "LIM", "BOG", "MEX", "YUL", "YVR", "SEA", "YYC", "YOW", "YHZ", "YEG"
]

COMMON_AIRLINES = [
    "AA", "BA", "SQ", "AI", "WY", "AC", "DL", "UA", "CO", "AS", "LH", "AF", "KL",
    "IB", "AZ", "LX", "TK", "EK", "QR", "EY", "SV", "QF", "NZ", "CX", "CA", "MU",
    "CZ", "NH", "JL", "OZ", "KE", "TG", "MH", "SQ", "GA", "PR", "SA", "ET", "MS",
    "RJ", "LA", "JJ", "AR", "AM", "CM", "AV", "TP", "LO", "OK", "SU", "S7", "U6"
]

# Currency codes (ISO 4217)
CURRENCY_CODES = [
    "NUC", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "SGD",
    "INR", "MXN", "BRL", "ZAR", "RUB", "TRY", "SAR", "AED", "THB", "MYR", "IDR",
    "PHP", "PKR", "BDT", "VND", "EGP", "NGN", "KES", "MAD", "DZD", "TND", "GHS",
    "UGX", "TZS", "XOF", "XAF", "CLP", "COP", "PEN", "ARS", "BOB", "PYG", "UYU",
    "DOP", "JMD", "TTD", "BBD", "BSD", "AWG", "ANG", "XCD", "FJD", "PGK", "SBD",
    "TOP", "VUV", "WST", "NZD", "ILS", "JOD", "KWD", "BHD", "QAR", "OMR", "YER",
    "CZK", "HUF", "PLN", "RON", "BGN", "HRK", "RSD", "ALL", "MKD", "ISK", "NOK",
    "SEK", "DKK", "UAH", "BYN", "MDL", "GEL", "AMD", "AZN", "KZT", "UZS", "TMT",
    "KGS", "TJS", "MNT", "KRW", "TWD", "LKR", "MVR", "NPR", "BTN", "MMK", "LAK",
    "KHR", "BND", "XPF", "SYP", "IQD", "IRR", "AFN", "PKR", "LBP", "LYD", "SDG",
    "SSP", "ETB", "SOS", "DJF", "KMF", "ERN", "SZL", "LSL", "ZMW", "MWK", "BIF",
    "RWF", "SLL", "GMD", "GNF", "XAU", "XAG", "XPT", "XPD"
]

# Special tokens that need to be preserved
SPECIAL_TOKENS = ["NUC", "END", "ROE", "Q", "//", "/-", "X/", "I-", "M/BT", "M/IT", "+", "PU", "P", "(", ")"] + CURRENCY_CODES

for code in COMMON_AIRPORTS:
    if code not in AIRPORT_CODES:
        AIRPORT_CODES.append(code)

for code in COMMON_AIRLINES:
    if code not in AIRLINE_CODES:
        AIRLINE_CODES.append(code)

def is_valid_token(token):
    """
    Check if a token is valid in a fare calculation pattern
    
    Args:
        token (str): The token to check
        
    Returns:
        tuple: (is_valid, token_type)
    """
    # Ensure token is a string
    token = str(token)
    
    # Check for airport code (e.g. JFK, SFO, LAX)
    if token in AIRPORT_CODES:
        return True, "AIRPORT"
    
    # Check for airline code (e.g. DL, AA, UA)
    if token in AIRLINE_CODES:
        return True, "AIRLINE"
    
    # Check for fare amount (e.g. 100.00)
    if re.match(r'^\d+(\.\d+)?$', token):
        return True, "FARE"
    
    # Check if token is a city pair (6-character code like LONBOM)
    if re.match(r'^[A-Z]{6}$', token):
        # Check if this is a valid city pair (both parts are airport codes)
        first_airport = token[:3]
        second_airport = token[3:]
        if first_airport in AIRPORT_CODES and second_airport in AIRPORT_CODES:
            return True, "CITY_PAIR"
    
    # Check if token is a fare amount with M prefix (mileage fare, e.g. M123.45)
    if re.match(r'^M\d+(\.\d+)?$', token):
        return True, "MILEAGE_FARE"
    
    # Check if token is a Q surcharge (e.g. Q10.00)
    if re.match(r'^Q\d+(\.\d+)?$', token):
        return True, "Q_SURCHARGE"
    
    # Check if token is a plus up amount (e.g. P10.00)
    if token.startswith("P") and re.match(r'^P\d+(\.\d+)?$', token):
        return True, "PLUS_UP"
    
    # Check if token is a class differential (e.g. D10.00)
    if token.startswith("D") and re.match(r'^D\d+(\.\d+)?$', token):
        return True, "CLASS_DIFFERENTIAL"
    
    # Check if token is a valid currency code (e.g. USD, GBP)
    if re.match(r'^[A-Z]{3}$', token):
        return True, "CURRENCY"
    
    # Check for valid keywords
    keywords = [
        "X/", "O/", "Q", "NUC", "END", "/-", "//",
        "FARE", "TX", "XF", "XT", "YQ", "YR",
        "D", "P"  # Add D and P as valid keywords
    ]
    
    if token in keywords:
        return True, "KEYWORD"
    
    # Check for ROE value (e.g. ROE1.25)
    if re.match(r'^ROE\d+(\.\d+)?$', token):
        return True, "ROE"
    
    # Check for concatenated tokens with ROE
    if "ROE" in token:
        return True, "ROE_CONCATENATED"
    
    # Is a direction (e.g. LH, AP, AT, EH)
    directions = ["LH", "AP", "AT", "EH"]
    if token in directions:
        return True, "DIRECTION"
    
    # Check for tour indicators
    if token in ["M/BT", "M/IT"]:
        return True, "TOUR_INDICATOR"
    
    # Check for side trip indicators
    if token in ["(", ")"]:
        return True, "SIDE_TRIP_INDICATOR"
    
    # If none of the above, token is invalid
    return False, None

def split_concatenated_tokens(token):
    """
    Split a token that may contain multiple concatenated tokens
    
    Args:
        token (str): The token to split
        
    Returns:
        list: The split tokens
    """
    # Special handling for tour indicators (M/BT, M/IT)
    if token == "M/BT" or token == "M/IT":
        return [token]
    
    # Special handling for plus up indicator (P)
    if token == "P":
        return [token]
    
    # Special handling for class differential indicator (D)
    if token == "D":
        return [token]
    
    # Special handling for city pairs associated with D or P (6-char codes like LONBOM)
    if re.match(r'^[A-Z]{6}$', token):
        # Check if this is a valid city pair (both parts are airport codes)
        first_airport = token[:3]
        second_airport = token[3:]
        if first_airport in AIRPORT_CODES and second_airport in AIRPORT_CODES:
            return [token]  # Preserve as a single token
    
    # Special handling for parentheses (side trip indicators)
    if token == "(" or token == ")":
        return [token]
    
    # Handle case where a token starts with "(" or ends with ")"
    if token.startswith("(") and len(token) > 1:
        remainder = token[1:].strip()
        if remainder:
            return ["("] + split_concatenated_tokens(remainder)
        return ["("]
    
    if token.endswith(")") and len(token) > 1:
        remainder = token[:-1].strip()
        if remainder:
            return split_concatenated_tokens(remainder) + [")"]
        return [")"]
    
    # Handle case where a token starts with M/BT or M/IT
    if token.startswith("M/BT"):
        remainder = token[4:].strip()
        if remainder:
            return ["M/BT"] + split_concatenated_tokens(remainder)
        return ["M/BT"]
    
    if token.startswith("M/IT"):
        remainder = token[4:].strip()
        if remainder:
            return ["M/IT"] + split_concatenated_tokens(remainder)
        return ["M/IT"]
    
    # ROE value (e.g., ROE1.0)
    if token.startswith("ROE") and re.search(r'\d', token):
        return [token]
    
    # Class differential pattern (e.g., D100.00)
    if token.startswith("D") and re.match(r'^D\d+(\.\d+)?$', token):
        return [token]
    
    # Mileage fare pattern (e.g., M100.00)
    if token.startswith("M") and re.match(r'^M\d+(\.\d+)?$', token):
        return [token]

    # Plus up pattern (e.g., P100.00)
    if token.startswith("P") and re.match(r'^P\d+(\.\d+)?$', token):
        return [token]
    
    # Q surcharge with value (e.g., Q20.00)
    if token.startswith("Q") and len(token) > 1 and token[1:].replace('.', '', 1).isdigit():
        return ["Q", token[1:]]
    
    # Transit indicator (X/) followed by something
    if token.startswith("X/"):
        remainder = token[2:].strip()
        if remainder:
            if remainder in AIRPORT_CODES:
                return ["X/", remainder]
            else:
                return ["X/"] + split_concatenated_tokens(remainder)
        return ["X/"]
    
    # Special case for fare amounts concatenated with special tokens
    # Check for patterns like "1000.00END" or "1000.00NUC"
    fare_special_match = re.match(r'^(\d+\.\d{2})(NUC|END|ROE)$', token)
    if fare_special_match:
        fare = fare_special_match.group(1)
        special = fare_special_match.group(2)
        return [fare, special]
    
    # Special case for Q surcharges
    # Check for patterns like "Q10.00"
    q_surcharge_match = re.match(r'^Q(\d+\.\d{2})$', token)
    if q_surcharge_match:
        return ["Q", q_surcharge_match.group(1)]
    
    # Special case for P plus ups
    # Check for patterns like "P10.00"
    p_plusup_match = re.match(r'^P(\d+\.\d{2})$', token)
    if p_plusup_match:
        return ["P", p_plusup_match.group(1)]
    
    # Special case for ROE values
    # Check for patterns like "ROE1.00"
    roe_match = re.match(r'^ROE(\d+\.\d{2})$', token)
    if roe_match:
        return ["ROE", roe_match.group(1)]
    
    # Special case for involuntary journey change indicators
    # Check for patterns like "I-LON"
    invol_match = re.match(r'^I-([A-Z]{3})$', token)
    if invol_match:
        airport = invol_match.group(1)
        if airport in AIRPORT_CODES:
            return ["I-", airport]
    
    # Special case for surface segment indicators
    # Check for patterns like "//LON" or "/-PAR"
    surface_match = re.match(r'^(//|/-)([A-Z]{3})$', token)
    if surface_match:
        surface = surface_match.group(1)
        airport = surface_match.group(2)
        if airport in AIRPORT_CODES:
            return [surface, airport]
    
    # Special case for fare amounts concatenated with airport codes
    # Check for patterns like "500.00NYC"
    fare_airport_match = re.match(r'^(\d+\.\d{2})([A-Z]{3})$', token)
    if fare_airport_match:
        fare = fare_airport_match.group(1)
        airport = fare_airport_match.group(2)
        if airport in AIRPORT_CODES:
            return [fare, airport]
    
    # Special case for fare amounts concatenated with partial airport codes
    # Check for patterns like "500.00N" where N is part of NYC
    fare_partial_match = re.match(r'^(\d+\.\d{2})([A-Z]{1,2})$', token)
    if fare_partial_match:
        fare = fare_partial_match.group(1)
        partial = fare_partial_match.group(2)
        
        # Check if this partial code could be part of a known airport code
        for airport in COMMON_AIRPORTS:
            if airport.startswith(partial):
                return [fare, partial]
        
        return [fare, partial]
    
    # Check for special tokens at the beginning or end of the token
    for special_token in SPECIAL_TOKENS:
        # Check if token starts with special token (e.g., "NUC1000.00")
        if token.startswith(special_token):
            remainder = token[len(special_token):]
            # Check if remainder is a valid token or can be split further
            remainder_split = split_concatenated_tokens(remainder)
            if remainder_split:
                return [special_token] + remainder_split
        
        # Check if token ends with special token (e.g., "1000.00END")
        if token.endswith(special_token):
            remainder = token[:-len(special_token)]
            # Check if remainder is a valid token or can be split further
            remainder_split = split_concatenated_tokens(remainder)
            if remainder_split:
                return remainder_split + [special_token]
    
    # Check for fare amounts in the token
    fare_match = re.search(r'(\d+\.\d{2})', token)
    if fare_match:
        fare = fare_match.group(1)
        fare_start = fare_match.start()
        fare_end = fare_match.end()
        
        # Split the token into parts before and after the fare
        before_fare = token[:fare_start]
        after_fare = token[fare_end:]
        
        # Process parts before and after fare
        before_split = split_concatenated_tokens(before_fare) if before_fare else []
        after_split = split_concatenated_tokens(after_fare) if after_fare else []
        
        if before_split or after_split:
            return before_split + [fare] + after_split
    
    # Try to split the token into valid tokens
    # Start with all possible airport and airline codes
    valid_codes = AIRPORT_CODES + AIRLINE_CODES + SPECIAL_TOKENS
    
    # Sort by length (descending) to prefer longer matches first
    valid_codes.sort(key=len, reverse=True)
    
    # Try to find a valid split
    best_split = []
    
    def find_splits(remaining, current_split):
        """Recursive function to find all possible ways to split the token"""
        if not remaining:
            # We've successfully split the entire token
            nonlocal best_split
            if len(current_split) > len(best_split):
                best_split = current_split.copy()
            return
        
        # Try each valid code as a prefix
        for code in valid_codes:
            if remaining.startswith(code):
                # This code is a valid prefix, try to split the rest
                find_splits(remaining[len(code):], current_split + [code])
    
    # Start the recursive search
    find_splits(token, [])
    
    return best_split

def find_valid_code_combinations(tokens):
    """
    Find valid airport or airline codes that might be split across multiple tokens
    
    Args:
        tokens (list): List of tokens to check
        
    Returns:
        list: List of tuples (start_index, end_index, combined_token, token_type)
    """
    combinations = []
    
    # Check for concatenated tokens (e.g., "SINSQLON" -> "SIN", "SQ", "LON")
    for i, token in enumerate(tokens):
        split_tokens = split_concatenated_tokens(token)
        if len(split_tokens) > 1:
            # We found a valid split for this token
            combinations.append((i, i, split_tokens, "CONCATENATED"))
    
    # Check for special tokens with spacing issues (e.g., "E N D" -> "END")
    for special_token in SPECIAL_TOKENS:
        # Try to find the special token split across multiple tokens
        for i in range(len(tokens)):
            # Check if this token starts a potential match
            if i + len(special_token) <= len(tokens):
                combined = ''.join(tokens[i:i+len(special_token)])
                if combined == special_token:
                    combinations.append((i, i+len(special_token)-1, special_token, "SPECIAL"))
                    continue
            
            # Check for partial matches (e.g., "EN D" -> "END")
            if i + 1 < len(tokens):
                # Try combining two tokens
                combined = tokens[i] + tokens[i+1]
                if combined == special_token:
                    combinations.append((i, i+1, special_token, "SPECIAL"))
                    continue
                
                # Try combining with removing spaces
                combined = ''.join(tokens[i].split()) + ''.join(tokens[i+1].split())
                if combined == special_token:
                    combinations.append((i, i+1, special_token, "SPECIAL"))
                    continue
            
            # Check for more complex splits (e.g., "E N D" -> "END")
            if i + 2 < len(tokens):
                combined = tokens[i] + tokens[i+1] + tokens[i+2]
                if combined == special_token:
                    combinations.append((i, i+2, special_token, "SPECIAL"))
    
    # Special case for NYC detection
    for i in range(len(tokens)):
        # Check for "N YC" pattern
        if i + 1 < len(tokens) and tokens[i] == "N" and tokens[i+1] == "YC":
            combinations.append((i, i+1, "NYC", "AIRPORT"))
            continue
        
        # Check for "N" followed by any token that might complete NYC
        if i + 1 < len(tokens) and tokens[i] == "N":
            for j in range(i+1, min(i+3, len(tokens))):
                combined = "N" + ''.join(tokens[i+1:j+1])
                if combined == "NYC":
                    combinations.append((i, j, "NYC", "AIRPORT"))
                    break
    
    # Special case for HOU detection
    for i in range(len(tokens)):
        # Check for "H OU" pattern
        if i + 1 < len(tokens) and tokens[i] == "H" and tokens[i+1] == "OU":
            combinations.append((i, i+1, "HOU", "AIRPORT"))
            continue
        
        # Check for "HO U" pattern
        if i + 1 < len(tokens) and tokens[i] == "HO" and tokens[i+1] == "U":
            combinations.append((i, i+1, "HOU", "AIRPORT"))
            continue
    
    # Check for common airport codes with spacing issues (e.g., "N Y C" -> "NYC")
    for airport_code in COMMON_AIRPORTS:
        # Try to find the airport code split across multiple tokens
        for i in range(len(tokens)):
            # Check for 3-letter airport codes split into individual letters
            if i + 2 < len(tokens) and len(tokens[i]) == 1 and len(tokens[i+1]) == 1 and len(tokens[i+2]) == 1:
                combined = tokens[i] + tokens[i+1] + tokens[i+2]
                if combined == airport_code:
                    combinations.append((i, i+2, airport_code, "AIRPORT"))
                    continue
            
            # Check for 2-token combinations (e.g., "N YC" -> "NYC")
            if i + 1 < len(tokens):
                # Try combining two tokens
                combined = tokens[i] + tokens[i+1]
                if combined == airport_code:
                    combinations.append((i, i+1, airport_code, "AIRPORT"))
                    continue
                
                # Try with first token being a single letter and second token being two letters
                if len(tokens[i]) == 1 and len(tokens[i+1]) == 2:
                    combined = tokens[i] + tokens[i+1]
                    if combined == airport_code:
                        combinations.append((i, i+1, airport_code, "AIRPORT"))
                        continue
                
                # Try with first token being two letters and second token being a single letter
                if len(tokens[i]) == 2 and len(tokens[i+1]) == 1:
                    combined = tokens[i] + tokens[i+1]
                    if combined == airport_code:
                        combinations.append((i, i+1, airport_code, "AIRPORT"))
                        continue
    
    # Check for 2-token combinations (e.g., "L" + "ON" = "LON")
    for i in range(len(tokens) - 1):
        # Try combining two tokens
        combined = tokens[i] + tokens[i+1]
        if combined in AIRPORT_CODES:
            combinations.append((i, i+1, combined, "AIRPORT"))
        elif combined in AIRLINE_CODES:
            combinations.append((i, i+1, combined, "AIRLINE"))
    
    # Check for 3-token combinations (e.g., "A" + "M" + "S" = "AMS")
    for i in range(len(tokens) - 2):
        # Try combining three tokens
        combined = tokens[i] + tokens[i+1] + tokens[i+2]
        if combined in AIRPORT_CODES:
            combinations.append((i, i+2, combined, "AIRPORT"))
        elif combined in AIRLINE_CODES:
            combinations.append((i, i+2, combined, "AIRLINE"))
    
    # Check for partial matches with known codes
    for i, token in enumerate(tokens):
        # Check if this token is a partial match for any airport code
        for code in AIRPORT_CODES:
            if len(token) >= 1 and token in code:
                # Look ahead for the rest of the code
                remaining = code[code.index(token) + len(token):]
                if remaining and i + 1 < len(tokens) and tokens[i+1].startswith(remaining):
                    combinations.append((i, i+1, code, "AIRPORT"))
        
        # Check if this token is a partial match for any airline code
        for code in AIRLINE_CODES:
            if len(token) >= 1 and token in code:
                # Look ahead for the rest of the code
                remaining = code[code.index(token) + len(token):]
                if remaining and i + 1 < len(tokens) and tokens[i+1].startswith(remaining):
                    combinations.append((i, i+1, code, "AIRLINE"))
    
    return combinations

def enhanced_fix_spacing_issues(pattern):
    """
    Enhanced function to fix spacing issues in an FCA pattern
    
    Args:
        pattern (str): The input pattern
        
    Returns:
        str: The pattern with spacing issues fixed
    """
    tokens = pattern.split()
    fixed_tokens = []
    i = 0
    
    # Find all possible valid combinations
    combinations = find_valid_code_combinations(tokens)
    
    # Sort combinations by start index
    combinations.sort(key=lambda x: x[0])
    
    # Apply combinations
    skip_indices = set()
    for combination in combinations:
        start_idx, end_idx = combination[0], combination[1]
        
        # Check if any of these indices have already been used
        if any(idx in skip_indices for idx in range(start_idx, end_idx + 1)):
            continue
        
        # Add all tokens before this combination
        while i < start_idx:
            if i not in skip_indices:
                fixed_tokens.append(tokens[i])
            i += 1
        
        # Add the combined token(s)
        if combination[3] == "CONCATENATED":
            # For concatenated tokens, add each split token
            fixed_tokens.extend(combination[2])
        else:
            # For other combinations, add the single combined token
            fixed_tokens.append(combination[2])
        
        # Mark these indices as used
        for idx in range(start_idx, end_idx + 1):
            skip_indices.add(idx)
        
        # Move the index past this combination
        i = end_idx + 1
    
    # Add any remaining tokens
    while i < len(tokens):
        if i not in skip_indices:
            fixed_tokens.append(tokens[i])
        i += 1
    
    return ' '.join(fixed_tokens)

def enhanced_clean_fca_pattern(pattern):
    """
    Clean a fare calculation pattern by removing invalid tokens and fixing spacing issues
    
    Args:
        pattern (str): The fare calculation pattern to clean
        
    Returns:
        str: The cleaned pattern
    """
    # Split the pattern into tokens
    tokens = pattern.split()
    
    # Check for tokens that might be concatenated without spaces
    expanded_tokens = []
    for token in tokens:
        # Try to split concatenated tokens (like X/DOH into X/ and DOH)
        split_tokens = split_concatenated_tokens(token)
        if len(split_tokens) > 1:
            expanded_tokens.extend(split_tokens)
        else:
            expanded_tokens.append(token)
    
    # Filter out invalid tokens while preserving fare amounts and Q surcharges
    valid_tokens = []
    i = 0
    while i < len(expanded_tokens):
        token = expanded_tokens[i]
        is_valid, token_type = is_valid_token(token)
        
        # Handle Q surcharge (Q followed by a fare amount)
        if is_valid and token == "Q" and i + 1 < len(expanded_tokens):
            next_token = expanded_tokens[i + 1]
            next_is_valid, next_token_type = is_valid_token(next_token)
            
            # If Q is followed by a valid fare amount, keep both tokens
            if next_is_valid and (next_token_type == "FARE" or next_token_type == "NUMERIC"):
                valid_tokens.append(token)  # Add Q
                valid_tokens.append(next_token)  # Add fare amount
                i += 2  # Skip both tokens
                continue
        
        # Handle fare amounts (should be preserved)
        if is_valid:
            valid_tokens.append(token)
        
        i += 1
    
    # Reconstruct the pattern
    cleaned = ' '.join(valid_tokens)
    
    # Validate the pattern structure
    validation_result = validate_pattern_structure(cleaned)
    is_valid = validation_result.get('is_valid', False)
    
    # If the pattern is not valid, try to fix it
    if not is_valid:
        # Try to reconstruct a valid pattern
        reconstructed = reconstruct_valid_pattern(valid_tokens)
        if reconstructed:
            cleaned = reconstructed
    
    return cleaned

def validate_pattern_structure(pattern):
    """
    Validate the structure of a fare calculation pattern
    
    Args:
        pattern (str): The fare calculation pattern to validate
        
    Returns:
        dict: Dictionary with validation results
    """
    tokens = pattern.split()
    
    # Check if pattern is too short
    if len(tokens) < 3:
        return {'is_valid': False, 'message': "Pattern is too short"}
    
    # Check for END token (required in all patterns)
    if "END" not in tokens:
        return {'is_valid': False, 'message': "Missing END token"}
    
    # Check for tour indicators (M/BT or M/IT)
    tour_indicators = []
    for token in tokens:
        if token in ["M/BT", "M/IT"]:
            tour_indicators.append(token)
    
    has_tour_indicator = len(tour_indicators) > 0
    
    # Check for side trips (indicated by parentheses)
    side_trips = []
    in_side_trip = False
    current_side_trip = []
    
    for token in tokens:
        if token == "(":
            in_side_trip = True
            current_side_trip = ["("]
        elif token == ")" and in_side_trip:
            in_side_trip = False
            current_side_trip.append(")")
            # Store the complete side trip
            side_trips.append(' '.join(current_side_trip))
            current_side_trip = []
        elif in_side_trip:
            # Handle surface transportation markers within side trips
            if token in ["//", "/-"]:
                # Mark these as valid tokens within side trips
                current_side_trip.append(token)
            else:
                current_side_trip.append(token)
    
    # Check for unbalanced parentheses
    if in_side_trip:
        return {'is_valid': False, 'message': "Unbalanced parentheses in side trip"}
    
    has_side_trips = len(side_trips) > 0
    
    # Check for currency code and fare value
    currency_code = None
    fare_value = None
    
    # Common currency codes
    currency_codes = ["NUC", "GBP", "INR", "USD", "EUR", "AUD", "CAD", "JPY", "SGD"]
    
    # Look for currency code in tokens
    for i, token in enumerate(tokens):
        upper_token = token.upper()
        if upper_token in currency_codes:
            currency_code = upper_token
            # Check if there's a fare value after the currency code
            if i + 1 < len(tokens) and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
                fare_value = float(tokens[i + 1])
            break
    
    # For tour fares or side trips, currency code is optional
    if (has_tour_indicator or has_side_trips) and currency_code is None:
        # If no currency code found but we have tour indicators or side trips, set currency to NUC
        currency_code = "NUC"
    elif currency_code is None:
        # If not a tour fare or side trip and no currency code, pattern is invalid
        return {'is_valid': False, 'message': "Missing currency code token"}
    
    # Check for ROE value
    roe_value = None
    has_roe = False
    
    # Look for ROE in tokens
    for i, token in enumerate(tokens):
        if token == "ROE" and i + 1 < len(tokens) and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
            has_roe = True
            roe_value = float(tokens[i + 1])
            break
        elif token.startswith("ROE") and re.match(r'^ROE\d+(\.\d+)?$', token):
            has_roe = True
            roe_value = float(token[3:])
            break
    
    # Extract journey segments, fares, Q surcharges, class differentials, plus ups
    journey_segments = []
    journey_fares = []
    q_surcharges = []
    class_differentials = []
    plus_up_amounts = []
    
    # Check if the pattern starts with an involuntary journey change indicator
    has_invol = False
    start_index = 0
    if tokens[0] == "I-":
        has_invol = True
        start_index = 1
    
    # Process tokens to extract segments, fares, etc.
    i = start_index
    current_segment = []
    end_index = len(tokens)
    
    # Find the END token to limit our processing
    if "END" in tokens:
        end_index = tokens.index("END")
    
    # Process tokens before END
    while i < end_index:
        token = tokens[i]
        
        # Check for Q surcharge
        if token == "Q" and i + 1 < end_index and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
            q_surcharges.append(float(tokens[i + 1]))
            i += 2
            continue
        
        # Check for Q surcharge in format Q10.00
        if token.startswith("Q") and re.match(r'^Q\d+(\.\d+)?$', token):
            q_value = float(token[1:])
            q_surcharges.append(q_value)
            i += 1
            continue
        
        # Check for class differential
        if token == "D" and i + 2 < end_index and re.match(r'^[A-Z]{6}$', tokens[i + 1]) and re.match(r'^\d+(\.\d+)?$', tokens[i + 2]):
            class_differentials.append(float(tokens[i + 2]))
            i += 3
            continue
        
        # Check for class differential with city pair and amount separated
        if token == "D" and i + 3 < end_index and tokens[i + 1] in AIRPORT_CODES and tokens[i + 2] in AIRPORT_CODES and re.match(r'^\d+(\.\d+)?$', tokens[i + 3]):
            class_differentials.append(float(tokens[i + 3]))
            i += 4
            continue
        
        # Check for class differential in format D10.00
        if token.startswith("D") and re.match(r'^D\d+(\.\d+)?$', token):
            d_value = float(token[1:])
            class_differentials.append(d_value)
            i += 1
            continue
        
        # Check for plus up with 6-char airport code and amount
        if token == "P" and i + 2 < end_index and re.match(r'^[A-Z]{6}$', tokens[i + 1]) and re.match(r'^\d+(\.\d+)?$', tokens[i + 2]):
            plus_up_amounts.append(float(tokens[i + 2]))
            i += 3
            continue
        
        # Check for plus up with separated airport codes
        if token == "P" and i + 3 < end_index and tokens[i + 1] in AIRPORT_CODES and tokens[i + 2] in AIRPORT_CODES and re.match(r'^\d+(\.\d+)?$', tokens[i + 3]):
            plus_up_amounts.append(float(tokens[i + 3]))
            i += 4
            continue
        
        # Check for plus up with city pair as combined code and amount
        if token == "P" and i + 2 < end_index and re.match(r'^[A-Z]{6}$', tokens[i + 1]) and re.match(r'^\d+(\.\d+)?$', tokens[i + 2]):
            plus_up_amounts.append(float(tokens[i + 2]))
            i += 3
            continue
        
        # Check for plus up in format P10.00
        if token.startswith("P") and re.match(r'^P\d+(\.\d+)?$', token):
            p_value = float(token[1:])
            plus_up_amounts.append(p_value)
            i += 1
            continue
        
        # Check for plus up with amount only
        if token == "P" and i + 1 < end_index and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
            plus_up_amounts.append(float(tokens[i + 1]))
            i += 2
            continue
        
        # Check for fare amount
        if re.match(r'^\d+(\.\d+)?$', token):
            # Check if this is a Q surcharge amount (preceded by Q)
            if i > 0 and tokens[i - 1] == "Q":
                i += 1
                continue
            
            # Check if this is a class differential amount (preceded by D and a segment pair)
            if i > 1 and tokens[i - 2] == "D" and re.match(r'^[A-Z]{6}$', tokens[i - 1]):
                i += 1
                continue
            
            # Check if this is a plus up amount (preceded by P and possibly a segment pair)
            if i > 0 and tokens[i - 1] == "P":
                i += 1
                continue
            
            if i > 1 and tokens[i - 2] == "P" and re.match(r'^[A-Z]{6}$', tokens[i - 1]):
                i += 1
                continue
            
            if i > 2 and tokens[i - 3] == "P" and tokens[i - 2] in AIRPORT_CODES and tokens[i - 1] in AIRPORT_CODES:
                i += 1
                continue
            
            # Check if this is a fare amount after a currency code
            if i > 0 and tokens[i - 1] in ["NUC", "GBP", "INR", "USD", "EUR", "AUD", "CAD", "JPY", "SGD"]:
                i += 1
                continue
            
            # Check if this is a ROE value (preceded by ROE)
            if i > 0 and tokens[i - 1] == "ROE":
                i += 1
                continue
            
            # This is a journey fare
            journey_fares.append(float(token))
            i += 1
            continue
        
        # Check for mileage fare amount (M-prefixed)
        if re.match(r'^M\d+(\.\d+)?$', token):
            # Extract the numeric value from the mileage fare token
            mileage_fare = float(token[1:])  # Remove the 'M' prefix
            
            # Add to journey fares
            journey_fares.append(mileage_fare)
            i += 1
            continue
        
        # Check for tour indicators (M/BT or M/IT)
        if token in ["M/BT", "M/IT"]:
            # Don't add to current segment, track separately
            if token not in tour_indicators:
                tour_indicators.append(token)
            i += 1
            continue
        
        # Add token to current segment
        current_segment.append(token)
        i += 1
    
    # Add the last segment if there is one
    if current_segment:
        journey_segments.append(' '.join(current_segment))
    
    # Calculate total fare
    total_journey_fare = sum(journey_fares)
    total_q_surcharge = sum(q_surcharges)
    total_class_differential = sum(class_differentials)
    total_plus_up = sum(plus_up_amounts)
    calculated_fare = total_journey_fare + total_q_surcharge + total_class_differential + total_plus_up
    
    # For tour fares, we don't need to match the fare value
    if has_tour_indicator:
        is_fare_match = True
    else:
        # Check if calculated fare matches the fare value in the pattern
        is_fare_match = True  # Default to true
        if fare_value is not None:
            is_fare_match = abs(calculated_fare - fare_value) < 0.01
    
    # Check for fare mismatch warning
    fare_mismatch_warning = None
    if not is_fare_match and fare_value is not None:
        if abs(total_journey_fare - fare_value) < 0.01:
            fare_mismatch_warning = f"Warning: Fare value {fare_value} matches total journey fare {total_journey_fare} but excludes Q surcharges {total_q_surcharge}, class differentials {total_class_differential}, and plus ups {total_plus_up}. Total should be {calculated_fare}."
        else:
            fare_mismatch_warning = f"Warning: Fare value {fare_value} does not match calculated fare total {calculated_fare} (journey fares: {total_journey_fare}, Q surcharges: {total_q_surcharge}, class differentials: {total_class_differential}, plus ups: {total_plus_up})."
    
    # For tour fares, consider the journey valid if tour indicators are present
    if has_tour_indicator:
        is_valid_journey = True
    else:
        # Validate journey segments for non-tour fares
        is_valid_journey = len(journey_segments) > 0
        
        # Additional validation for non-tour fares
        for segment in journey_segments:
            segment_tokens = segment.split()
            
            # Check if segment has at least an origin and destination
            if len(segment_tokens) < 2:
                is_valid_journey = False
                break
    
    # Return the validation result with side trip information added
    return {
        'is_valid': is_valid_journey and is_fare_match,
        'message': "Valid pattern" if (is_valid_journey and is_fare_match) else "Invalid pattern",
        'journey_segments': journey_segments,
        'journey_fares': journey_fares,
        'q_surcharges': q_surcharges,
        'class_differentials': class_differentials,
        'plus_up_amounts': plus_up_amounts,  # Add plus up amounts to the result
        'tour_indicators': tour_indicators,
        'side_trips': side_trips,
        'fare_value': fare_value,
        'calculated_fare': calculated_fare,
        'is_fare_match': is_fare_match,
        'has_roe': has_roe,
        'roe_value': roe_value,
        'currency_code': currency_code,
        'fare_mismatch_warning': fare_mismatch_warning
    }

def validate_journey_string(pattern, journey_string):
    """
    Validate if a journey string matches the route part of an FCA pattern
    
    Args:
        pattern (str): The full FCA pattern
        journey_string (str): The journey string to validate
        
    Returns:
        dict: Dictionary with validation results
    """
    # Clean the full pattern
    cleaned_pattern = enhanced_clean_fca_pattern(pattern)
    pattern_tokens = cleaned_pattern.split()
    
    # Extract the route part and journey fares
    route_tokens = []
    journey_fares = {}
    
    # First, identify all fare amounts and special tokens in the pattern
    fare_indices = []
    special_indices = []
    for i, token in enumerate(pattern_tokens):
        if re.match(r'^\d+\.\d{2}$', token):
            fare_indices.append(i)
        elif token in ['NUC', 'END']:
            special_indices.append(i)
    
    # Extract route tokens (everything before the last fare amount and excluding special tokens)
    last_route_token_idx = fare_indices[-1] if fare_indices else len(pattern_tokens)
    
    # Process each segment with its fare
    i = 0
    while i < last_route_token_idx:
        # Skip special tokens
        if pattern_tokens[i] in ['NUC', 'END']:
            i += 1
            continue
            
        # Check if this token is a fare amount
        if re.match(r'^\d+\.\d{2}$', pattern_tokens[i]):
            # Found a fare amount in the route part
            fare_amount = float(pattern_tokens[i])
            
            # Check if we have a valid segment before this fare
            if i >= 3:  # Need at least 3 tokens for a valid segment (origin-airline-destination)
                origin_idx = -1
                airline_idx = -1
                destination_idx = i - 1
                
                # Find the closest airport before the destination (should be the origin)
                for j in range(i - 3, -1, -2):  # Step back by 2 to check airport positions
                    if j >= 0 and pattern_tokens[j] in AIRPORT_CODES:
                        origin_idx = j
                        airline_idx = j + 1
                        break
                
                if (origin_idx >= 0 and 
                    pattern_tokens[origin_idx] in AIRPORT_CODES and
                    airline_idx < len(pattern_tokens) and pattern_tokens[airline_idx] in AIRLINE_CODES and
                    pattern_tokens[destination_idx] in AIRPORT_CODES):
                    
                    segment = f"{pattern_tokens[origin_idx]} {pattern_tokens[airline_idx]} {pattern_tokens[destination_idx]}"
                    journey_fares[segment] = fare_amount
            
            # Add the fare token to route tokens
            route_tokens.append(pattern_tokens[i])
        else:
            # Add non-fare token to route tokens
            route_tokens.append(pattern_tokens[i])
        
        i += 1
    
    # Clean the journey string
    cleaned_journey = enhanced_clean_fca_pattern(journey_string)
    journey_tokens = cleaned_journey.split()
    
    # Filter out fare amounts and special tokens from route tokens for comparison
    route_tokens_for_comparison = [token for token in route_tokens 
                                  if not re.match(r'^\d+\.\d{2}$', token) 
                                  and token not in ['NUC', 'END']]
    
    # Check if the journey matches the route (excluding fares and special tokens)
    is_match = ' '.join(journey_tokens) == ' '.join(route_tokens_for_comparison)
    
    # Find missing segments
    missing_segments = []
    if not is_match:
        # Check for missing segments at the beginning
        i, j = 0, 0
        while i < len(route_tokens_for_comparison) and j < len(journey_tokens):
            if route_tokens_for_comparison[i] == journey_tokens[j]:
                i += 1
                j += 1
            else:
                # Found a potential missing segment
                missing_segment = []
                start_i = i
                while i < len(route_tokens_for_comparison) and (j >= len(journey_tokens) or route_tokens_for_comparison[i] != journey_tokens[j]):
                    missing_segment.append(route_tokens_for_comparison[i])
                    i += 1
                
                if missing_segment:
                    missing_segments.append(' '.join(missing_segment))
        
        # Check for any remaining route tokens
        if i < len(route_tokens_for_comparison):
            missing_segments.append(' '.join(route_tokens_for_comparison[i:]))
    
    return {
        'is_match': is_match,
        'cleaned_pattern_route': ' '.join(route_tokens_for_comparison),
        'cleaned_journey': cleaned_journey,
        'missing_segments': missing_segments,
        'journey_fares': journey_fares
    }

def calculate_fare_total(pattern, journey_validation=None):
    """
    Calculate the total fare from a pattern
    
    Args:
        pattern (str): The fare calculation pattern
        journey_validation (dict, optional): Journey validation results
        
    Returns:
        tuple: (total_journey_fare, q_surcharge_total, class_differential_total, plus_up_total, tour_indicator, fare_total, expected_fare, currency_code, is_fare_match)
    """
    tokens = pattern.split()
    
    # Extract journey fares
    journey_fares = []
    q_surcharges = []
    class_differentials = []
    tour_indicators = []
    plus_up_amounts = []
    
    # If we have journey validation results, use them
    if journey_validation:
        journey_fares = journey_validation.get('journey_fares', [])
        q_surcharges = journey_validation.get('q_surcharges', [])
        class_differentials = journey_validation.get('class_differentials', [])
        tour_indicators = journey_validation.get('tour_indicators', [])
        plus_up_amounts = journey_validation.get('plus_up_amounts', [])
    else:
        # Extract fares, Q surcharges, class differentials, plus ups, and tour indicators
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check for Q surcharge
            if token == "Q" and i + 1 < len(tokens) and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
                q_surcharges.append(float(tokens[i + 1]))
                i += 2
                continue
            
            # Check for Q surcharge in format Q10.00
            if token.startswith("Q") and re.match(r'^Q\d+(\.\d+)?$', token):
                q_value = float(token[1:])
                q_surcharges.append(q_value)
                i += 1
                continue
            
            # Check for class differential (D AMSLON 10.00)
            if token == "D" and i + 2 < len(tokens) and re.match(r'^[A-Z]{6}$', tokens[i + 1]) and re.match(r'^\d+(\.\d+)?$', tokens[i + 2]):
                class_differentials.append(float(tokens[i + 2]))
                i += 3
                continue
            
            # Check for class differential in format D10.00
            if token.startswith("D") and re.match(r'^D\d+(\.\d+)?$', token):
                d_value = float(token[1:])
                class_differentials.append(d_value)
                i += 1
                continue
            
            # Check for plus up (P AMSLON 10.00)
            if token == "P" and i + 2 < len(tokens) and re.match(r'^[A-Z]{6}$', tokens[i + 1]) and re.match(r'^\d+(\.\d+)?$', tokens[i + 2]):
                plus_up_amounts.append(float(tokens[i + 2]))
                i += 3
                continue
            
            # Check for plus up with separated airport codes
            if token == "P" and i + 3 < len(tokens) and tokens[i + 1] in AIRPORT_CODES and tokens[i + 2] in AIRPORT_CODES and re.match(r'^\d+(\.\d+)?$', tokens[i + 3]):
                plus_up_amounts.append(float(tokens[i + 3]))
                i += 4
                continue
            
            # Check for plus up with city pair as combined code and amount
            if token == "P" and i + 2 < len(tokens) and re.match(r'^[A-Z]{6}$', tokens[i + 1]) and re.match(r'^\d+(\.\d+)?$', tokens[i + 2]):
                plus_up_amounts.append(float(tokens[i + 2]))
                i += 3
                continue
            
            # Check for plus up in format P10.00
            if token.startswith("P") and re.match(r'^P\d+(\.\d+)?$', token):
                p_value = float(token[1:])
                plus_up_amounts.append(p_value)
                i += 1
                continue
            
            # Check for plus up with amount only
            if token == "P" and i + 1 < len(tokens) and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
                plus_up_amounts.append(float(tokens[i + 1]))
                i += 2
                continue
            
            # Check for tour indicators (M/BT or M/IT)
            if token in ["M/BT", "M/IT"]:
                tour_indicators.append(token)
                i += 1
                continue
            
            # Check for fare amount
            if re.match(r'^\d+(\.\d+)?$', token):
                # Check if this is a Q surcharge amount (preceded by Q)
                if i > 0 and tokens[i - 1] == "Q":
                    i += 1
                    continue
                
                # Check if this is a class differential amount (preceded by D and a segment pair)
                if i > 1 and tokens[i - 2] == "D" and re.match(r'^[A-Z]{6}$', tokens[i - 1]):
                    i += 1
                    continue
                
                # Check if this is a plus up amount (preceded by P and possibly a segment pair)
                if i > 0 and tokens[i - 1] == "P":
                    i += 1
                    continue
                
                if i > 1 and tokens[i - 2] == "P" and re.match(r'^[A-Z]{6}$', tokens[i - 1]):
                    i += 1
                    continue
                
                if i > 2 and tokens[i - 3] == "P" and tokens[i - 2] in AIRPORT_CODES and tokens[i - 1] in AIRPORT_CODES:
                    i += 1
                    continue
                
                # Check if this is a fare amount after a currency code
                if i > 0 and tokens[i - 1] in ["NUC", "GBP", "INR", "USD", "EUR", "AUD", "CAD", "JPY", "SGD"]:
                    i += 1
                    continue
                
                # Check if this is a ROE value (preceded by ROE)
                if i > 0 and tokens[i - 1] == "ROE":
                    i += 1
                    continue
                
                # This is a journey fare
                journey_fares.append(float(token))
                i += 1
                continue
            
            # Check for mileage fare amount (M-prefixed)
            if re.match(r'^M\d+(\.\d+)?$', token):
                # Extract the numeric value from the mileage fare token
                mileage_fare = float(token[1:])  # Remove the 'M' prefix
                
                # Add to journey fares
                journey_fares.append(mileage_fare)
                i += 1
                continue
            
            i += 1
    
    # Calculate total journey fare
    total_journey_fare = sum(journey_fares)
    
    # Calculate total Q surcharge
    q_surcharge_total = sum(q_surcharges)
    
    # Calculate total class differentials
    class_differential_total = sum(class_differentials)
    
    # Calculate total plus ups
    plus_up_total = sum(plus_up_amounts)
    
    # Calculate total fare (including Q surcharges, class differentials, and plus ups)
    fare_total = total_journey_fare + q_surcharge_total + class_differential_total + plus_up_total
    
    # Extract currency code and expected fare
    currency_code = None
    expected_fare = None
    
    for i, token in enumerate(tokens):
        upper_token = token.upper()
        if upper_token in ["NUC", "GBP", "INR", "USD", "EUR", "AUD", "CAD", "JPY", "SGD"]:
            currency_code = upper_token
            # Check if there's a fare value after the currency code
            if i + 1 < len(tokens) and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
                expected_fare = float(tokens[i + 1])
            break
    
    # If we found tour indicators but no currency code, set default to NUC
    if len(tour_indicators) > 0 and currency_code is None:
        currency_code = "NUC"
    
    # Check if this is a tour fare (M/BT or M/IT)
    has_tour_indicator = len(tour_indicators) > 0
    
    # For tour fares, there might not be an expected fare to match against
    if has_tour_indicator:
        is_fare_match = True  # Tour fares don't require fare matching
    else:
        # Check if the expected fare matches the calculated fare total
        is_fare_match = False
        if expected_fare is not None:
            # MODIFIED: Always validate against total fare with Q surcharges, class differentials, and plus ups included
            is_fare_match = abs(fare_total - expected_fare) < 0.01
            
            # Add a warning if the expected fare doesn't match the calculated fare total
            if not is_fare_match:
                # If the expected fare matches journey fare but not total, provide specific message
                if abs(total_journey_fare - expected_fare) < 0.01:
                    print(f"Warning: Expected fare {expected_fare} matches journey fare {total_journey_fare} but excludes Q surcharges {q_surcharge_total}, class differentials {class_differential_total}, and plus ups {plus_up_total}. Total should be {fare_total}.")
                else:
                    print(f"Warning: Expected fare {expected_fare} does not match calculated fare total {fare_total} (journey fares: {total_journey_fare}, Q surcharges: {q_surcharge_total}, class differentials: {class_differential_total}, plus ups: {plus_up_total}).")
        else:
            # If no expected fare, consider it a match
            is_fare_match = True
    
    return total_journey_fare, q_surcharge_total, class_differential_total, plus_up_total, tour_indicators, fare_total, expected_fare, currency_code, is_fare_match

# Keep the original function for backward compatibility
def calculate_nuc_total(pattern, journey_validation):
    """
    Calculate the total NUC value from journey fares and Q surcharges (legacy function)
    
    Args:
        pattern (str): The fare calculation pattern
        journey_validation (dict): Dictionary containing journey validation information
        
    Returns:
        tuple: (total_journey_fare, total_q_surcharge, nuc_total, expected_nuc, is_valid)
    """
    total_journey_fare, q_surcharge_total, class_differential_total, plus_up_total, _, fare_total, expected_fare, currency_code, is_valid = calculate_fare_total(pattern, journey_validation)
    
    # For backward compatibility, if currency is not NUC, still return the values as if they were NUC
    if currency_code != "NUC":
        print(f"Warning: Currency code {currency_code} detected, but returning as NUC for backward compatibility")
    
    return total_journey_fare, q_surcharge_total, fare_total, expected_fare, is_valid

def analyze_pattern_with_journey(pattern, journey_string=None):
    """
    Analyze a fare calculation pattern with an optional journey string
    
    Args:
        pattern (str): The fare calculation pattern to analyze
        journey_string (str, optional): The journey string to validate against the pattern
        
    Returns:
        dict: Dictionary with analysis results
    """
    # Analyze the pattern
    pattern_analysis = analyze_pattern(pattern)
    
    # If no journey string is provided, return the pattern analysis
    if not journey_string:
        return pattern_analysis
    
    # Clean the journey string
    cleaned_journey = clean_journey_string(journey_string)
    
    # Validate the journey string against the pattern
    journey_validation = validate_journey_string(pattern_analysis['cleaned_pattern'], cleaned_journey)
    
    # Add journey validation to the pattern analysis
    pattern_analysis['journey_validation']['cleaned_journey'] = cleaned_journey
    pattern_analysis['journey_validation']['journey_validation'] = journey_validation
    
    return pattern_analysis

def identify_missing_journey_parts(pattern, journey_string):
    """
    Identify missing parts in a journey string compared to an FCA pattern
    
    Args:
        pattern (str): The full FCA pattern
        journey_string (str): The journey string to validate
        
    Returns:
        str: Description of missing parts
    """
    validation = validate_journey_string(pattern, journey_string)
    
    if validation['is_match']:
        return "Journey string matches the pattern route."
    
    missing_parts = []
    for segment in validation['missing_segments']:
        # Check if this is a complete segment (airport-airline-airport)
        tokens = segment.split()
        if len(tokens) >= 3 and tokens[0] in AIRPORT_CODES and tokens[1] in AIRLINE_CODES and tokens[2] in AIRPORT_CODES:
            missing_parts.append(f"Complete segment: {segment}")
        elif len(tokens) == 2 and tokens[0] in AIRPORT_CODES and tokens[1] in AIRLINE_CODES:
            missing_parts.append(f"Partial segment (origin-airline): {segment}")
        elif len(tokens) == 2 and tokens[0] in AIRLINE_CODES and tokens[1] in AIRPORT_CODES:
            missing_parts.append(f"Partial segment (airline-destination): {segment}")
        elif len(tokens) == 1 and tokens[0] in AIRPORT_CODES:
            missing_parts.append(f"Airport: {segment}")
        elif len(tokens) == 1 and tokens[0] in AIRLINE_CODES:
            missing_parts.append(f"Airline: {segment}")
        else:
            missing_parts.append(f"Unknown segment: {segment}")
    
    if missing_parts:
        return f"Missing parts: {'; '.join(missing_parts)}"
    else:
        return "Journey string does not match the pattern route, but no specific missing parts identified."

def clean_pattern(pattern):
    """
    Clean a fare calculation pattern by removing garbage tokens and fixing spacing issues
    
    Args:
        pattern (str): The fare calculation pattern to clean
        
    Returns:
        tuple: (cleaned_pattern, garbage_tokens, spacing_issues)
    """
    # Original pattern
    original = pattern
    
    # Check if the pattern starts with an involuntary journey change indicator (I-)
    has_invol = False
    if pattern.startswith("I-"):
        has_invol = True
        # Remove I- temporarily for processing
        pattern = pattern[2:].strip()
    
    # Check for tokens that might be concatenated without spaces
    tokens = pattern.split()
    expanded_tokens = []
    concatenated_fixes = []
    
    for token in tokens:
        # Try to split concatenated tokens
        split_tokens = split_concatenated_tokens(token)
        
        # Ensure split_tokens is a list of strings, not a list containing lists
        if isinstance(split_tokens, list):
            # If split_tokens contains any list elements, flatten them
            flattened_tokens = []
            for item in split_tokens:
                if isinstance(item, list):
                    flattened_tokens.extend(item)
                else:
                    flattened_tokens.append(item)
            split_tokens = flattened_tokens
        
        if len(split_tokens) > 1:
            expanded_tokens.extend(split_tokens)
            concatenated_fixes.append((token, split_tokens))
        else:
            expanded_tokens.append(token)
    
    # Rejoin tokens for further processing
    expanded_pattern = ' '.join(expanded_tokens)
    
    # Find valid code combinations
    valid_combinations = find_valid_code_combinations(expanded_tokens)
    
    # Apply valid combinations to create a new pattern
    if valid_combinations:
        # Sort combinations by start index
        valid_combinations.sort(key=lambda x: x[0])
        
        # Create a new list of tokens
        new_tokens = []
        i = 0
        while i < len(expanded_tokens):
            # Check if this index is the start of a valid combination
            found_combination = False
            for start, end, combined, token_type in valid_combinations:
                if start == i:
                    new_tokens.append(combined)
                    i = end + 1
                    found_combination = True
                    break
            
            if not found_combination:
                # Check if this token is valid
                is_valid, token_type = is_valid_token(expanded_tokens[i])
                if is_valid:
                    new_tokens.append(expanded_tokens[i])
                    
                    # Special handling for Q surcharges
                    if expanded_tokens[i] == "Q" and i + 1 < len(expanded_tokens):
                        next_token = expanded_tokens[i + 1]
                        next_is_valid, next_token_type = is_valid_token(next_token)
                        if next_is_valid and (next_token_type == "FARE" or next_token_type == "NUMERIC"):
                            new_tokens.append(next_token)
                            i += 1  # Skip the next token as we've already added it
                i += 1
        
        # Ensure all tokens are strings before joining
        new_tokens = [str(token) for token in new_tokens]
        
        # Rejoin tokens
        expanded_pattern = ' '.join(new_tokens)
    
    # Process tokens to preserve fare amounts, Q surcharges, and side trip indicators
    tokens = expanded_pattern.split()
    valid_tokens = []
    i = 0
    
    # Track whether we are within a side trip (parentheses)
    in_side_trip = False
    
    while i < len(tokens):
        token = tokens[i]
        is_valid, token_type = is_valid_token(token)
        
        # Always keep valid tokens
        if is_valid:
            # Handle opening parenthesis for side trip
            if token == "(":
                in_side_trip = True
            # Handle closing parenthesis for side trip
            elif token == ")" and in_side_trip:
                in_side_trip = False
                
            valid_tokens.append(token)
            
            # Special handling for Q surcharges
            if token == "Q" and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                next_is_valid, next_token_type = is_valid_token(next_token)
                
                # If Q is followed by a valid fare amount, ensure we keep both
                if next_is_valid and (next_token_type == "FARE" or next_token_type == "NUMERIC"):
                    valid_tokens.append(next_token)  # Add the fare amount after Q
                    i += 1  # Skip to the next token since we've already added it
        # If we're inside a side trip, preserve invalid tokens as well
        elif in_side_trip:
            valid_tokens.append(token)
        
        i += 1
    
    # Special handling for tour indicators (M/BT, M/IT) - ensure they are preserved
    for i in range(len(tokens)):
        if tokens[i] in ["M/BT", "M/IT"] and tokens[i] not in valid_tokens:
            valid_tokens.append(tokens[i])
    
    # Ensure all tokens are strings before joining
    valid_tokens = [str(token) for token in valid_tokens]
    
    # Reconstruct the pattern
    cleaned_pattern = ' '.join(valid_tokens)
    
    # Ensure I- is preserved at the beginning if it was in the original pattern
    if has_invol and not cleaned_pattern.startswith("I-"):
        cleaned_pattern = "I- " + cleaned_pattern
    
    # Identify tokens that were removed (garbage)
    original_tokens = original.split()
    cleaned_tokens = cleaned_pattern.split()
    
    # Identify tokens that were removed as garbage
    garbage_tokens = []
    for token in original_tokens:
        if token not in cleaned_tokens and token.strip():
            # Check if this token was split into multiple tokens
            was_split = False
            for orig, split in concatenated_fixes:
                if orig == token:
                    was_split = True
                    break
            if not was_split:
                garbage_tokens.append(token)
    
    # Check for spacing issues
    spacing_issues = []
    if concatenated_fixes:
        for original_token, split_tokens in concatenated_fixes:
            spacing_issues.append(f"Token '{original_token}' was split into {split_tokens}")
    
    return cleaned_pattern, garbage_tokens, spacing_issues

def reconstruct_valid_pattern(tokens):
    """
    Attempt to reconstruct a valid fare calculation pattern from tokens
    
    Args:
        tokens (list): List of tokens to reconstruct
        
    Returns:
        str: The reconstructed pattern, or None if reconstruction fails
    """
    # Check if we have enough tokens to form a valid pattern
    if len(tokens) < 3:
        return None
    
    # Check if we have NUC and END tokens
    has_nuc = "NUC" in tokens
    has_end = "END" in tokens
    
    if not has_nuc or not has_end:
        # Try to add missing tokens
        if not has_nuc:
            # Find a position to insert NUC
            for i, token in enumerate(tokens):
                if re.match(r'^\d+\.\d{2}$', token) and i + 1 < len(tokens) and tokens[i+1] == "END":
                    # Insert NUC before the fare amount
                    tokens.insert(i, "NUC")
                    has_nuc = True
                    break
        
        if not has_end:
            # Find a position to insert END
            for i, token in enumerate(tokens):
                if token == "NUC" and i + 1 < len(tokens) and re.match(r'^\d+\.\d{2}$', tokens[i+1]):
                    # Insert END after the NUC amount
                    tokens.insert(i+2, "END")
                    has_end = True
                    break
    
    # Check if we have fare amounts
    fare_amounts = []
    for token in tokens:
        if re.match(r'^\d+\.\d{2}$', token):
            fare_amounts.append(float(token))
    
    if len(fare_amounts) < 2:
        # Not enough fare amounts to form a valid pattern
        return None
    
    # Check if the pattern starts with an involuntary journey change indicator
    has_invol = "I-" in tokens and tokens.index("I-") == 0
    
    # Identify special tokens like transit indicators and surface segments
    transit_indicators = []
    surface_indicators = []
    for i, token in enumerate(tokens):
        if token == "X/":
            # Check if followed by an airport code
            if i + 1 < len(tokens) and tokens[i+1] in AIRPORT_CODES:
                transit_indicators.append((i, tokens[i+1]))
        elif token in ["//", "/-"]:
            # Check if followed by an airport code
            if i + 1 < len(tokens) and tokens[i+1] in AIRPORT_CODES:
                surface_indicators.append((i, tokens[i+1]))
    
    # Check if we have alternating airport and airline codes
    airport_codes = []
    airline_codes = []
    
    for token in tokens:
        if token in AIRPORT_CODES:
            airport_codes.append(token)
        elif token in AIRLINE_CODES:
            airline_codes.append(token)
    
    if len(airport_codes) < 2 or len(airline_codes) < 1:
        # Not enough codes to form a valid pattern
        return None
    
    # Try to reconstruct a valid pattern
    reconstructed = []
    
    # Start with I- if the pattern has an involuntary journey change
    if has_invol:
        reconstructed.append("I-")
    
    # Start with an airport code
    reconstructed.append(airport_codes[0])
    
    # Add alternating airline and airport codes, including transit and surface indicators
    airport_index = 1  # Start from the second airport code
    airline_index = 0
    
    while airport_index < len(airport_codes) and airline_index < len(airline_codes):
        # Add airline code
        reconstructed.append(airline_codes[airline_index])
        airline_index += 1
        
        # Check if the next airport should have a transit indicator
        has_transit = False
        for transit_idx, transit_airport in transit_indicators:
            if transit_airport == airport_codes[airport_index]:
                reconstructed.append("X/")
                has_transit = True
                break
    
        # Check if the next airport should have a surface indicator
        has_surface = False
        if not has_transit:  # Only check for surface if not transit
            for surface_idx, surface_airport in surface_indicators:
                if surface_airport == airport_codes[airport_index]:
                    reconstructed.append(tokens[surface_idx])  # Add the specific surface indicator
                    has_surface = True
                    break
        
        # Add airport code
        reconstructed.append(airport_codes[airport_index])
        airport_index += 1
    
    # Add fare amount
    reconstructed.append(f"{fare_amounts[0]:.2f}")
    
    # Add NUC and fare amount
    if "NUC" not in reconstructed:
        reconstructed.append("NUC")
    else:
        # Find the NUC position and ensure it's followed by a fare amount
        nuc_index = reconstructed.index("NUC")
        if nuc_index + 1 >= len(reconstructed) or not re.match(r'^\d+\.\d{2}$', reconstructed[nuc_index + 1]):
            # Add the total fare amount after NUC
            reconstructed.insert(nuc_index + 1, f"{sum(fare_amounts):.2f}")
    
    # Add END
    if "END" not in reconstructed:
        reconstructed.append("END")
    
    # Join the reconstructed pattern
    return ' '.join(reconstructed)

def analyze_pattern(pattern):
    """
    Analyze a fare calculation pattern for validity and structure.
    
    Args:
        pattern (str): The fare calculation pattern to analyze
    
    Returns:
        dict: A dictionary with analysis results
    """
    # Store the original pattern for reference
    original_pattern = pattern
    
    try:
        # Remove leading/trailing whitespace
        pattern = pattern.strip()
        
        # Check if pattern has an involuntary journey change indicator (I-)
        # Only preserve I- if it's already in the pattern, don't add it otherwise
        has_i_prefix = pattern.startswith("I-")
        
        # Special handling for Q surcharges in the pattern
        tokens = pattern.split()
        processed_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Handle Q surcharge (Q followed by a fare amount)
            if token == "Q" and i + 1 < len(tokens) and re.match(r'^\d+(\.\d+)?$', tokens[i + 1]):
                # Combine Q and fare amount into a Q surcharge token (e.g., "Q10.00")
                q_surcharge = f"Q{tokens[i + 1]}"
                processed_tokens.append(q_surcharge)
                i += 2  # Skip both tokens
                continue
            
            processed_tokens.append(token)
            i += 1
        
        # Use the processed pattern for cleaning
        processed_pattern = ' '.join(processed_tokens)
        
        # Clean the pattern
        cleaned_pattern, garbage_tokens, spacing_issues = clean_pattern(processed_pattern)
        
        # Ensure I- prefix is preserved in cleaned pattern if it was in the original
        if has_i_prefix and not cleaned_pattern.startswith("I-"):
            cleaned_pattern = "I- " + cleaned_pattern
        
        # Calculate fare total to get Q surcharges before any auto-correction
        journey_validation_temp = validate_pattern_structure(cleaned_pattern)
        
        # Extract fare calculation components from validation
        tour_indicators = journey_validation_temp.get('tour_indicators', [])
        side_trips = journey_validation_temp.get('side_trips', [])
        
        # Validate the pattern structure
        journey_validation = validate_pattern_structure(cleaned_pattern)
        
        # Extract fare calculation components
        journey_fares = journey_validation.get('journey_fares', [])
        q_surcharges = journey_validation.get('q_surcharges', [])
        class_differentials = journey_validation.get('class_differentials', [])
        plus_up_amounts = journey_validation.get('plus_up_amounts', [])
        tour_indicators = journey_validation.get('tour_indicators', [])
        side_trips = journey_validation.get('side_trips', [])
        fare_value = journey_validation.get('fare_value')
        currency_code = journey_validation.get('currency_code')
        roe_value = journey_validation.get('roe_value')
        
        # Calculate totals
        total_journey_fare = sum(journey_fares)
        q_surcharge_total = sum(q_surcharges)
        class_differential_total = sum(class_differentials)
        plus_up_total = sum(plus_up_amounts)
        calculated_fare_total = total_journey_fare + q_surcharge_total + class_differential_total + plus_up_total
        
        # Determine if the pattern is valid
        is_valid = journey_validation.get('is_valid', False)
        
        # Prepare the result dictionary
        result = {
            'is_valid': is_valid,
            'original_pattern': original_pattern,
            'cleaned_pattern': cleaned_pattern,
            'garbage_tokens': garbage_tokens,
            'spacing_issues': spacing_issues,
            'fare_calculation': {
                'journey_fares': journey_fares,
                'q_surcharge': q_surcharge_total,
                'class_differential': class_differential_total,
                'plus_up': plus_up_total,
                'tour_indicators': tour_indicators,
                'side_trips': side_trips,
                'total_journey_fare': total_journey_fare,
                'expected_fare': fare_value,
                'calculated_fare_total': calculated_fare_total,
                'roe_value': roe_value,
                'currency_code': currency_code
            }
        }
        
        return result
    except Exception as e:
        import traceback
        print(f"Exception in analyze_pattern: {e}")
        print(traceback.format_exc())
        # Return a valid result dictionary with error information
        return {
            'is_valid': False,
            'original_pattern': original_pattern,
            'cleaned_pattern': original_pattern,  # Use original as fallback
            'garbage_tokens': [],
            'spacing_issues': [],
            'error': str(e),
            'fare_calculation': {
                'journey_fares': [],
                'q_surcharge': 0.0,
                'class_differential': 0.0,
                'plus_up': 0.0,
                'tour_indicators': [],
                'side_trips': [],
                'total_journey_fare': 0.0,
                'expected_fare': None,
                'calculated_fare_total': 0.0,
                'roe_value': None,
                'currency_code': None
            }
        }

if __name__ == "__main__":
    # Test with the problematic pattern
    test_pattern = "LON BA PAR WY DOH 800.00 NUC 800.00 END"
    
    # Test with different journey strings
    journey_strings = [
        "LON BA PAR WY DOH",  # Complete match
        "PAR WY DOH",         # Missing beginning
        "LON BA PAR",         # Missing end
        "LON BA DOH",         # Missing middle
        "LON PAR DOH",        # Missing airlines
        "BA WY",              # Only airlines
        "LONBAPARWYDOH",      # Concatenated
        "LON BA PAR XYZ DOH"  # With garbage
    ]
    
    for journey in journey_strings:
        print(f"\n=== Testing Journey: {journey} ===")
        analysis = analyze_pattern_with_journey(test_pattern, journey)
        
        print(f"Original Pattern: {analysis['original_pattern']}")
        print(f"Cleaned Pattern: {analysis['cleaned_pattern']}")
        print(f"Journey String: {journey}")
        print(f"Cleaned Journey: {analysis['journey_validation']['cleaned_journey']}")
        print(f"Is Match: {analysis['journey_validation']['is_match']}")
        
        if not analysis['journey_validation']['is_match']:
            print(f"Missing Segments: {analysis['journey_validation']['missing_segments']}")
            print(f"Analysis: {analysis['missing_journey_parts']}") 
        
        # Print fare calculation
        if 'fare_calculation' in analysis:
            print("\nFare Calculation:")
            print(f"Journey Fares: {analysis['fare_calculation']['journey_fares']}")
            print(f"Q Surcharge: {analysis['fare_calculation']['q_surcharge']}")
            print(f"Total Journey Fare: {analysis['fare_calculation']['total_journey_fare']}")
            print(f"Calculated NUC Total: {analysis['fare_calculation']['calculated_nuc_total']}")
            print(f"Pattern NUC Total: {analysis['fare_calculation']['pattern_nuc_total']}")
            print(f"NUC Match: {analysis['fare_calculation']['is_nuc_match']}")
    
    # Test with Q surcharge
    print("\n\n=== Testing Pattern with Q Surcharge ===")
    q_pattern = "LON BA PAR WY DOH 500.00 Q300.00 NUC 800.00 END"
    q_journey = "LON BA PAR WY DOH"
    q_analysis = analyze_pattern_with_journey(q_pattern, q_journey)
    
    print(f"Original Pattern: {q_analysis['original_pattern']}")
    print(f"Cleaned Pattern: {q_analysis['cleaned_pattern']}")
    print(f"Journey String: {q_journey}")
    print(f"Cleaned Journey: {q_analysis['journey_validation']['cleaned_journey']}")
    print(f"Is Match: {q_analysis['journey_validation']['is_match']}")
    
    # Print fare calculation
    if 'fare_calculation' in q_analysis:
        print("\nFare Calculation:")
        print(f"Journey Fares: {q_analysis['fare_calculation']['journey_fares']}")
        print(f"Q Surcharge: {q_analysis['fare_calculation']['q_surcharge']}")
        print(f"Total Journey Fare: {q_analysis['fare_calculation']['total_journey_fare']}")
        print(f"Calculated NUC Total: {q_analysis['fare_calculation']['calculated_nuc_total']}")
        print(f"Pattern NUC Total: {q_analysis['fare_calculation']['pattern_nuc_total']}")
        print(f"NUC Match: {q_analysis['fare_calculation']['is_nuc_match']}")
    
    # Test with multiple journey fares
    print("\n\n=== Testing Pattern with Multiple Journey Fares ===")
    # Use a pattern with clearly separated journey segments and fares
    multi_pattern = "LON BA PAR 300.00 PAR WY DOH 500.00 NUC 800.00 END"
    multi_journey = "LON BA PAR PAR WY DOH"
    multi_analysis = analyze_pattern_with_journey(multi_pattern, multi_journey)
    
    print(f"Original Pattern: {multi_analysis['original_pattern']}")
    print(f"Cleaned Pattern: {multi_analysis['cleaned_pattern']}")
    print(f"Journey String: {multi_journey}")
    print(f"Cleaned Journey: {multi_analysis['journey_validation']['cleaned_journey']}")
    print(f"Is Match: {multi_analysis['journey_validation']['is_match']}")
    
    # Print fare calculation
    if 'fare_calculation' in multi_analysis:
        print("\nFare Calculation:")
        print(f"Journey Fares: {multi_analysis['fare_calculation']['journey_fares']}")
        print(f"Q Surcharge: {multi_analysis['fare_calculation']['q_surcharge']}")
        print(f"Total Journey Fare: {multi_analysis['fare_calculation']['total_journey_fare']}")
        print(f"Calculated NUC Total: {multi_analysis['fare_calculation']['calculated_nuc_total']}")
        print(f"Pattern NUC Total: {multi_analysis['fare_calculation']['pattern_nuc_total']}")
        print(f"NUC Match: {multi_analysis['fare_calculation']['is_nuc_match']}") 