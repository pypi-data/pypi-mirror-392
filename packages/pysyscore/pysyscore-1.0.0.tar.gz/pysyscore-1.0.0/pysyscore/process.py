import ctypes
import ctypes.wintypes as wintypes
from typing import List, Dict, Any

# Windows API Constants
TH32CS_SNAPPROCESS = 0x00000002
PROCESS_TERMINATE = 0x0001 

# Define Structures
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", wintypes.ULONG),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        # CORRECTION : Utilisation de WCHAR pour la compatibilité Unicode
        ("szExeFile", wintypes.WCHAR * 260), 
    ]

# Load DLL and define function signatures
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.restype = wintypes.HANDLE
Process32First = kernel32.Process32First
Process32First.restype = wintypes.BOOL
Process32Next = kernel32.Process32Next
Process32Next.restype = wintypes.BOOL
CloseHandle = kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL

OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)

TerminateProcess = kernel32.TerminateProcess
TerminateProcess.restype = wintypes.BOOL
TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)


class ProcessManager:
    """Manages process operations using the native Windows API (ctypes)."""

    def list_processes(self) -> List[Dict[str, Any]]:
        """Lists currently running processes (ID and name)."""
        snapshot_handle = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        
        if snapshot_handle == wintypes.HANDLE(-1).value:
            print("Error: Failed to create process snapshot.")
            return []

        process_list = []
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

        if Process32First(snapshot_handle, ctypes.byref(entry)):
            while True:
                # CORRECTION : Nettoyage de la chaîne Unicode
                exe_file = entry.szExeFile.strip('\x00')
                
                process_list.append({
                    "pid": entry.th32ProcessID,
                    "ppid": entry.th32ParentProcessID,
                    "name": exe_file,
                    "threads": entry.cntThreads
                })

                if not Process32Next(snapshot_handle, ctypes.byref(entry)):
                    break
        
        CloseHandle(snapshot_handle)
        return process_list

    def kill_process(self, pid: int) -> bool:
        """Terminates a process given its Process ID (PID) using native Windows API."""
        handle = OpenProcess(PROCESS_TERMINATE, False, pid)
        
        if handle is None or handle == 0:
            print(f"Error: Could not open process with PID {pid}.")
            return False

        success = TerminateProcess(handle, 0)
        CloseHandle(handle)

        if not success:
            print(f"Error: Failed to terminate process {pid}.")
        
        return bool(success)
