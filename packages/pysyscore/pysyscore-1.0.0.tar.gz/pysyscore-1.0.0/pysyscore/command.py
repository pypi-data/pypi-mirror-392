import subprocess
from typing import Tuple

class CommandExecutor:
    """Executes system commands (CMD and PowerShell) and manages output/errors."""

    def _execute(self, command: str, shell_type: str) -> Tuple[bool, str, str]:
        """Internal helper to execute a command."""
        
        if shell_type == 'powershell':
            executable = ['powershell.exe', '-Command', command]
        elif shell_type == 'cmd':
            executable = ['cmd.exe', '/C', command]
        else:
            return False, "", f"Error: Unknown shell type '{shell_type}'."

        try:
            result = subprocess.run(
                executable,
                capture_output=True,      
                text=True,                
                check=False,              
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            return success, stdout, stderr

        except FileNotFoundError:
            return False, "", f"Error: The executable '{executable[0]}' was not found."
        except Exception as e:
            return False, "", f"An unexpected execution error occurred: {e}"


    def run_cmd(self, command: str) -> Tuple[bool, str, str]:
        """Executes a command using Windows Command Prompt (CMD)."""
        return self._execute(command, 'cmd')


    def run_powershell(self, command: str) -> Tuple[bool, str, str]:
        """Executes a command using PowerShell."""
        return self._execute(command, 'powershell')
