"""Fast Streaming Agent Package.

A high-performance agent that executes code blocks immediately as they complete in the token stream.
"""
# Copyright (c) 2024 FastStreamingAgent Contributors

from .colors import Colors
from .main import FastStreamingAgent
from .custom_print import PrintCapture
from .error_collapse import collapse_error_sequences
from .token_guard import TokenLengthGuard
from .pre_action_loader import PreActionLoader
from .second_step_primer import SecondStepPrimer
from .verification_step_loader import VerificationStepLoader
from .step_describer import describe_step_in_dutch
from .code_storage import save_code_block
from .function_wrapper import wrap_configured_functions
from .function_loader import load_configured_functions
from .forking import ForkedResponder, ForkingError
from .code_block_utils import (
    apply_colors,
    detect_complete_code_blocks,
    has_partial_code_block,
)

__all__ = [
    "Colors",
    "FastStreamingAgent",
    "PrintCapture",
    "collapse_error_sequences",
    "TokenLengthGuard",
    "PreActionLoader",
    "SecondStepPrimer",
    "VerificationStepLoader",
    "describe_step_in_dutch",
    "save_code_block",
    "wrap_configured_functions",
    "load_configured_functions",
    "apply_colors",
    "detect_complete_code_blocks",
    "has_partial_code_block",
    "ForkedResponder",
    "ForkingError",
]
