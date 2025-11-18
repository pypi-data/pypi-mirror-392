\# PySysCore: Robust Windows System Management Utilities



\[!\[PyPI version](https://img.shields.io/pypi/v/pysyscore.svg)](https://pypi.org/project/pysyscore/)

\[!\[License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

\[!\[Python version](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)



PySysCore is a light and robust Python library for essential system administration and introspection tasks on Windows operating systems. It offers reliable, language-agnostic utilities for interacting with the Windows Registry, managing services, handling processes, and performing user account operations, even on localized systems.



---



\## ✨ Key Features



\* \*\*Reliable OS Detection:\*\* Accurately identifies Windows 10 vs. \*\*Windows 11\*\* by checking the Build Number, overcoming compatibility flags.

\* \*\*Localized User Management:\*\* Automatically detects the locale-specific name of the \*\*Administrators\*\* group (e.g., 'Administrateurs') for reliable user provisioning.

\* \*\*Service Control:\*\* Start, stop, and restart system services (`pywin32` dependency).

\* \*\*Command Execution:\*\* Safe wrappers for running both `cmd` and `PowerShell` commands.

\* \*\*System Introspection:\*\* Retrieval of FQDN, OS version, architecture, and registry values.



---



\## ⚙️ Installation



PySysCore requires `pywin32` for core Service Management features, which is specified as a Windows-only dependency.



```bash

pip install pysyscore



\#exemples



from pysyscore import SystemInfo



sys\_info = SystemInfo()

info = sys\_info.get\_system\_info\_summary()



print(f"OS Name: {info\['OS\_LongName']}")

\# Output (on Windows 11): Windows 11 Pro (25H2)





from pysyscore import WindowsUtility



util = WindowsUtility()

test\_user = "test\_sys\_user"

admin\_group = util.get\_admin\_group\_name() # Get localized name



print(f"Admin Group Detected: {admin\_group}")

util.create\_local\_user(test\_user, "P@sswOrd123")

util.add\_user\_to\_group(test\_user, admin\_group)

\# ... cleanup commands (delete\_local\_user)

