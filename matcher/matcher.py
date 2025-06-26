
import re
from logger_setup import get_logger

logger = get_logger()

def match_and_format(text, pattern_dict, greedy = False):
    """
    This function checks the input text against multiple regex patterns and formats the matched part
    based on the provided format strings in pattern_dict.

    :param text: The input text to search for patterns.
    :param pattern_dict: A dictionary where keys are regex patterns and values are format patterns.
    :return: A list of formatted results or an empty list if no match is found.
    """
    results = []
    
    for pattern, format_pattern in pattern_dict.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        match = matches[-1] if matches else None
        if match:
            logger.debug(f"found {match.group(0)} with {pattern}")
            if callable(format_pattern):
                formatted_result = format_pattern(match)
            else:
                formatted_result = re.sub(pattern, format_pattern, match.group(0))
            logger.debug(f"formatted_result: {formatted_result}")
            results.append(formatted_result)
            if not greedy:
                break
    
    return results
