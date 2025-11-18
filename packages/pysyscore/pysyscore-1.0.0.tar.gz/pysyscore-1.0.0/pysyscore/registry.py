import winreg
from typing import Any, Optional

REG_HIVES = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU": winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
}

def get_registry_value(hive_name: str, subkey: str, value_name: str) -> Optional[Any]:
    """Retrieves a specific value from the Windows Registry."""
    hive = REG_HIVES.get(hive_name.upper())
    if hive is None:
        print(f"Error: Unknown registry hive '{hive_name}'.")
        return None

    handle = None
    try:
        handle = winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(handle, value_name)
        return value

    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading registry: {e}")
        return None
    finally:
        if handle:
            winreg.CloseKey(handle)
