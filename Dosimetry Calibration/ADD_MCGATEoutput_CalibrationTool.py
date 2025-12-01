import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import nibabel as nib
import os

def dosimetry_calibration_mc(GATEoutput, PET, RWLV, AA_MBq, R_percent, LSF_percent, N_millions):
    """
    Calibrate GATE Monte Carlo absorbed dose  distribution output.
    Calibrates a personalized GATE's output absorbed dose distribution according to Y90 radioactive decay over time and patient's administrated 
    activity of Y90 within the reference whole liver volume, measured vial residue waste, estimated lung shunt fraction and the total number of primary particles (needs to be given in millions).
    """

    # Y-90 half-life (s)
    half_life = 2.7 * 24 * 60 * 60  
    # lambda calculation
    lambda_int = half_life / np.log(2)

    # PET image counts
    # RWLV image counts
    counts_pet = PET.sum()
    counts_RWLV = PET[RWLV > 0].sum()

    # Calibration factor formula
    calb_factor = (counts_pet / counts_RWLV) * AA_MBq * \
                  (1 - LSF_percent/100) * (1 - R_percent/100) * \
                  (lambda_int / N_millions)

    return GATEoutput * calb_factor

def run_calibration():
    try:
        # Get values from GUI
        AA_MBq = float(entry_activity.get())
        R_percent = float(entry_residue.get())
        LSF_percent = float(entry_lsf.get())
        N_millions = float(entry_nmillions.get())

        # Load NIfTI files
        gate_img = nib.load(entry_gate.get())
        GATEoutput = gate_img.get_fdata()
        
        pet_img = nib.load(entry_pet.get())
        PET = pet_img.get_fdata()

        rwlv_img = nib.load(entry_rwlv.get())
        RWLV = rwlv_img.get_fdata()

        # Run calibration
        ADD_array = dosimetry_calibration_mc(GATEoutput, PET, RWLV, AA_MBq, R_percent, LSF_percent, N_millions)

        # Ask where to save
        save_path = filedialog.asksaveasfilename(
            defaultextension=".nii.gz",
            filetypes=[("NIfTI files", "*.nii.gz"), ("NIfTI files", "*.nii")],
            title="Save calibrated dose image"
        )

        if not save_path:
            return  # User cancelled save dialog

        # Save as NIfTI
        ADD_nii = nib.Nifti1Image(ADD_array, affine=pet_img.affine, header=pet_img.header)
        nib.save(ADD_nii, save_path)

        messagebox.showinfo("Success", f"Calibrated absorbed dose saved at:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

def browse_file(entry):
    filename = filedialog.askopenfilename(
        filetypes=[
            ("All files", "*.*"),
            ("NIfTI files", "*.nii *.nii.gz")
        ]
    )
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

# ----------------- GUI -----------------
root = tk.Tk()
root.title("Monte Carlo Absorbed Dose Distribution Calibration")

# Load folder icon
folder_img = tk.PhotoImage(file="Github/Dosimetry Calculations/folder.png") # change the name for your directory if needed
folder_img = folder_img.subsample(6,6)

# --- File selectors ---
tk.Label(root, text="GATE Dose Output (.nii/.nii.gz):").grid(row=0, column=0, sticky="e")
entry_gate = tk.Entry(root, width=60)
entry_gate.grid(row=0, column=1)
tk.Button(root, image=folder_img, command=lambda: browse_file(entry_gate)).grid(row=0, column=2)

tk.Label(root, text="PET Image (.nii/.nii.gz):").grid(row=1, column=0, sticky="e")
entry_pet = tk.Entry(root, width=60)
entry_pet.grid(row=1, column=1)
tk.Button(root, image=folder_img, command=lambda: browse_file(entry_pet)).grid(row=1, column=2)

tk.Label(root, text="RWLV Segmentation (.nii/.nii.gz):").grid(row=2, column=0, sticky="e")
entry_rwlv = tk.Entry(root, width=60)
entry_rwlv.grid(row=2, column=1)
tk.Button(root, image=folder_img, command=lambda: browse_file(entry_rwlv)).grid(row=2, column=2)

# --- Parameters ---
tk.Label(root, text="Administered Activity (MBq):").grid(row=3, column=0, sticky="e")
entry_activity = tk.Entry(root)
entry_activity.grid(row=3, column=1)

tk.Label(root, text="Vial Residue waste (%):").grid(row=4, column=0, sticky="e")
entry_residue = tk.Entry(root)
entry_residue.grid(row=4, column=1)

tk.Label(root, text="Lung Shunt Fraction (%):").grid(row=5, column=0, sticky="e")
entry_lsf = tk.Entry(root)
entry_lsf.grid(row=5, column=1)

tk.Label(root, text="Number of Primaries (in millions):").grid(row=6, column=0, sticky="e")
entry_nmillions = tk.Entry(root)
entry_nmillions.grid(row=6, column=1)

# --- Run button ---
tk.Button(root, text="Calibrate and Save ADD Calibrated result", command=run_calibration, bg="green", fg="white").grid(row=7, column=0, columnspan=3, pady=10)

root.mainloop()
