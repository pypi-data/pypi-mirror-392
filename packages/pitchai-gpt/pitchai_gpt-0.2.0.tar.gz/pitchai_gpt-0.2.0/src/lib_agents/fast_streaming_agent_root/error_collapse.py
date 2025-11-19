"""Error sequence collapsing utilities for the Fast Streaming Agent.

This module provides functions to collapse error sequences in conversation histories,
combining initial reasoning with successful resolutions to create cleaner message lists.
"""

import re
from typing import List, Dict, Tuple


def extract_reasoning(content: str) -> str:
    """Extract the reasoning/thought process from assistant content.
    
    Args:
        content: The full assistant message content.
        
    Returns:
        The extracted reasoning text without code blocks or outputs.
    """
    # Remove code blocks and their outputs
    result = content
    
    # Pattern to match code blocks with their outputs
    code_output_pattern = re.compile(
        r'```[a-z]*\n.*?\n```\s*\n<output>.*?</output>', 
        re.DOTALL
    )
    result = code_output_pattern.sub('', result)
    
    # Also remove standalone code blocks
    code_pattern = re.compile(r'```[a-z]*\n.*?\n```', re.DOTALL)
    result = code_pattern.sub('', result)
    
    # Remove standalone outputs
    output_pattern = re.compile(r'<output>.*?</output>', re.DOTALL)
    result = output_pattern.sub('', result)
    
    return result.strip()


def collapse_error_sequences(messages: List[Dict[str, str]], verbose: bool = True, consecutive_successes_required: int = 2) -> int:
    """Collapse all error sequences in the conversation.
    
    This method finds sequences where the assistant tried multiple times
    with errors and eventually succeeded N times in a row, then collapses them to show
    only the initial reasoning combined with the first successful attempt.
    
    Args:
        messages: List of conversation messages to modify in-place.
        verbose: Whether to print debug information about collapsing.
        consecutive_successes_required: Number of consecutive successes needed to trigger collapse.
        
    Returns:
        Number of messages collapsed.
    """
    # Track sequences of assistant messages with their error status and code execution
    assistant_sequences: List[Tuple[int, bool, bool]] = []  # (index, has_error, has_code)
    
    for i, msg in enumerate(messages):
        if msg.get("role") == "assistant":
            # Use the had_error metadata if available, fallback to string checking
            has_error = msg.get("had_error", False)
            if not has_error and "had_error" not in msg:
                # Fallback for older messages without metadata
                content = msg.get("content", "")
                has_error = "ERROR:" in content or "<output>\nERROR:" in content
            
            # Check if this message has code execution (not just reasoning)
            has_code = msg.get("has_code", False)
            if not has_code and "has_code" not in msg:
                # Fallback check for code output
                content = msg.get("content", "")
                has_code = "<output>" in content and "</output>" in content
            
            assistant_sequences.append((i, has_error, has_code))
    
    # Find error sequences that are followed by TWO consecutive successes with code
    sequences_to_collapse: List[Tuple[int, int]] = []
    i = 0
    while i < len(assistant_sequences):
        idx, has_error, has_code = assistant_sequences[i]
        
        if has_error and has_code:
            # Start of potential error sequence
            error_start = idx
            j = i + 1
            
            # Find the end of error sequence (look for N consecutive successes)
            while j < len(assistant_sequences):
                next_idx, next_has_error, next_has_code = assistant_sequences[j]
                
                if not next_has_error and next_has_code:
                    # Found first success with code after errors
                    # Check if there are enough consecutive successes
                    consecutive_successes = 1
                    k = j + 1
                    while k < len(assistant_sequences) and consecutive_successes < consecutive_successes_required:
                        k_idx, k_has_error, k_has_code = assistant_sequences[k]
                        if not k_has_error and k_has_code:
                            consecutive_successes += 1
                            k += 1
                        else:
                            break
                    
                    if consecutive_successes >= consecutive_successes_required:
                        # Found enough consecutive successes! Collapse up to first success
                        sequences_to_collapse.append((error_start, next_idx))
                        i = k - 1  # Continue from last success checked
                        break
                    # Not enough consecutive successes yet, keep the errors for now
                    i = j
                    break
                elif next_has_error:
                    # Still in error sequence, continue
                    j += 1
                else:
                    # Success but no code (just reasoning), skip it
                    j += 1
            else:
                # No sufficient consecutive successes found after errors
                i = j if j > i else i + 1
        else:
            i += 1
    
    # Track total collapsed
    total_collapsed = 0
    
    # Collapse sequences in reverse order to preserve indices
    for error_start_idx, success_idx in reversed(sequences_to_collapse):
        num_collapsed = success_idx - error_start_idx
        if verbose and num_collapsed > 0:
            # Extract error type from first error message
            error_content = messages[error_start_idx].get("content", "")
            error_match = re.search(r'ERROR:\s*(\w+)', error_content)
            error_type = error_match.group(1) if error_match else "Unknown"
            print(f"  → Collapsing {num_collapsed} error attempts ({error_type}) into successful resolution")
        
        collapse_single_sequence(messages, error_start_idx, success_idx)
        total_collapsed += num_collapsed
    
    return total_collapsed


def collapse_single_sequence(messages: List[Dict[str, str]], error_start_idx: int, success_idx: int) -> None:
    """Collapse a single error-to-success sequence.
    
    Args:
        messages: List of conversation messages to modify in-place.
        error_start_idx: Index of the first message with an error.
        success_idx: Index of the successful resolution.
    """
    if error_start_idx >= success_idx or error_start_idx < 0:
        return
    
    # Extract initial reasoning from the first error attempt
    initial_content = messages[error_start_idx].get("content", "")
    initial_reasoning = extract_reasoning(initial_content)
    
    # Get the successful resolution content
    success_content = messages[success_idx].get("content", "")
    
    # Combine: initial reasoning + successful resolution
    # But only include reasoning if it's substantial
    if initial_reasoning and len(initial_reasoning) > 20:
        collapsed_content = initial_reasoning
        if not initial_reasoning.endswith("\n"):
            collapsed_content += "\n\n"
        # Extract just the code and output from success, not its reasoning
        success_code_match = re.search(r'(```[a-z]*\n.*?\n```.*?<output>.*?</output>)', success_content, re.DOTALL)
        if success_code_match:
            collapsed_content += success_code_match.group(1)
        else:
            collapsed_content += success_content
    else:
        # No substantial initial reasoning, just use the success content
        collapsed_content = success_content
    
    # Replace the error message with collapsed version
    messages[error_start_idx] = {
        "role": "assistant",
        "content": collapsed_content
    }
    
    # Remove intermediate messages
    del messages[error_start_idx + 1:success_idx + 1]
