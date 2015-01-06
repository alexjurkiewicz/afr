import sys
from cx_Freeze import setup, Executable

# re isn't automatically included as a dependency
#build_exe_options = {"packages": ["re"]}

# Dont display console on windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  
        options = {"build_exe": build_exe_options},
        executables = [Executable("afr.py", base=base)])
