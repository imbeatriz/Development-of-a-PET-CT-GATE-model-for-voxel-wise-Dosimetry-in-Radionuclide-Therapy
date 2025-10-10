import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk  # pip install pillow

# ====================================================================================
# --- Mapping of anatomical names to GATE material names (as in GateMaterials.db) ---
# ====================================================================================
# Edit these according to your segmentation VOIs and GATE material definitions
name_map = {
    'esophagus': 'SoftTissue',
    'vertebra': 'SpineBone',
    'right_hip': 'Bone',
    'spinal_cord': 'SoftTissue',
    'ribs': 'RibBone',
    'sternum': 'Sternum',
    'costal_cartilage': 'Cartilage',
    'body_trunc': 'Body',
    'right_kidney': 'Kidney',
    'left_kidney': 'Kidney',
    'gallbladder': 'Gallbladder',
    'liver': 'Liver',
    'stomach': 'Stomach',
    'right_adrenal_gland': 'Adrenal',
    'left_adrenal_gland': 'Adrenal',
    'lungs': 'Lung',
    'duodenum': 'SmallIntestine',
    'colon': 'Colon',
    'heart': 'Heart'
}


def normalize_name(name):
    return name.strip().lower().replace(" ", "_")


def generate_gate_range_translator(input_txt, output_dat):
    """Reads a segmentation label file and writes a GATE range translator .dat"""
    label_material_pairs = []

    with open(input_txt, 'r') as file:
        for line in file:
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                label = int(parts[0])
                raw_name = normalize_name(parts[1])
                material = name_map.get(raw_name, raw_name)
                label_material_pairs.append((label, material))

    label_material_pairs.sort()

    grouped_ranges = []
    i = 0
    while i < len(label_material_pairs):
        start_label, material = label_material_pairs[i]
        end_label = start_label
        j = i + 1
        while j < len(label_material_pairs) and \
              label_material_pairs[j][1] == material and \
              label_material_pairs[j][0] == end_label + 1:
            end_label = label_material_pairs[j][0]
            j += 1
        grouped_ranges.append((start_label, end_label, material))
        i = j

    with open(output_dat, 'w') as out_file:
        out_file.write(f"{len(grouped_ranges) + 1}\n")
        out_file.write("0 0 Air\n")
        for r in grouped_ranges:
            out_file.write(f"{r[0]} {r[1]} {r[2]}\n")

    messagebox.showinfo("Success", f"GATE-compatible range translator saved:\n{output_dat}")


# ==========================================================
# --- GUI FUNCTIONS ---
# ==========================================================
def select_input_file():
    file_path = filedialog.askopenfilename(
        title="Select segmentation label file",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, file_path)


def select_output_directory():
    dir_path = filedialog.askdirectory(title="Select output directory")
    if dir_path:
        entry_output_dir.delete(0, tk.END)
        entry_output_dir.insert(0, dir_path)


def run_converter():
    input_file = entry_input.get()
    output_dir = entry_output_dir.get()
    output_name = entry_output_name.get().strip()

    if not input_file or not os.path.exists(input_file):
        messagebox.showerror("Error", "Please select a valid input file.")
        return
    if not output_dir or not os.path.isdir(output_dir):
        messagebox.showerror("Error", "Please select a valid output directory.")
        return
    if not output_name:
        messagebox.showerror("Error", "Please enter a name for the output file.")
        return

    output_file = str(Path(output_dir) / (Path(output_name).stem + ".dat"))

    try:
        generate_gate_range_translator(input_file, output_file)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")


# ==========================================================
# --- MAIN WINDOW SETUP ---
# ==========================================================
root = tk.Tk()
root.title("GATE Range Translator Generator")
root.geometry("600x370")
root.resizable(False, False)
root.configure(bg="#f2f4f7")

# --- Header (Logo + Title Side by Side) ---
header_frame = tk.Frame(root, bg="#f2f4f7")
header_frame.pack(pady=10)

# Try to load the GATE logo
logo_path = "gate_logo.png"  # <--- UPDATE this path
try:
    logo_img = Image.open(logo_path)
    logo_img = logo_img.resize((90, 70), Image.LANCZOS)
    gate_logo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(header_frame, image=gate_logo, bg="#f2f4f7")
    logo_label.pack(side="left", padx=10)
except Exception as e:
    print(f"Logo not found or couldn't load: {e}")

title_label = tk.Label(header_frame, text="Range Translator Generator",
                       font=("Arial", 18, "bold"), bg="#f2f4f7", fg="#003366")
title_label.pack(side="left", padx=10)

# --- Folder icon for buttons ---
folder_icon = None
try:
    folder_img = Image.open("folder.png")  # <--- UPDATE this path
    folder_img = folder_img.resize((24, 24), Image.LANCZOS)
    folder_icon = ImageTk.PhotoImage(folder_img)
except Exception as e:
    print(f"Folder icon not found or couldn't load: {e}")

# --- Input File ---
tk.Label(root, text="Select input segmentation labels file (.txt):", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10, 0))
frame_input = tk.Frame(root, bg="#f2f4f7")
frame_input.pack(fill="x", padx=10)
entry_input = tk.Entry(frame_input, width=60)
entry_input.pack(side="left", fill="x", expand=True)
tk.Button(frame_input, image=folder_icon, text="Browse" if not folder_icon else "",
          command=select_input_file, relief="flat", bg="#f2f4f7").pack(side="right", padx=5)

# --- Output File Name ---
tk.Label(root, text="Enter output .dat file name (without extension):", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10, 0))
frame_name = tk.Frame(root, bg="#f2f4f7")
frame_name.pack(fill="x", padx=10)
entry_output_name = tk.Entry(frame_name, width=60)
entry_output_name.pack(side="left", fill="x", expand=True)

# --- Output Directory ---
tk.Label(root, text="Select directory to save the .dat file:", bg="#f2f4f7").pack(anchor="w", padx=10, pady=(10, 0))
frame_dir = tk.Frame(root, bg="#f2f4f7")
frame_dir.pack(fill="x", padx=10)
entry_output_dir = tk.Entry(frame_dir, width=60)
entry_output_dir.pack(side="left", fill="x", expand=True)
tk.Button(frame_dir, image=folder_icon, text="Browse" if not folder_icon else "",
          command=select_output_directory, relief="flat", bg="#f2f4f7").pack(side="right", padx=5)

# --- Run Button ---
tk.Button(root, text="Generate GATE Range Translator", command=run_converter,
          bg="#2e8b57", fg="white", height=2, font=("Arial", 11, "bold")).pack(pady=20)

root.mainloop()