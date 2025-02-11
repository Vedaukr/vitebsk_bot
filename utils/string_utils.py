import os
import re

def remove_linebreaks(text):
    # Use regular expression to replace all newlines and carriage returns
    return re.sub(r'[\r\n]+', '', text)

class StringBuilder:
    def __init__(self):
        self._strings = []

    def append(self, string) -> 'StringBuilder':
        """Appends the specified string to this StringBuilder."""
        self._strings.append(string)
        return self
    
    def append_line(self, string) -> 'StringBuilder':
        """Appends the specified string + linebreak to this StringBuilder."""
        self._strings.append(string)
        self._strings.append(os.linesep)
        return self
    
    def append_linebreaks(self, count: int = 1) -> 'StringBuilder':
        self._strings.append(os.linesep * count)
        return self

    def build(self) -> str:
        """Returns the entire built string."""
        return ''.join(self._strings)