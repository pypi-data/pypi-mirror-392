import platform
import os
import ctypes
from typing import Dict, Any, Optional
from .registry import get_registry_value

class SystemInfo:
    """
    Manages collection of core system information using native Python and ctypes/winreg.
    """

    def __init__(self):
        pass

    # --- Méthodes de base ---

    def get_computer_full_name(self) -> str:
        """Retrieves the FQDN using ctypes/WinAPI (fallback to platform.node)."""
        try:
            buf = ctypes.create_unicode_buffer(256)
            size = ctypes.c_ulong(256)
            
            if ctypes.windll.kernel32.GetComputerNameW(buf, ctypes.byref(size)):
                return buf.value
        except Exception:
            return platform.node()

    def get_os_architecture(self) -> str:
        """Retrieves the processor architecture (e.g., 'AMD64', 'ARM64')."""
        arch = get_registry_value(
            "HKLM", 
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 
            "CurrentProcessorArchitecture"
        )
        return arch if arch is not None else platform.machine()
    
    def get_os_release_id(self) -> str:
        """Retrieves the Windows Release ID (e.g., '22H2', '23H2')."""
        release_id = get_registry_value(
            "HKLM", 
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 
            "ReleaseId"
        )
        return release_id if release_id is not None else "N/A"
    
    def get_os_display_version(self) -> str:
        """Retrieves the Windows Marketing Version (e.g., '25H2')."""
        display_version = get_registry_value(
            "HKLM", 
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 
            "DisplayVersion"
        )
        return display_version if display_version is not None else "N/A"

    def get_os_edition_id(self) -> str:
        """Retrieves the Edition ID (e.g., 'Professional', 'Home')."""
        edition_id = get_registry_value(
            "HKLM", 
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 
            "EditionID"
        )
        return edition_id if edition_id is not None else "N/A"

    # --- MÉTHODE DE RECONSTRUCTION DU NOM LONG (Correction Windows 11) ---

    def get_os_long_name(self) -> str:
        """
        Reconstructs the long, descriptive OS name similar to Windows Settings.
        Prioritizes Windows 11 detection using CurrentBuildNumber.
        """
        REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        
        # 1. Clés primaires
        product_name = get_registry_value("HKLM", REG_PATH, "ProductName")
        build_number_str = get_registry_value("HKLM", REG_PATH, "CurrentBuildNumber")
        edition_id = self.get_os_edition_id()
        display_version = self.get_os_display_version()

        parts = []
        base_name = product_name or "Windows OS"
        
        try:
            build_number = int(build_number_str)
            # DÉTECTION WINDOWS 11 : Le numéro de build 22000 et au-delà est Win 11
            if build_number >= 22000:
                base_name = "Windows 11"
            # Sinon, on garde le nom de produit ou le nom de base
            elif "Windows 10" in base_name:
                base_name = "Windows 10"
        except:
            pass # Continue avec le nom par défaut si la lecture du build échoue

        parts.append(base_name)
        
        # 3. Édition (si elle est spécifique)
        if edition_id and edition_id != "N/A" and "Pro" not in base_name:
             if "professional" in edition_id.lower():
                 parts.append("Pro")
             else:
                 parts.append(edition_id)

        # 4. Version (pour la précision)
        if display_version and display_version != "N/A":
            parts.append(f"({display_version})")

        return " ".join(parts).replace("  ", " ").strip()


    def get_system_info_summary(self) -> Dict[str, Optional[str]]:
        """
        Compiles all major system information into a dictionary.
        """
        REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        
        build_number = get_registry_value("HKLM", REG_PATH, "CurrentBuildNumber")
        
        long_name = self.get_os_long_name()
        release_id = self.get_os_release_id()
        display_version = self.get_os_display_version()
        os_arch = self.get_os_architecture()
        edition_id = self.get_os_edition_id()
        
        return {
            "FQDN": self.get_computer_full_name(),
            "OS_LongName": long_name,                    
            "OS_ProductName": get_registry_value("HKLM", REG_PATH, "ProductName"),
            "OS_EditionID": edition_id,                  
            "OS_DisplayVersion": display_version,        
            "OS_ReleaseId": release_id,                  
            "OS_BuildNumber": build_number,
            "OS_Architecture": os_arch,
            "Platform_System": platform.system(),
            "Platform_Release": platform.release(),
        }
