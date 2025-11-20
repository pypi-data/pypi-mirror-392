"""
InceptBench - Unified Educational Content Evaluation Framework

Public API for the inceptbench package. This module provides stable, user-facing
entry points for evaluating educational questions, content, and articles.
"""

__version__ = "1.5.3"

# Main orchestration functions
from .orchestrator import (
    universal_unified_benchmark,
    benchmark_parallel,
    UniversalEvaluationRequest,
    UniversalEvaluationResponse,
    UniversalQuestionEvaluationScores,
)

# Core evaluator functions
from .core.evaluator.v3 import (
    call_single_shot_evaluator,
    build_single_shot_messages,
    EvaluationDimension,
    clip01,
)

from .core.evaluator.article_evaluator import (
    evaluate_article_holistic,
    ArticleHolisticEvaluatorResult,
)

# CLI entry point
from .cli import cli as cli_main

__all__ = [
    # Version
    "__version__",
    
    # Main orchestration
    "universal_unified_benchmark",
    "benchmark_parallel",
    "UniversalEvaluationRequest",
    "UniversalEvaluationResponse",
    "UniversalQuestionEvaluationScores",
    
    # Core evaluators
    "call_single_shot_evaluator",
    "build_single_shot_messages",
    "EvaluationDimension",
    "clip01",
    "evaluate_article_holistic",
    "ArticleHolisticEvaluatorResult",
    
    # CLI
    "cli_main",
]

