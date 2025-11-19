from __future__ import annotations
from typing import Any, Optional
from IPython.display import HTML, display


# =====================================================================
#  CSS + JAVASCRIPT (GLOBAL, EXECUTED EVERY RENDER)
# =====================================================================
STYLE = """
<style>
.ecoml-pill {
  display:inline-flex; align-items:center; gap:10px;
  background:#1a1a1a; border:1px solid #2f2f2f;
  padding:7px 16px; border-radius:24px;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI";
  color:#e9ffe9; font-size:14px; font-weight:600;
  cursor:pointer; transition:.15s;
}
.ecoml-pill:active { transform:scale(.97); opacity:.8; }

.ecoml-icon {
  width:22px;height:22px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:15px;background:#2ecc71;
}
.ecoml-warm .ecoml-icon { background:#f1c40f!important; }
.ecoml-hot  .ecoml-icon { background:#e74c3c!important; }

.ecoml-box {
  border-radius:14px;
  background:#101010;
  border:1px solid #2f2f2f;
  padding:14px 18px;
  color:#eaeaea;
  display:none;
  font-size:14px;
}

.ecoml-table {
  width:100%; border-collapse:collapse;
  font-size:13px; margin-top:6px;
}
.ecoml-table td {
  padding:5px 4px;
  border-bottom:1px solid #2a2a2a;
  text-align:left !important;
}
.ecoml-table tr:last-child td { border-bottom:none; }
.ecoml-table td:first-child { opacity:.65; font-weight:500;}

.eco-header { font-weight:700; margin-bottom:4px; color:#d5ffd5; }
.eco-suggest {
  font-size:12px; margin:3px 0; padding-left:7px;
  border-left:3px solid #3effaa; opacity:.9;
}

.ecoml-score-wrap { margin-top:10px;font-size:13px; }
.ecoml-score-bar {
  width:150px; height:6px;
  background:#333; border-radius:10px;
  overflow:hidden; margin-top:4px;
}
.ecoml-score-fill {
  height:100%; width:0%;
  background:linear-gradient(90deg,#12ff6e,#35ffb0);
  transition:width .35s;
}

.eco-compare-row { margin-top:10px; display:flex; justify-content:flex-end; }
.eco-compare-btn {
  padding:6px 12px; border-radius:999px;
  background:#181818; border:1px solid #333;
  font-size:13px; cursor:pointer; color:#fff;
}
.eco-compare-btn:hover { background:#222; }
</style>

<script>
if (!window.ecoToggle){
  window.ecoToggle = function(id, fill, score){
    let box = document.getElementById(id);
    let bar = document.getElementById(fill);
    if (!box) return;
    if (box.style.display === "block"){
      box.style.display="none";
      bar.style.width="0%";
    } else {
      box.style.display="block";
      setTimeout(() => bar.style.width = score + "%", 60);
    }
  }
}
</script>
"""


# =====================================================================
def _fmt(x, d=3):
    try: return f"{float(x):.{d}f}"
    except: return "-"


# =====================================================================
#  CELL HOOK
# =====================================================================
class CellHook:
    def __init__(self, tracker, recommender: Optional[Any] = None):
        self.tracker = tracker
        self.recommender = recommender
        self.shell = None

    # -----------------------------------------------------------------
    def register(self):
        from IPython import get_ipython
        sh = get_ipython()
        if not sh:
            print("⚠ Not inside IPython – UI disabled")
            return
        sh.events.register("pre_run_cell", self._pre)
        sh.events.register("post_run_cell", self._post)
        print("EcoML UI CellHook Registered ✓")

    # -----------------------------------------------------------------
    def _pre(self, *_):
        try: self.tracker.start_cell()
        except: pass

    # -----------------------------------------------------------------
    def _post(self, result):
        code  = getattr(result.info, "raw_cell", None)
        error = result.error_in_exec if result.error_in_exec else None

        try:
            rec = self.tracker.end_cell(
                recommender=self.recommender,
                error=error,
                code=code
            )
        except Exception as e:
            display(HTML(f"<div style='color:#ff4444'>EcoML Error: {e}</div>"))
            return

        if not rec:
            display(HTML(""))
            return

        # SAFE FIELDS
        runtime = float(rec.get("runtime_sec", 0))
        cpu  = float(rec.get("cpu_util_avg", 0))
        gpu  = float(rec.get("gpu_util_avg", 0))
        temp = float(rec.get("gpu_temp_c") or rec.get("cpu_temp_c") or 0)
        co2  = float(rec.get("co2_g", 0))
        energy = float(rec.get("energy_kwh", 0))

        rec_hw  = rec.get("recommended_hardware", "Unknown")
        reasons = rec.get("recommended_reasons", "")

        if isinstance(reasons, list):
            reasons = " | ".join(reasons)

        cid   = rec.get("cell_id", 0)
        box1  = f"eco-box-co2-{cid}"
        box2  = f"eco-box-rec-{cid}"
        fill1 = f"eco-fill-co2-{cid}"
        fill2 = f"eco-fill-rec-{cid}"

        score = max(0, min(100, int(100 - runtime*3 - gpu/2 - max(0, temp-60))))
        cls   = "ecoml-hot" if temp>90 else ("ecoml-warm" if temp>80 else "")

        # ---------------- INSIGHTS BLOCK ----------------
        insights = ""
        if reasons:
            insights += "<div class='eco-header'>💡 Insights</div>"
            for line in reasons.split(" | "):
                insights += f"<div class='eco-suggest'>{line}</div>"
        temp_cpu = float(rec.get("cpu_temp_c", 0))
        temp_gpu = float(rec.get("gpu_temp_c", 0))

        # ---------------- TABLE 1 ----------------
        table1 = f"""
        <table class='ecoml-table'>
          <tr><td>⏱ Runtime</td><td>{_fmt(runtime)} s</td></tr>
          <tr><td>⚡ Energy</td><td>{_fmt(energy,6)} kWh</td></tr>
          <tr><td>🖥 CPU</td><td>{_fmt(cpu,1)}%</td></tr>
          <tr><td>🎮 GPU</td><td>{_fmt(gpu,1)}%</td></tr>
          <tr><td>🌡️ Temp</td><td>{_fmt(temp_gpu,1)} °C</td></tr>

        </table>
        """

        # ---------------- TABLE 2 ----------------
        table2 = f"""
        <table class='ecoml-table'>
          <tr><td>🔧 Recommended</td><td><b>{rec_hw}</b></td></tr>
          <tr><td>♻ CO₂ (g)</td><td>{_fmt(co2,6)}</td></tr>
          <tr><td>⏱ Runtime</td><td>{_fmt(runtime)} s</td></tr>
        </table>
        """

        # =====================================================================
        #  🔥 SIDE-BY-SIDE BOX LAYOUT
        # =====================================================================
        html = f"""
        {STYLE}

        <div style="display:flex;gap:14px;align-items:center;margin-top:6px;">
          <div class="ecoml-pill {cls}" onclick="ecoToggle('{box1}','{fill1}',{score})">
            <div class="ecoml-icon">🌿</div><b>{_fmt(co2,3)} g CO₂</b>
          </div>

          <div class="ecoml-pill {cls}" onclick="ecoToggle('{box2}','{fill2}',{score})">
            <div class="ecoml-icon">⚙️</div><b>{rec_hw}</b>
          </div>

          <span style="opacity:.6;font-size:12px;">(Click pill)</span>
        </div>


        <!-- ⭐ TWO BOXES SIDE-BY-SIDE ⭐ -->
        <div style="display:flex; gap:18px; margin-top:10px; align-items:flex-start;">

          <!-- LEFT BOX -->
          <div class="ecoml-box" id="{box1}" style="width:50%;">
            {insights}
            {table1}
            <div class="ecoml-score-wrap">
              Eco Score <b>{score}/100</b>
              <div class="ecoml-score-bar"><div class="ecoml-score-fill" id="{fill1}"></div></div>
            </div>
          </div>

          <!-- RIGHT BOX -->
          <div class="ecoml-box" id="{box2}" style="width:50%;">
            {table2}
            <div class="ecoml-score-wrap">
              Eco Score <b>{score}/100</b>
              <div class="ecoml-score-bar"><div class="ecoml-score-fill" id="{fill2}"></div></div>
            </div>
            <div class="eco-compare-row">
              <button class="eco-compare-btn">📊 Compare</button>
            </div>
          </div>

        </div>
        """

        display(HTML(html))
