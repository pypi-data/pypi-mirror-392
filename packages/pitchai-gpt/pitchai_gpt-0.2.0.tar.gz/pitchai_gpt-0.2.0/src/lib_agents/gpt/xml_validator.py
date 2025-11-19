import re
from xml.etree import ElementTree as ET
from typing import Dict, Set, List, Tuple, Optional
import io
import linecache
from contextlib import contextmanager

# -------------  1. define the whitelist  -----------------
ALLOWED_CHILDREN: Dict[str, Set[str]] = {
    "prompt": {
        "user_question", "globals", "searchresults",
        "examplecodesnippets", "companyknowledgebase",
        "currenttask", "previouscode", "previouslogs",
        "global_goal", "instruction", "instructions",
    },
    "searchresults": {"search"},
    "examplecodesnippets": {"codesnippet"},
    "companyknowledgebase": {"knowledge"},
    # leaf tags ↓ are allowed *no* children:
    "user_question": set(),
    "globals":       set(),
    "search":        set(),
    "codesnippet":   set(),
    "knowledge":     set(),
    "currenttask":   set(),
    "previouscode":  set(),
    "previouslogs":  set(),
    "global_goal":   set(),
    "instruction":   set(),
    "instructions":  set(),
}

# Define maximum occurrences for specific tags
MAX_OCCURRENCES: Dict[str, int] = {
    "currenttask": 1,
    "global_goal": 1,
    "instruction": 2,
    "instructions": 2,  # Added plural form with same limit
    "searchresults": 1,
    "examplecodesnippets": 1,
    "companyknowledgebase": 1,
}

# All known tags that we care about
ALL_KNOWN_TAGS = set(ALLOWED_CHILDREN.keys()) | {
    tag for tags in ALLOWED_CHILDREN.values() for tag in tags
}

# Root tags that indicate proper XML structure we should validate
ROOT_TAGS = {"prompt"}

class XMLValidationError(ValueError):
    """Custom exception for XML validation errors with detailed information."""
    def __init__(self, error_type: str, message: str, details: Optional[Dict] = None, 
                 line_number: Optional[int] = None, context: Optional[str] = None):
        self.error_type = error_type
        self.details = details or {}
        self.line_number = line_number
        self.context = context
        
        # Build the full message
        full_message = f"[{error_type}] {message}"
        
        # Add line number if available
        if line_number is not None:
            full_message += f" at line {line_number}"
            
        # Add details if available
        if details:
            detail_str = "; ".join(f"{k}={v}" for k, v in details.items() 
                                  if k not in ["context"])
            full_message += f" ({detail_str})"
            
        # Add context if available
        if context:
            full_message += f"\n\nContext:\n{context}"
            
        super().__init__(full_message)

# -------------  2. helper utils  -------------------------
# More specific regex to match our root XML tags
ROOT_TAG_RE = re.compile(r"<(" + "|".join(re.escape(tag) for tag in ROOT_TAGS) + r")[\s>]")

# Regex to match opening and closing tags for our known tags
OPENING_TAG_RE = re.compile(r"<(" + "|".join(re.escape(tag) for tag in ALL_KNOWN_TAGS) + r")[\s>]")
CLOSING_TAG_RE = re.compile(r"</(" + "|".join(re.escape(tag) for tag in ALL_KNOWN_TAGS) + r")>")

def _has_root_xml_tag(text: str) -> bool:
    """Check if the text contains any of our root XML tags, indicating proper XML structure."""
    return bool(ROOT_TAG_RE.search(text))

def _has_proper_xml_structure(text: str) -> bool:
    """
    Check if the text has proper XML structure with our tags.
    This is more strict than just checking for the presence of root tags.
    """
    # Must have a root tag
    if not _has_root_xml_tag(text):
        return False
        
    # Check if we have balanced tags
    if not _is_balanced_xml(text):
        return False
        
    # Check if root tag is properly closed
    root_match = ROOT_TAG_RE.search(text)
    if root_match:
        root_tag = root_match.group(1)
        # Check if we have a proper closing tag for the root
        closing_pattern = f"</{root_tag}>"
        if not re.search(closing_pattern, text):
            return False
            
    return True

def _local(tag: str) -> str:
    """Strip namespace: '{urn:xyz}foo' -> 'foo'."""
    return tag.split("}", 1)[-1]

def _xpath(el: ET.Element) -> str:
    """Cheap XPath-ish breadcrumb for error messages."""
    parts = []
    while el is not None and el.tag != "__root":
        parts.append(_local(el.tag))
        # ElementTree doesn't have getparent(), so we can't navigate up
        # Just return what we have so far
        break
    return "/" + "/".join(reversed(parts))

def _get_line_number_for_tag(xml_text: str, tag_name: str, occurrence: int = 1) -> Optional[int]:
    """Find the line number for a specific tag occurrence."""
    pattern = f"<{tag_name}[\\s>]"
    lines = xml_text.splitlines()
    count = 0
    
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            count += 1
            if count == occurrence:
                return i + 1  # 1-based line numbering
    
    return None

def _get_context_around_line(text: str, line_number: int, context_lines: int = 5) -> str:
    """Get context lines around the specified line number."""
    if line_number is None:
        return ""
        
    lines = text.splitlines()
    if not lines or line_number <= 0 or line_number > len(lines):
        return ""
    
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    
    result = []
    for i in range(start, end):
        line_prefix = ">> " if i == line_number - 1 else "   "
        result.append(f"{i+1:4d}{line_prefix}{lines[i]}")
    
    return "\n".join(result)

def _find_tag_in_text(xml_text: str, tag_name: str) -> Tuple[Optional[int], Optional[str]]:
    """Find a tag in text and return its line number and context."""
    line_number = _get_line_number_for_tag(xml_text, tag_name)
    if line_number:
        context = _get_context_around_line(xml_text, line_number)
        return line_number, context
    return None, None

def _is_balanced_xml(text: str) -> bool:
    """Check if the XML structure is balanced by counting opening and closing tags."""
    # Quick check for balanced tags for our specific tags
    for tag in ALL_KNOWN_TAGS:
        opening_count = len(re.findall(f"<{tag}[\\s>]", text))
        closing_count = len(re.findall(f"</{tag}>", text))
        if opening_count != closing_count:
            return False
    return True

def _is_fragment_with_our_tags(text: str) -> bool:
    """
    Check if the text is a fragment that contains our tags but not in proper XML structure.
    This helps identify content that shouldn't be validated.
    """
    # Check if we have any of our tags
    has_opening_tags = bool(OPENING_TAG_RE.search(text))
    
    # If we have tags but not proper XML structure, it's a fragment
    if has_opening_tags and not _has_proper_xml_structure(text):
        return True
        
    return False

def _check_for_malformed_xml(text: str) -> Optional[XMLValidationError]:
    """
    Check if the XML is malformed and return an error if it is.
    Returns None if the XML is well-formed.
    """
    # Check if we have a root tag
    if not _has_root_xml_tag(text):
        return None  # Not our XML, so not malformed
        
    # Check for unbalanced tags
    for tag in ALL_KNOWN_TAGS:
        opening_count = len(re.findall(f"<{tag}[\\s>]", text))
        closing_count = len(re.findall(f"</{tag}>", text))
        
        if opening_count != closing_count:
            # Find the line number of the problematic tag
            line_number = None
            context = None
            
            if opening_count > closing_count:
                # Missing closing tag
                line_number = _get_line_number_for_tag(text, tag, closing_count + 1)
                context = _get_context_around_line(text, line_number) if line_number else None
                return XMLValidationError(
                    "MALFORMED_XML",
                    f"Missing closing tag for <{tag}>",
                    {"tag": tag, "opening_count": opening_count, "closing_count": closing_count},
                    line_number,
                    context
                )
            else:
                # Extra closing tag or missing opening tag
                # Try to find the line with the extra closing tag
                pattern = f"</{tag}>"
                lines = text.splitlines()
                closing_tags_found = 0
                for i, line in enumerate(lines):
                    closing_tags_in_line = len(re.findall(pattern, line))
                    closing_tags_found += closing_tags_in_line
                    if closing_tags_found > opening_count:
                        line_number = i + 1
                        context = _get_context_around_line(text, line_number)
                        return XMLValidationError(
                            "MALFORMED_XML",
                            f"Extra closing tag for <{tag}> or missing opening tag",
                            {"tag": tag, "opening_count": opening_count, "closing_count": closing_count},
                            line_number,
                            context
                        )
    
    # Try a simple parse test
    try:
        wrapped = f"<__root>{text}</__root>"
        ET.fromstring(wrapped)
    except ET.ParseError as e:
        error_msg = str(e)
        line_col_match = re.search(r"line (\d+), column (\d+)", error_msg)
        
        line_number = None
        if line_col_match:
            try:
                # Adjust for the added root tag (subtract 1)
                line_number = max(1, int(line_col_match.group(1)) - 1)
            except (ValueError, IndexError):
                pass
                
        context = _get_context_around_line(text, line_number) if line_number else None
        
        return XMLValidationError(
            "MALFORMED_XML", 
            f"Malformed XML fragment in string: {e}",
            {"parse_error": str(e)},
            line_number,
            context
        )
    
    return None

def _pre_validate_xml(text: str) -> Tuple[bool, Optional[XMLValidationError]]:
    """
    Pre-validate XML before parsing to catch common issues.
    Returns (is_valid, error) tuple.
    """
    # Check if we have proper XML structure with our root tags
    if not _has_root_xml_tag(text):
        return False, None  # Not our XML, but not an error
        
    # Check if it's a fragment with our tags but not proper XML structure
    if _is_fragment_with_our_tags(text):
        return False, None  # Fragment, not proper XML, but not an error
    
    # Check for malformed XML
    error = _check_for_malformed_xml(text)
    if error:
        return False, error
    
    return True, None

def _check_tag_occurrences(text: str) -> Optional[XMLValidationError]:
    """
    Check if any tag exceeds its maximum allowed occurrences.
    Returns an error if any tag exceeds its limit, None otherwise.
    """
    # Count occurrences of limited tags
    tag_counts = {tag: 0 for tag in MAX_OCCURRENCES}
    tag_line_numbers = {tag: [] for tag in MAX_OCCURRENCES}
    
    # Count all occurrences of limited tags
    for tag in MAX_OCCURRENCES:
        # Count opening tags
        pattern = f"<{tag}[\\s>]"
        matches = list(re.finditer(pattern, text))
        tag_counts[tag] = len(matches)
        
        # Find line numbers for each occurrence
        for i, match in enumerate(matches):
            # Get line number by counting newlines before the match
            line_number = text[:match.start()].count('\n') + 1
            tag_line_numbers[tag].append(line_number)
    
    # Check if any tag exceeds its maximum allowed occurrences
    for tag, count in tag_counts.items():
        if count > MAX_OCCURRENCES[tag]:
            # Find the first occurrence beyond the limit
            line_number = None
            if len(tag_line_numbers[tag]) >= MAX_OCCURRENCES[tag] + 1:
                line_number = tag_line_numbers[tag][MAX_OCCURRENCES[tag]]
                
            context = _get_context_around_line(text, line_number) if line_number else None
            
            return XMLValidationError(
                "EXCEEDED_MAX_OCCURRENCES",
                f"Tag <{tag}> appears {count} times, but is limited to {MAX_OCCURRENCES[tag]} occurrences",
                {"tag": tag, "count": count, "limit": MAX_OCCURRENCES[tag]},
                line_number,
                context
            )
    
    return None

# -------------  3. the validator  -------------------------
def validate_xml(text: str,
                 allowed: Dict[str, Set[str]] = ALLOWED_CHILDREN,
                 max_occurrences: Dict[str, int] = MAX_OCCURRENCES
                 ) -> None:
    """
    If any of our known XML tags are found in `text`, ensure:
    1. Every element's direct children are whitelisted
    2. Limited tags don't exceed their maximum allowed occurrences
    
    Raises XMLValidationError with detailed information on the first violation.
    """
    # Check for malformed XML first if we have our root tag
    if _has_root_xml_tag(text):
        error = _check_for_malformed_xml(text)
        if error:
            raise error
    
    # Check if any tag exceeds its maximum allowed occurrences
    # This check runs regardless of whether it's a fragment or not
    error = _check_tag_occurrences(text)
    if error:
        raise error
    
    # Check if it's a fragment with our tags but not proper XML structure
    if _is_fragment_with_our_tags(text):
        return  # Fragment, not proper XML, skip further validation
    
    # Pre-validate to catch common issues before full parsing
    is_valid, error = _pre_validate_xml(text)
    
    if not is_valid:
        if error:
            # We found an error, raise it
            raise error
        else:
            # Not our XML, just return
            return

    # Store original text for error reporting
    original_text = text
    
    # At this point, we know the XML is well-formed and contains our tags
    # Parse it for validation
    root = ET.fromstring(f"<__root>{text}</__root>")

    # Second pass: depth-first walk to validate parent-child relationships
    stack = [root]
    while stack:
        node = stack.pop()
        parent_name = _local(node.tag)
        if parent_name == "__root":
            # synthetic root: allow anything at top level
            allowed_children = set(allowed) | {"__root"}
        else:
            allowed_children = allowed.get(parent_name)
            if allowed_children is None:
                # Skip validation for tags we don't care about
                if parent_name not in ALL_KNOWN_TAGS:
                    continue
                    
                line_number, context = _find_tag_in_text(original_text, parent_name)
                
                raise XMLValidationError(
                    "UNKNOWN_TAG",
                    f"Tag <{parent_name}> is not recognised in whitelist",
                    {"tag": parent_name},
                    line_number,
                    context
                )
        for child in node:
            child_name = _local(child.tag)
            # Skip validation for tags we don't care about
            if parent_name not in ALL_KNOWN_TAGS and child_name not in ALL_KNOWN_TAGS:
                continue
                
            if child_name not in allowed_children and parent_name in ALL_KNOWN_TAGS:
                line_number, context = _find_tag_in_text(original_text, child_name)
                
                raise XMLValidationError(
                    "INVALID_CHILD_TAG",
                    f"<{child_name}> not allowed inside <{parent_name}>",
                    {"child_tag": child_name, "parent_tag": parent_name, 
                     "allowed_children": list(allowed_children)},
                    line_number,
                    context
                )
            stack.append(child)

# -------------  4. demo  ---------------------------------
if __name__ == "__main__":
    good = """
        <prompt>
            <user_question>Hi?</user_question>
            <searchresults><search>foo</search></searchresults>
        </prompt>
    """
    bad = """
        <prompt>
            <user_question>Hi?</user_question>
            <hacker>oops</hacker>
        </prompt>
    """
    
    too_many = """
        <prompt>
            <user_question>Hi?</user_question>
            <instruction>First instruction</instruction>
            <instruction>Second instruction</instruction>
            <instruction>Third instruction</instruction>
        </prompt>
    """
    
    malformed = """
        <prompt>
            <user_question>What is the revenue for Q1?
            <searchresults><search>Revenue for Q1 was $1.2M</search></searchresults>
        </prompt>
    """
    
    # Python code with triple quotes that shouldn't be parsed as XML
    python_code = '''
    def correlate_groupby(
        grouped: pl.internals.groupby.group_by.DataFrameGroupBy,  # Polars GroupBy object
        target_spec: Dict[str, str],                             # Dictionary with target column and aggregation specification e.g. 
        *,
        max_cat: int = 20                                        # Maximum number of categories for categorical columns
    ) -> pl.DataFrame:
        # Auto-generates helper features & correlates them with the target
    ```
    
    ## Output Format
    '''
    
    # Fragment with a companyknowledgebase tag but not in proper XML structure
    fragment = """
    ## Evaluation Request
    
    Here starts the real situation. Please evaluate, formulate todo's and task description.
    
    ## Company Knowledge & Terminology
    Here are relevant company terms and definitions that might help with your analysis:
    
    <companyknowledgebase>Negative amounts are donations in the accounting system, so negative means incoming money. Positive donations are refunds. So invert with sign.
    """

    validate_xml(good)           # ✔ OK

    try:
        validate_xml(bad)        # ❌ fails - invalid child
    except Exception as e:
        print("Validation error:", e)
        print("\n" + "-" * 60 + "\n")
        
    try:
        validate_xml(too_many)   # ❌ fails - too many instruction tags
    except Exception as e:
        print("Validation error:", e)
        print("\n" + "-" * 60 + "\n")
        
    try:
        validate_xml(malformed)  # ❌ fails - malformed XML
    except Exception as e:
        print("Validation error:", e)
        print("\n" + "-" * 60 + "\n")
        
    # These should pass validation since they don't contain proper XML structure with our tags
    validate_xml(python_code)    # ✔ OK
    print("Python code validation: Passed (ignored as not relevant XML)")
    
    validate_xml(fragment)       # ✔ OK
    print("Fragment validation: Passed (ignored as not proper XML structure)")