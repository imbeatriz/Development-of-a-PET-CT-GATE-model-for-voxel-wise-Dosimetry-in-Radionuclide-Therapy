# import packages
import numpy as np
import SimpleITK as sitk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import pandas as pd

# Helper function to load medical images using SimpleITK
def load_image(path):
    img = sitk.ReadImage(path)
    return sitk.GetArrayFromImage(img), img

# ==========================================================
# --- GUI FUNCTIONS ---
# ==========================================================

def select_dose_file():
    path = filedialog.askopenfilename(
        title="Select the calibrated Dose image (NIfTI / MHD)",
        filetypes=[("NIfTI", "*.nii *.nii.gz"), ("MetaImage", "*.mhd"), ("All files", "*.*")]
    )
    if path:
        entry_dose.delete(0, tk.END)
        entry_dose.insert(0, path)

def select_unc_file():
    path = filedialog.askopenfilename(
        title="Select Relative Statistical Uncertainty image from direct MC-GATE dosimetry simulation (NIfTI / MHD)",
        filetypes=[("NIfTI", "*.nii *.nii.gz"), ("MetaImage", "*.mhd"), ("All files", "*.*")]
    )
    if path:
        entry_unc.delete(0, tk.END)
        entry_unc.insert(0, path)

def select_voi_folder():
    path = filedialog.askdirectory(title="Select VOI folder (should contain all the VOI .nii files)")
    if path:
        entry_voi.delete(0, tk.END)
        entry_voi.insert(0, path)

def run_calculation():
    dose_path = entry_dose.get()
    unc_path = entry_unc.get()
    voi_folder = entry_voi.get()

    if not dose_path or not unc_path or not voi_folder:
        messagebox.showerror("Error", "Please select Dose file, Dose Statistical Uncertainty file and VOI folder.")
        return

    try:
        # Load images
        dose_array, dose_img = load_image(dose_path)
        unc_array, _ = load_image(unc_path)

        # Check shape match
        if dose_array.shape != unc_array.shape:
            messagebox.showerror("Error", "Dose and Dose Statistical Uncertainty images do not match!")
            return

        # Compute absolute uncertainty voxel-wise
        abs_unc_array = dose_array * unc_array

        # Compute squared uncertainty
        abs_unc_sq_array = abs_unc_array ** 2

        results = []

        # Loop over VOIs
        for filename in os.listdir(voi_folder):
            if filename.endswith(".nii") or filename.endswith(".nii.gz"):
                voi_path = os.path.join(voi_folder, filename)

                voi_array, _ = load_image(voi_path)

                # Shape check
                if voi_array.shape != dose_array.shape:
                    print(f"Skipping {filename}: shape mismatch")
                    continue

                mask = voi_array > 0
                n_voxels = np.count_nonzero(mask)

                if n_voxels == 0:
                    continue

                # Mean absorbed dose in VOI
                mean_dose = np.mean(dose_array[mask])

                # Sum of sigma^2
                sum_sigma2 = np.sum(abs_unc_sq_array[mask])

                # Total uncertainty in VOI (absolute)
                total_uncertainty = np.sqrt(sum_sigma2)

                # Mean absolute uncertainty per voxel
                mean_uncertainty_per_voxel = total_uncertainty / n_voxels

                # Mean absolute uncertainty per voxel percentage
                mean_abs_SU_per = mean_uncertainty_per_voxel * 100

                # Relative SU (%) for mean dose
                rel_unc_percent = (mean_uncertainty_per_voxel / mean_dose) * 100 if mean_dose != 0 else 0

                # Format values
                mean_dose_f = f"{mean_dose:.2f}"
                total_unc_f = f"{total_uncertainty:.2f}"
                mean_unc_voxel_f = f"{mean_uncertainty_per_voxel:.5f}"
                mean_abs_SU_per_f = f"{mean_abs_SU_per:.5f}"
                rel_unc_percent_f = f"{rel_unc_percent:.5f}"

                results.append({
                    "VOI": filename,
                    "Voxels": n_voxels,
                    "Mean Absorbed Dose (Gy)": mean_dose_f,
                    "Total SU (Gy)": total_unc_f,
                    "Mean Absolute SU (Gy)": mean_unc_voxel_f,
                    "Mean Absolute SU (%)":mean_abs_SU_per_f,
                    "Mean Relative SU (%)": rel_unc_percent_f
                })

        # Convert results to DataFrame
        df = pd.DataFrame(results)

        if df.empty:
            messagebox.showinfo("Results", "No VOIs found or all VOIs were skipped (shape mismatch).")
            return

        # Display results in table
        display_table(df)

        # Save to CSV
        csv_path = os.path.join(voi_folder, "VOI_SU_results.csv")
        df.to_csv(csv_path, index=False)
        messagebox.showinfo("Done", f"Results saved to:\n{csv_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

def display_table(df):
    # Clear previous table if exists
    for widget in frame_table.winfo_children():
        widget.destroy()

    table = ttk.Treeview(frame_table)
    table["columns"] = list(df.columns)
    table["show"] = "headings"

    for col in df.columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", width=200)

    for _, row in df.iterrows():
        table.insert("", "end", values=list(row))

    table.pack(fill="both", expand=True)

# ==========================================================
# --- MAIN WINDOW SETUP ---
# ==========================================================
root = tk.Tk()
root.title("MC-GATE Dosimetry simulations VOI Statistical Uncertainty Calculator")

# LARGER WINDOW & RESIZABLE
root.geometry("1200x800")
root.resizable(True, True)
root.configure(bg="#f2f4f7")

# Table style (bigger font)
style = ttk.Style()
style.configure("Treeview", font=("Arial", 12))
style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

# Dose selection
tk.Label(root, text="Select the calibrated Dose image (NIfTI / MHD):", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10,0))
frame_dose = tk.Frame(root, bg="#f2f4f7")
frame_dose.pack(fill="x", padx=10)
entry_dose = tk.Entry(frame_dose, width=70)
entry_dose.pack(side="left", fill="x", expand=True)
tk.Button(frame_dose, text="Browse", command=select_dose_file, bg="#dcdcdc").pack(side="right", padx=5)

# Uncertainty selection
tk.Label(root, text="Select Relative Statistical Uncertainty image from direct MC-GATE dosimetry simulation (NIfTI / MHD):", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10,0))
frame_unc = tk.Frame(root, bg="#f2f4f7")
frame_unc.pack(fill="x", padx=10)
entry_unc = tk.Entry(frame_unc, width=70)
entry_unc.pack(side="left", fill="x", expand=True)
tk.Button(frame_unc, text="Browse", command=select_unc_file, bg="#dcdcdc").pack(side="right", padx=5)

# VOI folder selection
tk.Label(root, text="Select VOI folder (should contain all the VOI .nii files):", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10,0))
frame_voi = tk.Frame(root, bg="#f2f4f7")
frame_voi.pack(fill="x", padx=10)
entry_voi = tk.Entry(frame_voi, width=70)
entry_voi.pack(side="left", fill="x", expand=True)
tk.Button(frame_voi, text="Browse", command=select_voi_folder, bg="#dcdcdc").pack(side="right", padx=5)

# Compute button
tk.Button(root, text="Compute each VOI Dose Statistical Uncertainty", command=run_calculation,
          bg="#2e8b57", fg="white", height=2, font=("Arial", 11, "bold")).pack(pady=15)

# Table display frame
frame_table = tk.Frame(root, bg="#f2f4f7")
frame_table.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()
