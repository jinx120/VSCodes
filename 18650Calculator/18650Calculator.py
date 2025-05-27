import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
import math

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Simple image generator
def generate_battery_pack_image(series, parallel, cell_size=40, margin=10):
    # Defensive: return None if not valid
    try:
        series = int(series)
        parallel = int(parallel)
        if series <= 0 or parallel <= 0:
            return None
    except Exception:
        return None
    width = series * cell_size + 2 * margin
    height = parallel * cell_size + 2 * margin
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    # Draw cells
    for i in range(series):
        for j in range(parallel):
            x0 = margin + i * cell_size
            y0 = margin + j * cell_size
            x1 = x0 + cell_size - 4
            y1 = y0 + cell_size - 4
            draw.ellipse([x0, y0, x1, y1], outline="black", fill="lightgray")
    # Draw parallel busbars (top of each column)
    busbar_color = "#ffb300"
    busbar_width = 8
    for i in range(series):
        x = margin + i * cell_size + cell_size // 2
        y_top = margin + cell_size // 8
        y_bot = margin + (parallel - 1) * cell_size + cell_size // 2
        draw.line([(x - cell_size // 3, y_top), (x + cell_size // 3, y_top)], fill=busbar_color, width=busbar_width)
        draw.line([(x - cell_size // 3, y_bot), (x + cell_size // 3, y_bot)], fill=busbar_color, width=busbar_width)
    # Draw snaking series busbar
    for i in range(series):
        x = margin + i * cell_size + cell_size // 2
        if i % 2 == 0:
            # Even: left to right at top
            y = margin + cell_size // 8
            if i < series - 1:
                x_next = margin + (i + 1) * cell_size + cell_size // 2
                draw.line([(x, y), (x_next, y)], fill=busbar_color, width=busbar_width)
            # Down at right
            if i < series - 1:
                x_next = margin + (i + 1) * cell_size + cell_size // 2
                y_down_start = y
                y_down_end = margin + (parallel - 1) * cell_size + cell_size // 2
                draw.line([(x_next, y_down_start), (x_next, y_down_end)], fill=busbar_color, width=busbar_width)
        else:
            # Odd: right to left at bottom
            y = margin + (parallel - 1) * cell_size + cell_size // 2
            if i < series - 1:
                x_next = margin + (i + 1) * cell_size + cell_size // 2
                draw.line([(x, y), (x_next, y)], fill=busbar_color, width=busbar_width)
            # Up at left
            if i < series - 1:
                x_next = margin + (i + 1) * cell_size + cell_size // 2
                y_up_start = y
                y_up_end = margin + cell_size // 8
                draw.line([(x_next, y_up_start), (x_next, y_up_end)], fill=busbar_color, width=busbar_width)
    return img

root = ctk.CTk()
root.title("18650 Battery Pack Calculator")

# Input fields
labels = [
    "Desired Usable Capacity (mAh/Ah):",
    "Desired Pack Voltage (V):",
    "Single Cell Capacity (mAh):",
    "Single Cell Nominal Voltage (V):"
]
entries = []
for i, label in enumerate(labels):
    ctk.CTkLabel(root, text=label).grid(row=i, column=0, padx=10, pady=8, sticky="w")
    entry = ctk.CTkEntry(root)
    entry.grid(row=i, column=1, padx=10, pady=8)
    entries.append(entry)

# Add a unit selection for pack capacity
pack_capacity_unit = ctk.StringVar(value="mAh")
unit_options = ["mAh", "Ah"]
ctk.CTkOptionMenu(root, variable=pack_capacity_unit, values=unit_options, width=80).grid(row=0, column=2, padx=5, pady=8)

# Add a spacer row for visual separation
spacer = ctk.CTkLabel(root, text="")
spacer.grid(row=3, column=0, columnspan=3, pady=(0, 2))

# Place the cell capacity variation slider under the Single Cell Capacity input, on its own row
cell_capacity_var = ctk.DoubleVar(value=100)
ctk.CTkLabel(root, text="Cell Capacity Variation (%):").grid(row=4, column=0, padx=10, pady=(0, 8), sticky="w")
cell_capacity_slider = ctk.CTkSlider(root, from_=1, to=100, variable=cell_capacity_var, number_of_steps=99, width=200)
cell_capacity_slider.grid(row=4, column=1, padx=10, pady=(0, 8))
cell_capacity_value_label = ctk.CTkLabel(root, textvariable=cell_capacity_var)
cell_capacity_value_label.grid(row=4, column=2, padx=5, pady=(0, 8))

# Adjust the rest of the rows accordingly (Loss Percentage row is now row=5, etc.)
ctk.CTkLabel(root, text="Loss Percentage (%):").grid(row=5, column=0, padx=10, pady=8, sticky="w")
loss_percent_var = ctk.DoubleVar(value=20)
loss_slider = ctk.CTkSlider(root, from_=1, to=100, variable=loss_percent_var, number_of_steps=99, width=200)
loss_slider.grid(row=5, column=1, padx=10, pady=8)
loss_value_label = ctk.CTkLabel(root, textvariable=loss_percent_var)
loss_value_label.grid(row=5, column=2, padx=5, pady=8)

result_text = ctk.StringVar()
ctk.CTkLabel(root, textvariable=result_text, text_color="#80d4ff").grid(row=7, column=0, columnspan=3, padx=10, pady=(4, 10), sticky="w")
image_label = ctk.CTkLabel(root, text="")
image_label.grid(row=8, column=0, columnspan=3, pady=10)

# Add a label for Wh capacity under the image
wh_capacity_text = ctk.StringVar()
wh_capacity_label = ctk.CTkLabel(root, textvariable=wh_capacity_text, text_color="#ffd966")
wh_capacity_label.grid(row=9, column=0, columnspan=3, pady=(0, 12))

# --- S/P Variation UI ---
sp_var_frame = ctk.CTkFrame(root)
sp_var_frame.grid(row=10, column=0, columnspan=3, pady=(10, 0), sticky="ew")
ctk.CTkLabel(sp_var_frame, text="Pack Layout Preference:").grid(row=0, column=0, padx=8, pady=4)
sp_pref_var = ctk.StringVar(value="Balanced")
sp_pref_menu = ctk.CTkOptionMenu(sp_var_frame, variable=sp_pref_var, values=["Balanced", "More Series", "More Parallel"], width=140)
sp_pref_menu.grid(row=0, column=1, padx=8, pady=4)

# --- Helper to get S/P combo based on preference ---
def get_sp_combo(pack_capacity, pack_voltage, cell_capacity, cell_voltage, loss_percent, preference):
    usable_fraction = 1 - loss_percent / 100.0
    required_capacity = pack_capacity / usable_fraction
    combos = []
    for s in range(1, 21):
        for p in range(1, 21):
            v = s * cell_voltage
            c = p * cell_capacity
            if v >= pack_voltage and c >= required_capacity:
                combos.append((s, p))
    if not combos:
        return None, None
    # Balanced: minimum total cells
    if preference == "Balanced":
        return min(combos, key=lambda x: x[0]*x[1])
    # More Series: maximize series, minimize parallel
    if preference == "More Series":
        return max(combos, key=lambda x: (x[0], -x[1]))
    # More Parallel: maximize parallel, minimize series
    if preference == "More Parallel":
        return max(combos, key=lambda x: (x[1], -x[0]))
    return combos[0]

# --- Update image/Wh for selected S/P preference ---
def update_sp_image_and_wh():
    try:
        vals = [e.get() for e in entries]
        base_cell_capacity = float(vals[2])
        cell_capacity_variation = float(cell_capacity_var.get())
        adjusted_cell_capacity = base_cell_capacity * (cell_capacity_variation / 100.0)
        vals[2] = str(adjusted_cell_capacity)
        if pack_capacity_unit.get() == "Ah":
            vals[0] = str(float(vals[0]) * 1000)
        pack_capacity, pack_voltage, cell_capacity, cell_voltage = map(float, vals)
        loss_percent = float(loss_percent_var.get())
        preference = sp_pref_var.get()
        s, p = get_sp_combo(pack_capacity, pack_voltage, cell_capacity, cell_voltage, loss_percent, preference)
        if s is None or p is None:
            image_label.configure(image=None, text="No image")
            image_label.image = None
            wh_capacity_text.set("")
            return
        img = generate_battery_pack_image(s, p)
        if img is not None:
            img = img.resize((min(400, img.width), min(300, img.height)), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            image_label.configure(image=ctk_img, text="")
            image_label.image = ctk_img
        else:
            image_label.configure(image=None, text="No image")
            image_label.image = None
        wh_capacity = (s * cell_voltage) * (p * cell_capacity) / 1000.0
        wh_capacity_text.set(f"Pack Energy: {wh_capacity:.2f} Wh")
    except Exception:
        image_label.configure(image=None, text="No image")
        image_label.image = None
        wh_capacity_text.set("")

sp_pref_var.trace_add("write", lambda *args: update_sp_image_and_wh())

def calculate():
    try:
        vals = [e.get() for e in entries]
        # Apply the slider percentage to the cell capacity input
        base_cell_capacity = float(vals[2])
        cell_capacity_variation = float(cell_capacity_var.get())
        adjusted_cell_capacity = base_cell_capacity * (cell_capacity_variation / 100.0)
        vals[2] = str(adjusted_cell_capacity)
        # Convert pack capacity to mAh if user selected Ah
        if pack_capacity_unit.get() == "Ah":
            vals[0] = str(float(vals[0]) * 1000)
        if any(v.strip() == "" for v in vals):
            messagebox.showerror("Error", "All fields must be filled.")
            image_label.configure(image=None, text="No image")
            image_label.image = None
            wh_capacity_text.set("")
            return
        try:
            pack_capacity, pack_voltage, cell_capacity, cell_voltage = map(float, vals)
            loss_percent = float(loss_percent_var.get())
        except Exception:
            messagebox.showerror("Error", "All fields must be valid numbers.")
            image_label.configure(image=None, text="No image")
            image_label.image = None
            wh_capacity_text.set("")
            return
        if cell_voltage == 0 or cell_capacity == 0:
            messagebox.showerror("Error", "Cell voltage and capacity must not be zero.")
            image_label.configure(image=None, text="No image")
            image_label.image = None
            wh_capacity_text.set("")
            return
        usable_fraction = 1 - loss_percent / 100.0
        if not (0 < usable_fraction <= 1):
            messagebox.showerror("Error", "Loss percentage must be between 0 and 99.")
            image_label.configure(image=None, text="No image")
            image_label.image = None
            wh_capacity_text.set("")
            return
        required_capacity = pack_capacity / usable_fraction
        series_count = int(math.ceil(pack_voltage / cell_voltage))
        parallel_count = int(math.ceil(required_capacity / cell_capacity))
        if series_count <= 0 or parallel_count <= 0:
            messagebox.showerror("Error", "Calculation resulted in non-positive cell counts.")
            image_label.configure(image=None, text="No image")
            image_label.image = None
            wh_capacity_text.set("")
            return
        total_cells = series_count * parallel_count
        result_text.set(
            f"Adjusted for {loss_percent:.1f}% system losses:\n"
            f"Series cells (S): {series_count}\n"
            f"Parallel cells (P): {parallel_count}\n"
            f"Total 18650 cells needed: {total_cells}\n\n"
            f"Required total cell capacity: {required_capacity:.0f} mAh"
        )
        img = generate_battery_pack_image(series_count, parallel_count)
        if img is not None:
            img = img.resize((min(400, img.width), min(300, img.height)), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            image_label.configure(image=ctk_img, text="")
            image_label.image = ctk_img
        else:
            image_label.configure(image=None, text="No image")
            image_label.image = None
        wh_capacity = (series_count * cell_voltage) * (parallel_count * cell_capacity) / 1000.0
        wh_capacity_text.set(f"Pack Energy: {wh_capacity:.2f} Wh")
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        messagebox.showerror("Error", f"Invalid input: {e}")
        image_label.configure(image=None, text="No image")
        image_label.image = None
        wh_capacity_text.set("")

ctk.CTkButton(root, text="Calculate", command=calculate).grid(row=6, column=0, columnspan=3, pady=18)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()