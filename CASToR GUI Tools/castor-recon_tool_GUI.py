# import packages, verify if they are all installed in your python
from calendar import c
import re
import tkinter as tk
from tkinter import ttk
from wsgiref import validate
import ttkbootstrap as ttk
from tkinter import messagebox
from tkinter import filedialog
from ttkbootstrap import Style
import os
import numpy as np
import locale
from pathlib import Path
import tkinter.scrolledtext as st
import tkinter.font as tkfont

# Set the locale to C at the start of your script
locale.setlocale(locale.LC_NUMERIC, 'C')

class BatchScriptGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python GUI for Running CASToR and Script Generator")
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        # Png logo
        self.iconphoto(False, tk.PhotoImage(file=os.path.join(self.script_dir, 'CASToR_logo.png')))
        self.resizable(True, True)
        self.minsize(675, 482)
        self.style = Style(theme='darkly')

        # Variables to store user inputs
        self.mpi_bool_var = tk.BooleanVar()
        self.mpi_threads_var = tk.IntVar()
        self.verbose_level_var = tk.IntVar()
        self.last_iter_bool_var = tk.BooleanVar()
        self.flip_var = tk.StringVar()
        self.stats_need_bool_var = tk.BooleanVar()

        self.main_program_path_var = tk.StringVar()
        self.datafile_path_var = tk.StringVar()
        self.attenuation_path_var = tk.StringVar()
        self.normalization_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.sensitivity_path_var = tk.StringVar()
        self.configuration_path_var = tk.StringVar()

        self.voxel_number_var = tk.StringVar()
        self.voxel_size_var = tk.StringVar()
        self.fov_size_var = tk.StringVar()
        self.offset_var = tk.StringVar()
        self.voxel_size_x_var = tk.DoubleVar()
        self.voxel_size_y_var = tk.DoubleVar()
        self.voxel_size_z_var = tk.DoubleVar()
        self.voxel_number_x_var = tk.IntVar()
        self.voxel_number_y_var = tk.IntVar()
        self.voxel_number_z_var = tk.IntVar()
        self.fov_size_x_var = tk.DoubleVar()
        self.fov_size_y_var = tk.DoubleVar()
        self.fov_size_z_var = tk.DoubleVar()
        self.offset_x_var = tk.DoubleVar()
        self.offset_y_var = tk.DoubleVar()
        self.offset_z_var = tk.DoubleVar()

        self.iterations_var = tk.StringVar()
        self.optimizer_var = tk.StringVar()
        self.projector_var = tk.StringVar()
        self.penalty_var = tk.StringVar()
        self.penalty_strength_var = tk.DoubleVar()
        self.convolution_need_bool_var = tk.BooleanVar()
        self.convolution_num_var = tk.IntVar()
        self.previous_num_conv = int()
        self.convolution_type_vars = []
        self.convolution_value_vars = []
        self.convolution_x_var = []
        self.convolution_y_var = []
        self.convolution_sigma_var = []

        # Corrections to ignore variables
        self.ignore_attn_var = tk.BooleanVar()
        self.ignore_norm_var = tk.BooleanVar()
        self.ignore_rand_var = tk.BooleanVar()
        self.ignore_scat_var = tk.BooleanVar()
        self.ignore_deca_var = tk.BooleanVar()
        self.ignore_brat_var = tk.BooleanVar()
        self.ignore_fdur_var = tk.BooleanVar()
        self.ignore_cali_var = tk.BooleanVar()

        # MultiSiddon projector parameters
        self.multisiddon_sensitivity_lines_var = tk.IntVar()
        self.multisiddon_reconstruction_lines_var = tk.IntVar()

        # Set initial values
        self.set_initial_values()

        # Create GUI elements
        self.create_widgets()

    def set_initial_values(self):
        """Set initial default values for GUI fields."""
        self.mpi_bool_var.set(True)
        self.mpi_threads_var.set(0)
        self.verbose_level_var.set(2)
        self.last_iter_bool_var.set(False)
        self.flip_var.set("None")
        self.stats_need_bool_var.set(True)

        home_dir = str(Path.home())
        castor_bin = os.path.join(home_dir, "Software/Castor/castor-install/bin/castor-recon")

    # Paths
        self.main_program_path_var.set(castor_bin)
        self.datafile_path_var.set("")
        self.attenuation_path_var.set("")
        self.normalization_path_var.set("")
        self.output_path_var.set("")
        self.sensitivity_path_var.set("")
        self.configuration_path_var.set("")

    # Image geometry parameters (left empty for user)
        self.voxel_number_var.set("")
        self.voxel_size_var.set("")
        self.fov_size_var.set("")
        self.offset_var.set("")

        self.voxel_size_x_var.set(0)
        self.voxel_size_y_var.set(0)
        self.voxel_size_z_var.set(0)
        self.voxel_number_x_var.set(0)
        self.voxel_number_y_var.set(0)
        self.voxel_number_z_var.set(0)
        self.fov_size_x_var.set(0)
        self.fov_size_y_var.set(0)
        self.fov_size_z_var.set(0)
        self.offset_x_var.set(0)
        self.offset_y_var.set(0)
        self.offset_z_var.set(0)

    # Iterations/subsets left blank
        self.iterations_var.set("")

    # Algorithm and convolution defaults
        self.optimizer_var.set("MLEM")
        self.projector_var.set("distanceDriven")
        self.penalty_var.set("MRF")
        self.penalty_strength_var.set(0.5)
        self.convolution_need_bool_var.set(True)
        self.convolution_num_var.set(1)

    # Corrections to ignore - all False by default (apply all corrections)
        self.ignore_attn_var.set(False)
        self.ignore_norm_var.set(False)
        self.ignore_rand_var.set(False)
        self.ignore_scat_var.set(False)
        self.ignore_deca_var.set(False)
        self.ignore_brat_var.set(False)
        self.ignore_fdur_var.set(False)
        self.ignore_cali_var.set(False)

    # MultiSiddon projector parameters
        self.multisiddon_sensitivity_lines_var.set(1)
        self.multisiddon_reconstruction_lines_var.set(1)

    # Initialize convolution settings
        self.convolution_type_vars = []
        self.convolution_value_vars = []
        self.convolution_x_var = []
        self.convolution_y_var = []
        self.convolution_sigma_var = []
        self.previous_num_conv = 0

        for _ in range(self.convolution_num_var.get()):
            self.convolution_type_vars.append(tk.StringVar(value="psf"))
            self.convolution_value_vars.append(tk.StringVar(value=""))
            self.convolution_x_var.append(tk.DoubleVar(value=1.0))
            self.convolution_y_var.append(tk.DoubleVar(value=1.0))
            self.convolution_sigma_var.append(tk.DoubleVar(value=3.0))

    def update_entries(self):
        # Update the entries that depend on other widgets
        self.voxel_number_var.set(f"{self.voxel_size_x_var.get()},{self.voxel_size_y_var.get()},{self.voxel_size_z_var.get()}")
        self.voxel_size_var.set(f"{self.voxel_number_x_var.get()},{self.voxel_number_y_var.get()},{self.voxel_number_z_var.get()}")
        self.fov_size_var.set(f"{self.fov_size_x_var.get()},{self.fov_size_y_var.get()},{self.fov_size_z_var.get()}")
        self.offset_var.set(f"{self.offset_x_var.get()},{self.offset_y_var.get()},{self.offset_z_var.get()}")
        self.convolution_value_vars = [f"gaussian,{self.convolution_x_var[i].get()},{self.convolution_y_var[i].get()},{self.convolution_sigma_var[i].get()}::{self.convolution_type_vars[i].get()}" for i in range(self.convolution_num_var.get())]
        # NEED TO CREATE self.button etc...

    def create_widgets(self):
        # title
        ttk.Label(self, text="CASToR-recon GUI", font=("Helvetica", 16, "bold")).pack(pady=(10,5))
        # Add GUI elements for user input
        options_frame = ttk.Frame(self)
        options_frame.pack(padx=10, pady=10)
        ttk.Sizegrip(self, style='info.TSizegrip').pack(side="right", fill="y")

        # Add a self.menubar
        self.create_menu()

        # Path variables section
        self.create_path_variables_widgets(options_frame)

        # Image specifications section
        self.create_image_specifications_widgets(options_frame)

        # Corrections section
        self.create_corrections_widgets(options_frame)

        # Miscellaneous section
        self.create_miscellaneous_widgets(options_frame)

        # Algorithm section
        self.create_algorithm_widgets(options_frame)

        # Convolution section
        self.create_convolution_widgets(options_frame)

        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=(0, 15))

        # Button to generate batch script
        generate_button = ttk.Button(button_frame, text="Generate batch script for Windows", command=self.generate_script)
        generate_button.pack(side="left", padx=5)
        
        # Button to generate shell script
        generateShell_button = ttk.Button(button_frame, text="Generate shell script for Linux", command=self.generateShell_script)
        generateShell_button.pack(side="left", padx=5)

        # Button to run CASToR
        run_button = ttk.Button(button_frame, text="Run CASToR program on Windows", command=self.run_castor_program)
        run_button.pack(side="left", padx=5)
        
        # Button to run CASToR
        run_button_Linux = ttk.Button(button_frame, text="Run CASToR program on Linux", command=self.run_castor_program_Linux)
        run_button_Linux.pack(side="left", padx=5)
    
    def change_theme(self, theme):
        # self.style = Style(self)
        self.style.theme_use(theme)
        self.update()

    def create_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset variable to default", command=lambda: (self.set_initial_values(),self.update_convolution_entries()))
        file_menu.add_command(label="Print all variables", command=self.print_test_all_variables)
        file_menu.add_command(label="Generate Script", command=self.generate_script)
        file_menu.add_command(label="Run CASToR Program for Windows", command=self.run_castor_program)
        file_menu.add_command(label="Run CASToR Program for Linux", command=self.run_castor_program_Linux)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        # Add a open from file menu
        self.menubar.add_command(label="Open Batch file", command=self.open_from_file)
        # Add a open from file menu - Linux
        self.menubar.add_command(label="Open Shell file", command=self.open_from_file_Linux)
        # Add light and dark theme
        self.mode_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Mode", menu=self.mode_menu)
        self.mode_menu.add_command(label="Light", command=lambda: self.change_theme('cosmo'))
        self.mode_menu.add_command(label="Dark", command=lambda: self.change_theme('darkly'))
        # Add a aboutme menu
        self.menubar.add_command(label="About Me", command=self.show_about)

    def create_path_variables_widgets(self, options_frame):
        path_frame = ttk.LabelFrame(options_frame, text="Path Variables")
        path_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self.folder_icon = tk.PhotoImage(file=os.path.join(self.script_dir, 'folder.png'))
        self.folder_icon = self.folder_icon.subsample(8, 8)

        ttk.Label(path_frame, text="CASToR Main Prog:").grid(row=0, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(path_frame, textvariable=self.main_program_path_var,validate="focusout",validatecommand=lambda: self.validate_program_path(self.main_program_path_var)).grid(row=0, column=1, pady=3)
        ttk.Button(path_frame, image=self.folder_icon, command=lambda: self.browse_path(self.main_program_path_var)).grid(row=0, column=2, pady=3, padx=(0, 5))
        
        ttk.Label(path_frame, text="Datafile Cdh Path:").grid(row=1, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(path_frame, textvariable=self.datafile_path_var,validate="focusout",validatecommand=lambda: self.validate_program_path(self.datafile_path_var)).grid(row=1, column=1, pady=3)
        ttk.Button(path_frame, image=self.folder_icon, command=lambda: self.browse_path(self.datafile_path_var)).grid(row=1, column=2, pady=3, padx=(0, 5))
        
        ttk.Label(path_frame, text="Attenuation hdr Path:").grid(row=2, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(path_frame, textvariable=self.attenuation_path_var,validate="focusout",validatecommand=lambda: self.validate_program_path(self.attenuation_path_var)).grid(row=2, column=1, pady=3)
        ttk.Button(path_frame, image=self.folder_icon, command=lambda: self.browse_path(self.attenuation_path_var)).grid(row=2, column=2, pady=3, padx=(0, 5))
        
        ttk.Label(path_frame, text="Normalization hdr Path:").grid(row=3, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(path_frame, textvariable=self.normalization_path_var,validate="focusout",validatecommand=lambda: self.validate_program_path(self.normalization_path_var)).grid(row=3, column=1, pady=3)
        ttk.Button(path_frame, image=self.folder_icon, command=lambda: self.browse_path(self.normalization_path_var)).grid(row=3, column=2, pady=3, padx=(0, 5))

        ttk.Label(path_frame, text="Output Folder:").grid(row=4, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(path_frame, textvariable=self.output_path_var,validate="focusout",validatecommand=lambda:
self.validate_program_path(self.output_path_var)).grid(row=4, column=1, pady=3)
        ttk.Button(path_frame, image=self.folder_icon, command=lambda: self.browse_folder(self.output_path_var)).grid(row=4, column=2, pady=3, padx=(0, 5))

        ttk.Label(path_frame, text="Sensitivity Path:").grid(row=5, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(path_frame, textvariable=self.sensitivity_path_var,validate="focusout",validatecommand=lambda: self.validate_program_path(self.sensitivity_path_var)).grid(row=5, column=1, pady=(3, 6))
        ttk.Button(path_frame, image=self.folder_icon, command=lambda: self.browse_path(self.sensitivity_path_var)).grid(row=5, column=2, pady=(3, 6), padx=(0, 5))

    def create_image_specifications_widgets(self, options_frame):
        image_frame = ttk.LabelFrame(options_frame, text="Image Specifications (X,Y,Z)")
        image_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        def set_voxel_size(value, axis):
            if axis == 'x':
                self.voxel_size_x_var.set(value)
            elif axis == 'y':
                self.voxel_size_y_var.set(value)
            elif axis == 'z':
                self.voxel_size_z_var.set(value)
            

        def set_voxel_number(value, axis):
            if axis == 'x':
                self.voxel_number_x_var.set(value)
            elif axis == 'y':
                self.voxel_number_y_var.set(value)
            elif axis == 'z':
                self.voxel_number_z_var.set(value)
           

        def set_fov_size(value, axis):
            if axis == 'x':
                self.fov_size_x_var.set(value)
            elif axis == 'y':
                self.fov_size_y_var.set(value)
            elif axis == 'z':
                self.fov_size_z_var.set(value)
            

        def set_offset(value, axis):
            if axis == 'x':
                self.offset_x_var.set(value)
            elif axis == 'y':
                self.offset_y_var.set(value)
            elif axis == 'z':
                self.offset_z_var.set(value)

        def validate_voxel_size(P, axis):
            if P == "":
                value = 0.2
            elif P.isdigit() or self.is_valid_float(P):
                value = round(float(P),5)
                if value > 1000:
                    value = 1000
                elif value <= 0:
                    value = 0.2
            else:
                value = 0.2

            self.after(10, lambda: set_voxel_size(value, axis))
            return True

        def validate_voxel_number(P, axis):
            if P == "":
                value = 200
            elif P.isdigit() or self.is_valid_float(P):
                value = round(float(P))
                if value > 100000:
                    value = 100000
                elif value <= 0:
                    value = 1
            else:
                value = 200

            self.after(10, lambda: set_voxel_number(value, axis))
            return True

        def validate_fov_size(P, axis):
            # P is the new value of the Spinbox after the edit
            if P == "":
                value = 40
            elif P.isdigit() or self.is_valid_float(P):
                value = round(float(P),5)
                if value > 1000000000:
                    value = 1000000000
                elif value <= 0:
                    value = 1
            else:
                value = 40

            self.after(10, lambda: set_fov_size(value, axis))
            return True

        def validate_offset(P, axis):
            # P is the new value of the Spinbox after the edit
            if P == "":
                value = 0
            elif P.isdigit() or self.is_valid_float(P):
                value = round(float(P),5)
                if value > 1000000:
                    value = 1000000
                elif value < -1000000:
                    value = -1000000
            else:
                value = 0

            self.after(10, lambda: set_offset(value, axis))
            return True
        
        vcmd_voxel_number_x = (self.register(lambda P: validate_voxel_number(P, 'x')), '%P')
        vcmd_voxel_number_y = (self.register(lambda P: validate_voxel_number(P, 'y')), '%P')
        vcmd_voxel_number_z = (self.register(lambda P: validate_voxel_number(P, 'z')), '%P')
        vcmd_voxel_size_x = (self.register(lambda P: validate_voxel_size(P, 'x')), '%P')
        vcmd_voxel_size_y = (self.register(lambda P: validate_voxel_size(P, 'y')), '%P')
        vcmd_voxel_size_z = (self.register(lambda P: validate_voxel_size(P, 'z')), '%P')
        vcmd_fov_size_x = (self.register(lambda P: validate_fov_size(P, 'x')), '%P')
        vcmd_fov_size_y = (self.register(lambda P: validate_fov_size(P, 'y')), '%P')
        vcmd_fov_size_z = (self.register(lambda P: validate_fov_size(P, 'z')), '%P')
        vcmd_offset_x = (self.register(lambda P: validate_offset(P, 'x')), '%P')
        vcmd_offset_y = (self.register(lambda P: validate_offset(P, 'y')), '%P')
        vcmd_offset_z = (self.register(lambda P: validate_offset(P, 'z')), '%P')

        def update_fov(*args):
            voxel_size_x = self.voxel_size_x_var.get() if self.voxel_size_x_var.get() else 0.
            voxel_size_y = self.voxel_size_y_var.get() if self.voxel_size_y_var.get() else 0
            voxel_size_z = self.voxel_size_z_var.get() if self.voxel_size_z_var.get() else 0
            voxel_number_x = self.voxel_number_x_var.get() if self.voxel_number_x_var.get() else 0
            voxel_number_y = self.voxel_number_y_var.get() if self.voxel_number_y_var.get() else 0
            voxel_number_z = self.voxel_number_z_var.get() if self.voxel_number_z_var.get() else 0
            fov_size_x = voxel_size_x * voxel_number_x
            fov_size_y = voxel_size_y * voxel_number_y
            fov_size_z = voxel_size_z * voxel_number_z
            self.fov_size_x_var.set(round(fov_size_x,5))
            self.fov_size_y_var.set(round(fov_size_y,5))
            self.fov_size_z_var.set(round(fov_size_z,5))

        def update_voxel_size(*args):
            fov_size_x = self.fov_size_x_var.get() if self.fov_size_x_var.get() else 0
            fov_size_y = self.fov_size_y_var.get() if self.fov_size_y_var.get() else 0
            fov_size_z = self.fov_size_z_var.get() if self.fov_size_z_var.get() else 0
            voxel_number_x = self.voxel_number_x_var.get() if self.voxel_size_x_var.get() else 0
            voxel_number_y = self.voxel_number_y_var.get() if self.voxel_size_y_var.get() else 0
            voxel_number_z = self.voxel_number_z_var.get() if self.voxel_size_z_var.get() else 0
            voxel_size_x = fov_size_x / voxel_number_x if voxel_number_x != 0 else 0
            voxel_size_y = fov_size_y / voxel_number_y if voxel_number_y != 0 else 0
            voxel_size_z = fov_size_z / voxel_number_z if voxel_number_z != 0 else 0
            self.voxel_size_x_var.set(round(voxel_size_x,5))
            self.voxel_size_y_var.set(round(voxel_size_y,5))
            self.voxel_size_z_var.set(round(voxel_size_z,5))

        ttk.Label(image_frame, text="Voxel Size (mm):").grid(row=0, column=0, sticky="nsew", padx=(5, 2))
        spinbox_voxsize_x = ttk.Spinbox(image_frame, textvariable=self.voxel_size_x_var, from_=0.0, to=1000.0,increment=0.1, width=6, validate='focusout', validatecommand=vcmd_voxel_size_x)
        spinbox_voxsize_x.grid(row=0, column=1, pady=3)
        spinbox_voxsize_x.bind('<Return>', lambda event: validate_voxel_size(spinbox_voxsize_x.get(), 'x'))
        spinbox_voxsize_y = ttk.Spinbox(image_frame, textvariable=self.voxel_size_y_var, from_=0, to=1000,increment=0.1, width=6, validate='focusout', validatecommand=vcmd_voxel_size_y)
        spinbox_voxsize_y.grid(row=0, column=2, pady=3)
        spinbox_voxsize_y.bind('<Return>', lambda event: validate_voxel_size(spinbox_voxsize_y.get(), 'y'))
        spinbox_voxsize_z = ttk.Spinbox(image_frame, textvariable=self.voxel_size_z_var, from_=0, to=1000,increment=0.1, width=6, validate='focusout', validatecommand=vcmd_voxel_size_z)
        spinbox_voxsize_z.grid(row=0, column=3, pady=3, padx=(0, 5))
        spinbox_voxsize_z.bind('<Return>', lambda event: validate_voxel_size(spinbox_voxsize_z.get(), 'z'))

        ttk.Label(image_frame, text="Voxel Number:").grid(row=1, column=0, sticky="nsew", padx=(5, 2))
        spinbox_voxnb_x = ttk.Spinbox(image_frame, textvariable=self.voxel_number_x_var, from_=0, to=100000,increment=1, width=6, validate='focusout', validatecommand=vcmd_voxel_number_x)
        spinbox_voxnb_x.grid(row=1, column=1, pady=3)
        spinbox_voxnb_x.bind('<Return>', lambda event: validate_voxel_number(spinbox_voxnb_x.get(), 'x'))
        spinbox_voxnb_y = ttk.Spinbox(image_frame, textvariable=self.voxel_number_y_var, from_=0, to=100000,increment=1, width=6, validate='focusout', validatecommand=vcmd_voxel_number_y)
        spinbox_voxnb_y.grid(row=1, column=2, pady=3)
        spinbox_voxnb_y.bind('<Return>', lambda event: validate_voxel_number(spinbox_voxnb_y.get(), 'y'))
        spinbox_voxnb_z = ttk.Spinbox(image_frame, textvariable=self.voxel_number_z_var, from_=0, to=100000,increment=1, width=6, validate='focusout', validatecommand=vcmd_voxel_number_z)
        spinbox_voxnb_z.grid(row=1, column=3, pady=3, padx=(0, 5))
        spinbox_voxnb_z.bind('<Return>', lambda event: validate_voxel_number(spinbox_voxnb_z.get(), 'z'))

        ttk.Label(image_frame, text="FOV Size (mm):").grid(row=2, column=0, sticky="nsew", padx=(5, 2))
        spinbox_fovsize_x = ttk.Spinbox(image_frame, textvariable=self.fov_size_x_var, from_=0, to=1000000000,increment=1, width=6, validate='focusout')
        spinbox_fovsize_x.grid(row=2, column=1, pady=3)
        spinbox_fovsize_x.bind('<Return>', lambda event: validate_fov_size(spinbox_fovsize_x.get(), 'x'))
        spinbox_fovsize_y = ttk.Spinbox(image_frame, textvariable=self.fov_size_y_var, from_=0, to=1000000000,increment=1, width=6, validate='focusout')
        spinbox_fovsize_y.grid(row=2, column=2, pady=3)
        spinbox_fovsize_y.bind('<Return>', lambda event: validate_fov_size(spinbox_fovsize_y.get(), 'y'))
        spinbox_fovsize_z = ttk.Spinbox(image_frame, textvariable=self.fov_size_z_var, from_=0, to=1000000000,increment=1, width=6, validate='focusout')
        spinbox_fovsize_z.grid(row=2, column=3, pady=3, padx=(0, 5))
        spinbox_fovsize_z.bind('<Return>', lambda event: validate_fov_size(spinbox_fovsize_z.get(), 'z'))

        ttk.Label(image_frame, text="Offset (mm):").grid(row=3, column=0, sticky="nsew", padx=(5, 2))
        spinbox_offset_x = ttk.Spinbox(image_frame, textvariable=self.offset_x_var, from_=-1000000,to=1000000, increment=1, width=6, validate='focusout', validatecommand=vcmd_offset_x)
        spinbox_offset_x.grid(row=3, column=1, pady=(3, 6))
        spinbox_offset_x.bind('<Return>', lambda event: validate_offset(spinbox_offset_x.get(), 'x'))
        spinbox_offset_y = ttk.Spinbox(image_frame, textvariable=self.offset_y_var, from_=-1000000,to=1000000, increment=1, width=6, validate='focusout', validatecommand=vcmd_offset_y)
        spinbox_offset_y.grid(row=3, column=2, pady=(3, 6))
        spinbox_offset_y.bind('<Return>', lambda event: validate_offset(spinbox_offset_y.get(), 'y'))
        spinbox_offset_z = ttk.Spinbox(image_frame, textvariable=self.offset_z_var, from_=-1000000,to=1000000, increment=1, width=6, validate='focusout', validatecommand=vcmd_offset_z)
        spinbox_offset_z.grid(row=3, column=3, pady=(3, 6), padx=(0, 5))
        spinbox_offset_z.bind('<Return>', lambda event: validate_offset(spinbox_offset_z.get(), 'z'))

    def create_corrections_widgets(self, options_frame):
        """Create widgets for selecting corrections to ignore"""
        corrections_frame = ttk.LabelFrame(options_frame, text="Corrections to Ignore")
        corrections_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Description label
        ttk.Label(corrections_frame, 
                  text="Select which corrections to ignore (leave unchecked to apply corrections):",
                  font=("Helvetica", 9)).grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=(5, 10))
        
        # Create checkbuttons in a grid layout
        ttk.Checkbutton(corrections_frame, text="Attenuation (attn)", 
                       variable=self.ignore_attn_var).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(corrections_frame, text="Normalization (norm)", 
                       variable=self.ignore_norm_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(corrections_frame, text="Random (rand) - PET only", 
                       variable=self.ignore_rand_var).grid(row=1, column=2, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(corrections_frame, text="Scatter (scat)", 
                       variable=self.ignore_scat_var).grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        ttk.Checkbutton(corrections_frame, text="Decay (deca)", 
                       variable=self.ignore_deca_var).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(corrections_frame, text="Branching Ratio (brat)", 
                       variable=self.ignore_brat_var).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(corrections_frame, text="Frame Duration (fdur)", 
                       variable=self.ignore_fdur_var).grid(row=2, column=2, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(corrections_frame, text="Calibration (cali)", 
                       variable=self.ignore_cali_var).grid(row=2, column=3, sticky="w", padx=5, pady=2)

    def create_miscellaneous_widgets(self, options_frame):
        misc_frame = ttk.LabelFrame(options_frame, text="Miscellaneous")
        misc_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        def validate_spinbox_mpi_input(P):
            # P is the new value of the Spinbox after the edit
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
            # P is the new value of the Spinbox after the edit
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

        
        # Checkbuttons
        ttk.Checkbutton(misc_frame, text="MPI", variable=self.mpi_bool_var, style='Roundtoggle.Toolbutton').grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ttk.Checkbutton(misc_frame, text="Print Stats", variable=self.stats_need_bool_var,style='Roundtoggle.Toolbutton').grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        ttk.Checkbutton(misc_frame, text="Save Last It", variable=self.last_iter_bool_var,style='Roundtoggle.Toolbutton').grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        # Add a separator line
        separator = ttk.Separator(misc_frame, orient="vertical")
        separator.grid(row=0, column=1, rowspan=3,sticky="ns", padx=10, pady=5)
        # Spinboxes and Menubutton
        ttk.Label(misc_frame, text="Nb of Threads:").grid(row=0, column=2, sticky="nsew")
        mpi_spinbox = ttk.Spinbox(misc_frame, textvariable=self.mpi_threads_var, from_=0,to=1000, increment=1, width=6, validate='focusout', validatecommand=vcmd_mpi)
        mpi_spinbox.grid(row=0, column=3)
        mpi_spinbox.bind('<Return>', lambda event: validate_spinbox_mpi_input(mpi_spinbox.get()))
        ttk.Label(misc_frame, text="Verbose Level:").grid(row=1, column=2, sticky="nsew")
        verbose_spinbox = ttk.Spinbox(misc_frame, textvariable=self.verbose_level_var, from_=1,to=5, increment=1, width=6, validate='focusout', validatecommand=vcmd_verbose)
        verbose_spinbox.grid(row=1, column=3)
        verbose_spinbox.bind('<Return>', lambda event: validate_spinbox_verbose_input(verbose_spinbox.get()))
        ttk.Label(misc_frame, text="Flip Images:").grid(row=2, column=2, sticky="nsew")
        menu_button = ttk.Menubutton(misc_frame, textvariable=self.flip_var, width=5)
        menu_button.grid(row=2, column=3)
        menu_button.menu = tk.Menu(menu_button, tearoff=0)
        menu_button["menu"] = menu_button.menu
        for item in ["None", "X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"]:
            menu_button.menu.add_radiobutton(label=item, variable=self.flip_var, value=item)

        # Entry for the conf path
        conf_frame = ttk.Frame(misc_frame)
        conf_frame.grid(row=3, column=0, columnspan=4, pady=3, sticky="nsew")
        ttk.Label(conf_frame, text="Conf Path:").grid(row=0, column=0, sticky="nsew", padx=5)
        ttk.Entry(conf_frame, textvariable=self.configuration_path_var,width=25,validate="focusout",validatecommand=lambda: self.validate_folder_path(self.configuration_path_var)).grid(row=0, column=1, pady=3)
        ttk.Button(conf_frame, image=self.folder_icon, command=lambda: self.browse_path(self.configuration_path_var)).grid(row=0, column=2, sticky="e", pady=3, padx=(0, 5))

    def create_algorithm_widgets(self, options_frame):
        algorithm_frame = ttk.LabelFrame(options_frame, text="Algorithm")
        algorithm_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        def validate_spinbox_penalty_strength(P):
            # P is the new value of the Spinbox after the edit
            if P == "":
                self.penalty_strength_var.set(0)
                return True
            elif P.isdigit() or self.is_valid_float(P):
                if float(P) > 100:
                    self.penalty_strength_var.set(100)
                    return True
                elif float(P) < 0:
                    self.penalty_strength_var.set(0)
                    return True
                else:
                    return True
            else:
                self.penalty_strength_var.set(0)
                return True
        vcmd_penalty_strength = (self.register(validate_spinbox_penalty_strength), '%P')

        def validate_multisiddon_lines(P, var):
            if P == "":
                var.set(1)
                return True
            elif P.isdigit():
                value = int(P)
                if value < 1:
                    var.set(1)
                elif value > 1000:
                    var.set(1000)
                else:
                    var.set(value)
                return True
            else:
                var.set(1)
                return True

        vcmd_multisiddon_sens = (self.register(lambda P: validate_multisiddon_lines(P, self.multisiddon_sensitivity_lines_var)), '%P')
        vcmd_multisiddon_recon = (self.register(lambda P: validate_multisiddon_lines(P, self.multisiddon_reconstruction_lines_var)), '%P')

        ttk.Label(algorithm_frame, text="Iterations and Subsets:").grid(row=0, column=0, sticky="nsew", padx=(5, 2))
        ttk.Entry(algorithm_frame, textvariable=self.iterations_var,width=29).grid(row=0, column=1, sticky="w")
        ttk.Label(algorithm_frame, text="Format: iterations:subsets").grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(5, 2))

        opt_proj_pnl_frame = ttk.Frame(algorithm_frame)
        opt_proj_pnl_frame.grid(row=2, column=0, columnspan=2, pady=3, sticky="nsew")
        # Optimizer
        ttk.Label(opt_proj_pnl_frame, text="Optimizer:").grid(row=0, column=0, sticky="nsew", padx=(5, 2))
        opti_menu_button = ttk.Menubutton(opt_proj_pnl_frame, textvariable=self.optimizer_var, width=12)
        opti_menu_button.grid(row=0, column=1, pady=3)
        opti_menu_button.menu = tk.Menu(opti_menu_button, tearoff=0)
        opti_menu_button["menu"] = opti_menu_button.menu
        for item in ["MLEM", "OSL", "DEPIERRO95", "BSREM", "MLMUMAP", "NEGML"]:
            opti_menu_button.menu.add_radiobutton(label=item, variable=self.optimizer_var, value=item)

        # Penalty
        ttk.Label(opt_proj_pnl_frame, text="Penalty:").grid(row=0, column=3, sticky="nsew", padx=(5, 2))
        penalty_menu = ttk.Menubutton(opt_proj_pnl_frame, textvariable=self.penalty_var)
        penalty_menu.grid(row=0, column=4, pady=3, padx=(0, 5))
        penalty_menu.menu = tk.Menu(penalty_menu, tearoff=0)
        penalty_menu["menu"] = penalty_menu.menu
        for item in ["MRF", "MRP"]:
            penalty_menu.menu.add_radiobutton(label=item, variable=self.penalty_var, value=item)

        # Projector
        ttk.Label(opt_proj_pnl_frame, text="Projector:").grid(row=1, column=0, sticky="nsew", padx=(5, 2))
        proj_menu_button = ttk.Menubutton(opt_proj_pnl_frame, textvariable=self.projector_var, width=12)
        proj_menu_button.grid(row=1, column=1)
        proj_menu_button.menu = tk.Menu(proj_menu_button, tearoff=0)
        proj_menu_button["menu"] = proj_menu_button.menu
        for item in ["joseph", "classicSiddon", "incrementalSiddon", "distanceDriven", "multiSiddon"]:
            proj_menu_button.menu.add_radiobutton(label=item, variable=self.projector_var, value=item)

        # Penalty strength
        ttk.Label(opt_proj_pnl_frame, text="Strength:").grid(row=1, column=3, sticky="nsew", padx=(5, 2))
        spinbox_penalty_strength = ttk.Spinbox(opt_proj_pnl_frame, textvariable=self.penalty_strength_var,from_=0, to=100, increment=0.1, width=6, validate='focusout', validatecommand=vcmd_penalty_strength)
        spinbox_penalty_strength.grid(row=1, column=4, padx=(0, 5))
        spinbox_penalty_strength.bind('<Return>', lambda event: validate_spinbox_penalty_strength(spinbox_penalty_strength.get()))

        # MultiSiddon parameters frame (initially hidden)
        self.multisiddon_frame = ttk.Frame(algorithm_frame)
        self.multisiddon_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="nsew")
        
        ttk.Label(self.multisiddon_frame, text="MultiSiddon Parameters:", font=("Helvetica", 9, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 5))
        
        ttk.Label(self.multisiddon_frame, text="Lines for Sensitivity:").grid(row=1, column=0, sticky="w", padx=(5, 2))
        spinbox_sens_lines = ttk.Spinbox(self.multisiddon_frame, textvariable=self.multisiddon_sensitivity_lines_var, 
                                        from_=1, to=1000, increment=1, width=8, validate='focusout', validatecommand=vcmd_multisiddon_sens)
        spinbox_sens_lines.grid(row=1, column=1, padx=(0, 10))
        spinbox_sens_lines.bind('<Return>', lambda event: validate_multisiddon_lines(spinbox_sens_lines.get(), self.multisiddon_sensitivity_lines_var))
        
        ttk.Label(self.multisiddon_frame, text="Lines for Reconstruction:").grid(row=1, column=2, sticky="w", padx=(5, 2))
        spinbox_recon_lines = ttk.Spinbox(self.multisiddon_frame, textvariable=self.multisiddon_reconstruction_lines_var, 
                                         from_=1, to=1000, increment=1, width=8, validate='focusout', validatecommand=vcmd_multisiddon_recon)
        spinbox_recon_lines.grid(row=1, column=3, padx=(0, 5))
        spinbox_recon_lines.bind('<Return>', lambda event: validate_multisiddon_lines(spinbox_recon_lines.get(), self.multisiddon_reconstruction_lines_var))

        # Initially hide the MultiSiddon parameters
        self.multisiddon_frame.grid_remove()

        # Function to toggle penalty options based on optimizer selection
        def update_penalty_menu():
            # replace with your actual optimizer variable
            optimizer = self.optimizer_var.get()
            if optimizer == "MLEM":
                penalty_menu.config(state="disabled")
                spinbox_penalty_strength.config(state="disabled")
            else:
                penalty_menu.config(state="normal")
                spinbox_penalty_strength.config(state="normal")
                if optimizer == "OSL":
                    penalty_menu.menu.delete(0, 'end')
                    for item in ["MRF", "MRP"]:
                        penalty_menu.menu.add_radiobutton(label=item, variable=self.penalty_var, value=item)
                elif optimizer == "DEPIERRO95":
                    penalty_menu.menu.delete(0, 'end')
                    penalty_menu.menu.add_radiobutton(label="MRF", variable=self.penalty_var, value="MRF")
                    self.penalty_var.set("MRF")

        # Function to show/hide MultiSiddon parameters
        def update_multisiddon_visibility():
            if self.projector_var.get() == "multiSiddon":
                self.multisiddon_frame.grid()
            else:
                self.multisiddon_frame.grid_remove()

        self.optimizer_var.trace_add("write", lambda *args: update_penalty_menu())
        self.projector_var.trace_add("write", lambda *args: update_multisiddon_visibility())
        
        # Initially call the functions to set the initial state
        update_penalty_menu()
        update_multisiddon_visibility()

    def update_single_convolution_value(self, index):
        """Update the convolution value string for a specific convolution"""
        if index < len(self.convolution_value_vars):
            x_val = self.convolution_x_var[index].get()
            y_val = self.convolution_y_var[index].get()
            sigma_val = self.convolution_sigma_var[index].get()
            type_val = self.convolution_type_vars[index].get()
            
            # Format: "gaussian,X,Y,sigma::type"
            conv_value = f"gaussian,{x_val},{y_val},{sigma_val}::{type_val}"
            self.convolution_value_vars[index].set(conv_value)

    def update_convolution_entries(self):
        # Get the current number of convolutions
        num_conv = self.convolution_num_var.get()

        # Initialize convolution arrays if they don't exist
        if not hasattr(self, 'previous_num_conv'):
            self.previous_num_conv = 0
            
        if not hasattr(self, 'convolution_frame'):
            return

        # Clear all existing convolution widgets (except the first row with checkbox and spinbox)
        for widget in self.convolution_frame.grid_slaves():
            row = widget.grid_info().get("row", -1)
            col = widget.grid_info().get("column", -1)
            if row is not None and col is not None and row >= 0 and col >= 3:
                widget.grid_forget()

        # If convolution is disabled, show disabled widgets
        if not self.convolution_need_bool_var.get() or num_conv == 0:
            # Clear any existing convolution widgets
            for widget in self.convolution_frame.grid_slaves():
                if int(widget.grid_info()["row"]) >= 0 and int(widget.grid_info()["column"]) >= 3:
                    widget.grid_forget()
                    
            ttk.Label(self.convolution_frame, text="Conv 0. Type:").grid(row=0, column=3, padx=(5, 2), sticky="w")
            menu_button = ttk.Menubutton(self.convolution_frame, textvariable=tk.StringVar(value="psf"), state="disabled", width=10)
            menu_button.grid(row=0, column=4, columnspan=3, sticky="w")
            menu_button.menu = tk.Menu(menu_button, tearoff=0)
            menu_button["menu"] = menu_button.menu
            for item in ["psf", "post", "sieve", "intra", "backward", "forward"]:
                menu_button.menu.add_radiobutton(label=item, variable=tk.StringVar(), value=item)
            
            ttk.Label(self.convolution_frame, text="Size (X,Y,Sig):").grid(row=1, column=3, padx=(5, 2), sticky="w")
            ttk.Spinbox(self.convolution_frame, textvariable=tk.DoubleVar(value=0.0), state="disabled", width=3).grid(row=1, column=4, sticky="w")
            ttk.Spinbox(self.convolution_frame, textvariable=tk.DoubleVar(value=0.0), state="disabled", width=3).grid(row=1, column=5, sticky="w")
            ttk.Spinbox(self.convolution_frame, textvariable=tk.DoubleVar(value=0.0), state="disabled", width=3).grid(row=1, column=6, sticky="w")
            
            self.previous_num_conv = 0
            return

        # Ensure we have enough convolution variables
        while len(self.convolution_type_vars) < num_conv:
            self.convolution_type_vars.append(tk.StringVar(value="psf"))
            self.convolution_x_var.append(tk.DoubleVar(value=1.0))
            self.convolution_y_var.append(tk.DoubleVar(value=1.0))
            self.convolution_sigma_var.append(tk.DoubleVar(value=3.0))
            self.convolution_value_vars.append(tk.StringVar(value=""))

        # Remove extra convolution variables if needed
        if len(self.convolution_type_vars) > num_conv:
            del self.convolution_type_vars[num_conv:]
            del self.convolution_x_var[num_conv:]
            del self.convolution_y_var[num_conv:]
            del self.convolution_sigma_var[num_conv:]
            del self.convolution_value_vars[num_conv:]

        # Create convolution parameter widgets
        for i in range(num_conv):
            # Calculate row and column positions
            # First 2 convolutions on row 0-1, next 2 on row 2-3, etc.
            base_row = (i // 2) * 2
            col_offset = (i % 2) * 5  # 5 columns per convolution (label + 3 spinboxes + spacing)
            
            # Type label and menu
            ttk.Label(self.convolution_frame, text=f"Conv {i+1} Type:").grid(
                row=base_row, column=3 + col_offset, padx=(5, 2), sticky="w")
            
            menu_button = ttk.Menubutton(self.convolution_frame, textvariable=self.convolution_type_vars[i], width=8)
            menu_button.grid(row=base_row, column=4 + col_offset, columnspan=2, sticky="w")
            menu_button.menu = tk.Menu(menu_button, tearoff=0)
            menu_button["menu"] = menu_button.menu
            for item in ["psf", "post", "sieve", "intra", "backward", "forward"]:
                menu_button.menu.add_radiobutton(label=item, variable=self.convolution_type_vars[i], value=item)
            
            # Size label
            ttk.Label(self.convolution_frame, text="Size (X,Y,Sig):").grid(
                row=base_row + 1, column=3 + col_offset, padx=(5, 2), sticky="w")
            
            # X spinbox
            spinbox_x = ttk.Spinbox(self.convolution_frame, from_=0, to=100, increment=0.1,
                                   textvariable=self.convolution_x_var[i], width=4)
            spinbox_x.grid(row=base_row + 1, column=4 + col_offset, sticky="w")
            
            # Y spinbox  
            spinbox_y = ttk.Spinbox(self.convolution_frame, from_=0, to=100, increment=0.1,
                                   textvariable=self.convolution_y_var[i], width=4)
            spinbox_y.grid(row=base_row + 1, column=5 + col_offset, sticky="w")
            
            # Sigma spinbox
            spinbox_sigma = ttk.Spinbox(self.convolution_frame, from_=0, to=100, increment=0.1,
                                       textvariable=self.convolution_sigma_var[i], width=4)
            spinbox_sigma.grid(row=base_row + 1, column=6 + col_offset, sticky="w")
            
            # Add trace to update convolution values when any parameter changes
            if not hasattr(self.convolution_x_var[i], '_trace_added'):
                self.convolution_x_var[i].trace_add("write", lambda *args, idx=i: self.update_single_convolution_value(idx))
                self.convolution_y_var[i].trace_add("write", lambda *args, idx=i: self.update_single_convolution_value(idx))
                self.convolution_sigma_var[i].trace_add("write", lambda *args, idx=i: self.update_single_convolution_value(idx))
                self.convolution_type_vars[i].trace_add("write", lambda *args, idx=i: self.update_single_convolution_value(idx))
                self.convolution_x_var[i]._trace_added = True

        self.previous_num_conv = num_conv
        
        # Update all convolution values
        for i in range(num_conv):
            self.update_single_convolution_value(i)

    def create_convolution_widgets(self, options_frame):
        self.convolution_frame = ttk.LabelFrame(options_frame, text="Convolutions")
        self.convolution_frame.grid(row=2, column=0, columnspan=2,padx=10, pady=5, sticky="nsew")

        def toggle_spinbox():
            if self.convolution_need_bool_var.get() == 0:
                self.convolution_num_var.set(0)
                self.conv_spinbox.config(state='disabled')
                self.update_convolution_entries()
            else:
                self.convolution_num_var.set(1)
                self.conv_spinbox.config(state='normal')
                self.update_convolution_entries()

        def validate_spinbox_input(P):
            # P is the new value of the Spinbox after the edit
            if P == "":
                self.convolution_num_var.set(0)
            elif P.isdigit():
                if int(P) > 10:
                    self.convolution_num_var.set(10)
                elif int(P) < 0:
                    self.convolution_num_var.set(0)
            else:
                self.convolution_num_var.set(0)
                
            self.update_convolution_entries()
            return True
        vcmd = (self.register(validate_spinbox_input), '%P')

        # CheckButton for Convolution
        ttk.Checkbutton(self.convolution_frame, text="Apply Convolutions", variable=self.convolution_need_bool_var, command=toggle_spinbox).grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5)
        # Spinbox for number of convolutions
        ttk.Label(self.convolution_frame, text="Nb of Conv:").grid(row=1, column=0, sticky="nsew", padx=(5, 0), pady=3)
        self.conv_spinbox = ttk.Spinbox(self.convolution_frame, textvariable=self.convolution_num_var, from_=0, to=10, increment=1, width=3, validate='focusout', validatecommand=vcmd, command=lambda: self.update_convolution_entries())
        self.conv_spinbox.grid(row=1, column=1, pady=(0, 5))
        self.conv_spinbox.bind('<Return>', lambda event: validate_spinbox_input(self.conv_spinbox.get()))
        # Separator between these two and convolutions entries
        separator = ttk.Separator(self.convolution_frame, orient="vertical")
        separator.grid(row=0, column=2, rowspan=2, sticky="ns", padx=5, pady=5)
        
        # Call the function initially to create the initial entries
        self.update_convolution_entries()

    def convert_absolute_to_relative_path(self, abs_path):
        # Assuming your script's directory is the base for relative paths
        rel_path = os.path.relpath(abs_path, self.script_dir)
        return os.path.normpath(rel_path)

    def browse_path(self, path_var):
        """Open file dialog starting at user's home directory."""
        initial_dir = path_var.get() or str(Path.home())
        abs_path = filedialog.askopenfilename(initialdir=initial_dir)
        if abs_path:
            path_var.set(abs_path)
            
    def browse_folder(self, path_var):
        """Open folder dialog starting at user's home directory."""
        initial_dir = path_var.get() or str(Path.home())
        abs_path = filedialog.askdirectory(initialdir=initial_dir)
        if abs_path:
            path_var.set(abs_path)

    def validate_program_path(self, path_var):
        path = path_var.get()
        if path_var == self.sensitivity_path_var and path == "":
            return True
        elif not os.path.isfile(path):
            messagebox.showerror("Invalid File Path", "The specified file path is invalid.")
            return False
        elif path_var == self.main_program_path_var and not path.endswith(".exe"):
            messagebox.showerror("Invalid Main Program Path", "The specified path is not an executable.")
            return False
        elif path_var == self.datafile_path_var and not path.endswith(".Cdh"):
            messagebox.showerror("Invalid DataFile Path", "The specified path is not a Cdh file.")
            return False
        elif path_var == self.attenuation_path_var and not path.endswith(".hdr"):
            messagebox.showerror("Invalid Attenuation Image", "The specified Image is not a hdr file.")
            return False
        elif path_var == self.normalization_path_var and not path.endswith(".hdr"):
            messagebox.showerror("Invalid Normalization Path", "The specified Image is not a hdr file.")
            return False
        elif path_var == self.sensitivity_path_var and not path.endswith(".hdr"):
            messagebox.showerror("Invalid Sensitivity Path", "The specified file path is not a hdr file.")
            return False
        return True
    
    def validate_folder_path(self, path_var):
        path = path_var.get()
        if path_var == self.configuration_path_var and path == "":
            return True
        elif not os.path.isdir(path):
            messagebox.showerror("Invalid Folder Path", "The specified folder path is invalid.")
            return False
        return True
    
    def is_valid_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def get_ignore_corrections_string(self):
        """Generate the string for ignored corrections based on checkbox states"""
        corrections_to_ignore = []
        
        if self.ignore_attn_var.get():
            corrections_to_ignore.append("attn")
        if self.ignore_norm_var.get():
            corrections_to_ignore.append("norm")
        if self.ignore_rand_var.get():
            corrections_to_ignore.append("rand")
        if self.ignore_scat_var.get():
            corrections_to_ignore.append("scat")
        if self.ignore_deca_var.get():
            corrections_to_ignore.append("deca")
        if self.ignore_brat_var.get():
            corrections_to_ignore.append("brat")
        if self.ignore_fdur_var.get():
            corrections_to_ignore.append("fdur")
        if self.ignore_cali_var.get():
            corrections_to_ignore.append("cali")
        
        if corrections_to_ignore:
            return ",".join(corrections_to_ignore)
        else:
            return ""

    def generate_script(self, save = True, info = True):
        # Retrieve user inputs
        mpi_enabled = self.mpi_bool_var.get()
        mpi_threads = self.mpi_threads_var.get()
        verbose_level = self.verbose_level_var.get()
        last_iter = self.last_iter_bool_var.get()
        flip = self.flip_var.get()
        stats_need = self.stats_need_bool_var.get()

        main_program_path = self.main_program_path_var.get()
        datafile = self.datafile_path_var.get()
        attenuation = self.attenuation_path_var.get()
        normalization = self.normalization_path_var.get()
        output_path = self.output_path_var.get()
        sensitivity_path = self.sensitivity_path_var.get()
        configuration_path = self.configuration_path_var.get()

        voxel_number = self.voxel_number_var.get()
        voxel_size = self.voxel_size_var.get()
        fov_size = self.fov_size_var.get()
        offset = self.offset_var.get()
        voxel_size_x = self.voxel_size_x_var.get()
        voxel_size_y = self.voxel_size_y_var.get()
        voxel_size_z = self.voxel_size_z_var.get()
        voxel_number_x = self.voxel_number_x_var.get()
        voxel_number_y = self.voxel_number_y_var.get()
        voxel_number_z = self.voxel_number_z_var.get()
        fov_size_x = self.fov_size_x_var.get()
        fov_size_y = self.fov_size_y_var.get()
        fov_size_z = self.fov_size_z_var.get()
        offset_x = self.offset_x_var.get()
        offset_y = self.offset_y_var.get()
        offset_z = self.offset_z_var.get()

        iterations = self.iterations_var.get()
        optimizer = self.optimizer_var.get()
        projector = self.projector_var.get()
        penalty = self.penalty_var.get()
        penalty_strength = self.penalty_strength_var.get()
        convolution_need = self.convolution_need_bool_var.get()
        convolution_num = self.convolution_num_var.get()
        convolution_types = [var.get() for var in self.convolution_type_vars]
        convolution_values = [var.get() for var in self.convolution_value_vars]
        convolution_x = [var.get() for var in self.convolution_x_var]
        convolution_y = [var.get() for var in self.convolution_y_var]
        convolution_sigma = [var.get() for var in self.convolution_sigma_var]

        # Get corrections to ignore
        ignore_corrections = self.get_ignore_corrections_string()

        # Get MultiSiddon parameters if applicable
        multisiddon_sens_lines = self.multisiddon_sensitivity_lines_var.get()
        multisiddon_recon_lines = self.multisiddon_reconstruction_lines_var.get()

       
        # Start writing the batch script
        script_content = "@echo off\n"
        script_content += ":: Batch script generated by Python GUI to run the CASToR program\n"
        script_content += ":: To get help run the main programm in the comman-line withou any argument or with 'h', '-help' or '--help' options\n\n"

        # Set Command Line Options
        script_content += ":::::::::::::::::::::::::::::\n"
        script_content += ":: Set Command Line Options\n"
        script_content += ":::::::::::::::::::::::::::::\n\n"

        # Set MPI stuff and recon program
        if mpi_enabled:
            script_content += f"@REM MPI enabled with {mpi_threads} threads\n"
            if mpi_threads > 0:
                script_content += "set mpi_exe=mpiexec.exe -n %d\n" % mpi_threads
            if mpi_threads == 0:
                script_content += "set mpi_exe=mpiexec.exe\n"
        else:
            script_content += "@REM MPI disabled\n"
            script_content += "set mpi_exe=\n"

        # Set the main program path
        script_content += f"set recon_exe={main_program_path}\n\n"

        # Set verbose level, threads, stats need, last iter, flip
        script_content += f"set verbose= -vb {verbose_level}\n"
        script_content += f"set threads= -th {mpi_threads}\n\n"
        if stats_need:
            script_content += "set stats= -opti-stat\n"
        else: 
            script_content += "set stats=\n"
        if last_iter:
            script_content += "set last_it= -oit -1\n"
        else:
            script_content += "set last_it=\n"
        if flip != "None":
            script_content += f"set flip_out= -flip-out {flip}\n"
        else:
            script_content += "set flip_out=\n\n"
        
        # Set the datafile path
        script_content += f"set datafile= -df {datafile}\n"
        # Set the output path
        script_content += f"set output= -dout {output_path}\n"
        # Set the sensitivity path
        if sensitivity_path != "":
            script_content += f"set sensitivity= -sens {sensitivity_path}\n"
        else:
            script_content += "set sensitivity=\n"
        # Set the configuration path
        if configuration_path != "":
            script_content += f"set configuration= -conf {configuration_path}\n\n"
        else:
            script_content += "set configuration=\n\n"

        # Set the voxel number, size, fov size, offset
        script_content += f"set voxel_number= -dim {voxel_number_x},{voxel_number_y},{voxel_number_z}\n"
        script_content += f"set voxel_size= -vox {voxel_size_x},{voxel_size_y},{voxel_size_z}\n"
        script_content += f"set offset= -off {offset_x},{offset_y},{offset_z}\n\n"

        # Set the iterations, optimizer, projector, penalty, penalty strength
        script_content += f"set iterations= -it {iterations}\n"
        script_content += f"set optimizer= -opti {optimizer}\n"
        
        # Set projector with MultiSiddon parameters if applicable
        if projector == "multiSiddon":
            script_content += f"set projector= -proj {projector},{multisiddon_sens_lines},{multisiddon_recon_lines}\n"
        else:
            script_content += f"set projector= -proj {projector}\n"
            
        if optimizer == "MLEM":
            script_content += "set penalty=\n"
            script_content += "set penalty_strength=\n"
        else:
            script_content += f"set penalty= -pnlt {penalty}\n"
            script_content += f"set penalty_strength= -pnlt-beta {penalty_strength}\n\n"

        # Set the ignore corrections
        if ignore_corrections:
            script_content += f"set ignore_corr= -ignore-corr {ignore_corrections}\n\n"
        else:
            script_content += "set ignore_corr=\n\n"
        
        # Set the convolution options
        if convolution_need:
            script_content += f"@REM Set {convolution_num} convolution(s)\n"
            for i in range(convolution_num):
                script_content += f"set psf_{i+1}= -conv {convolution_values[i]}\n\n"

        # Run the main program
        script_content += ":::::::::::::::::::::::::::::\n"
        script_content += ":: Launch the reconstruction\n"
        script_content += ":::::::::::::::::::::::::::::\n\n"

        script_content += "echo ==========================================================\n"
        script_content += "echo Reconstruction is going on. Should take several minutes\n"
        script_content += "echo ==========================================================\n\n"

        script_content += f"%mpi_exe% %recon_exe% %verbose% %threads% %stats% %last_it% %flip_out% %datafile% %output% %sensitivity% %configuration% %voxel_number% %voxel_size% %offset% %iterations% %optimizer% %projector% %penalty% %penalty_strength% %ignore_corr% "
        if convolution_need:
            for i in range(convolution_num):
                script_content += f"%psf_{i+1}% "
        script_content += "\n\n"

        script_content += "echo ==========================================================\n"
        script_content += "echo Reconstruction is finished!\n"
        script_content += "echo ==========================================================\n\n"
        # Define the path for the script
        self.script_name = "run_castor_python_script.bat"
        self.script_path = os.path.join(self.script_dir, self.script_name)
        
        if save:
            # Write and save the script to the file
            with open(self.script_path, "w") as file:
                file.write(script_content)
        
        # Display the generated script in a message box
        if info:
            with open(self.script_path, "r") as file:
                script = file.read()
            messagebox.showinfo("Generated Batch Script", script)
            
    def generateShell_script(self, save = True, info = True):
        # Retrieve user inputs
        mpi_enabled = self.mpi_bool_var.get()
        mpi_threads = self.mpi_threads_var.get()
        verbose_level = self.verbose_level_var.get()
        last_iter = self.last_iter_bool_var.get()
        flip = self.flip_var.get()
        stats_need = self.stats_need_bool_var.get()

        main_program_path = self.main_program_path_var.get()
        datafile = self.datafile_path_var.get()
        attenuation = self.attenuation_path_var.get()
        normalization = self.normalization_path_var.get()
        output_path = self.output_path_var.get()
        sensitivity_path = self.sensitivity_path_var.get()
        configuration_path = self.configuration_path_var.get()

        voxel_number = self.voxel_number_var.get()
        voxel_size = self.voxel_size_var.get()
        fov_size = self.fov_size_var.get()
        offset = self.offset_var.get()
        voxel_size_x = self.voxel_size_x_var.get()
        voxel_size_y = self.voxel_size_y_var.get()
        voxel_size_z = self.voxel_size_z_var.get()
        voxel_number_x = self.voxel_number_x_var.get()
        voxel_number_y = self.voxel_number_y_var.get()
        voxel_number_z = self.voxel_number_z_var.get()
        fov_size_x = self.fov_size_x_var.get()
        fov_size_y = self.fov_size_y_var.get()
        fov_size_z = self.fov_size_z_var.get()
        offset_x = self.offset_x_var.get()
        offset_y = self.offset_y_var.get()
        offset_z = self.offset_z_var.get()

        iterations = self.iterations_var.get()
        optimizer = self.optimizer_var.get()
        projector = self.projector_var.get()
        penalty = self.penalty_var.get()
        penalty_strength = self.penalty_strength_var.get()
        convolution_need = self.convolution_need_bool_var.get()
        convolution_num = self.convolution_num_var.get()
        convolution_types = [var.get() for var in self.convolution_type_vars]
        convolution_values = [var.get() for var in self.convolution_value_vars]
        convolution_x = [var.get() for var in self.convolution_x_var]
        convolution_y = [var.get() for var in self.convolution_y_var]
        convolution_sigma = [var.get() for var in self.convolution_sigma_var]
        
        # Get corrections to ignore
        ignore_corrections = self.get_ignore_corrections_string()
        
        # Get MultiSiddon parameters if applicable
        multisiddon_sens_lines = self.multisiddon_sensitivity_lines_var.get()
        multisiddon_recon_lines = self.multisiddon_reconstruction_lines_var.get()
        
        # Start writing the batch script
        script_content = "#!/bin/bash\n"
        script_content += "# Batch script generated by Python GUI to run the CASToR program\n"
        script_content += "# To get help run the main programm in the comman-line withou any argument or with 'h', '-help' or '--help' options\n\n"
        
        # Set Command Line Options
        script_content += "###########################\n"
        script_content += "## Set Command Line Options\n"
        script_content += "###########################\n\n"
        
        # Set MPI stuff and recon program ---- nao percebo como adaptar para linux
        if mpi_enabled:
            if mpi_threads > 0:
                script_content += f"mpi_exe=\"mpiexec -n {mpi_threads}\"\n"
            else:
                script_content += "mpi_exe=\"mpiexec\"\n"
        else:
            script_content += "mpi_exe=\"\"\n"
            
        # Set the main program path
        script_content += f"recon_exe={main_program_path}\n\n"

        # Set verbose level, threads, stats need, last iter, flip
        script_content += f"verbose=\"-vb {verbose_level}\"\n"
        #script_content += f"threads=\"-th {mpi_threads}\"\n\n"
        if mpi_enabled:
            script_content += f"threads=\"-th {mpi_threads}\"\n\n"
        else:
            script_content += "threads=\"\"\n"
            
        if stats_need:
            script_content += "stats=\"-opti-stat\"\n"
        else: 
            script_content += "stats=\n"
        if last_iter:
            script_content += "last_it=\"-oit -1\"\n"
        else:
            script_content += "last_it=\n"
        if flip != "None":
            script_content += f"flip_out=\"-flip-out {flip}\"\n"
        else:
            script_content += "flip_out=\n\n"
        
        # Set the datafile path
        script_content += f"datafile=\"-df {datafile}\"\n"
        
        # Set the attenuation path (only if specified)
        if attenuation != "":
            script_content += f"attenuation=\"-atn {attenuation}\"\n"
        else:
            script_content += "attenuation=\n"
        
        # Set the normalization path (only if specified)
        if normalization != "":
            script_content += f"normalization=\"-norm {normalization}\"\n"
        else:
            script_content += "normalization=\n"
        
        # Set the output path
        script_content += f"output=\"-dout {output_path}\"\n"
        # Set the sensitivity path
        if sensitivity_path != "":
            script_content += f"sensitivity=\"-sens {sensitivity_path}\"\n"
        else:
            script_content += "sensitivity=\n"
        # Set the configuration path
        if configuration_path != "":
            script_content += f"configuration=\"-conf {configuration_path}\"\n\n"
        else:
            script_content += "configuration=\n\n"
            
        # Set the voxel number, size, fov size, offset
        script_content += f"voxel_number=\"-dim {voxel_number_x},{voxel_number_y},{voxel_number_z}\"\n"
        script_content += f"voxel_size=\"-vox {voxel_size_x},{voxel_size_y},{voxel_size_z}\"\n"
        script_content += f"offset=\"-off {offset_x},{offset_y},{offset_z}\"\n\n"
        
         # Set the iterations, optimizer, projector, penalty, penalty strength
        script_content += f"iterations=\"-it {iterations}\"\n"
        script_content += f"optimizer=\"-opti {optimizer}\"\n"
        
        # Set projector with MultiSiddon parameters if applicable
        if projector == "multiSiddon":
            script_content += f"projector=\"-proj {projector},{multisiddon_sens_lines},{multisiddon_recon_lines}\"\n"
        else:
            script_content += f"projector=\"-proj {projector}\"\n"
            
        if optimizer == "MLEM":
            script_content += "penalty=\n"
            script_content += "penalty_strength=\n"
        else:
            script_content += f"penalty=\"-pnlt {penalty}\"\n"
            script_content += f"penalty_strength=\"-pnlt-beta {penalty_strength}\"\n\n"

        # Set the ignore corrections
        if ignore_corrections:
            script_content += f"ignore_corr=\"-ignore-corr {ignore_corrections}\"\n\n"
        else:
            script_content += "ignore_corr=\n\n"
            
        # Set the convolution options
        if convolution_need:
            script_content += f"# {convolution_num} convolution(s)\n"
            for i in range(convolution_num):
                script_content += f"psf_{i+1}=\"-conv {convolution_values[i]}\"\n\n"

        # Run the main program
        script_content += "############################\n"
        script_content += "## Launch the reconstruction\n"
        script_content += "############################\n\n"

        script_content += "echo ==========================================================\n"
        script_content += "echo Reconstruction is going on. Should take several minutes\n"
        script_content += "echo ==========================================================\n\n"

        script_content += "${mpi_exe} ${recon_exe} ${verbose} ${threads} ${stats} ${last_it} ${flip_out} ${datafile} ${attenuation} ${normalization} ${output} ${sensitivity} ${configuration} ${voxel_number} ${voxel_size} ${offset} ${iterations} ${optimizer} ${projector} ${penalty} ${penalty_strength} ${ignore_corr} "
        if convolution_need:
            for i in range(convolution_num):
                script_content += f"${{psf_{i+1}}} "
        script_content += "\n\n"

        script_content += "echo ==========================================================\n"
        script_content += "echo Reconstruction is finished!\n"
        script_content += "echo ==========================================================\n\n"
        # Define the path for the script
        self.script_name = "run_castor_python_script.sh"
        self.script_path = os.path.join(self.script_dir, self.script_name)
        
        if save:
            # Write and save the script to the file
            with open(self.script_path, "w") as file:
                file.write(script_content)
        
        # Display the generated script in a message box
        if info:
            with open(self.script_path, "r") as file:
                script = file.read()
            messagebox.showinfo("Generated Shell Script", script)
         

    def run_castor_program(self):
        # Run CASToR with the generated script
        self.generate_script(save=False, info=True)
        print(f'Running the CASToR program with the generated script: \"{self.script_path}\"')
        command = f"powershell -NoExit -Command \"& '{self.script_path}'\""
        os.system(f"start {command}")
        
    def run_castor_program_Linux(self):
        # Generate the shell script before running
        self.generateShell_script()

        # Ensure the script has execution permissions
        os.chmod(self.script_path, 0o755)  

        # Run the script in a new terminal window
        print(f'Running the CASToR program with the generated script: \"{self.script_path}\"')
        os.system(f"gnome-terminal -- bash -c '{self.script_path}; exec bash'")


    def print_test_all_variables(self):
        self.update_entries()

        print("All Variables:")
        print("MPI:", self.mpi_bool_var.get())
        print("MPI Threads:", self.mpi_threads_var.get())
        print("Verbose Level:", self.verbose_level_var.get())
        print("Last Iteration:", self.last_iter_bool_var.get())
        print("Flip:", self.flip_var.get())
        print("Stats Need:", self.stats_need_bool_var.get())

        print("Main Program Path:", self.main_program_path_var.get())
        print("Datafile Path:", self.datafile_path_var.get())
        print("Attenuation Path:", self.attenuation_path_var.get())
        print("Normalization Path:", self.normalization_path_var.get())
        print("Output Path:", self.output_path_var.get())
        print("Sensitivity Path:", self.sensitivity_path_var.get())
        print("Configuration Path:", self.configuration_path_var.get())

        print("Voxel Number:", self.voxel_number_var.get())
        print("Voxel Size:", self.voxel_size_var.get())
        print("FOV Size:", self.fov_size_var.get())
        print("Offset:", self.offset_var.get())
        print("Voxel Size X:", self.voxel_size_x_var.get())
        print("Voxel Size Y:", self.voxel_size_y_var.get())
        print("Voxel Size Z:", self.voxel_size_z_var.get())
        print("Voxel Number X:", self.voxel_number_x_var.get())
        print("Voxel Number Y:", self.voxel_number_y_var.get())
        print("Voxel Number Z:", self.voxel_number_z_var.get())
        print("FOV Size X:", self.fov_size_x_var.get())
        print("FOV Size Y:", self.fov_size_y_var.get())
        print("FOV Size Z:", self.fov_size_z_var.get())
        print("Offset X:", self.offset_x_var.get())
        print("Offset Y:", self.offset_y_var.get())
        print("Offset Z:", self.offset_z_var.get())

        print("Iterations:", self.iterations_var.get())
        print("Optimizer:", self.optimizer_var.get())
        print("Projector:", self.projector_var.get())
        print("Penalty:", self.penalty_var.get())
        print("Penalty Strength:", self.penalty_strength_var.get())
        print("Convolution Need:", self.convolution_need_bool_var.get())
        print("Convolution Num:", self.convolution_num_var.get())
        print("Convolution Types:", [var.get()for var in self.convolution_type_vars])
        print("Convolution Values:", [var.get() for var in self.convolution_value_vars])
        print("Convolution X:", [var.get() for var in self.convolution_x_var])
        print("Convolution Y:", [var.get() for var in self.convolution_y_var])
        print("Convolution Sigma:", [var.get()for var in self.convolution_sigma_var])

        # Corrections to ignore
        print("Ignore Attenuation:", self.ignore_attn_var.get())
        print("Ignore Normalization:", self.ignore_norm_var.get())
        print("Ignore Random:", self.ignore_rand_var.get())
        print("Ignore Scatter:", self.ignore_scat_var.get())
        print("Ignore Decay:", self.ignore_deca_var.get())
        print("Ignore Branching Ratio:", self.ignore_brat_var.get())
        print("Ignore Frame Duration:", self.ignore_fdur_var.get())
        print("Ignore Calibration:", self.ignore_cali_var.get())
        print("Ignore Corrections String:", self.get_ignore_corrections_string())

        # MultiSiddon parameters
        print("MultiSiddon Sensitivity Lines:", self.multisiddon_sensitivity_lines_var.get())
        print("MultiSiddon Reconstruction Lines:", self.multisiddon_reconstruction_lines_var.get())

    def show_about(self):

        help_window = tk.Toplevel()
        help_window.title("About the CASToR Reconstruction GUI")
        help_window.geometry("1000x600")
        help_window.resizable(True, True)

    # Create a scrollable text area with visible colors
        text_area = st.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=("Courier", 11),
            bg="white",
            fg="black",
            insertbackground="black"
        )
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Define font styles
        bold_font = tkfont.Font(text_area, text_area.cget("font"))
        bold_font.configure(weight="bold")

        # Create tag for bold text
        text_area.tag_configure("bold", font=bold_font)

        # --- Insert content ---
        text_area.insert(tk.END, "==============================\n", ())
        text_area.insert(tk.END, "CASToR Reconstruction GUI Tool\n", ("bold",))
        text_area.insert(tk.END, "==============================\n\n", ())

        text_area.insert(tk.END, "This application provides a graphical interface to configure and run PET, SPECT or CT image reconstructions\n"
                             "using the CASToR (Customizable and Advanced Software for Tomographic Reconstruction) framework.\n\n")

        text_area.insert(tk.END, "------------------------\nWhat this tool does:\n------------------------\n", ("bold",))
        text_area.insert(tk.END, "• Simplifies the creation of batch (.bat) or shell (.sh) scripts to run the CASToR reconstructor on the terminal.\n"
                             "• Allows you to define and manage all reconstruction parameters visually.\n"
                             "• Lets you run the CASToR reconstruction directly from the GUI (on both Windows and Linux).\n"
                             "• Automatically generates organized output scripts for reproducibility and documentation.\n\n")

        text_area.insert(tk.END, "------------------------\nBasic Usage Instructions:\n------------------------\n", ("bold",))

        text_area.insert(tk.END, "1. Main Program Path\n", ("bold",))
        text_area.insert(tk.END, "   Select the 'castor-recon' executable file from your CASToR installation directory.\n\n")

        text_area.insert(tk.END, "2. Datafile (.cdh)\n", ("bold",))
        text_area.insert(tk.END, "   Select the reconstructed dataset file (*.cdh). This file is mandatory — the reconstruction cannot start without it.\n\n")

        text_area.insert(tk.END, "3. Attenuation / Normalization / Sensitivity (optional)\n", ("bold",))
        text_area.insert(tk.END, "   You can optionally provide attenuation, normalization, or sensitivity image files (*.hdr). "
                             "If not used, leave these fields empty.\n\n")

        text_area.insert(tk.END, "4. Output Folder\n", ("bold",))
        text_area.insert(tk.END, "   Choose a destination folder where CASToR will save reconstructed images and statistics. "
                             "This field is mandatory. You can also define a custom prefix for the output file names.\n\n")

        text_area.insert(tk.END, "5. Image Geometry\n", ("bold",))
        text_area.insert(tk.END, "   Define voxel number, voxel size, FOV (field of view), and image offset manually. "
                             "These parameters describe the dimensions and spatial positioning of your reconstructed image volume.\n\n")

        text_area.insert(tk.END, "6. Reconstruction Algorithm\n", ("bold",))
        text_area.insert(tk.END, "   Specify the number of iterations and subsets using the format iterations:subsets "
                             "(e.g., 10:20 for 10 iterations with 20 subsets each). "
                             "You can also choose the optimizer, projector model, and optional penalty function.\n\n")

        text_area.insert(tk.END, "7. Convolutions (optional)\n", ("bold",))
        text_area.insert(tk.END, "   Enable and configure one or more convolution filters (e.g., PSF or post-reconstruction smoothing).\n\n")

        text_area.insert(tk.END, "8. Corrections to Ignore\n", ("bold",))
        text_area.insert(tk.END, "   Select which corrections to ignore during reconstruction. Leave unchecked to apply all corrections.\n\n")

        text_area.insert(tk.END, "9. MPI (Parallel Computing)\n", ("bold",))
        text_area.insert(tk.END, "   Activate MPI to use multiple CPU threads for faster reconstruction. "
                             "If enabled, specify the number of threads according to your system's capabilities.\n"
                             "   ⚠️ Important: CASToR must be installed with the MPI option activated (compiled with MPI support). "
                             "Without MPI support, this feature will not work.\n\n")

        text_area.insert(tk.END, "10. Script Generation and Execution\n", ("bold",))
        text_area.insert(tk.END, "   • Click \"Generate batch script for Windows\" or \"Generate shell script for Linux\" to export your setup.\n"
                             "   • You can review the generated script content before saving.\n"
                             "   • Click \"Run CASToR program\" to execute the reconstruction directly from the GUI. "
                             "It will open a terminal window where the reconstruction will start.\n\n")

        text_area.insert(tk.END, "Additional Notes\n", ("bold",))
        text_area.insert(tk.END, "• The GUI automatically validates input paths and prevents invalid file types.\n"
                             "• Optional files can be left empty without affecting execution.\n"
                             "• For more details on CASToR parameters, run 'castor-recon' in a terminal window "
                             "or visit the CASToR documentation at https://castor-project.org/.\n\n"
                             "Developed originally by Miguel Lopes, adapted by Beatriz Ornelas for GATE PET reconstructions "
                             "to streamline CASToR reconstruction workflows.\n")

        # Make it read-only
        text_area.configure(state="disabled")

        # Add Close button
        close_button = tk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=5)

    def open_from_file(self):
        file_path = filedialog.askopenfilename(initialdir=self.script_dir)
        if file_path:
            with open(file_path, "r") as file:
                lines = file.readlines()
                del self.convolution_value_vars[:], self.convolution_type_vars[:], self.convolution_x_var[:], self.convolution_y_var[:], self.convolution_sigma_var[:]
                self.convolution_num_var.set(0)
                # Reset corrections to default (all False)
                self.ignore_attn_var.set(False)
                self.ignore_norm_var.set(False)
                self.ignore_rand_var.set(False)
                self.ignore_scat_var.set(False)
                self.ignore_deca_var.set(False)
                self.ignore_brat_var.set(False)
                self.ignore_fdur_var.set(False)
                self.ignore_cali_var.set(False)
                # Reset MultiSiddon parameters
                self.multisiddon_sensitivity_lines_var.set(1)
                self.multisiddon_reconstruction_lines_var.set(1)
                
                for line in lines:
                    print(line)
                    if "set mpi_exe=" in line:
                        mpi_exe = line.split("set mpi_exe=")[1]
                        if mpi_exe == "\n":
                            self.mpi_bool_var.set(False)
                        else:
                            self.mpi_bool_var.set(True)
                    if "set threads=" in line:
                        mpi_threads = line.split("set threads=")[1].split()[1]
                        self.mpi_threads_var.set(mpi_threads)
                    if "set verbose=" in line:
                        verbose = line.split("set verbose=")[1].split()[1]
                        self.verbose_level_var.set(verbose)
                    if "set last_it=" in line:
                        last_it = line.split("set last_it=")[1]
                        if last_it == "\n":
                            self.last_iter_bool_var.set(False)
                        else:
                            self.last_iter_bool_var.set(True)
                    if "set flip_out=" in line:
                        flip_out = line.split("set flip_out=")[1]
                        if flip_out == "\n":
                            self.flip_var.set("None")
                        else:
                            self.flip_var.set(flip_out.split()[1])
                    if "set stats=" in line:
                        stats = line.split("set stats=")[1]
                        if stats == "\n":
                            self.stats_need_bool_var.set(False)
                        else:
                            self.stats_need_bool_var.set(True)
                    if "set recon_exe=" in line:
                        recon_exe = line.split("set recon_exe=")[1]
                        self.main_program_path_var.set(recon_exe)
                    if "set datafile=" in line:
                        datafile = line.split("set datafile=")[1].split()[1]
                        self.datafile_path_var.set(datafile)
                    if "set attenuation=" in line:
                        attenuation = line.split("set attenuation=")[1].split()[1]
                        self.attenuation_path_var.set(attenuation)
                    if "set normalization=" in line:
                        normalization = line.split("set normalization=")[1].split()[1]
                        self.normalization_path_var.set(normalization)
                    if "set output=" in line:
                        output = line.split("set output=")[1].split()[1]
                        self.output_path_var.set(output)
                    if "set sensitivity=" in line:
                        sensitivity = line.split("set sensitivity=")[1]
                        if sensitivity == "\n":
                            self.sensitivity_path_var.set("")
                        else:
                            self.sensitivity_path_var.set(sensitivity.split()[1])
                    if "set configuration=" in line:
                        configuration = line.split("set configuration=")[1]
                        if configuration == "\n":
                            self.configuration_path_var.set("")
                        else:
                            self.configuration_path_var.set(configuration.split()[1])
                    if "set voxel_number=" in line:
                        voxel_number = line.split("set voxel_number=")[1].split()[1]
                        self.voxel_number_var.set(voxel_number)
                        # Update the voxel number x, y, z
                        self.voxel_number_x_var.set(voxel_number.split(",")[0])
                        self.voxel_number_y_var.set(voxel_number.split(",")[1])
                        self.voxel_number_z_var.set(voxel_number.split(",")[2])
                    if "set voxel_size=" in line:
                        voxel_size = line.split("set voxel_size=")[1].split()[1]
                        self.voxel_size_var.set(voxel_size)
                        # Update the voxel size x, y, z
                        self.voxel_size_x_var.set(voxel_size.split(",")[0])
                        self.voxel_size_y_var.set(voxel_size.split(",")[1])
                        self.voxel_size_z_var.set(voxel_size.split(",")[2])
                    if "set offset=" in line:
                        offset = line.split("set offset=")[1].split()[1]
                        self.offset_var.set(offset)
                        # Update the offset x, y, z
                        self.offset_x_var.set(offset.split(",")[0])
                        self.offset_y_var.set(offset.split(",")[1])
                        self.offset_z_var.set(offset.split(",")[2])
                    if "set iterations=" in line:
                        iterations = line.split("set iterations=")[1].split()[1]
                        self.iterations_var.set(iterations)
                    if "set optimizer=" in line:
                        optimizer = line.split("set optimizer=")[1].split()[1]
                        self.optimizer_var.set(optimizer)
                    if "set projector=" in line:
                        projector_line = line.split("set projector=")[1].strip()
                        if "," in projector_line:
                            # MultiSiddon with parameters
                            parts = projector_line.split()
                            projector_value = parts[0]
                            if "," in projector_value:
                                projector_parts = projector_value.split(",")
                                self.projector_var.set(projector_parts[0])
                                if len(projector_parts) >= 3:
                                    self.multisiddon_sensitivity_lines_var.set(int(projector_parts[1]))
                                    self.multisiddon_reconstruction_lines_var.set(int(projector_parts[2]))
                        else:
                            # Regular projector
                            self.projector_var.set(projector_line.split()[0])
                    if "set penalty=" in line:
                        penalty = line.split("set penalty=")[1]
                        if penalty == "\n":
                            self.penalty_var.set("MRF")
                        else:
                            self.penalty_var.set(penalty.split()[1])
                    if "set penalty_strength=" in line:
                        penalty_strength = line.split("set penalty_strength=")[1]
                        if penalty_strength == "\n":
                            self.penalty_strength_var.set(0.5)
                        else:
                            self.penalty_strength_var.set(penalty_strength.split()[1])
                    if "set ignore_corr=" in line:
                        ignore_corr = line.split("set ignore_corr=")[1].strip()
                        if ignore_corr and ignore_corr != "\n":
                            corrections_list = ignore_corr.split()[1].split(",")
                            if "attn" in corrections_list:
                                self.ignore_attn_var.set(True)
                            if "norm" in corrections_list:
                                self.ignore_norm_var.set(True)
                            if "rand" in corrections_list:
                                self.ignore_rand_var.set(True)
                            if "scat" in corrections_list:
                                self.ignore_scat_var.set(True)
                            if "deca" in corrections_list:
                                self.ignore_deca_var.set(True)
                            if "brat" in corrections_list:
                                self.ignore_brat_var.set(True)
                            if "fdur" in corrections_list:
                                self.ignore_fdur_var.set(True)
                            if "cali" in corrections_list:
                                self.ignore_cali_var.set(True)
                    if "set psf_" in line:
                        psf = line.split("=")[1].strip().split()[1]  # Split the line at "=" and remove leading/trailing whitespace
                        print(psf)
                        if psf == "\n":
                            self.convolution_need_bool_var.set(False)
                            self.conv_spinbox.config(state='disabled')
                        else:
                            self.convolution_need_bool_var.set(True)
                            self.conv_spinbox.config(state='normal')
                            self.convolution_num_var.set(self.convolution_num_var.get() + 1)
                            # self.convolution_value_vars.append(psf)
                            psf_values = psf.split("::")[0].split(",")  # Split the psf values at "::" and ","
                            self.convolution_type_vars.append(tk.StringVar(value=psf.split("::")[1]))
                            self.convolution_x_var.append(tk.DoubleVar(value=float(psf_values[1])))
                            self.convolution_y_var.append(tk.DoubleVar(value=float(psf_values[2])))
                            self.convolution_sigma_var.append(tk.DoubleVar(value=float(psf_values[3])))
                        self.update_convolution_entries()
        
        # Get from the file the values of the variables
        
    def open_from_file_Linux(self):
        file_path = filedialog.askopenfilename(initialdir=self.script_dir)
        if file_path:
            with open(file_path, "r") as file:
                lines = file.readlines()
                del self.convolution_value_vars[:], self.convolution_type_vars[:], self.convolution_x_var[:], self.convolution_y_var[:], self.convolution_sigma_var[:]
                self.convolution_num_var.set(0)
                # Reset corrections to default (all False)
                self.ignore_attn_var.set(False)
                self.ignore_norm_var.set(False)
                self.ignore_rand_var.set(False)
                self.ignore_scat_var.set(False)
                self.ignore_deca_var.set(False)
                self.ignore_brat_var.set(False)
                self.ignore_fdur_var.set(False)
                self.ignore_cali_var.set(False)
                # Reset MultiSiddon parameters
                self.multisiddon_sensitivity_lines_var.set(1)
                self.multisiddon_reconstruction_lines_var.set(1)
                
                for line in lines:
                    print(line)
                    if "mpi_exe=" in line:
                        mpi_exe = line.split("mpi_exe=")[1]
                        if mpi_exe == "\n":
                            self.mpi_bool_var.set(False)
                        else:
                            self.mpi_bool_var.set(True)
                    if "threads=" in line:
                        mpi_threads = line.split("threads=")[1].split()[1]
                        self.mpi_threads_var.set(mpi_threads)
                    if "verbose=" in line:
                        verbose = line.split("verbose=")[1].split()[1]
                        self.verbose_level_var.set(verbose)
                    if "last_it=" in line:
                        last_it = line.split("last_it=")[1]
                        if last_it == "\n":
                            self.last_iter_bool_var.set(False)
                        else:
                            self.last_iter_bool_var.set(True)
                    if "flip_out=" in line:
                        flip_out = line.split("flip_out=")[1]
                        if flip_out == "\n":
                            self.flip_var.set("None")
                        else:
                            self.flip_var.set(flip_out.split()[1])
                    if "stats=" in line:
                        stats = line.split("stats=")[1]
                        if stats == "\n":
                            self.stats_need_bool_var.set(False)
                        else:
                            self.stats_need_bool_var.set(True)
                    if "recon_exe=" in line:
                        recon_exe = line.split("recon_exe=")[1]
                        self.main_program_path_var.set(recon_exe)
                    if "datafile=" in line:
                        datafile = line.split("datafile=")[1].split()[1]
                        self.datafile_path_var.set(datafile)
                    if "attenuation=" in line:
                        attenuation = line.split("attenuation=")[1].split()[1]
                        self.attenuation_path_var.set(attenuation)
                    if "normalization=" in line:
                        normalization = line.split("normalization=")[1].split()[1]
                        self.normalization_path_var.set(normalization)
                    if "output=" in line:
                        output = line.split("output=")[1].split()[1]
                        self.output_path_var.set(output)
                    if "sensitivity=" in line:
                        sensitivity = line.split("sensitivity=")[1]
                        if sensitivity == "\n":
                            self.sensitivity_path_var.set("")
                        else:
                            self.sensitivity_path_var.set(sensitivity.split()[1])
                    if "configuration=" in line:
                        configuration = line.split("configuration=")[1]
                        if configuration == "\n":
                            self.configuration_path_var.set("")
                        else:
                            self.configuration_path_var.set(configuration.split()[1])
                    if "voxel_number=" in line:
                        voxel_number = line.split("voxel_number=")[1].split()[1]
                        self.voxel_number_var.set(voxel_number)
                        # Update the voxel number x, y, z
                        self.voxel_number_x_var.set(voxel_number.split(",")[0])
                        self.voxel_number_y_var.set(voxel_number.split(",")[1])
                        self.voxel_number_z_var.set(voxel_number.split(",")[2])
                    if "voxel_size=" in line:
                        voxel_size = line.split("voxel_size=")[1].split()[1]
                        self.voxel_size_var.set(voxel_size)
                        # Update the voxel size x, y, z
                        self.voxel_size_x_var.set(voxel_size.split(",")[0])
                        self.voxel_size_y_var.set(voxel_size.split(",")[1])
                        self.voxel_size_z_var.set(voxel_size.split(",")[2])
                    if "offset=" in line:
                        offset = line.split("offset=")[1].split()[1]
                        self.offset_var.set(offset)
                        # Update the offset x, y, z
                        self.offset_x_var.set(offset.split(",")[0])
                        self.offset_y_var.set(offset.split(",")[1])
                        self.offset_z_var.set(offset.split(",")[2])
                    if "iterations=" in line:
                        iterations = line.split("iterations=")[1].split()[1]
                        self.iterations_var.set(iterations)
                    if "optimizer=" in line:
                        optimizer = line.split("optimizer=")[1].split()[1]
                        self.optimizer_var.set(optimizer)
                    if "projector=" in line:
                        projector_line = line.split("projector=")[1].strip()
                        if "," in projector_line:
                            # MultiSiddon with parameters
                            parts = projector_line.split()
                            projector_value = parts[0]
                            if "," in projector_value:
                                projector_parts = projector_value.split(",")
                                self.projector_var.set(projector_parts[0])
                                if len(projector_parts) >= 3:
                                    self.multisiddon_sensitivity_lines_var.set(int(projector_parts[1]))
                                    self.multisiddon_reconstruction_lines_var.set(int(projector_parts[2]))
                        else:
                            # Regular projector
                            self.projector_var.set(projector_line.split()[0])
                    if "penalty=" in line:
                        penalty = line.split("penalty=")[1]
                        if penalty == "\n":
                            self.penalty_var.set("MRF")
                        else:
                            self.penalty_var.set(penalty.split()[1])
                    if "penalty_strength=" in line:
                        penalty_strength = line.split("penalty_strength=")[1]
                        if penalty_strength == "\n":
                            self.penalty_strength_var.set(0.5)
                        else:
                            self.penalty_strength_var.set(penalty_strength.split()[1])
                    if "ignore_corr=" in line:
                        ignore_corr = line.split("ignore_corr=")[1].strip()
                        if ignore_corr and ignore_corr != "\n" and not ignore_corr.startswith('"'):
                            corrections_list = ignore_corr.split()[1].split(",")
                            if "attn" in corrections_list:
                                self.ignore_attn_var.set(True)
                            if "norm" in corrections_list:
                                self.ignore_norm_var.set(True)
                            if "rand" in corrections_list:
                                self.ignore_rand_var.set(True)
                            if "scat" in corrections_list:
                                self.ignore_scat_var.set(True)
                            if "deca" in corrections_list:
                                self.ignore_deca_var.set(True)
                            if "brat" in corrections_list:
                                self.ignore_brat_var.set(True)
                            if "fdur" in corrections_list:
                                self.ignore_fdur_var.set(True)
                            if "cali" in corrections_list:
                                self.ignore_cali_var.set(True)
                    if "psf_" in line:
                        psf = line.split("=")[1].strip().split()[1]  # Split the line at "=" and remove leading/trailing whitespace
                        print(psf)
                        if psf == "\n":
                            self.convolution_need_bool_var.set(False)
                            self.conv_spinbox.config(state='disabled')
                        else:
                            self.convolution_need_bool_var.set(True)
                            self.conv_spinbox.config(state='normal')
                            self.convolution_num_var.set(self.convolution_num_var.get() + 1)
                            # self.convolution_value_vars.append(psf)
                            psf_values = psf.split("::")[0].split(",")  # Split the psf values at "::" and ","
                            self.convolution_type_vars.append(tk.StringVar(value=psf.split("::")[1]))
                            self.convolution_x_var.append(tk.DoubleVar(value=float(psf_values[1])))
                            self.convolution_y_var.append(tk.DoubleVar(value=float(psf_values[2])))
                            self.convolution_sigma_var.append(tk.DoubleVar(value=float(psf_values[3])))
                        self.update_convolution_entries()

    
if __name__ == "__main__":
    app = BatchScriptGenerator()
    app.mainloop()
