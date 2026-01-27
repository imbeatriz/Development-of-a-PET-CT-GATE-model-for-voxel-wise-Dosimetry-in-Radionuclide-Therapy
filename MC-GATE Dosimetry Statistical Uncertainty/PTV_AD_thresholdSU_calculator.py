# Import packages
import numpy as np
import SimpleITK as sitk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

# Helpers
def load_image(path):
    img = sitk.ReadImage(path)
    return sitk.GetArrayFromImage(img), img

# File Selection
def select_dose():
    path = filedialog.askopenfilename(
        title="Select the calibrated Dose image (NIfTI / MHD):",
        filetypes=[("NIfTI", "*.nii *.nii.gz"), ("MetaImage", "*.mhd"), ("All files", "*.*")]
    )
    if path:
        entry_dose.delete(0, tk.END)
        entry_dose.insert(0, path)


def select_unc():
    path = filedialog.askopenfilename(
        title="Select Relative Statistical Uncertainty image (NIfTI / MHD):",
        filetypes=[("NIfTI", "*.nii *.nii.gz"), ("MetaImage", "*.mhd"), ("All files", "*.*")]
    )
    if path:
        entry_unc.delete(0, tk.END)
        entry_unc.insert(0, path)


def select_voi():
    path = filedialog.askopenfilename(
        title="Select PTV VOI:",
        filetypes=[("NIfTI", "*.nii *.nii.gz")]
    )
    if path:
        entry_voi.delete(0, tk.END)
        entry_voi.insert(0, path)

# Results Display
def display_results(results):
    text_results.config(state="normal")
    text_results.delete("1.0", tk.END)

    for key, value in results.items():
        text_results.insert(tk.END, f"{key}: {value}\n")

    text_results.config(state="disabled")


# Main Calculations
def run_calculation():

    dose_path = entry_dose.get()
    unc_path = entry_unc.get()
    voi_path = entry_voi.get()

    if not dose_path or not unc_path or not voi_path:
        messagebox.showerror(
            "Error",
            "Please select Dose file, Dose Statistical Uncertainty file and PTV VOI file."
        )
        return

    # --------------------------
    # Read number of primaries
    # --------------------------
    try:
        N_current = float(entry_primaries.get())
        if N_current <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Error",
            "Total number of primaries must be a positive number."
        )
        return

    try:
        # Load images
        dose, _ = load_image(dose_path)
        rel_unc, _ = load_image(unc_path)
        voi, _ = load_image(voi_path)

        if dose.shape != rel_unc.shape or dose.shape != voi.shape:
            messagebox.showerror(
                "Error",
                "Dose and Dose Statistical Uncertainty images do not match!"
            )
            return

        # Masks
        voi_mask = voi > 0
        n_vox_voi = np.count_nonzero(voi_mask)

        if n_vox_voi == 0:
            messagebox.showerror("Error", "VOI contains no voxels.")
            return

        dose_threshold = 80.0  # Gy
        high_dose_mask = voi_mask & (dose > dose_threshold)
        n_vox_high = np.count_nonzero(high_dose_mask)

        if n_vox_high == 0:
            messagebox.showinfo(
                "Result",
                "No voxels in VOI with Dose > 80 Gy."
            )
            return

        # --------------------------
        # Mean absorbed dose
        # --------------------------
        mean_dose_voi = np.mean(dose[voi_mask])
        mean_dose_high = np.mean(dose[high_dose_mask])

        # --------------------------
        # SU propagation
        # --------------------------
        abs_unc = dose * rel_unc
        sum_sigma2 = np.sum((abs_unc ** 2)[high_dose_mask])
        total_unc = np.sqrt(sum_sigma2)

        mean_unc = total_unc / n_vox_high
        mean_unc_per = mean_unc * 100
        rel_unc_percent = (mean_unc / mean_dose_high) * 100

        fraction = n_vox_high / n_vox_voi

        # ==================================================
        # MC scaling to reach target SU
        # ==================================================
        TARGET_SU = 2.0  # %

        # Use the actual mean_unc_per for calculation
        current_su = mean_unc_per
        
        # Get the rounded value for display and comparison
        current_su_rounded = round(current_su, 1)
        
        if current_su_rounded <= TARGET_SU:
            M = 1.0
            runs_required = 1
            N_required = N_current
            scaling_text = (
                f"Target achieved! Current mean SU = {current_su_rounded:.1f}% "
                f"(<= {TARGET_SU:.1f}%)"
            )
        else:
            M = (current_su / TARGET_SU) ** 2
            runs_required = int(np.ceil(M))
            N_required = N_current * M
            scaling_text = (
                f"To reduce mean SU from {current_su_rounded:.1f}% to {TARGET_SU:.1f}%:\n"
                f"  Multiplier M = {M:.3f}\n"
                f"  Required total primaries ≈ {N_required:.3e}\n"
                f"  Expected SU after combination ≈ "
                f"{current_su / np.sqrt(runs_required):.2f}%"
            )

        # --------------------------
        # Results
        # --------------------------
        results = {
            "VOI": os.path.basename(voi_path),
            "Mean Absorbed Dose PTV (Gy)": f"{mean_dose_voi:.2f}",
            "Mean Absorbed Dose PTV (Dose > 80 Gy) (Gy)": f"{mean_dose_high:.2f}",
            "Total PTV Voxels": n_vox_voi,
            "Total PTV Voxels > 80 Gy": n_vox_high,
            "Fraction > 80 Gy": f"{fraction:.3f}",
            "Mean Absolute SU (Gy)": f"{mean_unc:.5f}",
            "Mean Absolute SU (%)": f"{current_su_rounded:.1f}",
            "Mean Relative SU (%)": f"{rel_unc_percent:.5f}",
            "Current MC primaries": f"{N_current:.3e}",
            "Target mean SU (%)": f"{TARGET_SU:.1f}",
            "MC-GATE Simulation Runs Summary": scaling_text
        }

        display_results(results)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==========================================================
# GUI LAYOUT
# ==========================================================
root = tk.Tk()
root.title("PTV Dose > 80 Gy Statistical Uncertainty Calculator")
root.geometry("890x560")
root.resizable(True, True)

# Input frame
frame_inputs = ttk.LabelFrame(root, text="Input Files", padding=10)
frame_inputs.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_inputs, text="Select the calibrated Dose image (NIfTI / MHD):").grid(row=0, column=0, sticky="w", pady=5)
entry_dose = ttk.Entry(frame_inputs, width=60)
entry_dose.grid(row=0, column=1, padx=5)
ttk.Button(frame_inputs, text="Browse", command=select_dose).grid(row=0, column=2)

ttk.Label(frame_inputs, text="Select Relative Statistical Uncertainty image (NIfTI / MHD):").grid(row=1, column=0, sticky="w", pady=5)
entry_unc = ttk.Entry(frame_inputs, width=60)
entry_unc.grid(row=1, column=1, padx=5)
ttk.Button(frame_inputs, text="Browse", command=select_unc).grid(row=1, column=2)

ttk.Label(frame_inputs, text="Select PTV VOI:").grid(row=2, column=0, sticky="w", pady=5)
entry_voi = ttk.Entry(frame_inputs, width=60)
entry_voi.grid(row=2, column=1, padx=5)
ttk.Button(frame_inputs, text="Browse", command=select_voi).grid(row=2, column=2)

ttk.Label(
    frame_inputs,
    text="Total MC-GATE primaries used:"
).grid(row=3, column=0, sticky="w", pady=5)

entry_primaries = ttk.Entry(frame_inputs, width=25)
entry_primaries.grid(row=3, column=1, sticky="w", padx=5)
entry_primaries.insert(0, "1.18e8")

# --------------------------
# Compute button
# --------------------------
tk.Button(
    root,
    text="Compute PTV Dose > 80 Gy SU",
    command=run_calculation,
    bg="#2e8b57",
    fg="white",
    activebackground="#276749",
    activeforeground="white",
    font=("Arial", 11, "bold"),
    height=2
).pack(pady=10)

# Results frame
frame_results = ttk.LabelFrame(root, text="Results", padding=10)
frame_results.pack(fill="both", expand=True, padx=10, pady=10)

text_results = tk.Text(
    frame_results,
    height=12,
    wrap="word",
    font=("Courier", 11)
)
text_results.pack(fill="both", expand=True)
text_results.config(state="disabled")

# ==========================================================
# START GUI
# ==========================================================
root.mainloop()
