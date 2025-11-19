"""Stream Replacer Module.

Handles transformation of problematic language tags in streaming content.
Takes a stream, applies replacements, and forwards the modified stream.
"""
# Copyright (c) 2024 FastStreamingAgent Contributors

from typing import AsyncGenerator, Any


class StreamReplacer:
    """Handles stream content replacement and buffering for problematic language tags."""
    
    def __init__(self, problematic_languages: list[str] | None = None) -> None:
        """Initialize the stream replacer.
        
        Args:
            problematic_languages: List of language tags to replace with 'python'.
        """
        # Define replacements as a mapping from problematic tag to replacement
        self.replacements = {
            "tool_code": "python",
            "tool_call": "python", 
            "tool_code>": "python",
            "tool_call>": "python",
            "<execute_python>": "python",
            "<execute_bash>": "bash"
        }
        
        # For backward compatibility, extract problematic languages list
        self.problematic_languages = list(self.replacements.keys())
        
        # Buffering state
        self.buffer = ""
        self.buffering = False
    
    def _should_start_buffering(self, content: str) -> bool:
        """Check if content contains problematic language tags that require buffering.
        
        Args:
            content: Stream content chunk.
            
        Returns:
            True if buffering should start.
        """
        if "```" not in content:
            return False
            
        for lang in self.problematic_languages:
            if f"{lang}" in content:
                return True
        return False
    
    def _apply_replacements(self, content: str) -> str:
        """Apply language tag replacements to content.
        
        Args:
            content: Content to transform.
            
        Returns:
            Transformed content with problematic languages replaced.
        """
        fixed_content = content
        for problematic_tag, replacement in self.replacements.items():
            fixed_content = fixed_content.replace(f"```{problematic_tag}", f"```{replacement}")
        return fixed_content
    
    def process_chunk(self, content: str) -> tuple[str, bool]:
        """Process a single stream chunk, handling buffering and replacements.
        
        Args:
            content: Stream content chunk.
            
        Returns:
            Tuple of (processed_content, should_print) where:
            - processed_content: Content to add to assistant_content
            - should_print: Whether this content should be printed immediately
        """
        if self.buffering:
            self.buffer += content
            
            # Check if we have complete code block language declaration
            if "\n" in self.buffer and self.buffer.count("```") >= 1:
                # Apply replacements and process the buffered content
                fixed_buffer = self._apply_replacements(self.buffer)
                
                # Reset buffering state
                self.buffer = ""
                self.buffering = False
                
                return fixed_buffer, True
            
            # Check if we see closing ``` while buffering, flush everything
            elif self.buffer.count("```") >= 2:
                fixed_buffer = self._apply_replacements(self.buffer)
                
                self.buffer = ""
                self.buffering = False
                
                return fixed_buffer, True
            
            # Still buffering, don't print yet
            return "", False
        
        else:
            # Check if we need to start buffering
            if self._should_start_buffering(content):
                self.buffering = True
                self.buffer = content
                return "", False
            else:
                # Normal streaming - no buffering needed
                return content, True
    
    def reset(self) -> None:
        """Reset the replacer state for a new stream."""
        self.buffer = ""
        self.buffering = False


async def replace_stream_content(
    stream: AsyncGenerator[Any, None], 
    replacer: StreamReplacer
) -> AsyncGenerator[tuple[str, str], None]:
    """Transform a stream by applying content replacements.
    
    Args:
        stream: Original stream to transform.
        replacer: StreamReplacer instance to use for transformations.
        
    Yields:
        Tuples of (processed_content, colored_content) for each chunk.
    """
    async for chunk in stream:
        if (hasattr(chunk, 'choices') and 
            len(chunk.choices) > 0 and 
            hasattr(chunk.choices[0], 'delta') and 
            chunk.choices[0].delta.content):
            
            content = chunk.choices[0].delta.content
            processed_content, should_print = replacer.process_chunk(content)
            
            if should_print and processed_content:
                colored_content = replacer.get_colored_content(processed_content)
                yield processed_content, colored_content