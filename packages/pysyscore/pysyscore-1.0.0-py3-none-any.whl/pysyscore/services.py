import win32serviceutil
import winerror
import time
from typing import Optional

class ServiceManager:
    """Manages basic operations for Windows services. (Requires pywin32)."""

    def get_status(self, service_name: str) -> Optional[str]:
        """Retrieves the current status of a Windows service."""
        try:
            status_info = win32serviceutil.QueryServiceStatus(service_name)
            status_code = status_info[1] 
            
            status_map = {
                1: "stopped", 2: "start_pending", 3: "stop_pending", 
                4: "running", 5: "continue_pending", 6: "pause_pending", 
                7: "paused",
            }
            return status_map.get(status_code, "unknown")

        except win32serviceutil.error as e:
            if e.winerror == winerror.ERROR_SERVICE_DOES_NOT_EXIST:
                return "not_found"
            return None
        except Exception:
            return None

    def start_service(self, service_name: str) -> bool:
        """Starts a Windows service."""
        try:
            win32serviceutil.StartService(service_name)
            return True
        except Exception as e:
            print(f"Error starting service '{service_name}': {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stops a Windows service."""
        try:
            win32serviceutil.StopService(service_name)
            return True
        except Exception as e:
            print(f"Error stopping service '{service_name}': {e}")
            return False

    def restart_service(self, service_name: str) -> bool:
        """Stops and then starts a Windows service."""
        print(f"Attempting to restart service '{service_name}'...")
        if self.stop_service(service_name):
            time.sleep(1) 
            return self.start_service(service_name)
        else:
            print(f"Failed to stop service '{service_name}'. Restart aborted.")
            return False
