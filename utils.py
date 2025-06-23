import re

def validate_input(data):
    """Validate input data ranges for crop recommendation."""
    ranges = {
        'Nitrogen': (0, 140),
        'Phosporus': (0, 145),
        'Potassium': (0, 205),
        'Temperature': (8.0, 44.0),
        'Humidity': (14.0, 100.0),
        'pH': (3.5, 10.0),
        'Rainfall': (20.0, 300.0)
    }
    
    for key, (min_val, max_val) in ranges.items():
        try:
            value = float(data[key])
            if not min_val <= value <= max_val:
                return False, f"{key} should be between {min_val} and {max_val}"
        except (ValueError, KeyError):
            return False, f"Invalid {key} value"
    return True, ""

def parse_range(value_str):
    """Helper function to parse a string like '10-20' or '₹10,000-15,000' and return the average."""
    if not value_str or not isinstance(value_str, str):
        return 0
    
    # Remove currency symbols, commas, and other non-numeric characters except for the hyphen
    cleaned_str = re.sub(r'[₹,]', '', value_str).split()[0]
    
    # Find all numbers in the cleaned string
    numbers = [float(s) for s in re.findall(r'\d+\.?\d*', cleaned_str)]
    
    if not numbers:
        return 0
    
    # Return the average of the numbers found (handles single values and ranges)
    return sum(numbers) / len(numbers) if len(numbers) > 0 else 0 