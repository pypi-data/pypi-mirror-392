import time
import asyncio
import functools
import openai

def use_fall_back_on_fail(func):
    """
    A decorator that retries the function execution with an exponential backoff
    and falls back to a predefined model if an exception occurs.
    """
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        max_retries = 3  # Maximum number of retries
        base_delay = 2  # Initial delay in seconds
        attempt = 0
        
        while attempt <= max_retries:
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                print(f"Error in {func.__name__}: {e}")
                attempt += 1
                
                # Check if a fallback model is available
                if self.model in self.fallback_mapping:
                    fallback_model = self.fallback_mapping[self.model]
                    print(f"Switching model from {self.model} to {fallback_model}")
                    self.model = fallback_model
                    
                    # Dynamically reinitialize the client based on model type
                    self.initialize_client()
                else:
                    print("No fallback model available. Retrying with the same model.")
                
                # Apply exponential backoff
                delay = base_delay * (2 ** (attempt - 1))
                print(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        raise RuntimeError(f"Function {func.__name__} failed after {max_retries} attempts")
    
    return wrapper
