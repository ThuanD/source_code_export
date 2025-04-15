import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import os
from pathlib import Path


class ExcludeExtensionHelpDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(
            master, text="\nExclude Extensions - Hướng dẫn:", font=("Arial", 10, "bold")
        ).pack(pady=5)
        tk.Label(
            master,
            text="Nhập các phần mở rộng file bạn muốn bỏ qua:",
            anchor="w",
            justify="left",
        ).pack(fill="x")
        tk.Label(master, text="Ví dụ:", fg="blue", anchor="w", justify="left").pack(
            fill="x"
        )
        tk.Label(
            master,
            text="- '.log .tmp .cache': Bỏ qua các file log, tạm thời và cache",
            anchor="w",
            justify="left",
        ).pack(fill="x")

        return None

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE).pack(
            pady=8
        )
        self.bind("<Return>", self.ok)
        box.pack()


class ExcludePathsBrowserDialog(tk.Toplevel):
    def __init__(self, parent, root_path, current_excludes=None, title="Select Paths to Exclude"):
        super().__init__(parent)
        self.parent = parent
        self.root_path = Path(root_path)
        self.current_excludes = current_excludes or []
        self.result = None  # Will hold the list of selected paths

        # Configure dialog
        self.title(title)
        self.transient(parent)  # Make dialog modal
        self.resizable(True, True)
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Create components
        self.create_widgets()
        
        # Make dialog modal
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)  # Wait until window is destroyed

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="Select folders or files to exclude (relative to project root):", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Project root info
        ttk.Label(main_frame, text=f"Project Root: {self.root_path}",
                 font=("Arial", 9)).pack(anchor="w", pady=(0, 10))
        
        # Selected paths frame
        paths_frame = ttk.LabelFrame(main_frame, text="Selected Paths")
        paths_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Listbox for selected paths
        self.paths_listbox = tk.Listbox(paths_frame, selectmode=tk.EXTENDED, height=10)
        self.paths_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(paths_frame, orient=tk.VERTICAL, command=self.paths_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.paths_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Populate the listbox with current excludes
        for path in self.current_excludes:
            if path.strip():
                self.paths_listbox.insert(tk.END, path)
        
        # Buttons for actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        
        # OK/Cancel buttons
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(close_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(close_frame, text="OK", command=self.ok, default="active").pack(side=tk.RIGHT, padx=5)
    
    def add_files(self):
        """Add files to exclude list"""
        files = filedialog.askopenfilenames(
            title="Select Files to Exclude",
            initialdir=self.root_path,
            parent=self
        )
        
        if files:
            for file_path in files:
                # Convert to Path object
                path = Path(file_path)
                
                # Make path relative to root path
                try:
                    rel_path = path.relative_to(self.root_path)
                    self.paths_listbox.insert(tk.END, str(rel_path))
                except ValueError:
                    # If path is not relative to root_path
                    messagebox.showwarning(
                        "Warning", 
                        f"Path '{path}' is not within project root and cannot be added.",
                        parent=self
                    )
    
    def add_folder(self):
        """Add folder to exclude list"""
        folder = filedialog.askdirectory(
            title="Select Folder to Exclude",
            initialdir=self.root_path,
            parent=self
        )
        
        if folder:
            # Convert to Path object
            path = Path(folder)
            
            # Make path relative to root path
            try:
                rel_path = path.relative_to(self.root_path)
                self.paths_listbox.insert(tk.END, str(rel_path))
            except ValueError:
                # If path is not relative to root_path
                messagebox.showwarning(
                    "Warning", 
                    f"Path '{path}' is not within project root and cannot be added.",
                    parent=self
                )
    
    def remove_selected(self):
        """Remove selected paths from the listbox"""
        selected_indices = self.paths_listbox.curselection()
        
        # Delete from highest index to lowest to avoid index shifting issues
        for i in sorted(selected_indices, reverse=True):
            self.paths_listbox.delete(i)
    
    def get_selected_paths(self):
        """Return all paths in the listbox"""
        return list(self.paths_listbox.get(0, tk.END))
    
    def ok(self):
        """Save results and close dialog"""
        self.result = self.get_selected_paths()
        self.destroy()
    
    def cancel(self):
        """Cancel and close dialog without saving"""
        self.result = None
        self.destroy()
