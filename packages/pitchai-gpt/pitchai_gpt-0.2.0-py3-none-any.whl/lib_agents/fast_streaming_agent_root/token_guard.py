"""Token Length Guard Module.

Monitors and limits output based on token count to prevent context explosion.
"""
# Copyright (c) 2024 FastStreamingAgent Contributors

import tiktoken
from typing import Optional


class TokenLengthGuard:
    """Guards against excessive token usage in outputs."""
    
    def __init__(self, max_tokens: int = 20000, model: str = "gpt-4o") -> None:
        """Initialize the token guard.
        
        Args:
            max_tokens: Maximum allowed tokens in output.
            model: Model name for tokenizer selection.
        """
        self.max_tokens = max_tokens
        
        # Initialize tokenizer
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding (used by GPT-4 models)
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.
        
        Args:
            text: Text to count tokens for.
            
        Returns:
            Number of tokens.
        """
        try:
            return len(self.encoder.encode(text))
        except Exception:
            # Fallback to rough estimation (1 token ≈ 4 chars)
            return len(text) // 4
    
    def check_and_limit_output(self, output: str) -> tuple[str, bool]:
        """Check if output exceeds token limit and return appropriate response.
        
        Args:
            output: The output text to check.
            
        Returns:
            Tuple of (processed_output, was_limited).
            If limited, returns a summary message instead of full output.
        """
        token_count = self.count_tokens(output)
        
        if token_count <= self.max_tokens:
            return output, False
        
        # Calculate statistics for the summary message
        lines = output.count('\n') + 1
        chars = len(output)
        
        summary_message = (
            f"⚠️ OUTPUT TOO LARGE\n"
            f"• Tokens: {token_count:,}\n"
            f"• Characters: {chars:,}\n"  
            f"• Lines: {lines:,}\n"
            f"• Maximum allowed: {self.max_tokens:,} tokens\n\n"
            f"This output is too long to display. Please be more specific with your "
            f"query/code to get more focused results and more limited output, or save the output to a file instead."
        )
        
        return summary_message, True
    
    def get_token_stats(self, text: str) -> dict[str, int]:
        """Get detailed token statistics for text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Dictionary with token, character, and line counts.
        """
        return {
            "tokens": self.count_tokens(text),
            "characters": len(text),
            "lines": text.count('\n') + 1
        }
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o") -> float:
        """Estimate API cost based on token usage.
        
        Args:
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.
            model: Model name for pricing.
            
        Returns:
            Estimated cost in USD.
        """
        # Pricing per 1K tokens (as of 2024)
        pricing = {
            "gpt-4o": {"prompt": 0.0025, "completion": 0.01},
            "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
            "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
            # Gemini models (rough estimates)
            "gemini-2.0-flash": {"prompt": 0.00007, "completion": 0.00028},
            "gemini-2.0-flash-lite": {"prompt": 0.00005, "completion": 0.0002},
        }
        
        # Get pricing or use default
        model_pricing = pricing.get(model, {"prompt": 0.0001, "completion": 0.0002})
        
        prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * model_pricing["completion"]
        
        return prompt_cost + completion_cost