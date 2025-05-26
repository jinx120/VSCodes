# 18650 Battery Pack Calculator

This project is a GUI application for calculating battery pack configurations using 18650 cells. It allows users to input desired specifications and calculates the number of cells required based on the provided parameters.

## Files

- **18650Calculator.py**: The main application code that implements the calculator using the `customtkinter` library for the GUI.
- **build.py**: The build script for cx_Freeze, which compiles the application into an executable.
- **README.md**: This documentation file.

## Usage

1. Ensure you have Python installed on your system.
2. Install the required libraries:
   ```
   pip install customtkinter cx_Freeze
   ```
3. Run the application:
   ```
   python 18650Calculator.py
   ```
4. To build the executable, run:
   ```
   python build.py build
   ```
   This will create a `build` directory containing the executable for your application.

## Features

- Input fields for desired usable capacity, pack voltage, single cell capacity, single cell voltage, and loss percentage.
- Calculates the number of series and parallel cells required based on the input values.
- Displays the required total cell capacity adjusted for system losses.

## License

This project is licensed under the MIT License.