# import packages, verify if they are all installed in your python
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import tkinter.scrolledtext as st
import tkinter.font as tkfont
from ttkbootstrap import Style
import ttkbootstrap as ttk
import shlex
import subprocess

class GATERootToCastorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CASToR - GATERootToCastor GUI")
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        # Use same logos (expects CASToR_logo.png and folder.png in same folder)
        try:
            self.iconphoto(False, tk.PhotoImage(file=os.path.join(self.script_dir, 'CASToR_logo.png')))
        except Exception:
            pass
        self.home_dir = str(Path.home())

        # Window and style
        self.resizable(True, True)
        self.minsize(675, 482)
        self.style = Style(theme='darkly')

        # Variables
        # Mandatory
        self.input_root_var = tk.StringVar()
        self.input_list_var = tk.StringVar()
        self.scanner_alias_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.macro_file_var = tk.StringVar()

        # Optional flags / args
        self.prompt_type_var = tk.StringVar(value="")  # e.g. -t, -os, ...
        self.cf_var = tk.StringVar()
        self.histogram_bool = tk.BooleanVar(value=False)
        self.norm_file_var = tk.StringVar()
        self.norm_list_var = tk.StringVar()
        self.norm_img_var = tk.StringVar()
        self.atn_var = tk.StringVar()     # format: path:proj (user supplies)
        self.k_bool = tk.BooleanVar(value=False)  # -k
        self.isotope_var = tk.StringVar()  # -ist
        self.tof_reso_var = tk.StringVar()
        self.tof_branch_var = tk.StringVar()
        self.tof_range_var = tk.StringVar()
        self.geo_bool = tk.BooleanVar(value=False)
        self.threads_var = tk.StringVar()
        self.conf_dir_var = tk.StringVar()
        self.vb_var = tk.StringVar(value="1")
        
        # Miscellaneous variables
        self.mpi_bool_var = tk.BooleanVar(value=False)
        self.stats_need_bool_var = tk.BooleanVar(value=True)
        self.mpi_threads_var = tk.IntVar(value=0)
        self.verbose_level_var = tk.IntVar(value=2)
        # New variable for the working directory
        self.working_dir_var = tk.StringVar(value=self.home_dir)

        # Build UI
        self.create_menu()
        self.create_widgets()

    # ---------------- UI ----------------
    def create_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Print all variables", command=self.print_all_variables)
        file_menu.add_command(label="Exit", command=self.quit)
        self.menubar.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        # Title
        ttk.Label(self, text="CASToR-GATERootToCastor GUI", font=("Helvetica", 16, "bold")).pack(pady=(10,5))

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        # Configure grid weights for main frame
        main_frame.columnconfigure(0, weight=1)  
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1) 
        
        # Row 0 and Row 1 are set to weight 0 to shrink wrap around the contents
        main_frame.rowconfigure(0, weight=0) 
        main_frame.rowconfigure(1, weight=0) 
        main_frame.rowconfigure(2, weight=1) # Filler row, if needed for expansion

        # Left: Mandatory settings (row 0, column 0)
        mand_frame = ttk.LabelFrame(main_frame, text="Mandatory Settings")
        mand_frame.grid(row=0, column=0, sticky="nw", padx=(5, 2), pady=5)
        mand_frame.columnconfigure(1, weight=1)  

        # Middle: Data corrections (row 0, column 1)
        data_corr_frame = ttk.LabelFrame(main_frame, text="Data Corrections (Optional)")
        data_corr_frame.grid(row=0, column=1, sticky="nw", padx=(5, 2), pady=5)
        data_corr_frame.columnconfigure(1, weight=1)

        # Right: Attenuation and normalization (row 0, column 2)
        norm_atn_frame = ttk.LabelFrame(main_frame, text="Attenuation & Normalization Corrections (Optional)")
        norm_atn_frame.grid(row=0, column=2, sticky="nw", padx=(5, 2), pady=5)
        norm_atn_frame.columnconfigure(1, weight=1)

        # --- ROW 1: Bottom section reorganized ---
        
        # New Bottom Left: Miscellaneous (MOVED to row 1, column 0)
        misc_frame = ttk.LabelFrame(main_frame, text="Miscellaneous")
        # Placing it in row 1, column 0, directly below Mandatory Settings
        misc_frame.grid(row=1, column=0, sticky="nw", padx=(5, 2), pady=5)
        misc_frame.columnconfigure(1, weight=1)

        # New Bottom Middle/Right: Output/Calibration Settings (MOVED to row 1, columns 1 & 2)
        combined_output_calib_frame = ttk.LabelFrame(main_frame, text="Output/Calibration Settings (Optional)")
        # This frame now spans columns 1 and 2, placing it directly below Data Corrections and Attenuation/Normalization
        combined_output_calib_frame.grid(row=1, column=1, columnspan=2, sticky="nw", padx=(5, 2), pady=5)
        combined_output_calib_frame.columnconfigure(1, weight=1)
        
        
        # Folder icon (same as other script)
        try:
            self.folder_icon = tk.PhotoImage(file=os.path.join(self.script_dir, 'folder.png'))
            self.folder_icon = self.folder_icon.subsample(8, 8)
        except Exception:
            self.folder_icon = None

        # --- Mandatory rows ---
        self.add_file_row(mand_frame, "Input GATE .root file:", self.input_root_var, row=0)
        self.add_file_row(mand_frame, "Input .txt list file:", self.input_list_var, row=1)
        self.add_file_row(mand_frame, "GATE Macro file:", self.macro_file_var, row=2)
        # Browse type 'none' - Folder icon removed, user must type the name/path.
        self.add_entry_row(mand_frame, "Output file name:", self.output_file_var, row=3)

        # Browse type 'none' - Folder icon removed, user must type the name/path.
        self.add_entry_row(mand_frame, "Scanner geometry file:", self.scanner_alias_var, row=4)
        
        # Geometry option in mandatory section with info
        geo_frame = ttk.Frame(mand_frame)
        geo_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 5))
        ttk.Checkbutton(geo_frame, text="Generate geometry scanner file", 
                            variable=self.geo_bool).grid(row=0, column=0, sticky="w")
        ttk.Label(geo_frame, text="(Only if scanner geometry file wasn't generated previously)", 
                    font=("", 8), foreground="gray").grid(row=1, column=0, sticky="w", padx=(20, 0))

        # --- Data Corrections Frame ---
        # Prompt type options
        ttk.Label(data_corr_frame, text="Coincidences types to recover:", font=("", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(5,2), pady=3)
        prompt_opts = [
            ("Trues (non-scattered)", "-t"),
            ("Scattered (Compton and Rayleigh Scattering)", "-os"), 
            ("Random only ", "-or"),
            ("Trues + scattered (scattered and unscattered)", "-ots"),
            ("Trues + random (non scattered)", "-otr")
        ]
        
        for i, (lab, val) in enumerate(prompt_opts):
            ttk.Radiobutton(data_corr_frame, text=lab, variable=self.prompt_type_var, value=val).grid(
                row=1+i, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        # TOF options (now grouped in Data Corrections Frame, rows 7-10)
        ttk.Label(data_corr_frame, text="TOF Options:", font=("", 9, "bold")).grid(
            row=7, column=0, sticky="w", pady=(10, 5))
        self.add_entry_row(data_corr_frame, "TOF resolution [ps]:", self.tof_reso_var, row=8)
        self.add_entry_row(data_corr_frame, "TOF branch name:", self.tof_branch_var, row=9)
        self.add_entry_row(data_corr_frame, "TOF range [ps]:", self.tof_range_var, row=10)

        # --- Norm & Attenuation Frame ---
        # Norm and norm image
        self.add_file_row(norm_atn_frame, "Normalization .root file:", self.norm_file_var, row=0)
        self.add_file_row(norm_atn_frame, "Normalization .txt list:", self.norm_list_var, row=1)
        self.add_file_row(norm_atn_frame, "Normalization hdr file:", self.norm_img_var, row=2)

        # Attenuation with folder icon
        ttk.Label(norm_atn_frame, text="Attenuation hdr file:").grid(row=3, column=0, sticky="w", padx=(5,2), pady=3)
        ent_atn = ttk.Entry(norm_atn_frame, textvariable=self.atn_var, width=30)
        ent_atn.grid(row=3, column=1, sticky="we", padx=(2,4))
        if self.folder_icon:
            btn_atn = ttk.Button(norm_atn_frame, image=self.folder_icon, 
                                 command=lambda: self.browse_open(self.atn_var))
            btn_atn.grid(row=3, column=2, padx=(2,6))
        else:
            btn_atn = ttk.Button(norm_atn_frame, text="Browse", 
                                 command=lambda: self.browse_open(self.atn_var))
            btn_atn.grid(row=3, column=2, padx=(2,6))
        norm_atn_frame.columnconfigure(1, weight=1)

        # --- Combined Output/Calibration Frame (Row 1, Columns 1-2) ---
        # List mode and histogram output together (Output Format)
        output_sub_frame = ttk.Frame(combined_output_calib_frame)
        output_sub_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(output_sub_frame, text="List-mode output", variable=self.k_bool).pack(
            side=tk.LEFT, padx=5)
        ttk.Checkbutton(output_sub_frame, text="Histogram output", variable=self.histogram_bool).pack(
            side=tk.LEFT, padx=5)

        # Calibration & Isotope 
        calib_sub_frame = ttk.Frame(combined_output_calib_frame)
        calib_sub_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.add_entry_row(calib_sub_frame, "Calibration factor:", self.cf_var, row=0, col=0)
        self.add_entry_row(calib_sub_frame, "Isotope:", self.isotope_var, row=1, col=0)
        calib_sub_frame.columnconfigure(1, weight=1)
        

        # --- Miscellaneous Frame (Row 1, Column 0) ---
        # Validation functions for spinboxes
        def validate_spinbox_mpi_input(P):
            if P == "":
                self.mpi_threads_var.set(0)
                return True
            elif P.isdigit():
                if int(P) > 1000:
                    self.mpi_threads_var.set(1000)
                    return True
                elif int(P) < 0:
                    self.mpi_threads_var.set(0)
                    return True
                else:
                    return True
            else:
                self.mpi_threads_var.set(0)
                return True

        def validate_spinbox_verbose_input(P):
            if P == "":
                self.verbose_level_var.set(2)
                return True
            elif P.isdigit():
                if int(P) > 5:
                    self.verbose_level_var.set(5)
                    return True
                elif int(P) < 1:
                    self.verbose_level_var.set(1)
                    return True
                else:
                    return True
            else:
                self.verbose_level_var.set(2)
                return True

        vcmd_mpi = (self.register(validate_spinbox_mpi_input), '%P')
        vcmd_verbose = (self.register(validate_spinbox_verbose_input), '%P')

        # Checkbuttons for MPI and Stats
        ttk.Checkbutton(misc_frame, text="MPI", variable=self.mpi_bool_var, style='Roundtoggle.Toolbutton').grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(misc_frame, text="Print Stats", variable=self.stats_need_bool_var, style='Roundtoggle.Toolbutton').grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Threads and verbosity
        ttk.Label(misc_frame, text="Nb of Threads:").grid(row=0, column=1, sticky="w", padx=(20,2), pady=5)
        mpi_spinbox = ttk.Spinbox(misc_frame, textvariable=self.mpi_threads_var, from_=0, to=1000, increment=1, width=6, validate='focusout', validatecommand=vcmd_mpi)
        mpi_spinbox.grid(row=0, column=2, sticky="w", padx=(2,5), pady=5)
        mpi_spinbox.bind('<Return>', lambda event: validate_spinbox_mpi_input(mpi_spinbox.get()))

        ttk.Label(misc_frame, text="Verbose Level:").grid(row=1, column=1, sticky="w", padx=(20,2), pady=5)
        verbose_spinbox = ttk.Spinbox(misc_frame, textvariable=self.verbose_level_var, from_=1, to=5, increment=1, width=6, validate='focusout', validatecommand=vcmd_verbose)
        verbose_spinbox.grid(row=1, column=2, sticky="w", padx=(2,5), pady=5)
        verbose_spinbox.bind('<Return>', lambda event: validate_spinbox_verbose_input(verbose_spinbox.get()))
        
        # --- Working Directory Input (Adapted to use add_dir_row) ---
        self.add_dir_row(misc_frame, "Working Directory:", self.working_dir_var, row=2)

        # -- bottom buttons --
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Generate Command", command=self.generate_command).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Copy Command", command=self.copy_command).grid(row=0, column=1, padx=6)
        ttk.Button(btn_frame, text="Run CASToR-GATERootToCastor (Linux)", command=self.run_on_linux).grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="Exit", command=self.quit).grid(row=0, column=4, padx=6)

    # ---------------- helpers to add rows ----------------
    def add_file_row(self, parent, label, var, row=None, save=False):
        r = row if row is not None else 0
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", padx=(5,2), pady=3)
        ent = ttk.Entry(parent, textvariable=var, width=30)
        ent.grid(row=r, column=1, sticky="we", padx=(2,4))
        if self.folder_icon:
            btn = ttk.Button(parent, image=self.folder_icon, 
                             command=(lambda v=var, s=save: self.browse_save(v) if s else self.browse_open(v)))
            btn.grid(row=r, column=2, padx=(2,6))
        else:
            btn = ttk.Button(parent, text="Browse", 
                             command=(lambda v=var, s=save: self.browse_save(v) if s else self.browse_open(v)))
            btn.grid(row=r, column=2, padx=(2,6))
        parent.columnconfigure(1, weight=1)
        return var

    def add_entry_row(self, parent, label, var, row=None, col=0):
        r = row if row is not None else 0
        # Use bold for the label for visual separation
        ttk.Label(parent, text=label, font=("", 9, "bold")).grid(row=r, column=col, sticky="w", padx=(5,2), pady=3)
        ent = ttk.Entry(parent, textvariable=var, width=25)
        ent.grid(row=r, column=col+1, sticky="we", padx=(2,6))
        parent.columnconfigure(col+1, weight=1)
        return var
        
    def add_dir_row(self, parent, label, var, row=None, col_span=2): # <-- ADAPTED DIRECTORY HELPER
        r = row if row is not None else 0
        # Use bold for the label for visual separation
        ttk.Label(parent, text=label, font=("", 9, "bold")).grid(row=r, column=0, sticky="w", padx=(5,2), pady=3)
        ent = ttk.Entry(parent, textvariable=var, width=25)
        ent.grid(row=r, column=1, sticky="we", padx=(2,4))
        if self.folder_icon:
            btn = ttk.Button(parent, image=self.folder_icon, 
                             command=lambda v=var: self.browse_directory(v)) # <-- Calls browse_directory
            btn.grid(row=r, column=2, padx=(2,6))
        else:
            btn = ttk.Button(parent, text="Browse Dir", 
                             command=lambda v=var: self.browse_directory(v)) # <-- Calls browse_directory
            btn.grid(row=r, column=2, padx=(2,6))
        
        # Configure weight to ensure entry expands nicely
        parent.columnconfigure(1, weight=1) 
        return var

    # ---------------- file dialogs ----------------
    def browse_open(self, var):
        path = filedialog.askopenfilename(initialdir=self.home_dir)
        if path:
            var.set(path)

    def browse_save(self, var):
        path = filedialog.asksaveasfilename(initialdir=self.home_dir)
        if path:
            var.set(path)

    def browse_directory(self, var): # <-- NEW FUNCTION
        path = filedialog.askdirectory(initialdir=self.home_dir)
        if path:
            var.set(path)

    # ---------------- build command ----------------
    def generate_command(self):
        # construct command list
        cmd = ["castor-GATERootToCastor"]

        # mandatory: input root or input list
        if self.input_root_var.get() and self.input_list_var.get():
            messagebox.showerror("Conflict", "You must specify EITHER input GATE root OR input list, not both.")
            return ""
        elif self.input_root_var.get():
            cmd += ["-i", self.input_root_var.get()]
        elif self.input_list_var.get():
            cmd += ["-il", self.input_list_var.get()]
        else:
            messagebox.showerror("Missing argument", "You must specify either input GATE root or input list.")
            return ""

        # check other mandatory
        if not self.scanner_alias_var.get():
            messagebox.showerror("Missing argument", "Scanner geometry file is required.")
            return ""
        if not self.output_file_var.get():
            messagebox.showerror("Missing argument", "Output file is required.")
            return ""
        if not self.macro_file_var.get():
            messagebox.showerror("Missing argument", "GATE Macro file is required.")
            return ""

        cmd += ["-s", self.scanner_alias_var.get()]
        cmd += ["-o", self.output_file_var.get()]
        cmd += ["-m", self.macro_file_var.get()]

        # optional flags and arguments
        if self.prompt_type_var.get():
            cmd.append(self.prompt_type_var.get())
        if self.cf_var.get():
            cmd += ["-cf", self.cf_var.get()]
        if self.histogram_bool.get():
            cmd.append("-oh")
        if self.norm_file_var.get():
            cmd += ["-n", self.norm_file_var.get()]
        if self.norm_list_var.get():
            cmd += ["-nl", self.norm_list_var.get()]
        if self.norm_img_var.get():
            cmd += ["-nimg", self.norm_img_var.get()]
        if self.atn_var.get():
            cmd += ["-atn", self.atn_var.get()]
        if self.k_bool.get():
            cmd.append("-k")
        if self.isotope_var.get():
            cmd += ["-ist", self.isotope_var.get()]
        if self.tof_reso_var.get():
            cmd += ["-TOF_reso", self.tof_reso_var.get()]
        if self.tof_branch_var.get():
            cmd += ["-TOF_branch", self.tof_branch_var.get()]
        if self.tof_range_var.get():
            cmd += ["-TOF_range", self.tof_range_var.get()]
        if self.geo_bool.get():
            cmd.append("-geo")
            
        # Threads/MPI handling
        if self.mpi_bool_var.get():
            if self.mpi_threads_var.get() > 0:
                # MPI is enabled, use mpirun and the thread count
                mpi_prefix = [f"mpirun", "-np", str(self.mpi_threads_var.get())]
                cmd = mpi_prefix + cmd
            # If MPI is checked but threads is 0, it will run the base command without mpirun.
        elif self.mpi_threads_var.get() > 0:
            # If threads is > 0 but MPI isn't checked, use -th flag for OpenMP/simple threading
            cmd += ["-th", str(self.mpi_threads_var.get())]
            
        # Verbose level is a spinbox variable (integer)
        if self.verbose_level_var.get() != 2: # Default is 2, only add if different
            cmd += ["-vb", str(self.verbose_level_var.get())]
        
        # sanitize / quote paths that contain spaces
        cmd_quoted = []
        for part in cmd:
            # Use shlex.quote to handle spaces and special characters robustly
            cmd_quoted.append(shlex.quote(part))

        final_cmd = " ".join(cmd_quoted)
        return final_cmd

    # ---------------- copy to clipboard ----------------
    def copy_command(self):
        cmd = self.generate_command() # Generate command directly
        if not cmd:
            return
        self.clipboard_clear()
        self.clipboard_append(cmd)
        messagebox.showinfo("Copied", "Command copied to clipboard.")

        # ---------------- run in new terminal (Linux) ----------------
     # ---------------- run in new terminal (Linux) ----------------
    def run_on_linux(self):
        cmd = self.generate_command() # Generate command directly
        if not cmd:
            return
        
        work_dir = self.working_dir_var.get()
        if not work_dir or not Path(work_dir).is_dir():
            # Fallback to home dir or script dir if path is invalid/empty
            work_dir = self.home_dir 
            messagebox.showwarning("Warning", f"Invalid working directory selected. Using default: {work_dir}")

        # --- ADAPTED SCRIPT CONTENT ---
        # Note: We are using a single script variable to pass to bash -c
        # The command is dynamically built in Python's 'cmd' variable.
        
        script = f"""
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo ":: Launch the conversion from GATE ROOT file to CASToR file"
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"

echo "=========================================================="
echo "Executing command: {cmd}"
echo "=========================================================="
time {cmd}
EXIT_CODE=$?

echo "=========================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo " CASToR - GATERootToCastor has finished successfully!"
else
    echo " CASToR - GATERootToCastor FAILED with exit code: $EXIT_CODE"
fi
echo "=========================================================="

# Keep the terminal open after execution
exec bash
"""
        # --- END ADAPTED SCRIPT CONTENT ---
        
        # Use shlex.quote around the entire script block to ensure it's passed as one argument to bash -c
        terminal_cmd = f"gnome-terminal --working-directory={shlex.quote(work_dir)} -- bash -c {shlex.quote(script)}"
        
        try:
            # Check if castor is accessible before running
            subprocess.run(["which", "castor-GATERootToCastor"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Use shell=True for the gnome-terminal command
            subprocess.Popen(terminal_cmd, shell=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Run error", "castor-GATERootToCastor command not found. Ensure CASToR is installed and in your PATH.")
        except Exception as e:
            messagebox.showerror("Run error", f"Could not open terminal to run command.\n\n{e}")

    
        # ---------------- About ----------------
    def show_about(self):
        help_window = tk.Toplevel()
        help_window.title("About CASToR - GATERootToCastor GUI")
        help_window.geometry("1000x650")
        help_window.resizable(True, True)

        # Scrollable text area
        text_area = st.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=("Courier", 11),
            bg="white",
            fg="black",
            insertbackground="black"
        )
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Define bold text style
        bold_font = tkfont.Font(text_area, text_area.cget("font"))
        bold_font.configure(weight="bold")
        text_area.tag_configure("bold", font=bold_font)

        # ===== Insert content =====
        text_area.insert(tk.END, "==============================\n", ())
        text_area.insert(tk.END, "CASToR - GATERootToCastor GUI\n", ("bold",))
        text_area.insert(tk.END, "==============================\n\n", ())

        text_area.insert(
            tk.END,
            "This application provides a graphical interface to convert the GATE .root output files "
            "into CASToR datafiles (.cdh) for PET, SPECT or CT image reconstructions, "
            "using the CASToR (Customizable and Advanced Software for Tomographic Reconstruction) framework, "
            "namely the `castor-GATERootToCastor` tool.\n\n"
        )

        text_area.insert(tk.END, "------------------------\nWhat this tool does:\n------------------------\n", ("bold",))
        text_area.insert(
            tk.END,
            "• Simplifies the writing process on the terminal to run the castor-GATERootToCastor tool.\n"
            "• Allows you to define and manage all parameters visually.\n"
            "• Lets you run castor-GATERootToCastor directly from the GUI (on Linux).\n"
            "• Automatically generates organized output commands for reproducibility and documentation.\n\n"
        )

        text_area.insert(tk.END, "------------------------\nBasic Usage Instructions:\n------------------------\n", ("bold",))
        text_area.insert(
            tk.END,
            "1. Fill mandatory inputs on the left:\n"
            "    - A single .root file or a list .txt file containing ROOT files to convert.\n"
            "    - The scanner alias corresponding to your geometry (previously created using castor-GATEMacToGeom), "
            "or activate the 'Generate Geometry File' option to create it automatically.\n"
            "    - The GATE macro file used in your simulation.\n"
            "    - The output file name to generate.\n\n"
            "2. Fill optional parameters such as data corrections, attenuation, normalization, calibration factor, isotopes and TOF settings as needed.\n"
            "3. Click 'Generate Command' to preview the command line.\n"
            "4. Click 'Copy Command' to copy it to the clipboard if you wish to run it manually in another terminal.\n"
            "5. Click 'Run CASToR-GATERootToCastor (Linux)' to open a new terminal and execute the command "
            "(the terminal will remain open after execution).\n\n"
        )

        text_area.insert(tk.END, "MPI (Parallel Computing)\n", ("bold",))
        text_area.insert(
            tk.END,
            "Activate MPI to use multiple CPU cores for faster conversion. "
            "If enabled, specify the number of threads (Nb of Threads) according to your system’s capabilities.\n"
            "Note: If MPI is not enabled, the 'Nb of Threads' value is used for OpenMP-based multithreading (using '-th' flag).\n"
            "⚠️ Important: For MPI, CASToR must be installed with the MPI option activated (compiled with MPI support).\n\n"
        )

        text_area.insert(tk.END, "Additional Notes\n", ("bold",))
        text_area.insert(
            tk.END,
            "• File/folder dialogs open in your home directory by default.\n"
            "• If a path contains spaces, it will be automatically quoted.\n"
            "• For full details about all options, run `castor-GATERootToCastor --help` in a terminal "
            "or visit the CASToR documentation at https://castor-project.org/.\n"
            "• Make sure CASToR is installed and that your build includes the GATERootToCastor tool "
            "(compiled with the same GATE version used for simulation).\n\n"
        )

        text_area.insert(
            tk.END,
            "Developed by Beatriz Ornelas for GATE PET reconstruction workflows "
            "to streamline CASToR data conversion and preprocessing.\n"
        )

        # Make text read-only
        text_area.configure(state="disabled")

        # Close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=6)


    # ---------------- debug print ----------------
    def print_all_variables(self):
        print("=== Current GUI variables ===")
        for varname, var in [
            ("input_root", self.input_root_var),
            ("input_list", self.input_list_var),
            ("scanner_alias", self.scanner_alias_var),
            ("output_file", self.output_file_var),
            ("macro_file", self.macro_file_var),
            ("prompt_type", self.prompt_type_var),
            ("cf", self.cf_var),
            ("histogram", self.histogram_bool),
            ("norm_file", self.norm_file_var),
            ("norm_list", self.norm_list_var),
            ("norm_img", self.norm_img_var),
            ("atn", self.atn_var),
            ("k_flag", self.k_bool),
            ("isotope", self.isotope_var),
            ("TOF_reso", self.tof_reso_var),
            ("TOF_branch", self.tof_branch_var),
            ("TOF_range", self.tof_range_var),
            ("geo", self.geo_bool),
            ("threads", self.threads_var),
            ("vb", self.vb_var),
            ("mpi", self.mpi_bool_var),
            ("stats_need", self.stats_need_bool_var),
            ("mpi_threads", self.mpi_threads_var),
            ("verbose_level", self.verbose_level_var),
        ]:
            try:
                print(f"{varname}: {var.get()}")
            except Exception:
                print(f"{varname}: (bool) {var.get()}")

if __name__ == "__main__":
    app = GATERootToCastorGUI()
    app.mainloop()
