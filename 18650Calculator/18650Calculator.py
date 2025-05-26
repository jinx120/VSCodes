import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")  # "dark" or "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

def calculate():
    try:
        pack_capacity = float(entry_pack_capacity.get())
        pack_voltage = float(entry_pack_voltage.get())
        cell_capacity = float(entry_cell_capacity.get())
        cell_voltage = float(entry_cell_voltage.get())
        loss_percent = float(entry_loss_percent.get())

        usable_fraction = 1 - loss_percent / 100.0
        if usable_fraction <= 0 or usable_fraction > 1:
            raise ValueError("Loss percentage must be between 0 and 99.")

        required_capacity = pack_capacity / usable_fraction

        # Series: Round up voltage division
        series_count = -(-pack_voltage // cell_voltage)
        series_count = int(series_count)
        # Parallel: Round up capacity division
        parallel_count = -(-required_capacity // cell_capacity)
        parallel_count = int(parallel_count)
        total_cells = series_count * parallel_count

        result_text.set(
            f"Adjusted for {loss_percent:.1f}% system losses:\n"
            f"Series cells (S): {series_count}\n"
            f"Parallel cells (P): {parallel_count}\n"
            f"Total 18650 cells needed: {total_cells}\n\n"
            f"Required total cell capacity: {required_capacity:.0f} mAh"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

root = ctk.CTk()
root.title("18650 Battery Pack Calculator")
root.geometry("420x350")

font_lbl = ("Segoe UI", 14)
font_ent = ("Segoe UI", 14)
font_btn = ("Segoe UI", 14, "bold")

# Input fields
ctk.CTkLabel(root, text="Desired Usable Capacity (mAh):", font=font_lbl, anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
entry_pack_capacity = ctk.CTkEntry(root, font=font_ent)
entry_pack_capacity.grid(row=0, column=1, padx=10, pady=8)

ctk.CTkLabel(root, text="Desired Pack Voltage (V):", font=font_lbl, anchor="w").grid(row=1, column=0, padx=10, pady=8, sticky="w")
entry_pack_voltage = ctk.CTkEntry(root, font=font_ent)
entry_pack_voltage.grid(row=1, column=1, padx=10, pady=8)

ctk.CTkLabel(root, text="Single Cell Capacity (mAh):", font=font_lbl, anchor="w").grid(row=2, column=0, padx=10, pady=8, sticky="w")
entry_cell_capacity = ctk.CTkEntry(root, font=font_ent)
entry_cell_capacity.grid(row=2, column=1, padx=10, pady=8)

ctk.CTkLabel(root, text="Single Cell Nominal Voltage (V):", font=font_lbl, anchor="w").grid(row=3, column=0, padx=10, pady=8, sticky="w")
entry_cell_voltage = ctk.CTkEntry(root, font=font_ent)
entry_cell_voltage.grid(row=3, column=1, padx=10, pady=8)

ctk.CTkLabel(root, text="Loss Percentage (%):", font=font_lbl, anchor="w").grid(row=4, column=0, padx=10, pady=8, sticky="w")
entry_loss_percent = ctk.CTkEntry(root, font=font_ent)
entry_loss_percent.insert(0, "20")  # Default value
entry_loss_percent.grid(row=4, column=1, padx=10, pady=8)

ctk.CTkButton(root, text="Calculate", font=font_btn, command=calculate).grid(row=5, column=0, columnspan=2, pady=18)

result_text = ctk.StringVar()
ctk.CTkLabel(root, textvariable=result_text, text_color="#80d4ff", font=font_lbl, justify="left").grid(
    row=6, column=0, columnspan=2, padx=10, pady=(4, 10), sticky="w"
)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
