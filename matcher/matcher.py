
import re

def match_and_format(text, pattern_dict):
    """
    This function checks the input text against multiple regex patterns and formats the matched part
    based on the provided format strings in pattern_dict.

    :param text: The input text to search for patterns.
    :param pattern_dict: A dictionary where keys are regex patterns and values are format patterns.
    :return: A list of formatted results or an empty list if no match is found.
    """
    results = []
    
    for pattern, format_pattern in pattern_dict.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            formatted_result = re.sub(pattern, format_pattern, match.group(0))
            results.append(formatted_result)
    
    return results
