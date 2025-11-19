"""Function Wrapper for FastStreamingAgent

This module provides generic function wrapping capabilities that capture and 
format function outputs in a user-friendly way. It handles both sync and async 
functions and formats different result types appropriately.
"""

from typing import Dict, Any, Callable, Awaitable, Union
from .custom_print import PrintCapture
from .agent_config import FunctionConfig


def wrap_configured_functions(
    execution_globals: Dict[str, Any], 
    function_configs: list[FunctionConfig],
    print_capture: PrintCapture,
    special_functions: list[str] = None
) -> None:
    """
    Wrap all configured functions with generic output formatting wrappers.
    
    This replaces the ugly hardcoded function-specific checks with a clean,
    generic system that can wrap ANY function and print its output.
    
    Args:
        execution_globals: Dictionary of functions available for execution
        function_configs: List of function configurations from agent config
        print_capture: Print capture instance for custom printing
        special_functions: List of function names to skip (handled separately)
    """
    if special_functions is None:
        special_functions = ["stop", "task", "todo_write"]
    
    for func_config in function_configs:
        func_name = func_config.name
        
        # Skip special functions that are registered later
        if func_name in special_functions:
            continue
        
        # Only wrap if the function exists in execution_globals
        if func_name in execution_globals:
            orig_func = execution_globals[func_name]
            
            # Create wrapper based on whether function is async
            if func_config.is_async:
                # Create async wrapper
                def make_async_wrapper(original_func: Callable, name: str) -> Callable:
                    async def async_wrapper(*args, **kwargs):
                        """Generic async wrapper that prints function results."""
                        result = await original_func(*args, **kwargs)
                        
                        # Format and print the result
                        _format_and_print_result(result, name, print_capture)
                        
                        return result
                    return async_wrapper
                
                # Replace with wrapped version
                execution_globals[func_name] = make_async_wrapper(orig_func, func_name)
            else:
                # Create sync wrapper
                def make_sync_wrapper(original_func: Callable, name: str) -> Callable:
                    def sync_wrapper(*args, **kwargs):
                        """Generic sync wrapper that prints function results."""
                        result = original_func(*args, **kwargs)
                        
                        # Format and print the result
                        _format_and_print_result(result, name, print_capture)
                        
                        return result
                    return sync_wrapper
                
                # Replace with wrapped version
                execution_globals[func_name] = make_sync_wrapper(orig_func, func_name)


def _format_and_print_result(result: Any, function_name: str, print_capture: PrintCapture) -> None:
    """Format and print function result in a user-friendly way.
    
    Args:
        result: The function result to format and print
        function_name: Name of the function that returned the result
        print_capture: Print capture instance for custom printing
    """
    if result is not None:
        print_capture.custom_print(f"\n{function_name} returned:")
        
        # Handle different result types
        if isinstance(result, (list, tuple)):
            if result:
                for item in result[:10]:  # Limit output
                    if isinstance(item, dict):
                        # Pretty print dict items
                        print_capture.custom_print(f"  • {str(item)[:200]}")
                    else:
                        print_capture.custom_print(f"  • {str(item)[:200]}")
                if len(result) > 10:
                    print_capture.custom_print(f"  ... and {len(result) - 10} more items")
            else:
                print_capture.custom_print("  (empty result)")
        elif isinstance(result, dict):
            # Pretty print dict
            for key, value in list(result.items())[:10]:
                print_capture.custom_print(f"  {key}: {str(value)[:200]}")
            if len(result) > 10:
                print_capture.custom_print(f"  ... and {len(result) - 10} more items")
        else:
            # Print string representation
            result_str = str(result)
            if len(result_str) > 500:
                print_capture.custom_print(f"  {result_str[:500]}...")
            else:
                print_capture.custom_print(f"  {result_str}")
