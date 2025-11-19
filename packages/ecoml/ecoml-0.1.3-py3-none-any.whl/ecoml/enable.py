from .tracker import EcoTracker
from .ui import CellHook
from .recommender import RecommendationEngine
from .gemini_helper import GeminiAdvisor


def enable_tracking(
    notebook_name: str = "Notebook",
    log_path: str | None = None,
) -> None:
    """
    One-line helper to enable EcoML tracking in any Jupyter notebook.

    Usage
    -----
    from ecoml import enable_tracking
    enable_tracking()
    """

    tracker = EcoTracker(
        notebook_name=notebook_name,
        log_path=log_path or "data/emissions_log.csv",
    )

    gemini = GeminiAdvisor()
    recommender = RecommendationEngine(tracker=tracker, gemini=gemini)

    CellHook(tracker, recommender).register()
    print("🔥 EcoML tracking enabled – pills will appear after each cell.")
