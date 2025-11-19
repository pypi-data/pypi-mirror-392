import json
import os
from typing import Union, List, Dict, Any
import logging
from collections import defaultdict
import re
from gpt.xml_validator import validate_xml

logger = logging.getLogger(__name__)

class PromptLoader:
    def load_prompt(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    def load_scheme(self, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f'error when loading prompt schema {path}, {e}')
            raise

    def _is_inclusion_allowed(self, prompt_path: str) -> bool:
        """
        Check if a prompt inclusion is allowed based on agent_config settings.
        
        Args:
            prompt_path: The path specified in the {prompt:path} placeholder
            
        Returns:
            bool: True if the inclusion is allowed, False otherwise
        """
        try:
            from agent.agent_config import is_inclusion_enabled, ENABLE_PROMPT_INCLUSIONS
            
            # If global inclusions are disabled, block everything
            if not ENABLE_PROMPT_INCLUSIONS:
                logger.info(f"Prompt inclusion globally disabled, skipping: {prompt_path}")
                return False
            
            # Extract component name from path for checking
            # Handle different path formats: "component.md", "dir/component.md", etc.
            component_name = os.path.splitext(os.path.basename(prompt_path))[0]
            
            # Check if this specific component is enabled
            if is_inclusion_enabled(component_name):
                logger.debug(f"Prompt inclusion allowed for: {component_name}")
                return True
            else:
                logger.info(f"Prompt inclusion disabled for: {component_name} (path: {prompt_path})")
                return False
                
        except ImportError:
            # If agent_config is not available, allow all inclusions (backward compatibility)
            logger.warning("agent_config not available, allowing all prompt inclusions")
            return True
        except Exception as e:
            # If there's any error checking config, log it but allow inclusion (fail-safe)
            logger.warning(f"Error checking inclusion config for {prompt_path}: {e}, allowing inclusion")
            return True

    def _resolve_prompt_includes(self, content: str, visited_paths: set = None, base_path: str = None) -> str:
        """
        Recursively resolve {prompt:path} placeholders in prompt content.
        
        Args:
            content: The prompt content that may contain {prompt:path} placeholders
            visited_paths: Set of already visited paths to prevent circular references
            base_path: Base directory path for resolving relative includes
            
        Returns:
            Content with all {prompt:path} placeholders resolved
        """
        if visited_paths is None:
            visited_paths = set()
            
        # Find all {prompt:path} patterns
        prompt_pattern = r'\{prompt:([^}]+)\}'
        matches = re.findall(prompt_pattern, content)
        
        for prompt_path in matches:
            # Prevent circular references
            if prompt_path in visited_paths:
                logger.warning(f"Circular reference detected for prompt path: {prompt_path}")
                continue
            
            # Check if this inclusion is allowed by agent_config
            if not self._is_inclusion_allowed(prompt_path):
                # Replace with empty string or comment to indicate disabled inclusion
                placeholder = f"{{prompt:{prompt_path}}}"
                disabled_comment = f"<!-- Prompt inclusion disabled: {prompt_path} -->"
                content = content.replace(placeholder, disabled_comment)
                logger.info(f"Replaced disabled inclusion {prompt_path} with comment")
                continue
                
            visited_paths.add(prompt_path)
            original_prompt_path = prompt_path  # Preserve original for visited_paths removal
            
            try:
                # Determine the full path for the included file
                full_path = self._resolve_include_path(prompt_path, base_path)
                
                # Load the referenced prompt - handle both directory and file paths
                if not prompt_path.endswith(".md") and not prompt_path.endswith(".json"):
                    # It's a directory path - load all prompts from it
                    included_prompts = self.load(full_path)
                    
                    # If it's a Prompts object, get the appropriate content
                    if isinstance(included_prompts, Prompts):
                        # For included prompts, we'll concatenate sys and user content
                        included_content = ""
                        if included_prompts.sys:
                            included_content += included_prompts.sys + "\n\n"
                        if included_prompts.user:
                            included_content += included_prompts.user
                    else:
                        # If it's a string (single file), use it directly
                        included_content = included_prompts
                else:
                    # It's a file path - load it directly
                    if full_path.endswith(".json"):
                        included_content = json.dumps(self.load_scheme(full_path), indent=2)
                    else:
                        included_content = self.load_prompt(full_path)
                
                # Recursively resolve any includes in the included content
                # Pass the directory of the included file as the new base_path
                include_base_path = os.path.dirname(full_path) if os.path.isfile(full_path) else full_path
                included_content = self._resolve_prompt_includes(included_content, visited_paths.copy(), include_base_path)
                
                # Replace the placeholder with the included content
                placeholder = f"{{prompt:{original_prompt_path}}}"
                content = content.replace(placeholder, included_content)
                
                logger.info(f"Successfully included prompt from: {original_prompt_path}")
                
            except Exception as e:
                logger.error(f"Failed to include prompt from {original_prompt_path}: {e}")
                # Keep the placeholder if inclusion fails
                continue
            finally:
                # Always remove from visited_paths to allow reuse in different branches
                visited_paths.discard(original_prompt_path)
        
        return content

    def _resolve_include_path(self, prompt_path: str, base_path: str = None) -> str:
        """
        Resolve the full path for an included prompt file.
        
        Args:
            prompt_path: The path specified in the {prompt:path} placeholder
            base_path: The base directory to resolve relative paths from
            
        Returns:
            The full resolved path
        """
        # If it's an absolute path, use it as-is
        if os.path.isabs(prompt_path):
            return prompt_path
            
        # If we have a base_path (from a file being processed), try relative to that first
        if base_path:
            relative_path = os.path.join(base_path, prompt_path)
            if os.path.exists(relative_path):
                return relative_path
        
        # Try relative to local prompts/ directory (default behavior)
        if not prompt_path.startswith("prompts"):
            local_path = os.path.join("prompts", prompt_path)
            if os.path.exists(local_path):
                return local_path

        # If the path already starts with prompts/, use it as-is
        if prompt_path.startswith("prompts"):
            return prompt_path
            
        # Return the original path (will likely fail, but let the caller handle it)
        return prompt_path

    def load(self, path: str, schema_gen_source: dict = None, skip_xml_validation: bool = False) -> Union['Prompts', str]:
        """Load a prompt collection from a directory."""
        loaded_prompts = {}
        # If path does not end with extension it is a directory
        if not path.endswith(".json") and not path.endswith(".md"):
            # Ensure path starts with 'prompts/' in this repository
            if not path.startswith("prompts"):
                path = os.path.join("prompts", path)

            if not os.path.exists(path):
                raise FileNotFoundError(f"Path {path} does not exist")

            # Go recursively through subdirs in any depth
            for root, dirs, files in os.walk(path):
                for file in files:
                    filepath = os.path.join(root, file)
                    logger.debug(f"Loading prompts from {filepath}")

                    # Check whether the path is correct
                    filename_no_ext  = os.path.splitext(file)[0]
                    if not filename_no_ext.endswith('user') and not filename_no_ext.endswith('sys') and not filename_no_ext.endswith('schema'):
                        logger.info(
                            f"Skipping file {filepath} because it does not end with 'user' or 'sys'")
                        continue

                    # Just save the last 2 parts of the path and no extension
                    underscore_path = "_".join(
                        filepath.split(os.path.sep)[-2:]).split(".")[0]

                    # If it was not in a nested 'reason'/'parse' directory
                    # Quick fix
                    splitpath = underscore_path.split("_")
                    if splitpath[0] not in ["reason", "parse"]:
                        underscore_path = f"reason_{splitpath[1]}"

                    if file.endswith(".json"):
                        loaded_prompts[underscore_path] = self.load_scheme(filepath)
                    elif file.endswith(".md"):
                        content = self.load_prompt(filepath)
                        # Resolve any prompt includes in the content
                        # Use the original path (the directory being loaded) as base_path
                        content = self._resolve_prompt_includes(content, base_path=path)
                        loaded_prompts[underscore_path] = content

                        # Validate the XML
                        if not skip_xml_validation:
                            validate_xml(content)

            logger.debug(
                f"Loaded {len(loaded_prompts.keys())} prompts from {path}"
            )

            # If we want to parse but no schema is provided throw an error
            if 'parse_sys' in loaded_prompts and not 'parse_schema' in loaded_prompts:
                if not schema_gen_source:
                    raise ValueError("Either a schema.json must be in the prompt path or a schema_gen_source must be provided.")
                
            if schema_gen_source:
                if 'parse_schema' in loaded_prompts:
                    logger.warning("Both schema.json and schema_gen_source are provided. schema.json path will be ignored and be a dynamically generated schema will be used.")
                loaded_prompts['parse_schema'] = generate_schema(schema_gen_source)
                
                    

            # Unpack dict into object
            return Prompts(**loaded_prompts)

        # If path is a file
        else:
            logger.info(f"Loading direct str prompts from {path}")
            if path.endswith(".json"):
                return self.load_scheme(path)
            elif path.endswith(".md"):
                content = self.load_prompt(path)
                # Resolve any prompt includes in the content
                content = self._resolve_prompt_includes(content, base_path=os.path.dirname(path))
                return content


class MissingKeyDict(dict):
    """A dictionary that returns the placeholder name itself if a key is missing."""

    def __missing__(self, key):
        # Handle prompt: patterns specially - they should be preserved for later resolution
        if key.startswith('prompt:') or key == 'prompt':
            return f"{{{key}}}"
        if key.strip() not in ['base_info_prompt', 'previous_response', 'role, field']:            
            raise ValueError(f"Missing key {key} in the prompt formatting.")
        return f"{{{key}}}"  # Keeps the placeholder as {key}

try:
    base_info_prompt = PromptLoader().load_prompt(os.path.join("prompts", "base_info.md"))
except FileNotFoundError:
    logger.warning("Base info prompt not bundled; continuing with empty fallback.")
    base_info_prompt = ""

class Prompts:
    '''A collection of prompts that can be loaded from a directory.
    
    Either simply a sys and user prompt.
    Or for nested directories a reason_sys and reason_user prompt and a parse_sys and parse_user prompt.
    Can also include images as URLs, file paths, or base64 strings.
    '''

    def __init__(self, sys: str= None, user: str= None, reason_sys: str= None, reason_user: str= None, 
                 parse_sys: str= None, parse_user: str= None, parse_schema: dict= None, skip_sys: bool= False,
                 images: List[Dict[str, Any]] = None):
        if sys and reason_sys:
            raise ValueError('Cannot have both sys and reason_sys when loading prompts')
        if user and reason_user:
            raise ValueError("Cannot have both user and reason_user when loading prompts")

        self.sys:str = sys
        self.user: str = user
        if reason_sys:
            self.sys: str = reason_sys
        if reason_user:
            self.user: str = reason_user
        self.parse_sys: str = parse_sys
        self.parse_user: str = parse_user
        self.parse_schema: dict = parse_schema
        self.skip_sys: bool = skip_sys
        self.images: List[Dict[str, Any]] = images or []

    @staticmethod
    def from_path(path: str, schema_gen_source: dict = None) -> Union['Prompts', str]:
        '''Load a prompt collection from a directory.'''
        return PromptLoader().load(path, schema_gen_source)
    
    def get_msg_list(self):
        '''Construct a simple message lists from the prompts on this object.'''
        function_call_schema = None
        if self.parse_schema:
            function_call_schema = self.parse_schema

        self.function_call_schema = function_call_schema
        self.msg_list = self.construct_msg_list(self.sys, self.user)

        return self.construct_msg_list(self.sys, self.user)
    
    def construct_msg_list(self, sys_msg: str, user_msg: str) -> list[dict]:
        """Given system message and user message string, constructs the messages list for OpenAI API"""
        sys = {"role": "system", "content": sys_msg}
        user = {"role": "user", "content": user_msg}
        return [sys, user]

    def add_image(self, image_url_or_base64: str, detail: str = "auto"):
        """Add an image to the prompts.
        
        Args:
            image_url_or_base64: URL, file path, or base64 string of the image
            detail: Detail level for the image processing ('auto', 'low', 'high')
        """
        self.images = self.images or []
        self.images.append({
            "url": image_url_or_base64,
            "detail": detail
        })
        return self

    def format(self, skip_xml_validation: bool = False, **kwargs) -> 'Prompts':
        '''Format the prompts with the given keyword arguments.'''
        logger.debug(f"Formatting prompts with kwargs: {kwargs.keys()}")
        
        # # Remove skip_format_msgs from kwargs (We to skip formatting the sys message if it is a system message)
        skip_parse_sys_msg_formatting = kwargs.pop('skip_parse_sys_msg_formatting', False)
        skip_xml_validation = kwargs.pop('skip_xml_validation', False)
        
        prompts_to_format = [(self.sys, 'sys'), (self.user, 'user'), (self.parse_sys, 'parse_sys'), (self.parse_user, 'parse_user')]
   

        # if we skip formatting the sys message, we only format the user and parse messages
        if skip_parse_sys_msg_formatting:
            self.skip_sys = skip_parse_sys_msg_formatting
            prompts_to_format = [(self.user, 'user'), (self.parse_user, 'parse_user')]

        # Create a prompt loader instance for resolving includes
        prompt_loader = PromptLoader()

        for str_to_format, prompt_type in prompts_to_format:
            # Might be none (for example when we don't parse)
            if not str_to_format:
                continue

            # Always format with base_info_prompt
            kwargs['base_info_prompt'] = base_info_prompt
            
            # First, resolve any prompt includes before formatting
            str_to_format = prompt_loader._resolve_prompt_includes(str_to_format, base_path="afasask/prompts")
            
            # When template keys are missing we log a warning but still format the string
            required_format_kwargs = re.findall(r'\{([^}]+)\}', str_to_format)
            for required_format_kwarg in required_format_kwargs:
                if required_format_kwarg not in kwargs:
                    if required_format_kwarg not in ['base_info_prompt', 'previous_response'] and 'prompt:' not in required_format_kwarg:
                        logger.warning(f"Keyword argument {required_format_kwarg} is missing in the prompt formatting. Prompt will be formatted without it.")

            # Format the string and keep missing keys as {key}
            formatted_str = str_to_format.format_map(MissingKeyDict(**kwargs))

            # Validate the XML
            if not skip_xml_validation:
                validate_xml(formatted_str)
            
            # Assign the formatted string back to the appropriate attribute
            if prompt_type == 'sys':
                self.sys = formatted_str
            elif prompt_type == 'user':
                self.user = formatted_str
            elif prompt_type == 'parse_sys':
                self.parse_sys = formatted_str
            elif prompt_type == 'parse_user':
                self.parse_user = formatted_str
        return self

    def print(self):
        '''Print the prompts to the console. Useful for asking GPT to design a new collection of prompts for some task. You can print these and give them as example.'''
        print('###################')
        print('Reason sys:')
        print(self.sys)
        print('Reason user:')
        print(self.user)
        print('Parse sys:')
        print(self.parse_sys)
        print('Parse user:')
        print(self.parse_user)
        print('Parse schema:')
        print(self.parse_schema)
