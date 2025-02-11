import re

def remove_linebreaks(text):
    # Use regular expression to replace all newlines and carriage returns
    return re.sub(r'[\r\n]+', '', text)