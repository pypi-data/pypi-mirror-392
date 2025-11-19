from typing import Dict, Any


class RecommendationEngine:

    def __init__(self, tracker=None, gemini=None):
        self.tracker = tracker
        self.gemini = gemini

    # ==========================================================
    def recommend(self, m: Dict[str, Any], code=None, error=None):
        """
        Takes metric record dictionary
        Returns dict with:
            recommended_hardware
            recommended_confidence
            recommended_reasons
        """

        suggestions = []
        label = "Balanced – Continue Current Hardware"
        confidence = None

        cpu = float(m.get("cpu_util_avg", 0))
        gpu = float(m.get("gpu_util_avg", 0))
        temp = float(m.get("cpu_temp_c", 0))

        # ---------------------------------------------
        # RULE 1: CPU bottleneck
        # ---------------------------------------------
        if cpu > 60 and gpu < 40:
            label = "CPU Bottleneck – Enable GPU"
            suggestions.append("⚠ High CPU load while GPU is idle → move workload to GPU")

        # ---------------------------------------------
        # RULE 2: GPU overload
        # ---------------------------------------------
        if gpu > 85:
            suggestions.append("⚠ GPU heavily utilized")

        # ---------------------------------------------
        # RULE 3: Overheating
        # ---------------------------------------------
        if temp > 65:
            suggestions.append("🔥 CPU overheating detected")

        # ---------------------------------------------
        # RULE 4: Runtime error
        # ---------------------------------------------
        if error:
            suggestions.append(f"❌ Runtime error: {str(error)[:80]}")

        # =========================================================
        # 🧠 ONLY CALL GEMINI IF SOMETHING IS WRONG
        # =========================================================
        problem_detected = (
            cpu > 70 or
            gpu > 75 or
            temp > 75 or
            error is not None
        )

        if self.gemini and self.gemini.enabled and problem_detected:

            # 🔹 Optimization hint
            ask = f"CPU {cpu}% | GPU {gpu}% | Temp {temp}°C → Give 1-line optimization tip"
            out = self.gemini.ask(ask)

            if out:
                suggestions.append("🤖 " + out)

            # 🔹 If error, request a FIX
            if error and code:
                fix = self.gemini.generate_fix(error, code)
                if fix:
                    suggestions.append("💡 Fix → " + fix)

        # =========================================================
        # DEFAULT → NO PROBLEMS
        # =========================================================
        if not suggestions:
            return {
                "recommended_hardware": "Optimal",
                "recommended_confidence": 1.0,
                "recommended_reasons": "No changes required – system efficient"
            }

        # =========================================================
        # RETURN STANDARD STRUCTURE
        # =========================================================
        return {
            "recommended_hardware": label,
            "recommended_confidence": confidence,
            "recommended_reasons": " | ".join(suggestions)
        }
