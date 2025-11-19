import os
import sys
from pathlib import Path

# Try to load pythonnet CLR
try:
    import clr
    CLR_AVAILABLE = True
except ImportError:
    CLR_AVAILABLE = False

# Path to the DLL inside ecoml/libs/
DLL_PATH = Path(__file__).resolve().parent / "libs" / "LibreHardwareMonitorLib.dll"

def init_hardware():
    """
    Initialize LibreHardwareMonitor.
    Returns a Computer() object or None if unavailable.
    """
    if not CLR_AVAILABLE:
        print("pythonnet not installed — LibreHardwareMonitor disabled.")
        return None

    if not DLL_PATH.exists():
        print(f"⚠ DLL missing at {DLL_PATH}")
        return None

    try:
        # Add DLL folder to sys.path
        sys.path.append(str(DLL_PATH.parent))

        # Load the DLL using pythonnet
        clr.AddReference(str(DLL_PATH))
    except Exception as e:
        print("⚠ Failed to load LibreHardwareMonitor DLL:", e)
        return None

    try:
        from LibreHardwareMonitor.Hardware import Computer 

        computer = Computer()
        computer.CPUEnabled = True
        computer.Open()
        return computer

    except Exception as e:
        print("⚠ LibreHardwareMonitor init error:", e)
        return None


# Initialize only once
_computer = init_hardware()


def get_cpu_temp_lhm():
    """
    Read CPU temperature via LibreHardwareMonitor.
    Returns:
        float (temp °C) or None if unavailable.
    """
    if _computer is None:
        return None

    try:
        from LibreHardwareMonitor.Hardware import SensorType

        for hardware in _computer.Hardware:
            hardware.Update()

            if "cpu" in hardware.Name.lower():
                for sensor in hardware.Sensors:
                    if sensor.SensorType == SensorType.Temperature:
                        return float(sensor.Value)

    except:
        return None

    return None
