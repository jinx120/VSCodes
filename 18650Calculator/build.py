from cx_Freeze import setup, Executable
import sys
import subprocess
import os

# Ensure cx_Freeze and customtkinter are installed
try:
    from cx_Freeze import setup, Executable
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cx_Freeze"])
    from cx_Freeze import setup, Executable

try:
    import customtkinter
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter

try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image

# Build options
build_options = {
    "packages": ["customtkinter", "tkinter", "PIL"],
    "excludes": [],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="18650Calculator",
    version="0.1",
    description="18650 Battery Pack Calculator",
    options={"build_exe": build_options},
    executables=[Executable("18650Calculator.py", base=base)],
)

# Automatically build when script is run directly
if __name__ == "__main__":
    os.system(f'"{sys.executable}" "{sys.argv[0]}" build')