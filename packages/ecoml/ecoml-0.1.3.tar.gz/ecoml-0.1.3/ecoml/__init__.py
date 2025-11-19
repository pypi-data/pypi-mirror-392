from .tracker import EcoTracker
from .ui import CellHook
from .recommender import RecommendationEngine
from .gemini_helper import GeminiAdvisor
from pathlib import Path

def enable_tracking():
    """
    One-line activation for EcoML inside any Jupyter Notebook.
    """
    log_path = Path.home() / ".ecoml" / "emissions_log.csv"
    log_path.parent.mkdir(exist_ok=True, parents=True)

    tracker = EcoTracker(log_path=str(log_path))
    recommender = RecommendationEngine(tracker)
    CellHook(tracker, recommender).register()

    print("🌱 EcoML tracking enabled – monitoring CPU/GPU/CO₂")

__all__ = [
    "EcoTracker",
    "CellHook",
    "RecommendationEngine",
    "GeminiAdvisor",
    "enable_tracking"
]
