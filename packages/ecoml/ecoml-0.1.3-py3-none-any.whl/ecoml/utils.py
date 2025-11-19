import os, csv, datetime as dt

LOG_HEADERS = [
 "timestamp","notebook","cell_id","runtime_sec",
 "cpu_util_avg","gpu_util_avg","cpu_power_w","gpu_power_w",
 "energy_kwh","co2_g","hardware_type","hardware_name",
 "cpu_temp_c","gpu_temp_c","gpu_mem_used_mb","gpu_mem_free_mb",
 "gpu_mem_total_mb","notes","recommended_hardware","recommended_confidence","recommended_reasons"
]

# ==================================================
def now():
    return dt.datetime.now().isoformat(timespec="seconds")

# ==================================================
def ensure_log(path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(LOG_HEADERS)

# ==================================================
def append_log_row(path: str, row: dict):
    ensure_log(path)

    ordered = [row.get(h, "") for h in LOG_HEADERS]

    try:
        with open(path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(ordered)
    except:
        print("⚠ Failed to write log row – continuing.")
