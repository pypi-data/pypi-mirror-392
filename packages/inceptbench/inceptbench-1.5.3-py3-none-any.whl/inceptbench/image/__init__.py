"""
Image Generation and Quality Assessment Module
"""

from .image_quality_checker_di import (
    ImageRanking,
    QualityCheckResult,
    ImageQualityChecker,
)

# Alias for backward compatibility
evaluate_image_quality_di = ImageQualityChecker

__all__ = [
    "ImageRanking",
    "QualityCheckResult",
    "ImageQualityChecker",
    "evaluate_image_quality_di",
]

