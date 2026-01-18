#Neal Pandhi

import tkinter as tk
from tkinter import filedialog, messagebox
import trimesh
import numpy as np
import math
import os
import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *


MATERIALS = {
    "Choose": 0,
    "PLA(+) (approx)": 1240,
    "PETG (approx)": 1325,
    "PET (approx)": 1350,
    "ABS (approx)": 1115,
    "Custom (enter density)": None
}

def human_float(x, n=6):
    return float(f"{float(x):.{n}g}")

def axis_vector_from_choice(choice):
    c = choice.lower()
    if c == 'x': return np.array([1.0,0.0,0.0])
    if c == 'y': return np.array([0.0,1.0,0.0])
    return np.array([0.0,0.0,1.0])

def analyze_mesh(path, density, scale=1.0, axis=np.array([0,0,1])):
    mesh = trimesh.load_mesh(path, force='mesh')
    mesh.apply_scale(scale)
    props = mesh.mass_properties
    mass = props['mass'] * density
    com = np.array(props['center_mass'])
    inertia_tensor = np.array(props['inertia']) * density
    u = axis / np.linalg.norm(axis)
    I_axis = float(u @ inertia_tensor @ u)

    return {
        'mesh': mesh,
        'mass': mass,
        'com': com,
        'inertia_tensor': inertia_tensor,
        'I_axis': I_axis
    }

class InertiaApp:
    def __init__(self, root):
        self.root = root
        root.title("Weapon Power Calculator")
        self.file_path = None

        row = 0
        tk.Label(root, text="1) Load mesh (STL/OBJ:").grid(row=row, column=0, sticky='w', pady = 10)
        self.load_btn = tb.Button(root, text="Choose file...", bootstyle="success", command=self.choose_file)
        self.load_btn.grid(row=row, column=1, sticky='w')
        row += 1

        tk.Label(root, text="Selected file:").grid(row=row, column=0, sticky='w')
        self.file_label = tk.Label(root, text="(none)", fg='gray')
        self.file_label.grid(row=row, column=1, sticky='w')
        row += 1

        tk.Label(root, text="2) Material / density:").grid(row=row, column=0, sticky='w')
        self.material_var = tk.StringVar(root)
        self.material_var.set(next(iter(MATERIALS.keys())))
        tb.OptionMenu(root, self.material_var, *MATERIALS.keys(), command=self.on_material_change, bootstyle="success").grid(row=row, column=1, sticky='w')
        row += 1

        tk.Label(root, text="Custom density (kg/m^3):").grid(row=row, column=0, sticky='w')
        self.custom_density = tk.Entry(root)
        self.custom_density.grid(row=row, column=1, sticky='w')
        self.custom_density.insert(0, "0")
        row += 1

        tk.Label(root, text="3) Input units of mesh (choose):").grid(row=row, column=0, sticky='w')
        self.units_var = tk.StringVar(root)
        self.units_var.set('mm')
        tb.OptionMenu(root, self.units_var, 'mm', 'cm', 'm', bootstyle="success").grid(row=row, column=1, sticky='w')
        row += 1

        tk.Label(root, text="4) Spin axis (X/Y/Z) or custom vector (x,y,z):").grid(row=row, column=0, sticky='w')
        self.axis_entry = tk.Entry(root)
        self.axis_entry.grid(row=row, column=1, sticky='w')
        self.axis_entry.insert(0, "Z")
        row += 1

        tk.Label(root, text="5) Motor kV:").grid(row=row, column=0, sticky='w')
        self.kv_entry = tk.Entry(root)
        self.kv_entry.grid(row=row, column=1, sticky='w')
        self.kv_entry.insert(0, "1100")
        row += 1
        
        tk.Label(root, text="6) Battery Voltage:").grid(row=row, column=0, sticky='w')
        self.volt_entry = tk.Entry(root)
        self.volt_entry.grid(row=row, column=1, sticky='w')
        self.volt_entry.insert(0, "7.4")
        row += 1

        tb.Button(root, text="Compute", bootstyle="success", command=self.compute ).grid(row=row, column=0, sticky='w', pady = 10)
        tb.Button(root, text="Save Report...", bootstyle="success", command=self.save_report).grid(row=row, column=1, sticky='w', pady = 10)
        row += 1

        tk.Label(root, text="Results:").grid(row=row, column=0, sticky='w')
        row += 1

        self.results_text = tk.Text(root, width=80, height=18)
        self.results_text.grid(row=row, column=0, columnspan=3)
        self.results_text.insert('end', "Load a mesh and click Compute.\n")

        self.last_result = None

    def choose_file(self):
        p = filedialog.askopenfilename(filetypes=[("Mesh files", "*.stl *.obj"), ("All files","*.*")])
        if p:
            self.file_path = p
            self.file_label.config(text=os.path.basename(p))
            self.results_text.delete('1.0', 'end')
            self.results_text.insert('end', f"Selected {p}\n")

    def on_material_change(self, val):
        if MATERIALS[val] is None:
            self.custom_density.config(state='normal')
        else:
            self.custom_density.delete(0,'end')
            self.custom_density.insert(0, str(MATERIALS[val]))
            self.custom_density.config(state='normal')

    def parse_axis(self, text):
        t = text.strip()
        if ',' in t:
            parts = [float(x) for x in t.split(',')]
            v = np.array(parts, dtype=float)
        else:
            v = axis_vector_from_choice(t)
        if np.linalg.norm(v) == 0:
            raise ValueError("Axis vector cannot be zero.")
        return v

    def compute(self):
        if not self.file_path:
            messagebox.showerror("No file", "Choose a mesh file first.")
            return
        try:
            density = float(self.custom_density.get())
        except:
            messagebox.showerror("Bad density", "Enter a valid numeric density in kg/m^3.")
            return

        units = self.units_var.get().lower()
        scale_map = {'mm': 0.001, 'cm': 0.01, 'm': 1.0}
        scale = scale_map.get(units, 0.001)

        try:
            axis = self.parse_axis(self.axis_entry.get())
        except Exception as e:
            messagebox.showerror("Bad axis", f"Could not parse axis: {e}")
            return

        try:
            self.results_text.delete('1.0', 'end')
            self.results_text.insert('end', f"Analyzing {os.path.basename(self.file_path)} ...\n")
            res = analyze_mesh(self.file_path, density=density, scale=scale, axis=axis)
            mass = res['mass']
            com = res['com']
            I_axis = res['I_axis']
            tensor = res['inertia_tensor']

            kv = float(self.kv_entry.get())
            volt = float(self.volt_entry.get())
            omega = kv * volt * 2.0*math.pi / 60.0
            E_rot = 0.5 * I_axis * omega**2

            out = []
            out.append(f"Timestamp: {datetime.datetime.now().isoformat()}")
            out.append(f"File: {self.file_path}")
            out.append(f"Material density: {density} kg/m^3, https://forms.gle/vRpQpNHDVG9JmBni7")
            out.append(f"Units scale applied: 1 mesh-unit = {scale} m")
            out.append(f"Mass (kg): {human_float(mass,6)}")
            out.append(f"Center of mass (m): [{human_float(com[0])}, {human_float(com[1])}, {human_float(com[2])}]")
            out.append("Rotational Inertia (kg·m^2):")
            out.append(np.array2string(tensor, precision=6, separator=', '))
            out.append(f"I about axis {axis/np.linalg.norm(axis)} (kg·m^2): {human_float(I_axis,7)}")
            out.append(f"RPM: {kv*volt} -> omega: {human_float(omega,7)} rad/s")
            out.append(f"Rotational kinetic energy E = 0.5 I ω^2 (J): {human_float(E_rot,6)}")

            self.results_text.insert('end', "\n".join(out) + "\n")
            self.last_result = "\n".join(out) + "\n"
        except Exception as e:
            messagebox.showerror("Error analyzing mesh", str(e))
            return

    def save_report(self):
        if not self.last_result:
            messagebox.showwarning("No result", "Compute results first.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")])
        if p:
            with open(p, 'w') as f:
                f.write(self.last_result)
            messagebox.showinfo("Saved", f"Report saved to {p}")

if __name__ == '__main__':
    root = tb.Window(themename="superhero")
    app = InertiaApp(root)
    root.mainloop()
