from cx_Freeze import setup, Executable

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