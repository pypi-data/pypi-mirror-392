import time
from typing import Dict, Any
from .metrics import get_metrics
from . import utils


class EcoTracker:
    """
    Tracks runtime, energy, CO₂ emissions, power usage and
    passes metrics to recommender + UI.
    """

    def __init__(self, log_path, notebook_name="Notebook", emission_factor=0.475):
        self.log_path = log_path
        self.notebook_name = notebook_name
        self.emission_factor = emission_factor

        self._cell_id = 0
        self._start_time = None
        self._start_metrics = None

    # ================================================================
    def start_cell(self):
        """Called BEFORE code executes"""
        self._cell_id += 1
        self._start_time = time.time()
        self._start_metrics = get_metrics()

    # ================================================================
    def end_cell(self, recommender=None, error=None, code=None) -> Dict[str, Any]:
        """
        Called AFTER code executes.

        ⚠️ 100% SAFE VERSION:
           - Prevents "NoneType - float" crash
           - Returns {} instead of exploding
           - Logs metrics + insights
        """

        # -----------------------------------------------------------------
        # 🛑 SAFETY CHECK — if start_cell NEVER ran → DO NOT CRASH
        # -----------------------------------------------------------------
        if self._start_time is None or self._start_metrics is None:
            return {}      # UI handles empty dict safely

        # -----------------------------------------------------------------
        # BASE METRICS
        # -----------------------------------------------------------------
        runtime = time.time() - self._start_time
        end = get_metrics()

        cpu_avg = (self._start_metrics["cpu_util_avg"] + end["cpu_util_avg"]) / 2
        gpu_avg = (self._start_metrics["gpu_util_avg"] + end["gpu_util_avg"]) / 2

        # Energy (Wh) and CO₂ (g)
        energy_wh = (end["cpu_power_w"] + end["gpu_power_w"]) * (runtime / 3600)
        co2 = energy_wh * self.emission_factor

        # -----------------------------------------------------------------
        # FINAL RECORD (BASE FIELDS)
        # -----------------------------------------------------------------
        rec = dict(
            timestamp=utils.now(),
            notebook=self.notebook_name,
            cell_id=self._cell_id,
            runtime_sec=runtime,

            cpu_util_avg=cpu_avg,
            gpu_util_avg=gpu_avg,
            cpu_power_w=end["cpu_power_w"],
            gpu_power_w=end["gpu_power_w"],

            energy_kwh=energy_wh / 1000,
            co2_g=co2,

            hardware_type=end["hardware_type"],
            hardware_name=end["hardware_name"],

            cpu_temp_c=end["cpu_temp_c"],
            gpu_temp_c=end["gpu_temp_c"],

            gpu_mem_used_mb=end["gpu_mem_used_mb"],
            gpu_mem_free_mb=end["gpu_mem_free_mb"],
            gpu_mem_total_mb=end["gpu_mem_total_mb"],

            notes="",
        )

        # -----------------------------------------------------------------
        # RECOMMENDER (Gemini + rule based)
        # -----------------------------------------------------------------
        if recommender:
            out = recommender.recommend(rec, code=code, error=error)
            rec.update(out)

        # -----------------------------------------------------------------
        # WRITE TO CSV (SAFE – never crashes runtime)
        # -----------------------------------------------------------------
        utils.append_log_row(self.log_path, rec)

        return rec
