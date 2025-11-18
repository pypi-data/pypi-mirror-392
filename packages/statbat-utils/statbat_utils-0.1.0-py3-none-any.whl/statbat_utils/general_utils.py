from unidecode import unidecode

def remove_non_ascii(
    item,
):
    """
    Removes any non-ascii characters within a string/array of strings.
    
    Args:
        input_object (str | list): Input string(s) to be cleaned.
    
    Returns:
        str | list: Cleaned string/array.
    
    Raises:
        ValueError: Input is not string or array.
    """
    if isinstance(item, list):
        return [
            unidecode(x)
            for x in item
        ]
    return unidecode(item)