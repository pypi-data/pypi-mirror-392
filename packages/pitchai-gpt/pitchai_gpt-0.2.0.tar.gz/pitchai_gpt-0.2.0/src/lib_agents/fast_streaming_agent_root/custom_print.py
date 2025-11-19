"""Custom print function for FastStreamingAgent that captures output cleanly."""

import sys
from io import StringIO


class PrintCapture:
    """Captures print output while filtering out library debug logs."""
    
    def __init__(self):
        self.buffer = StringIO()
        self.original_print = print
    
    def custom_print(self, *args, **kwargs):
        """Custom print function that captures output to our buffer."""
        # Handle sep and end parameters
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        file = kwargs.get('file', None)
        
        # If file is specified and it's not stdout, use original print
        if file and file != sys.stdout:
            return self.original_print(*args, **kwargs)
        
        # Format the output
        formatted = sep.join(str(arg) for arg in args) + end
        
        # Write ONLY to our buffer (not to stdout to avoid duplicate output)
        self.buffer.write(formatted)
    
    def get_output(self) -> str:
        """Get the captured output."""
        return self.buffer.getvalue()
    
    def clear(self):
        """Clear the buffer."""
        self.buffer = StringIO()