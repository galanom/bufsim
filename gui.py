import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def get_params():
    result = {}

    def on_ok():
        try:
            if batch_var.get():
                manual_var.set(False)  # Force manual to False if batch is enabled
            result["z"] = int(z_var.get())
            result["x"] = int(x_var.get())
            result["t_shift"] = int(t_shift_var.get())
            result["read_size"] = int(read_size_var.get())
            result["batch"] = batch_var.get()
            result["cell_size"] = int(cell_size_var.get())
            result["delay"] = int(delay_var.get())
            result["manual"] = manual_var.get()
            root.quit()  # Stop the mainloop instead of destroying
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")

    def on_cancel():
        result.clear()  # Ensure result is empty if cancelled
        root.quit()

    def toggle_manual():
        if batch_var.get():
            manual_var.set(False)
            manual_check.config(state="disabled")
            manual_label.config(foreground="gray")  # Gray out the text label
        else:
            manual_check.config(state="normal")
            manual_label.config(foreground="black")  # Restore text color

    root = tk.Tk()
    root.title("Enter Parameters")

    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0)

    z_var = tk.StringVar(value="8")
    x_var = tk.StringVar(value="8")
    t_shift_var = tk.StringVar(value="65")
    read_size_var = tk.StringVar(value="8")
    batch_var = tk.BooleanVar(value=False)
    cell_size_var = tk.StringVar(value="24")
    delay_var = tk.StringVar(value="100")
    manual_var = tk.BooleanVar(value=True)

    def create_entry(label, var, row, hint):
        lbl = ttk.Label(frame, text=label)
        lbl.grid(row=row, column=0, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(frame, textvariable=var)
        entry.grid(row=row, column=1, padx=5, pady=2)

    ttk.Label(frame, text="Main Parameters", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
    create_entry("z:", z_var, 1, "Number of bands")
    create_entry("x:", x_var, 2, "Pixel count of the x dimension")
    create_entry("t_shift:", t_shift_var, 3, "Time delay before reader starts")
    create_entry("read_size:", read_size_var, 4, "Pipeline depth")

    ttk.Label(frame, text="Batch mode:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
    batch_check = ttk.Checkbutton(frame, variable=batch_var, command=toggle_manual)
    batch_check.grid(row=5, column=1, padx=5, pady=2)

    ttk.Separator(frame, orient="horizontal").grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

    ttk.Label(frame, text="Display Settings", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=2, pady=5)
    create_entry("cell_size:", cell_size_var, 8, "Display size of cell")
    create_entry("delay:", delay_var, 9, "Step delay for animation in ms")

    manual_label = ttk.Label(frame, text="Manual stepping:")
    manual_label.grid(row=10, column=0, sticky="w", padx=5, pady=2)

    manual_check = ttk.Checkbutton(frame, variable=manual_var)
    manual_check.grid(row=10, column=1, padx=5, pady=2)

    hint_label = ttk.Label(frame, text="", foreground="gray")
    hint_label.grid(row=11, column=0, columnspan=2, pady=5)

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=12, column=0, columnspan=2, pady=10)
    ttk.Button(button_frame, text="OK", command=on_ok).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="right", padx=5)

    root.mainloop()  # Wait for user interaction
    root.destroy()  # Properly close the window

    return result  # Return the dictionary with the user inputs

def Checkerboard(z, x, t_shift, read_size, cell_size, delay, manual):
    print(f"Running Checkerboard with: z={z}, x={x}, t_shift={t_shift}, read_size={read_size}, cell_size={cell_size}, delay={delay}, manual={manual}")

