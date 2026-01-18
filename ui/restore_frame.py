"""
Restore Frame UI Component - PRODUCTION READY
ALL CRITICAL ISSUES FIXED:
- Issue #4: Thread cancellation support
- Issue #3: All widget updates via self.after()
- Issue #1: Proper lambda value captures
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.restore_manager import RestoreManager
from pathlib import Path
import json
import threading


class RestoreFrame(ttk.Frame):
    """Restore interface - PRODUCTION READY"""
    
    def __init__(self, parent, get_connection_callback, on_logout_callback, theme_manager):
        super().__init__(parent)
        self.get_connection = get_connection_callback
        self.on_logout = on_logout_callback
        self.theme_manager = theme_manager
        self.colors = theme_manager.colors
        
        # State management
        self.selected_backup = None
        self._is_restoring = False
        self._operation_lock = threading.Lock()
        
        # Thread cancellation support (Issue #4 Fix)
        self._cancel_event = threading.Event()
        self._restore_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup restore interface"""
        # Top bar with logout button
        top_bar = ttk.Frame(self, padding="5")
        top_bar.pack(fill='x', side='top')
        
        ttk.Label(top_bar, text="Restore Manager", font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        ttk.Button(top_bar, text="🚪 Logout", command=self.handle_logout, width=12).pack(side='right', padx=10)
        
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=5)
        
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True)
        
        # Top panel - Backup selection
        top_panel = ttk.Frame(content_frame, padding="10")
        top_panel.pack(fill='x')
        
        ttk.Label(top_panel, text="Select Backup to Restore", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        select_frame = ttk.Frame(top_panel)
        select_frame.pack(fill='x', pady=5)
        
        self.backup_path_var = tk.StringVar(value="No backup selected")
        ttk.Label(select_frame, textvariable=self.backup_path_var, relief='sunken', width=60).pack(side='left', padx=5)
        
        self.browse_btn = ttk.Button(select_frame, text="Browse...", command=self.browse_backup)
        self.browse_btn.pack(side='left', padx=5)
        
        self.load_backup_btn = ttk.Button(select_frame, text="Load Backup", command=self.load_backup)
        self.load_backup_btn.pack(side='left', padx=5)
        
        # Middle panel - Backup details
        middle_panel = ttk.LabelFrame(content_frame, text="Backup Details", padding="10")
        middle_panel.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add scrollbar to details
        details_frame = ttk.Frame(middle_panel)
        details_frame.pack(fill='both', expand=True)
        
        self.details_text = tk.Text(details_frame, height=10, wrap='word')
        self.theme_manager.configure_widget(self.details_text)
        details_scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.details_text.yview)
        self.details_text.config(yscrollcommand=details_scrollbar.set)
        self.details_text.pack(side='left', fill='both', expand=True)
        details_scrollbar.pack(side='right', fill='y')
        
        # Bottom panel - Restore actions
        bottom_panel = ttk.Frame(content_frame, padding="10")
        bottom_panel.pack(fill='both', expand=True)
        
        # Progress
        self.progress_var = tk.StringVar(value="Select a backup to begin")
        ttk.Label(bottom_panel, textvariable=self.progress_var).pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(bottom_panel, mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(bottom_panel)
        buttons_frame.pack(pady=10)
        
        # Restore button
        self.restore_btn = ttk.Button(
            buttons_frame,
            text="Start Restore",
            command=self.start_restore,
            width=20,
            state='disabled'
        )
        self.restore_btn.pack(side='left', padx=5)
        
        # Cancel button (Issue #4 Fix)
        self.cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.cancel_restore,
            width=15,
            state='disabled'
        )
        self.cancel_btn.pack(side='left', padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(bottom_panel, text="Restore Results", padding="5")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        results_content = ttk.Frame(results_frame)
        results_content.pack(fill='both', expand=True)
        
        self.results_text = tk.Text(results_content, height=8, wrap='word')
        self.theme_manager.configure_widget(self.results_text)
        results_scrollbar = ttk.Scrollbar(results_content, orient='vertical', command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        self.results_text.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
    
    def handle_logout(self):
        """Handle logout with operation check (Issue #4 Fix)"""
        if self._is_restoring:
            response = messagebox.askyesno(
                "Restore in Progress",
                "A restore operation is running. Cancel it and logout?"
            )
            if response:
                self.cancel_restore()
                # Give thread time to clean up
                self.after(500, self.on_logout)
            return
        
        response = messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to logout from Salesforce?"
        )
        if response:
            self.on_logout()
    
    def cancel_restore(self):
        """Cancel ongoing restore (Issue #4 Fix)"""
        self._cancel_event.set()
        
        # Update UI (Issue #3 Fix)
        self.after(0, lambda: self.progress_var.set("Cancelling restore..."))
        self.after(0, lambda: self.cancel_btn.config(state='disabled'))
        
        # Wait for thread to finish
        def wait_for_thread():
            if self._restore_thread and self._restore_thread.is_alive():
                self._restore_thread.join(timeout=5.0)
            
            # Clean up in main thread (Issue #3 Fix)
            self.after(0, self._cleanup_after_cancel)
        
        threading.Thread(target=wait_for_thread, daemon=True).start()
    
    def _cleanup_after_cancel(self):
        """Clean up after cancellation - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        self.restore_btn.config(state='normal')
        self.browse_btn.config(state='normal')
        self.load_backup_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_var.set("Restore cancelled")
        self.results_text.insert(tk.END, "\n⚠️ Restore cancelled by user\n")
        
        with self._operation_lock:
            self._is_restoring = False
    
    def browse_backup(self):
        """Browse for backup directory"""
        from config.settings import BACKUP_DIR
        directory = filedialog.askdirectory(
            title="Select Backup Directory",
            initialdir=BACKUP_DIR
        )
        if directory:
            self.backup_path_var.set(directory)
            self.selected_backup = directory
    
    def load_backup(self):
        """Load and display backup metadata"""
        if not self.selected_backup:
            messagebox.showwarning("No Backup", "Please select a backup directory first")
            return
        
        try:
            metadata_file = Path(self.selected_backup) / "metadata.json"
            
            if not metadata_file.exists():
                messagebox.showerror("Invalid Backup", "Selected directory does not contain a valid backup (metadata.json not found)")
                return
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Display details
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Backup Name: {metadata['backup_name']}\n")
            self.details_text.insert(tk.END, f"Created: {metadata.get('created_at', metadata['timestamp'])}\n")
            self.details_text.insert(tk.END, f"Location: {self.selected_backup}\n\n")
            self.details_text.insert(tk.END, f"Objects in backup:\n")
            
            total_records = 0
            for obj_name, obj_info in metadata['objects'].items():
                record_count = obj_info['record_count']
                total_records += record_count
                self.details_text.insert(tk.END, f"\n• {obj_name}\n")
                self.details_text.insert(tk.END, f"  Fields: {len(obj_info['fields'])}\n")
                self.details_text.insert(tk.END, f"  Records: {record_count}\n")
            
            self.details_text.insert(tk.END, f"\nTotal: {len(metadata['objects'])} objects, {total_records} records\n")
            
            # Enable restore button
            self.restore_btn.config(state='normal')
            self.progress_var.set("Ready to restore")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Invalid Backup", f"Backup metadata file is corrupted:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load backup:\n{str(e)}")
    
    def start_restore(self):
        """Start restore with cancellation support (Issue #4 Fix)"""
        with self._operation_lock:
            if self._is_restoring:
                messagebox.showwarning("Restore in Progress", "A restore operation is already in progress")
                return
            self._is_restoring = True
        
        sf = self.get_connection()
        if not sf:
            self._is_restoring = False
            return
        
        if not self.selected_backup:
            self._is_restoring = False
            messagebox.showwarning("No Backup", "Please select and load a backup first")
            return
        
        # Confirm
        response = messagebox.askyesno(
            "Confirm Restore",
            "This will import data into your Salesforce org.\n\n"
            "⚠️ Warning: This operation cannot be undone.\n\n"
            "Are you sure you want to continue?"
        )
        if not response:
            self._is_restoring = False
            return
        
        # Clear cancel event
        self._cancel_event.clear()
        
        # Update UI (Issue #3 Fix)
        self.after(0, lambda: self.restore_btn.config(state='disabled'))
        self.after(0, lambda: self.browse_btn.config(state='disabled'))
        self.after(0, lambda: self.load_backup_btn.config(state='disabled'))
        self.after(0, lambda: self.cancel_btn.config(state='normal'))
        self.after(0, lambda: self.progress_bar.config(value=0))
        self.after(0, lambda: self.progress_var.set("Restoring..."))
        self.after(0, lambda: self.results_text.delete(1.0, tk.END))
        
        def progress_callback(obj_name, progress):
            """Thread-safe progress callback (Issue #1 Fix - explicit capture)"""
            self.after(0, lambda name=obj_name, prog=progress: self.update_progress(name, prog))
        
        def restore_thread():
            results = None
            error = None
            
            try:
                restore_mgr = RestoreManager(sf)
                
                # Pass cancel event to restore manager (Issue #4 Fix)
                results = restore_mgr.restore_backup(
                    self.selected_backup, 
                    progress_callback,
                    self._cancel_event  # Pass cancel event
                )
                
            except Exception as e:
                if not self._cancel_event.is_set():
                    error = str(e)
            finally:
                with self._operation_lock:
                    self._is_restoring = False
            
            # Update UI in main thread (Issue #1 Fix - explicit capture)
            if self._cancel_event.is_set():
                self.after(0, lambda: self._on_restore_cancelled())
            elif results:
                self.after(0, lambda res=results: self.on_restore_complete(res))
            else:
                self.after(0, lambda err=error: self.on_restore_error(err))
        
        self._restore_thread = threading.Thread(target=restore_thread, daemon=True)
        self._restore_thread.start()
    
    def update_progress(self, obj_name, progress):
        """Update progress - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            self.progress_bar['value'] = progress
            self.progress_var.set(f"Restoring {obj_name}...")
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def _on_restore_cancelled(self):
        """Handle cancelled restore - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        self.restore_btn.config(state='normal')
        self.browse_btn.config(state='normal')
        self.load_backup_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_var.set("Restore cancelled")
        self.results_text.insert(tk.END, "⚠️ Restore cancelled by user\n")
    
    def on_restore_complete(self, results):
        """Handle successful restore - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            # Re-enable controls
            self.restore_btn.config(state='normal')
            self.browse_btn.config(state='normal')
            self.load_backup_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            
            self.progress_bar['value'] = 100
            self.progress_var.set("Restore completed!")
            
            self.results_text.insert(tk.END, f"✓ Restore completed!\n\n")
            self.results_text.insert(tk.END, f"Summary:\n")
            
            total_success = 0
            total_failed = 0
            
            for obj_name, obj_result in results['objects'].items():
                self.results_text.insert(tk.END, f"\n• {obj_name}\n")
                self.results_text.insert(tk.END, f"  Success: {obj_result['success']}\n")
                self.results_text.insert(tk.END, f"  Failed: {obj_result['failed']}\n")
                total_success += obj_result['success']
                total_failed += obj_result['failed']
            
            self.results_text.insert(tk.END, f"\nTotal: {total_success} success, {total_failed} failed\n")
            
            if results['errors']:
                self.results_text.insert(tk.END, f"\n⚠️ Errors: {len(results['errors'])}\n")
            
            self.results_text.insert(tk.END, f"\n📄 Upload log saved: #uploadlog.txt\n")
            
            messagebox.showinfo("Success", f"Restore completed!\n\n{total_success} records imported\n\nLog saved in backup folder")
        except Exception as e:
            print(f"Error in on_restore_complete: {e}")
            messagebox.showerror("Error", f"Restore completed but UI update failed: {e}")
    
    def on_restore_error(self, error_msg):
        """Handle restore error - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            # Re-enable controls
            self.restore_btn.config(state='normal')
            self.browse_btn.config(state='normal')
            self.load_backup_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            
            self.progress_var.set("Restore failed")
            self.results_text.insert(tk.END, f"✗ Restore failed:\n{error_msg}\n")
            messagebox.showerror("Restore Error", f"Restore failed:\n{error_msg}")
        except Exception as e:
            print(f"Error in on_restore_error: {e}")