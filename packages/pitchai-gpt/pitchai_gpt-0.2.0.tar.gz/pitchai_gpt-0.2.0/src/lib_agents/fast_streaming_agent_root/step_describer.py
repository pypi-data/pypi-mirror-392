"""
Dutch Step Describer for FastStreamingAgent
==========================================

This component generates intuitive Dutch descriptions of analysis steps,
converting technical operations into layman-friendly language for business users.

Based on patterns from:
- /afasask/pipelines/components/single_sent.py
- /afasask/instant/agent/summarizers/cell_describer.py
"""

import logging
from typing import Tuple
from ..gpt.gpt import GPT
from ..gpt.prompt_loader import Prompts

logger = logging.getLogger(__name__)


async def describe_step_in_dutch(
    original_question: str,
    step_reasoning: str,
    step_code: str,
    step_output: str,
    model: str = "gemini-2.5-flash-lite"
) -> str:
    """
    Generate an intuitive Dutch description of an analysis step.
    
    Args:
        original_question: The user's original question for context
        step_reasoning: The reasoning/thought process for this step
        step_code: The code being executed in this step
        step_output: The output from code execution
        model: Model to use for generating descriptions
        
    Returns:
        A single intuitive Dutch sentence (8-15 words) with emoji prefix, starting with "Ik"
        Example: "🔍 Ik bekijk het schema van financiele_mutaties tabel"
    """
    # Skip if no meaningful content (both reasoning and code are empty)
    if (not step_reasoning or step_reasoning.strip() == "") and (not step_code or step_code.strip() == ""):
        return "⏳ Ik bereid de volgende stap voor"

    try:
        # Load the fast step describer prompts
        prompts = Prompts.from_path("fast_step_describer").format(
            original_question=original_question,
            step_reasoning=step_reasoning if step_reasoning else "Geen expliciete redenering gegeven.",
            step_code=step_code,
            step_output=step_output if step_output else "Geen output beschikbaar."
        )
        
        # Use configured model for real-time generation
        gpt = GPT(model=model)
        
        # Get the Dutch description
        response, _, _ = await gpt.run(prompts=prompts, silent=True)
        
        # Extract the description (should be a single line with emoji)
        description = response.strip()
        
        # Clean up any remaining markdown artifacts
        if description.startswith("```") and description.endswith("```"):
            description = description[3:-3].strip()
        
        # Ensure it starts with an emoji
        if description and not _starts_with_emoji(description):
            description = "📊 " + description
            
        # Ensure the text part (after emoji) starts with "Ik"
        if description:
            # Split on first space to separate emoji from text
            parts = description.split(' ', 1)
            if len(parts) == 2:
                emoji_part = parts[0]
                text_part = parts[1]
                
                # If text doesn't start with "Ik", adjust it
                if not text_part.lower().startswith('ik '):
                    # Add "Ik " at the beginning and make first letter lowercase
                    if text_part:
                        text_part = "Ik " + text_part[0].lower() + text_part[1:] if len(text_part) > 1 else "Ik " + text_part.lower()
                    else:
                        text_part = "Ik analyseer de gegevens"
                
                description = emoji_part + " " + text_part
            
        return description
        
    except Exception as e:
        logger.error(f"Error generating Dutch step description: {e}")
        return "📊 Ik analyseer van gegevens"


def _starts_with_emoji(text: str) -> bool:
    """Check if text starts with an emoji."""
    if not text:
        return False
    
    # Simple check for common emoji patterns
    first_char = text[0]
    return ord(first_char) > 127  # Unicode characters beyond ASCII


# Convenience function for testing
async def test_step_describer():
    """Test the step describer with various examples."""
    test_cases = [
        {
            "question": "Hoeveel verkoop hadden we dit jaar?",
            "reasoning": "I need to first explore the available data to understand the schema",
            "code": "df.info()",
            "output": "DataFrame info showing columns and data types"
        },
        {
            "question": "Welke klanten bestelden het meest?",
            "reasoning": "Filter the data for this year's sales",
            "code": "sales_df.filter(pl.col('year') == 2024)",
            "output": "Filtered 1,243 records for year 2024"
        },
        {
            "question": "Wat zijn de trends per regio?",
            "reasoning": "Group by region and calculate totals",
            "code": "df.group_by('region').agg(pl.col('amount').sum())",
            "output": "Aggregated sales by region: Noord (€123K), Zuid (€98K)"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Question: {case['question']}")
        print(f"Code: {case['code']}")
        
        description = await describe_step_in_dutch(
            case['question'],
            case['reasoning'], 
            case['code'],
            case['output']
        )
        
        print(f"Dutch Description: {description}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_step_describer())
