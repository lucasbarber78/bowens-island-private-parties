"""Graphical user interface for Bowens Island Private Parties connector."""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .config import Config
from .sync_manager import SyncManager


class ConnectorGUI:
    """GUI for the Bowens Island Private Parties connector."""

    def __init__(self, root: tk.Tk, config: Config):
        """Initialize the GUI.

        Args:
            root: The Tkinter root window
            config: Configuration manager
        """
        self.root = root
        self.config = config
        self.sync_manager = None
        
        # Set up the main window
        self.root.title("Bowens Island Private Parties Connector")
        self.root.geometry("800x600")
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Sync tab
        self.sync_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.sync_tab, text="Sync")
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_tab, text="Settings")
        
        # Add the tab control to the main frame
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Set up the sync tab
        self._setup_sync_tab()
        
        # Set up the settings tab
        self._setup_settings_tab()
        
        # Initialize the sync manager if configured
        self._initialize_sync_manager()
    
    def _setup_sync_tab(self) -> None:
        """Set up the synchronization tab."""
        # Excel file frame
        excel_frame = ttk.LabelFrame(
            self.sync_tab, text="Excel File", padding=10
        )
        excel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Excel file path
        ttk.Label(excel_frame, text="Excel File Path:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        self.excel_path_var = tk.StringVar(
            value=self.config.get("excel.template_path", "")
        )
        ttk.Entry(excel_frame, textvariable=self.excel_path_var, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        ttk.Button(
            excel_frame, text="Browse...", command=self._browse_excel_file
        ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Last sync time
        ttk.Label(excel_frame, text="Last Sync:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        self.last_sync_var = tk.StringVar(value="Never")
        ttk.Label(excel_frame, textvariable=self.last_sync_var).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Sync buttons frame
        sync_buttons_frame = ttk.Frame(self.sync_tab, padding=10)
        sync_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            sync_buttons_frame,
            text="Sync from Cognito to Excel",
            command=self._sync_to_excel
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            sync_buttons_frame,
            text="Sync from Excel to Cognito",
            command=self._sync_to_cognito
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(
            self.sync_tab, text="Status", padding=10
        )
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=10, width=70)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for status text
        status_scrollbar = ttk.Scrollbar(
            status_frame, orient=tk.VERTICAL, command=self.status_text.yview
        )
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=status_scrollbar.set)
        
        # Set status text to read-only
        self.status_text.config(state=tk.DISABLED)
    
    def _setup_settings_tab(self) -> None:
        """Set up the settings tab."""
        # Cognito Forms settings frame
        cognito_frame = ttk.LabelFrame(
            self.settings_tab, text="Cognito Forms Settings", padding=10
        )
        cognito_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # API key
        ttk.Label(cognito_frame, text="API Key:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        self.api_key_var = tk.StringVar(
            value=self.config.get("cognito.api_key", "")
        )
        api_key_entry = ttk.Entry(
            cognito_frame, textvariable=self.api_key_var, width=50, show="*"
        )
        api_key_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Toggle API key visibility
        self.show_api_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            cognito_frame, text="Show", variable=self.show_api_key_var,
            command=lambda: api_key_entry.config(
                show="" if self.show_api_key_var.get() else "*"
            )
        ).grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Form ID
        ttk.Label(cognito_frame, text="Form ID:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        self.form_id_var = tk.StringVar(
            value=self.config.get("cognito.form_id", "17")
        )
        ttk.Entry(cognito_frame, textvariable=self.form_id_var, width=50).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Excel settings frame
        excel_settings_frame = ttk.LabelFrame(
            self.settings_tab, text="Excel Settings", padding=10
        )
        excel_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main sheet name
        ttk.Label(excel_settings_frame, text="Main Sheet Name:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        self.main_sheet_var = tk.StringVar(
            value=self.config.get("excel.main_sheet", "MainData")
        )
        ttk.Entry(excel_settings_frame, textvariable=self.main_sheet_var, width=50).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Read-only main sheet
        self.read_only_var = tk.BooleanVar(
            value=self.config.get("excel.read_only", True)
        )
        ttk.Checkbutton(
            excel_settings_frame, text="Make main sheet read-only",
            variable=self.read_only_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Sync settings frame
        sync_settings_frame = ttk.LabelFrame(
            self.settings_tab, text="Sync Settings", padding=10
        )
        sync_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Auto sync on open
        self.auto_sync_open_var = tk.BooleanVar(
            value=self.config.get("sync.auto_sync_on_open", True)
        )
        ttk.Checkbutton(
            sync_settings_frame, text="Auto-sync when Excel file is opened",
            variable=self.auto_sync_open_var
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Auto sync on save
        self.auto_sync_save_var = tk.BooleanVar(
            value=self.config.get("sync.auto_sync_on_save", False)
        )
        ttk.Checkbutton(
            sync_settings_frame, text="Auto-sync when Excel file is saved",
            variable=self.auto_sync_save_var
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Confirm changes
        self.confirm_changes_var = tk.BooleanVar(
            value=self.config.get("sync.confirm_changes", True)
        )
        ttk.Checkbutton(
            sync_settings_frame, text="Confirm changes before syncing to Cognito",
            variable=self.confirm_changes_var
        ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Save settings button
        ttk.Button(
            self.settings_tab, text="Save Settings", command=self._save_settings
        ).pack(side=tk.LEFT, padx=5, pady=10)
    
    def _browse_excel_file(self) -> None:
        """Open a file dialog to select an Excel file."""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        
        if filename:
            self.excel_path_var.set(filename)
            self.config.set("excel.template_path", filename)
            self._update_last_sync_time()
            self._initialize_sync_manager()
    
    def _save_settings(self) -> None:
        """Save settings to the configuration file."""
        # Save Cognito Forms settings
        self.config.set("cognito.api_key", self.api_key_var.get())
        self.config.set("cognito.form_id", self.form_id_var.get())
        
        # Save Excel settings
        self.config.set("excel.template_path", self.excel_path_var.get())
        self.config.set("excel.main_sheet", self.main_sheet_var.get())
        self.config.set("excel.read_only", self.read_only_var.get())
        
        # Save sync settings
        self.config.set("sync.auto_sync_on_open", self.auto_sync_open_var.get())
        self.config.set("sync.auto_sync_on_save", self.auto_sync_save_var.get())
        self.config.set("sync.confirm_changes", self.confirm_changes_var.get())
        
        # Reinitialize sync manager
        self._initialize_sync_manager()
        
        # Show confirmation
        messagebox.showinfo(
            "Settings Saved",
            "Settings have been saved successfully."
        )
    
    def _initialize_sync_manager(self) -> None:
        """Initialize the sync manager if settings are configured."""
        # Check if required settings are configured
        api_key = self.config.get("cognito.api_key")
        form_id = self.config.get("cognito.form_id")
        excel_path = self.config.get("excel.template_path")
        
        if api_key and form_id and excel_path:
            self.sync_manager = SyncManager(self.config)
            self._update_last_sync_time()
            self._log_status("Ready to sync.")
        else:
            self.sync_manager = None
            missing = []
            if not api_key:
                missing.append("API Key")
            if not form_id:
                missing.append("Form ID")
            if not excel_path:
                missing.append("Excel Path")
            
            self._log_status(f"Configuration incomplete. Missing: {', '.join(missing)}")
    
    def _update_last_sync_time(self) -> None:
        """Update the last sync time display."""
        excel_path = self.config.get("excel.template_path")
        if excel_path and os.path.exists(excel_path):
            from .excel_handler import ExcelHandler
            excel_handler = ExcelHandler(
                file_path=excel_path,
                main_sheet=self.config.get("excel.main_sheet", "MainData")
            )
            
            last_sync = excel_handler.get_last_sync_time()
            if last_sync:
                self.last_sync_var.set(last_sync.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                self.last_sync_var.set("Never")
        else:
            self.last_sync_var.set("Never")
    
    def _sync_to_excel(self) -> None:
        """Synchronize data from Cognito Forms to Excel."""
        if not self.sync_manager:
            messagebox.showerror(
                "Error",
                "Sync manager not initialized. Please configure settings first."
            )
            return
        
        excel_path = self.config.get("excel.template_path")
        if not excel_path:
            messagebox.showerror(
                "Error",
                "Excel file path not configured. Please configure in settings."
            )
            return
        
        try:
            self._log_status("Synchronizing from Cognito Forms to Excel...")
            updated, added, deleted = self.sync_manager.sync_to_excel()
            self._update_last_sync_time()
            
            self._log_status(
                f"Synchronization complete:\n"
                f"  - {updated} entries updated\n"
                f"  - {added} entries added\n"
                f"  - {deleted} entries deleted"
            )
            
            messagebox.showinfo(
                "Sync Complete",
                f"Synchronized successfully:\n"
                f"  - {updated} entries updated\n"
                f"  - {added} entries added\n"
                f"  - {deleted} entries deleted"
            )
        except Exception as e:
            self._log_status(f"Error synchronizing: {e}")
            messagebox.showerror(
                "Sync Error",
                f"An error occurred during synchronization:\n{e}"
            )
    
    def _sync_to_cognito(self) -> None:
        """Synchronize data from Excel to Cognito Forms."""
        if not self.sync_manager:
            messagebox.showerror(
                "Error",
                "Sync manager not initialized. Please configure settings first."
            )
            return
        
        excel_path = self.config.get("excel.template_path")
        if not excel_path:
            messagebox.showerror(
                "Error",
                "Excel file path not configured. Please configure in settings."
            )
            return
        
        if not os.path.exists(excel_path):
            messagebox.showerror(
                "Error",
                f"Excel file not found at {excel_path}"
            )
            return
        
        # Check if confirmation is required
        if self.config.get("sync.confirm_changes", True):
            confirm = messagebox.askyesno(
                "Confirm Sync",
                "Are you sure you want to sync changes from Excel to Cognito Forms?"
            )
            if not confirm:
                self._log_status("Sync to Cognito Forms cancelled by user.")
                return
        
        try:
            self._log_status("Synchronizing from Excel to Cognito Forms...")
            updated, added, deleted = self.sync_manager.sync_to_cognito()
            self._update_last_sync_time()
            
            self._log_status(
                f"Synchronization complete:\n"
                f"  - {updated} entries updated\n"
                f"  - {added} entries added\n"
                f"  - {deleted} entries deleted"
            )
            
            messagebox.showinfo(
                "Sync Complete",
                f"Synchronized successfully:\n"
                f"  - {updated} entries updated\n"
                f"  - {added} entries added\n"
                f"  - {deleted} entries deleted"
            )
        except Exception as e:
            self._log_status(f"Error synchronizing: {e}")
            messagebox.showerror(
                "Sync Error",
                f"An error occurred during synchronization:\n{e}"
            )
    
    def _log_status(self, message: str) -> None:
        """Log a status message to the status text widget.

        Args:
            message: The status message to log
        """
        # Enable editing
        self.status_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add message with timestamp
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Scroll to the end
        self.status_text.see(tk.END)
        
        # Disable editing
        self.status_text.config(state=tk.DISABLED)


def main() -> None:
    """Main entry point for the GUI."""
    root = tk.Tk()
    config = Config()
    app = ConnectorGUI(root, config)
    root.mainloop()


if __name__ == "__main__":
    main()
