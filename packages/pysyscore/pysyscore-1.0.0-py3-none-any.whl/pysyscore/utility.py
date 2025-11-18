import datetime
import os
from typing import Dict, Any, List

# Import all core modules to create composite functions
from .services import ServiceManager
from .process import ProcessManager
from .command import CommandExecutor
from .system_info import SystemInfo
from .registry import get_registry_value

class WindowsUtility:
    """
    Provides high-level, composite administrative functions 
    by leveraging all PySysCore modules.
    """
    
    def __init__(self):
        self.svc_mgr = ServiceManager()
        self.proc_mgr = ProcessManager()
        self.cmd_exec = CommandExecutor()
        self.sys_info = SystemInfo()

    def ensure_service_running_and_log(self, service_name: str, log_file: str = "syscore_utility.log") -> bool:
        # ... (unchanged) ...
        status = self.svc_mgr.get_status(service_name)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hostname = self.sys_info.get_computer_full_name()
        
        log_message = f"[{timestamp}][HOST: {hostname}] SERVICE: {service_name} - "

        if status == "running":
            log_message += "Status checked: RUNNING. No action taken."
            result = True
        elif status == "stopped":
            log_message += "Status checked: STOPPED. Attempting restart..."
            if self.svc_mgr.restart_service(service_name):
                log_message += "SUCCESSFULLY RESTARTED."
                result = True
            else:
                log_message += "RESTART FAILED."
                result = False
        else:
             log_message += f"Status checked: {status.upper()}. Ignoring."
             result = False

        with open(log_file, "a") as f:
            f.write(log_message + "\n")
            
        return result

    def get_system_security_report(self) -> Dict[str, Any]:
        # ... (unchanged) ...
        report = {}
        
        # 1. Registry Check 
        fw_enabled = get_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware")
        report['WindowsDefender_AV_Disabled'] = fw_enabled == 1
        
        # 2. Process Check 
        process_list = self.proc_mgr.list_processes()
        suspicious_process_name = "hacktool.exe" 
        report['Suspicious_Process_Running'] = any(p['name'].lower() == suspicious_process_name.lower() for p in process_list)

        # 3. Command Check 
        ps_command = "(Get-NetTCPConnection -State Listen).Count"
        success, output, _ = self.cmd_exec.run_powershell(ps_command)
        
        try:
            listen_count = int(output.strip())
            report['Network_Listening_Ports'] = listen_count
        except:
            report['Network_Listening_Ports'] = "Error running PS command"

        return report

    # --- Group Name Localization ---
    def get_admin_group_name(self) -> str:
        """
        Retrieves the localized name of the built-in Administrators group.
        Uses PowerShell to look up the group by its universal SID suffix (-544).
        """
        # Commande PowerShell pour trouver le groupe dont le SID se termine par -544 (Administrators)
        ps_command = '(Get-LocalGroup | Where-Object { $_.SID -like "*-544" }).Name'
        success, output, _ = self.cmd_exec.run_powershell(ps_command)
        
        if success and output.strip():
            # Retourne le nom localisé (ex: "Administrateurs" ou "Administrators")
            return output.strip()
        else:
            # Fallback sûr
            return "Administrators"


    # --- Local User and Group Management ---

    def create_local_user(self, username: str, password: str, description: str = "") -> bool:
        """
        Creates a new local user on the system using PowerShell commands (New-LocalUser).
        """
        ps_command = (
            f'$SecPass = ConvertTo-SecureString -String "{password}" -AsPlainText -Force; '
            f'New-LocalUser -Name "{username}" -Password $SecPass '
            f'-Description "{description}"'
        )
        
        success, _, stderr = self.cmd_exec.run_powershell(ps_command)
        
        if not success:
            print(f"Error creating user {username} (via PowerShell): {stderr}")
            
        return success

    def delete_local_user(self, username: str) -> bool:
        """
        Deletes a local user from the system using PowerShell (Remove-LocalUser).
        """
        ps_command = f'Remove-LocalUser -Name "{username}" -ErrorAction SilentlyContinue'
        
        success, _, stderr = self.cmd_exec.run_powershell(ps_command)
        
        if not success and stderr.strip():
            print(f"Error deleting user {username} (via PowerShell): {stderr}")
            
        return success or ("not found" in stderr.lower())


    def add_user_to_group(self, username: str, group_name: str) -> bool:
        """
        Adds a local user to a local group using PowerShell (Add-LocalGroupMember).
        """
        # NOUVEAU: Utilise la détection de langue si c'est le groupe admin par défaut
        if group_name.lower() == "administrators":
            group_name = self.get_admin_group_name()
            
        ps_command = f'Add-LocalGroupMember -Group "{group_name}" -Member "{username}"'
        success, _, stderr = self.cmd_exec.run_powershell(ps_command)
        
        if not success:
            print(f"Error adding user {username} to group {group_name} (via PowerShell): {stderr}")
            
        return success

    def remove_user_from_group(self, username: str, group_name: str) -> bool:
        """
        Removes a local user from a local group using PowerShell (Remove-LocalGroupMember).
        """
        # NOUVEAU: Utilise la détection de langue si c'est le groupe admin par défaut
        if group_name.lower() == "administrators":
            group_name = self.get_admin_group_name()
            
        ps_command = f'Remove-LocalGroupMember -Group "{group_name}" -Member "{username}" -ErrorAction SilentlyContinue'
        success, _, stderr = self.cmd_exec.run_powershell(ps_command)
        
        return success
