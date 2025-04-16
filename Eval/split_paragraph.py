import re

def split_paragraph(paragraph, max_length=4000):
    """
    Split a paragraph into multiple complete sentences, each not exceeding max_length.
    
    Args:
        paragraph (str): The input paragraph.
        max_length (int, optional): The maximum length of each split. Defaults to 4000.
        
    Returns:
        list: A list of strings, each representing a part of the original paragraph.
              If the original paragraph is shorter than max_length, it is returned
              as the only element in the list.
    """
    
    # Define a regular expression pattern to match sentence boundaries
    # sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    # Split the paragraph into sentences
    # sentences = re.split(sentence_pattern, paragraph)

    sentence_pattern = re.compile(r'([^.!?\n]+[.!?\n])')
    sentences = sentence_pattern.findall(paragraph)
    
    # If the paragraph is shorter than max_length, return it as a single-element list
    if len(paragraph) <= max_length:
        return [paragraph]
    
    # Initialize a list to store the parts
    parts = []
    current_part = ''
    
    # Iterate over sentences and accumulate them into parts
    for sentence in sentences:
        if len(current_part) + len(sentence) <= max_length:
            current_part += sentence
        else:
            parts.append(current_part)
            current_part = sentence
    
    # Append the last part
    if current_part:
        parts.append(current_part)
    
    return parts