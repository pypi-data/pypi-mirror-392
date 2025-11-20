"""
Agents module for educational content evaluation and generation.

This module provides agent-based evaluators and tools for content assessment.
"""

# Import main evaluators
from .content_evaluator import evaluate_content
from .eval_agent import EvalAgent
from .curriculum_search import search_curriculum_standards, search_curriculum_tool

# Re-export core submodules
from . import core

__all__ = [
    "evaluate_content",
    "EvalAgent",
    "search_curriculum_standards",
    "search_curriculum_tool",
    "core",
]
