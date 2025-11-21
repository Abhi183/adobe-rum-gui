#!/usr/bin/python3
import subprocess
import re
import sys
import os
import threading
import argparse
import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas, Frame, Label, Button, Toplevel
from tkinter import ttk

# Try to import Pillow for advanced image handling
try:
    from PIL import Image, ImageTk
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("DEBUG: Pillow (PIL) library not found. Images will not load. Install with 'pip install Pillow'")

# --- Configuration: SAP Codes to Names (Universal Adobe Codes) ---
SAP_MAP = {
    "Acrobat": "Acrobat DC", "AcrobatDC": "Acrobat DC", "AdobeAcrobatDC": "Acrobat DC",
    "AcroRdr": "Acrobat Reader", "Reader": "Acrobat Reader",
    "PHSP": "Photoshop", "Photoshop": "Photoshop",
    "ILST": "Illustrator", "Illustrator": "Illustrator",
    "IDSN": "InDesign", "InDesign": "InDesign",
    "AICY": "InCopy", "InCopy": "InCopy",
    "PPRO": "Premiere Pro", "PremierePro": "Premiere Pro", "Premiere": "Premiere Pro",
    "AEFT": "After Effects", "AfterEffects": "After Effects",
    "AME": "Media Encoder", "MediaEncoder": "Media Encoder",
    "LRCC": "Lightroom", "LrMobile": "Lightroom", "Lightroom": "Lightroom",
    "LTRM": "Lightroom Classic", "LRClassic": "Lightroom Classic", "LightroomClassic": "Lightroom Classic",
    "KBRG": "Bridge", "Bridge": "Bridge",
    "FLPR": "Animate", "Animate": "Animate",
    "DRWV": "Dreamweaver", "Dreamweaver": "Dreamweaver",
    "AUDT": "Audition", "Audition": "Audition",
    "CHAR": "Character Animator", "CharacterAnimator": "Character Animator",
    "ESHR": "Dimension", "Dimension": "Dimension",
    "FRSC": "Fresco", "Fresco": "Fresco",
    "SPRK": "Adobe XD", "XD": "Adobe XD",
    "RUSH": "Premiere Rush", "PremiereRush": "Premiere Rush",
    "SBSTD": "Substance 3D Designer", "SBSTP": "Substance 3D Painter",
    "SBSTA": "Substance 3D Sampler", "STGR": "Substance 3D Stager",
    "SHPR": "Substance 3D Modeler", "ACR": "Adobe Camera Raw",
    "CCXP": "Creative Cloud Experience", "HLAN": "Highlights (HLAN)", "SEPS": "Stager (SEPS)"
}

def get_product_name(sap_code):
    """Maps SAP code to friendly name."""
    clean_code = sap_code.split('-')[0]
    if clean_code in SAP_MAP:
        return SAP_MAP[clean_code]
    for key in SAP_MAP:
        if key in clean_code:
            return SAP_MAP[key]
    return clean_code

def run_rum_check(rum_path):
    """Runs the RUM command and parses output for the list."""
    command = [rum_path, "--action=list"]
    
    print("\n" + "="*60)
    print(f"DEBUG: Starting RUM Check using: {rum_path}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
    except FileNotFoundError:
        print(f"CRITICAL ERROR: RemoteUpdateManager not found at {rum_path}.")
        return []
    except PermissionError:
        print("CRITICAL ERROR: Permission Denied. Run with sudo.")
        return []
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return []

    updates = []
    regex = r"\((?P<code>[^/]+)/(?P<version>[^/]+)(?:/.*)?\)"
    
    for line in output.splitlines():
        line = line.strip()
        if not line: continue
        match = re.search(regex, line)
        if match:
            sap_code = match.group("code").strip()
            version = match.group("version").strip()
            name = get_product_name(sap_code)
            updates.append({"sap": sap_code, "name": name, "version": version})
            
    return updates

class UpdateManagerApp:
    def __init__(self, root, updates, config):
        self.root = root
        self.config = config
        self.root.title(f"{self.config.title} | Adobe Update Manager")
        self.root.geometry("600x750")
        
        # Center window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = int((screen_width/2) - (600/2))
        y = int((screen_height/2) - (750/2))
        root.geometry(f"600x750+{x}+{y}")

        self.updates = updates
        self.check_vars = []
        self.bg_image_ref = None
        self.logo_image_ref = None
        
        # Master toggle variable
        self.all_var = tk.BooleanVar()

        self.setup_aesthetic_ui()

    def load_image(self, file_path, width=None, height=None):
        if not HAS_PILLOW or not file_path: return None
        if not os.path.exists(file_path): 
            print(f"DEBUG: Image not found at {file_path}")
            return None
        try:
            img = Image.open(file_path)
            if width and height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            elif width: 
                w_percent = (width / float(img.size[0]))
                h_size = int((float(img.size[1]) * float(w_percent)))
                img = img.resize((width, h_size), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e: 
            print(f"DEBUG: Error loading image: {e}")
            return None

    def setup_aesthetic_ui(self):
        self.canvas = Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background
        if self.config.background:
            self.bg_image_ref = self.load_image(self.config.background, width=1200, height=900)
            if self.bg_image_ref:
                self.canvas.create_image(0, 0, image=self.bg_image_ref, anchor="nw", tags="bg")
            else:
                self.canvas.configure(bg="#f0f0f0")
        else:
            self.canvas.configure(bg="#f0f0f0")

        # Logo
        if self.config.logo:
            self.logo_image_ref = self.load_image(self.config.logo, width=250)
        
        if self.logo_image_ref:
            self.canvas.create_image(300, 60, image=self.logo_image_ref, anchor="center")
        else:
            # Fallback text if no logo provided
            self.canvas.create_text(300, 50, text=self.config.title.upper(), 
                                    font=("Times New Roman", 24, "bold"), fill=self.config.accent_color)

        # Card Frame
        card_frame = Frame(self.canvas, bg="white", bd=0)
        self.canvas.create_window(300, 400, window=card_frame, width=500, height=550, anchor="center")

        # Title
        Label(card_frame, text="Available Software Updates", 
              font=("Helvetica", 16, "bold"), bg="white", fg="#333").pack(pady=(20, 10))
        Frame(card_frame, height=2, bg=self.config.accent_color, width=400).pack(pady=(0, 10))

        # --- Select All Checkbox ---
        select_all_frame = Frame(card_frame, bg="white")
        select_all_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        chk_all = tk.Checkbutton(select_all_frame, text="Select All Apps", variable=self.all_var, 
                                 command=self.toggle_all,
                                 font=("Helvetica", 11, "bold"), bg="white", activebackground="white",
                                 fg=self.config.accent_color)
        chk_all.pack(side="left")

        # List Container
        list_container = Frame(card_frame, bg="white")
        list_container.pack(fill="both", expand=True, padx=20, pady=5)

        # Scrollbar Setup
        vsb = Scrollbar(list_container, orient="vertical")
        list_canvas = Canvas(list_container, bg="white", highlightthickness=0, yscrollcommand=vsb.set)
        vsb.config(command=list_canvas.yview)
        vsb.pack(side="right", fill="y")
        list_canvas.pack(side="left", fill="both", expand=True)

        self.inner_list_frame = Frame(list_canvas, bg="white")
        list_canvas.create_window((0,0), window=self.inner_list_frame, anchor="nw")
        self.inner_list_frame.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))

        self.populate_list(self.inner_list_frame)

        # Buttons
        btn_frame = Frame(card_frame, bg="white", pady=20)
        btn_frame.pack(side="bottom", fill="x")

        install_btn = Button(btn_frame, text="INSTALL SELECTED", command=self.on_install_click,
                             bg=self.config.accent_color, fg="white", font=("Helvetica", 11, "bold"), 
                             relief="flat", padx=20, pady=5, cursor="hand2")
        install_btn.pack(side="right", padx=30)

        cancel_btn = Button(btn_frame, text="CANCEL", command=self.root.quit,
                            bg="white", fg="#333", font=("Helvetica", 11), 
                            relief="flat", padx=20, pady=5, cursor="hand2")
        cancel_btn.pack(side="right")

    def populate_list(self, parent_frame):
        if not self.updates:
            Label(parent_frame, text="Great! No updates found.", 
                  font=("Helvetica", 12), bg="white", fg="#666").pack(pady=20)
            return

        for up in self.updates:
            var = tk.BooleanVar()
            row = Frame(parent_frame, bg="white", pady=5)
            row.pack(fill="x", pady=2)

            chk = tk.Checkbutton(row, variable=var, bg="white", activebackground="white")
            chk.pack(side="left")

            Label(row, text=up['name'], font=("Helvetica", 12, "bold"), bg="white", fg="#333").pack(side="left", padx=(5, 0))
            Label(row, text=f"v{up['version']}", font=("Helvetica", 10), bg="white", fg="#777").pack(side="left", padx=(5, 0))

            self.check_vars.append((up, var))

    def toggle_all(self):
        is_checked = self.all_var.get()
        for _, var in self.check_vars:
            var.set(is_checked)

    def on_install_click(self):
        selected_saps = [u['sap'] for u, var in self.check_vars if var.get()]
        total_available = len(self.updates)
        
        if not selected_saps:
            messagebox.showwarning("No Selection", "Please select at least one update to install.")
            return

        if len(selected_saps) == total_available and total_available > 0:
            cmd = [self.config.rum_path, "--action=install"]
        else:
            sap_string = ",".join(selected_saps)
            cmd = [self.config.rum_path, "--action=install", f"--productVersions={sap_string}"]

        self.open_progress_window(cmd)

    def open_progress_window(self, cmd):
        progress_win = Toplevel(self.root)
        progress_win.title("Installing Updates...")
        progress_win.geometry("550x250")
        progress_win.configure(bg="white")
        
        x = self.root.winfo_x() + 25
        y = self.root.winfo_y() + 200
        progress_win.geometry(f"+{x}+{y}")
        
        progress_win.transient(self.root)
        progress_win.grab_set()
        progress_win.protocol("WM_DELETE_WINDOW", self.on_progress_close_attempt)

        Label(progress_win, text="Installation in Progress", font=("Helvetica", 14, "bold"), 
              bg="white", fg=self.config.accent_color).pack(pady=(20,10))
        
        status_var = tk.StringVar()
        status_var.set("Initializing RemoteUpdateManager...")
        Label(progress_win, textvariable=status_var, font=("Helvetica", 10), 
              bg="white", fg="#666").pack(pady=5)

        self.progress_val = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_win, variable=self.progress_val, maximum=100, length=450)
        self.progress_bar.pack(pady=20)

        t = threading.Thread(target=self.run_install_process, args=(cmd, status_var, progress_win))
        t.start()
        
    def on_progress_close_attempt(self):
        messagebox.showwarning("Installation in Progress", "Please wait for the installation to complete.")

    def run_install_process(self, cmd, status_var, progress_win):
        installed_apps = []
        return_code = None
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            action_regex = r"\*\*\* (Downloading|Installing|Successfully installed) \((?P<code>[^/]+)/(?P<version>[^/]+)"
            progress_regex = r"Progress: (\d+)%"
            exit_regex = r"Return Code \((?P<code>\d+)\)"
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    line = line.strip()
                    print(f"INSTALLER STREAM: {line}")

                    match_exit = re.search(exit_regex, line, re.IGNORECASE)
                    if match_exit:
                        return_code = int(match_exit.group("code"))
                        process.kill()
                        break
                    
                    match_action = re.search(action_regex, line)
                    if match_action:
                        action = match_action.group(1)
                        sap = match_action.group("code")
                        ver = match_action.group("version")
                        friendly_name = get_product_name(sap)
                        
                        if action == "Successfully installed":
                            installed_apps.append(f"{friendly_name} (v{ver})")
                        else:
                            status_var.set(f"{action} {friendly_name}...")

                    match_prog = re.search(progress_regex, line)
                    if match_prog:
                        percent = int(match_prog.group(1))
                        self.progress_val.set(percent)

            if return_code is None:
                return_code = process.poll()
            
            progress_win.destroy()

            if return_code == 0:
                self.show_summary_window(installed_apps, success=True)
            else:
                self.show_summary_window(installed_apps, success=False, error_code=return_code)
                
        except Exception as e:
            print(f"Thread Error: {e}")
            progress_win.destroy()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def show_summary_window(self, installed_list, success=True, error_code=None):
        summary_win = Toplevel(self.root)
        summary_win.title("Installation Summary")
        summary_win.geometry("500x400")
        summary_win.configure(bg="white")
        
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 100
        summary_win.geometry(f"+{x}+{y}")
        
        title_text = "Update Complete" if success else "Update Finished with Errors"
        title_color = self.config.accent_color if success else "#D32F2F"
        
        Label(summary_win, text=title_text, font=("Helvetica", 16, "bold"), 
              bg="white", fg=title_color).pack(pady=(20, 10))
        
        Frame(summary_win, height=2, bg=self.config.accent_color, width=400).pack(pady=(0, 15))

        if installed_list:
            Label(summary_win, text="The following applications were successfully updated:", 
                  font=("Helvetica", 11), bg="white", fg="#333").pack()
            
            list_frame = Frame(summary_win, bg="#f9f9f9", bd=1, relief="sunken")
            list_frame.pack(fill="both", expand=True, padx=40, pady=15)
            
            for app_str in installed_list:
                Label(list_frame, text=f"• {app_str}", font=("Helvetica", 10, "bold"), 
                      bg="#f9f9f9", fg="#333", anchor="w").pack(fill="x", padx=10, pady=2)
        else:
            msg = "No updates were installed." if success else f"Process failed with error code: {error_code}"
            Label(summary_win, text=msg, font=("Helvetica", 11), bg="white", fg="#333").pack(pady=20)

        lbl_timer = Label(summary_win, text="Application closing in 30 seconds...", 
                          font=("Helvetica", 9, "italic"), bg="white", fg="#777")
        lbl_timer.pack(pady=(0, 5))

        close_btn = Button(summary_win, text="Close Application Now", command=self.close_all,
                           bg=self.config.accent_color, fg="white", font=("Helvetica", 10, "bold"),
                           relief="flat", padx=20, pady=5)
        close_btn.pack(side="bottom", pady=20)

        self.root.after(30000, self.close_all)
        
    def close_all(self):
        self.root.destroy()
        sys.exit(0)

# --- MAIN ENTRY POINT WITH ARGUMENT PARSING ---
if __name__ == "__main__":
    # Set defaults
    DEFAULT_RUM = "/usr/local/bin/RemoteUpdateManager"
    DEFAULT_COLOR = "#333333" # Neutral Dark Grey
    DEFAULT_TITLE = "Organization Name"

    parser = argparse.ArgumentParser(description="Generic Adobe RUM GUI Updater")
    
    parser.add_argument("--title", default=DEFAULT_TITLE, help="Name of your organization (appears in window title and header)")
    parser.add_argument("--logo", help="Absolute path to a PNG logo file (approx 250px width)")
    parser.add_argument("--background", help="Absolute path to a JPG/PNG background image")
    parser.add_argument("--accent-color", dest="accent_color", default=DEFAULT_COLOR, help="Hex color code for buttons and accents (e.g., #C8102E)")
    parser.add_argument("--rum-path", dest="rum_path", default=DEFAULT_RUM, help="Path to the RemoteUpdateManager binary")

    args = parser.parse_args()

    # Run Logic
    updates_data = run_rum_check(args.rum_path)
    
    print("DEBUG: Launching GUI...")
    root = tk.Tk()
    app = UpdateManagerApp(root, updates_data, args)
    root.mainloop()