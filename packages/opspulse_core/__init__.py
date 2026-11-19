"""Shared data contracts and feature engineering for OpsPulse MLOps.

CRITICAL MLOPS INVARIANT:
Both offline training pipelines (`pipelines/training/`) and online serving
(`services/inference_api/`) MUST import feature computation from this package
to eliminate Train-Serving Skew.
"""

from opspulse_core.features import FEATURE_NAMES, extract_features
from opspulse_core.schemas import (
    AnomalyPrediction,
    FaultScenario,
    MetricWindowInput,
    ModelInfoResponse,
)

__all__ = [
    "AnomalyPrediction",
    "FEATURE_NAMES",
    "FaultScenario",
    "MetricWindowInput",
    "ModelInfoResponse",
    "extract_features",
]
