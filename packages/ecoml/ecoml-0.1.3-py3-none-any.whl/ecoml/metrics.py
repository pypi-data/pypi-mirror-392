import psutil, GPUtil, subprocess

# Needed for temperature fallback
def _read_gpu_temp_wmi():
    """
    Windows WMI GPU temperature reader.
    Works on MX series GPUs (MX330).
    """
    try:
        import wmi
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        for sensor in w.Sensor():
            if sensor.SensorType == "Temperature" and "gpu" in sensor.Name.lower():
                return float(sensor.Value)
    except:
        return None


def get_metrics() -> dict:
    """
    SAFE SYSTEM METRICS
    ALWAYS returns full dict → UI NEVER breaks
    """

    m = {}

    # ==========================================================
    # CPU UTIL
    # ==========================================================
    try:
        m["cpu_util_avg"] = float(psutil.cpu_percent(interval=None))
    except:
        m["cpu_util_avg"] = 0.0

    # ==========================================================
    # CPU TEMP
    # ==========================================================
    try:
        temps = psutil.sensors_temperatures()
        if temps and "coretemp" in temps:
            m["cpu_temp_c"] = temps["coretemp"][0].current
        else:
            m["cpu_temp_c"] = 0.0
    except:
        m["cpu_temp_c"] = 0.0

    # ==========================================================
    # GPU (PRIMARY: GPUtil)
    # ==========================================================
    try:
        g = GPUtil.getGPUs()
        if g:
            gpu = g[0]

            m.update({
                "gpu_util_avg": gpu.load * 100,
                "gpu_temp_c": gpu.temperature,
                "gpu_mem_used_mb": gpu.memoryUsed,
                "gpu_mem_free_mb": gpu.memoryFree,
                "gpu_mem_total_mb": gpu.memoryTotal,
                "gpu_power_w": 0.0,        # GPUtil cannot read power
                "hardware_type": "GPU",
                "hardware_name": gpu.name
            })

        else:
            raise Exception("NO GPU")

    except:
        pass  # FALLBACK BELOW

    # ==========================================================
    # GPU TEMP FALLBACK (WMI)
    # ==========================================================
    if m.get("gpu_temp_c", 0) in [None, 0.0]:
        t = _read_gpu_temp_wmi()
        if t:
            m["gpu_temp_c"] = t

    # ==========================================================
    # CPU-ONLY FALLBACK
    # ==========================================================
    if "hardware_type" not in m:
        m.update({
            "gpu_util_avg": 0.0,
            "gpu_temp_c": 0.0,
            "gpu_power_w": 0.0,
            "gpu_mem_used_mb": 0.0,
            "gpu_mem_free_mb": 0.0,
            "gpu_mem_total_mb": 0.0,
            "hardware_type": "CPU",
            "hardware_name": "CPU Only"
        })

    # ==========================================================
    # CPU POWER ESTIMATE
    # ==========================================================
    try:
        m["cpu_power_w"] = max(2.0, m["cpu_util_avg"] * 0.35)
    except:
        m["cpu_power_w"] = 3.0

    return m
