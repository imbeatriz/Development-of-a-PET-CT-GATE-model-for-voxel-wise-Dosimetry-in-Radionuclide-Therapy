# import packages
import numpy as np
import SimpleITK as sitk
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk # pip install pillow

# --- Helper function to load medical images using SimpleITK ---
def load_image(path):
    """
    Loads a medical image using SimpleITK and converts it to a NumPy array.
    Returns both the NumPy array and the SimpleITK image object.
    """
    img = sitk.ReadImage(path)
    return sitk.GetArrayFromImage(img), img

# ==========================================================
# --- GUI FUNCTIONS ---
# ==========================================================

def select_dose_file():
    """Open file dialog to select Dose image and update entry field."""
    path = filedialog.askopenfilename(title="Select Dose image from MC-GATE Dosimetry simulation (calibrated or not)")
    if path:
        entry_dose.delete(0, tk.END)
        entry_dose.insert(0, path)

def select_unc_file():
    """Open file dialog to select relative Statistical Uncertainty image and update entry field."""
    path = filedialog.askopenfilename(title="Select relative Statistical Uncertainty image from MC-GATE Dosimetry simulation")
    if path:
        entry_unc.delete(0, tk.END)
        entry_unc.insert(0, path)

def select_roi_file():
    """Open file dialog to select VOI (Volume of Interest) mask image and update entry field."""
    path = filedialog.askopenfilename(title="Select VOI mark image")
    if path:
        entry_roi.delete(0, tk.END)
        entry_roi.insert(0, path)

def run_calculation():
    """
    Main function that computes the VOI statistics:
    - Loads Dose, relative Statictical Uncertainty, and VOI mask images
    - Checks that the images have the same dimensions
    - Computes counts in VOI
    - Computes absolute and relative statistical uncertainty in VOI
    - Displays results in a popup
    """
    dose_path = entry_dose.get()
    unc_path = entry_unc.get()
    roi_path = entry_roi.get()

    # Ensure all files are selected
    if not dose_path or not unc_path or not roi_path:
        messagebox.showerror("Error", "Please select all three files.")
        return

    try:
        # --- Load images ---
        dose_array, _ = load_image(dose_path)
        unc_array, _ = load_image(unc_path)
        roi_array, _ = load_image(roi_path)

        # --- Check that image shapes match ---
        if dose_array.shape != unc_array.shape or dose_array.shape != roi_array.shape:
            messagebox.showerror("Error", "Image shapes do not match!")
            return

        # --- Create VOI mask from ROI image ---
        voi_mask = roi_array > 0

        # --- Total dose counts inside VOI ---
        total_counts = np.sum(dose_array[voi_mask])

        # --- Compute absolute uncertainty inside VOI ---
        abs_unc_array = dose_array * unc_array
        total_abs_unc = np.sqrt(np.sum((abs_unc_array[voi_mask])**2))

        # --- Compute relative uncertainty in VOI ---
        if total_counts > 0:
            total_rel_unc = (total_abs_unc / total_counts) * 100
        else:
            total_rel_unc = np.nan

        # --- Show results in a popup window ---
        messagebox.showinfo("Results",
            f"Total counts in VOI: {total_counts:.2f}\n"
            f"Total Absolute Statistical Uncertainty: {total_abs_unc:.2f}\n"
            f"Statistical Uncertainty (%): {total_rel_unc:.4f} %"
        )

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

# ==========================================================
# --- MAIN WINDOW SETUP ---
# ==========================================================
root = tk.Tk()
root.title("MC-GATE Dosimetry simulations VOI Statistical Uncertainty")
root.geometry("600x300")
root.resizable(False, False)
root.configure(bg="#f2f4f7")

# --- Load folder icon for browse buttons ---
folder_icon = None
try:
    folder_img = Image.open("/home/administrator/Secretária/Github/Patient-Specific Phantom/folder.png")
    folder_img = folder_img.resize((24, 24), Image.LANCZOS)
    folder_icon = ImageTk.PhotoImage(folder_img)
except Exception as e:
    print(f"Folder icon not found or couldn't load: {e}")

# --- Dose image selection widgets ---
tk.Label(root, text="Select Dose image from MC-GATE Dosimetry simulation (calibrated or not):", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10,0))
frame_dose = tk.Frame(root, bg="#f2f4f7")
frame_dose.pack(fill="x", padx=10)
entry_dose = tk.Entry(frame_dose, width=60)
entry_dose.pack(side="left", fill="x", expand=True)
tk.Button(frame_dose, text="Browse", image=folder_icon, compound="left",
          command=select_dose_file, relief="flat", bg="#dcdcdc").pack(side="right", padx=5)

# --- Statistical Uncertainty image selection widgets ---
tk.Label(root, text="Select relative Statistical Uncertainty image from MC-GATE Dosimetry simulation:", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10,0))
frame_unc = tk.Frame(root, bg="#f2f4f7")
frame_unc.pack(fill="x", padx=10)
entry_unc = tk.Entry(frame_unc, width=60)
entry_unc.pack(side="left", fill="x", expand=True)
tk.Button(frame_unc, text="Browse", image=folder_icon, compound="left",
          command=select_unc_file, relief="flat", bg="#dcdcdc").pack(side="right", padx=5)

# --- VOI mask selection widgets ---
tk.Label(root, text="Select VOI mask image:", bg="#dcdcdc").pack(anchor="w", padx=10, pady=(10,0))
frame_roi = tk.Frame(root, bg="#f2f4f7")
frame_roi.pack(fill="x", padx=10)
entry_roi = tk.Entry(frame_roi, width=60)
entry_roi.pack(side="left", fill="x", expand=True)
tk.Button(frame_roi, text="Browse", image=folder_icon, compound="left",
          command=select_roi_file, relief="flat", bg="#dcdcdc").pack(side="right", padx=5)

# --- Button to compute VOI dose statistics ---
tk.Button(root, text="Compute VOI Dose Statictical Uncertainty Calculator", command=run_calculation,
          bg="#2e8b57", fg="white", height=2, font=("Arial", 11, "bold")).pack(pady=20)

root.mainloop()  # Start the GUI event loop
