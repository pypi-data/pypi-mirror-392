"""Code Apply Function for FastStreamingAgent.

This module provides the code_apply function that uses Gemini 2.5 Flash-Lite
to apply edits to code files based on natural language descriptions.
"""

import re
from pathlib import Path
from typing import Optional
import traceback

from ..gpt.gpt import GPT
from .code_storage import get_code_filepath
from libs.lib_utils.src.lib_utils.code_ops.aexec import async_execute_catch_logs_errors


async def code_apply(filepath: str, edit_explanation: str, edit_markers: str = "") -> str:
    """Apply edits to a code file using Gemini 2.5 Flash-Lite, update the file, and execute it.

    This function takes a code file and applies edits based on natural language
    descriptions and optional code markers. It uses Gemini 2.5 Flash-Lite to
    understand the edit requirements, writes the updated code back to the file,
    executes it, and returns both the updated code and execution output.

    Args:
        filepath: Path to the code file to edit, or 6-character code ID
        edit_explanation: Natural language description of what to change
        edit_markers: Optional code snippet showing the desired change with markers
                     like "# CHANGE THIS" or "// TODO: fix this"

    Returns:
        String containing the updated code followed by execution output
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If the file type is not supported or edit cannot be applied
        Exception: For any other errors during processing
        
    Example:
        >>> # Simple edit
        >>> updated_code = await code_apply(
        ...     "temp_file.py",
        ...     "Change the function name from 'calculate' to 'compute_result'"
        ... )
        
        >>> # Edit with markers
        >>> updated_code = await code_apply(
        ...     "script.js", 
        ...     "Fix the bug in the validation function",
        ...     "// TODO: fix validation bug here"
        ... )
    """
    # Try to resolve as code ID first if it looks like one (6 chars, no path separators)
    if '/' not in filepath and '\\' not in filepath and len(filepath) == 6:
        try:
            filepath = get_code_filepath(filepath)
        except (ValueError, KeyError):
            # Not tracked in storage, try filesystem directly
            potential_path = Path("/tmp/faststream_code") / f"{filepath}.py"
            if potential_path.exists():
                filepath = str(potential_path)

    # Validate file path
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Read original file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
    except Exception as e:
        raise Exception(f"Failed to read file {filepath}: {traceback.format_exc()}")
    
    # Detect file type from extension
    file_extension = file_path.suffix.lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    detected_language = language_map.get(file_extension, 'text')
    
    # Create strict system prompt that forces only code block output
    system_prompt = f"""You are a precise code editing assistant. Your ONLY job is to apply the requested edit to the provided code and return the COMPLETE updated file.

CRITICAL REQUIREMENTS:
1. You MUST return ONLY a markdown code block containing the complete updated file
2. You MUST preserve ALL formatting, comments, and whitespace in non-edited sections
3. You MUST apply ONLY the requested edit - do not make additional changes
4. You MUST NOT provide explanations, summaries, or any text outside the code block
5. You MUST start your response immediately with ```{detected_language} and end with ```

OUTPUT FORMAT (this is the ONLY acceptable format):
```{detected_language}
[complete updated file content here]
```

Do NOT include anything else in your response - no explanations, no comments, no additional text."""

    # Create user prompt with original code and edit instructions
    user_prompt = f"""ORIGINAL FILE ({filepath}):
```{detected_language}
{original_code}
```

EDIT INSTRUCTION: {edit_explanation}"""

    # Add edit markers if provided
    if edit_markers and edit_markers.strip():
        user_prompt += f"""

EDIT MARKERS/CONTEXT: {edit_markers.strip()}"""

    user_prompt += f"""

Apply the edit and return the COMPLETE updated file in a ```{detected_language} code block. Remember: ONLY return the code block, nothing else."""

    # Call Gemini 2.5 Flash-Lite via GPT class
    try:
        gpt = GPT(
            sys_msg=system_prompt,
            user_msg=user_prompt,
            model="gemini-2.5-flash-lite"
        )
        
        response, _, _ = await gpt.run(silent=True)
        
        if not response:
            raise ValueError("Empty response from Gemini model")
            
    except Exception as e:
        raise Exception(f"Failed to get response from Gemini model: {traceback.format_exc()}")
    
    # Parse the response to extract code block
    try:
        updated_code = _extract_code_block(response, detected_language)
        
        # Basic validation - ensure we got some content
        if not updated_code or not updated_code.strip():
            raise ValueError("Model returned empty code content")
            
        # Verify the code looks reasonable (not just error messages)
        if "error" in updated_code.lower() and len(updated_code) < 100:
            raise ValueError(f"Model appears to have returned an error message instead of code: {updated_code[:200]}")

        # Write updated code back to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_code)
        except Exception:
            raise Exception(f"Failed to write updated code to file {file_path}: {traceback.format_exc()}")

        # Execute the updated code and capture output
        try:
            had_error, updated_globals, logs = await async_execute_catch_logs_errors(
                updated_code,
                {},
                timeout=30.0
            )

            execution_output = logs if logs else "(no output)"

            # Return both the updated code and execution output
            return f"{updated_code}\n\n# Execution output:\n{execution_output}"

        except Exception:
            raise Exception(f"Failed to execute updated code: {traceback.format_exc()}")

    except Exception as e:
        raise Exception(f"Failed to parse model response: {traceback.format_exc()}")


def _extract_code_block(response: str, expected_language: str) -> str:
    """Extract code block from model response.
    
    Args:
        response: Raw response from the model
        expected_language: Expected programming language
        
    Returns:
        Extracted code content
        
    Raises:
        ValueError: If no valid code block is found
    """
    # Pattern to match code blocks with optional language specification
    patterns = [
        rf'```{expected_language}\s*\n(.*?)\n```',  # Exact language match
        rf'```\w*\s*\n(.*?)\n```',  # Any language or no language
        r'```\s*\n(.*?)\n```',  # No language specified
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            # Return the first (and hopefully only) match
            code_content = matches[0].strip()
            if code_content:
                return code_content
    
    # If no code block found, check if the entire response looks like code
    # This handles cases where the model ignores the code block formatting
    response_stripped = response.strip()
    if response_stripped and not any(word in response_stripped.lower() for word in ['error', 'sorry', 'cannot', "i can't", 'unable']):
        # Response might be raw code without code block markers
        return response_stripped
    
    raise ValueError(f"No valid code block found in response. Response: {response[:500]}...")
