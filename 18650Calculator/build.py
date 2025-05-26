from cx_Freeze import setup, Executable
import sys
import subprocess

try:
    from cx_Freeze import setup, Executable
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cx_Freeze"])
    from cx_Freeze import setup, Executable

# ...existing build_options and setup code...
build_options = {
    "packages": ["customtkinter"],
    "excludes": [],
}

setup(
    name="18650Calculator",
    version="0.1",
    description="18650 Battery Pack Calculator",
    options={"build_exe": build_options},
    executables=[Executable("18650Calculator.py", base=None)],
)