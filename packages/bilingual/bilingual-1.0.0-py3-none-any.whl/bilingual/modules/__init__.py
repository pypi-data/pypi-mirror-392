"""
Literary and style analysis modules for bilingual text processing.

This package provides tools for:
- Literary device detection (metaphors, similes)
- Poetic meter analysis
- Style transfer capabilities
"""

from bilingual.modules.literary_analysis import (
    metaphor_detector,
    simile_detector,
    tone_classifier,
)
from bilingual.modules.poetic_meter import detect_meter
from bilingual.modules.style_transfer_gan import StyleTransferModel

# Optional ML-based imports (require torch/transformers)
try:
    from bilingual.modules.poetic_meter import PoeticMeterDetector
    from bilingual.modules.style_transfer_gan import StyleTransferGPT

    _ML_AVAILABLE = True
except ImportError:
    PoeticMeterDetector = None
    StyleTransferGPT = None
    _ML_AVAILABLE = False

__all__ = [
    "metaphor_detector",
    "simile_detector",
    "tone_classifier",
    "detect_meter",
    "StyleTransferModel",
]

# Add ML classes to __all__ if available
if _ML_AVAILABLE:
    __all__.extend(
        [
            "PoeticMeterDetector",
            "StyleTransferGPT",
        ]
    )
