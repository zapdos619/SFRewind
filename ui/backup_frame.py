"""
Backup Frame UI Component - PRODUCTION READY
ALL CRITICAL ISSUES FIXED:
- Issue #4: Thread cancellation for all operations
- Issue #2: Shared state locks for selected_objects and all_objects
- Issue #3: All widget updates via self.after()
- Issue #1: Proper lambda value captures
MEDIUM PRIORITY ISSUES FIXED:
- Issue #16: Duplicate selection prevention
- Issue #14: Determinate progress bars (shows real progress)
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.backup_manager import BackupManager
from datetime import datetime
from pathlib import Path
import threading


class BackupFrame(ttk.Frame):
    """Backup interface - PRODUCTION READY"""
    
    def __init__(self, parent, get_connection_callback, on_logout_callback, theme_manager):
        super().__init__(parent)
        self.get_connection = get_connection_callback
        self.on_logout = on_logout_callback
        self.theme_manager = theme_manager
        self.colors = theme_manager.colors
        
        # Shared state with locks (Issue #2 Fix)
        self._objects_lock = threading.Lock()
        self.selected_objects = {}
        self.all_objects = []
        self._adding_objects = set()  # Issue #16 Fix: Track objects being added
        
        self.backup_location = None
        
        # Operation state management
        self._operation_lock = threading.Lock()
        self._is_loading = False
        self._is_backing_up = False
        
        # Thread cancellation support (Issue #4 Fix)
        self._cancel_event = threading.Event()
        self._active_threads = []
        
        self.setup_ui()
        self.load_default_location()
    
    def load_default_location(self):
        """Load default backup location"""
        from config.settings import BACKUP_DIR
        self.backup_location = BACKUP_DIR
        self.location_var.set(str(BACKUP_DIR))
    
    def setup_ui(self):
        """Setup backup interface"""
        # Top bar with logout button
        top_bar = ttk.Frame(self, padding="5")
        top_bar.pack(fill='x', side='top')
        
        ttk.Label(top_bar, text="Backup Manager", font=('Arial', 11, 'bold')).pack(side='left', padx=10)
        ttk.Button(top_bar, text="🚪 Logout", command=self.handle_logout, width=12).pack(side='right', padx=10)
        
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=5)
        
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True)
        
        # Left panel - Object selection
        left_panel = ttk.Frame(content_frame, padding="10")
        left_panel.pack(side='left', fill='both', expand=True)
        
        ttk.Label(left_panel, text="Select Objects to Backup", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Object search section
        search_frame = ttk.LabelFrame(left_panel, text="Search Objects", padding="5")
        search_frame.pack(fill='x', pady=5)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_input_frame, text="Search:").pack(side='left', padx=5)
        # Enlarged input field for better visual balance
        self.search_entry = ttk.Entry(search_input_frame, width=35)
        self.search_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.search_entry.bind('<Return>', lambda e: self.search_objects())
        
        # Larger buttons for consistent spacing
        self.search_btn = ttk.Button(search_input_frame, text="Search", command=self.search_objects, width=12)
        self.search_btn.pack(side='left', padx=3)
        
        self.load_all_btn = ttk.Button(search_input_frame, text="Load All Objects", command=self.load_all_objects, width=16)
        self.load_all_btn.pack(side='left', padx=3)
        
        # Available objects display
        available_frame = ttk.Frame(search_frame)
        available_frame.pack(fill='both', expand=True, pady=5)
        
        canvas = tk.Canvas(available_frame, height=120, bg=self.colors['entry_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=canvas.yview)
        self.available_objects_frame = ttk.Frame(canvas)
        
        self.available_objects_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.available_objects_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.show_default_objects()
        
        # Selected objects list
        ttk.Label(left_panel, text="Selected Objects:", font=('Arial', 10, 'bold')).pack(pady=(10, 5))
        
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill='both', expand=True)
        
        self.objects_listbox = tk.Listbox(list_frame, height=10)
        self.objects_listbox.pack(side='left', fill='both', expand=True)
        self.theme_manager.configure_widget(self.objects_listbox)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.objects_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.objects_listbox.config(yscrollcommand=scrollbar.set)
        
        ttk.Button(left_panel, text="Remove Selected", command=self.remove_object).pack(pady=5)
        
        # Right panel - Backup actions
        right_panel = ttk.Frame(content_frame, padding="10")
        right_panel.pack(side='right', fill='both', expand=True)
        
        ttk.Label(right_panel, text="Backup Configuration", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Backup location
        location_frame = ttk.LabelFrame(right_panel, text="Backup Location", padding="5")
        location_frame.pack(fill='x', pady=10)
        
        self.location_var = tk.StringVar(value="")
        location_display = ttk.Entry(location_frame, textvariable=self.location_var, state='readonly', width=35)
        location_display.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(location_frame, text="Browse...", command=self.browse_location).pack(side='left', padx=5)
        
        # Backup name
        name_frame = ttk.Frame(right_panel)
        name_frame.pack(fill='x', pady=10)
        ttk.Label(name_frame, text="Backup Name:").pack(side='left', padx=5)
        self.backup_name_entry = ttk.Entry(name_frame, width=25)
        self.backup_name_entry.pack(side='left', padx=5)
        
        ttk.Label(name_frame, text="(Optional)", font=('Arial', 8), foreground='gray').pack(side='left', padx=5)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to backup")
        ttk.Label(right_panel, textvariable=self.progress_var).pack(pady=10)
        
        # Issue #14 Fix: Use determinate mode for real progress
        self.progress_bar = ttk.Progressbar(
            right_panel, 
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill='x', pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(right_panel)
        buttons_frame.pack(pady=10)
        
        # Backup button
        self.backup_btn = ttk.Button(
            buttons_frame,
            text="Start Backup",
            command=self.start_backup,
            width=20
        )
        self.backup_btn.pack(side='left', padx=5)
        
        # Cancel button (Issue #4 Fix)
        self.cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.cancel_operation,
            width=15,
            state='disabled'
        )
        self.cancel_btn.pack(side='left', padx=5)
        
        # Results text
        results_frame = ttk.LabelFrame(right_panel, text="Results", padding="5")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10, width=40, wrap='word')
        self.theme_manager.configure_widget(self.results_text)
        results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        self.results_text.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
    
    def handle_logout(self):
        """Handle logout with operation check (Issue #4 Fix)"""
        if self._is_loading or self._is_backing_up:
            response = messagebox.askyesno(
                "Operation in Progress",
                "An operation is running. Cancel it and logout?"
            )
            if response:
                self.cancel_operation()
                # Give threads time to clean up
                self.after(500, self.on_logout)
            return
        
        response = messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to logout from Salesforce?"
        )
        if response:
            self.on_logout()
    
    def cancel_operation(self):
        """Cancel current operation (Issue #4 Fix)"""
        self._cancel_event.set()
        
        # Update UI (Issue #3 Fix)
        self.after(0, lambda: self.progress_var.set("Cancelling..."))
        self.after(0, lambda: self.cancel_btn.config(state='disabled'))
        
        # Wait for threads to finish
        def wait_for_threads():
            for thread in self._active_threads:
                if thread.is_alive():
                    thread.join(timeout=5.0)
            
            # Clean up in main thread (Issue #3 Fix)
            self.after(0, self._cleanup_after_cancel)
        
        threading.Thread(target=wait_for_threads, daemon=True).start()
    
    def _cleanup_after_cancel(self):
        """Clean up UI after cancellation - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        self._active_threads = []
        self.progress_bar.stop()
        self.backup_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.progress_var.set("Operation cancelled")
        
        with self._operation_lock:
            self._is_loading = False
            self._is_backing_up = False
    
    def browse_location(self):
        """Browse for backup location"""
        directory = filedialog.askdirectory(
            title="Select Backup Location",
            initialdir=self.backup_location
        )
        if directory:
            self.backup_location = Path(directory)
            self.location_var.set(str(directory))
    
    def show_default_objects(self):
        """Show default common objects"""
        for widget in self.available_objects_frame.winfo_children():
            widget.destroy()
        
        default_objects = ['Account', 'Contact', 'Opportunity', 'Case', 'Lead', 
                          'Campaign', 'Task', 'Event', 'User', 'Product2']
        
        row, col = 0, 0
        for obj in default_objects:
            btn = ttk.Button(
                self.available_objects_frame,
                text=obj,
                command=lambda o=obj: self.add_object_to_list(o),
                width=25  # Fixed: Increased from 15 to 25
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
            col += 1
            if col > 2:
                col = 0
                row += 1
    
    def load_all_objects(self):
        """Load all objects with cancellation support (Issue #4 Fix)"""
        with self._operation_lock:
            if self._is_loading or self._is_backing_up:
                return
            self._is_loading = True
        
        sf = self.get_connection()
        if not sf:
            self._is_loading = False
            return
        
        # Clear cancel event
        self._cancel_event.clear()
        
        # Update UI (Issue #3 Fix)
        self.after(0, lambda: self.progress_var.set("Loading all objects..."))
        self.after(0, lambda: self.search_entry.config(state='disabled'))
        self.after(0, lambda: self.search_btn.config(state='disabled'))
        self.after(0, lambda: self.load_all_btn.config(state='disabled'))
        self.after(0, lambda: self.cancel_btn.config(state='normal'))
        
        def load_thread():
            all_objects = None
            error = None
            
            try:
                # Check for cancellation
                if self._cancel_event.is_set():
                    return
                
                describe = sf.describe()
                
                # Check for cancellation
                if self._cancel_event.is_set():
                    return
                
                all_objects = [obj['name'] for obj in describe['sobjects'] 
                             if obj['createable'] or obj['queryable']]
                all_objects.sort()
            except Exception as e:
                if not self._cancel_event.is_set():
                    error = str(e)
            finally:
                with self._operation_lock:
                    self._is_loading = False
            
            # Update UI in main thread (Issue #1 Fix - explicit capture)
            if self._cancel_event.is_set():
                self.after(0, lambda: self._on_load_cancelled())
            elif all_objects:
                # Thread-safe update (Issue #2 Fix)
                with self._objects_lock:
                    self.all_objects = all_objects
                self.after(0, lambda objs=all_objects: self.display_objects(objs))
                self.after(0, lambda count=len(all_objects): self.progress_var.set(f"Loaded {count} objects"))
            else:
                self.after(0, lambda err=error: messagebox.showerror("Error", f"Failed to load objects:\n{err}"))
                self.after(0, lambda: self.progress_var.set("Ready to backup"))
            
            # Re-enable controls (Issue #3 Fix)
            self.after(0, lambda: self.search_entry.config(state='normal'))
            self.after(0, lambda: self.search_btn.config(state='normal'))
            self.after(0, lambda: self.load_all_btn.config(state='normal'))
            self.after(0, lambda: self.cancel_btn.config(state='disabled'))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        self._active_threads.append(thread)
        thread.start()
    
    def _on_load_cancelled(self):
        """Handle cancelled load - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        self.search_entry.config(state='normal')
        self.search_btn.config(state='normal')
        self.load_all_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.progress_var.set("Load cancelled")
    
    def search_objects(self):
        """Search objects with cancellation support (Issue #4 Fix)"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.show_default_objects()
            return
        
        # Thread-safe read (Issue #2 Fix)
        with self._objects_lock:
            objects_copy = self.all_objects.copy()
        
        if not objects_copy:
            # Need to load first
            self.load_all_objects()
        else:
            # Search in loaded objects (instant, no threading needed)
            filtered = [obj for obj in objects_copy if search_term in obj.lower()]
            if filtered:
                self.display_objects(filtered[:20])
                self.progress_var.set(f"Found {len(filtered)} objects")
            else:
                self.show_default_objects()
                self.progress_var.set("No objects found")
    
    def display_objects(self, objects):
        """Display objects in grid"""
        for widget in self.available_objects_frame.winfo_children():
            widget.destroy()
        
        row, col = 0, 0
        for obj in objects:
            btn = ttk.Button(
                self.available_objects_frame,
                text=obj,
                command=lambda o=obj: self.add_object_to_list(o),
                width=25  # Fixed: Increased from 15 to 25
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
            col += 1
            if col > 2:
                col = 0
                row += 1
    
    def add_object_to_list(self, obj_name):
        """Add object with cancellation support (Issue #4 Fix) and duplicate prevention (Issue #16 Fix)"""
        # Thread-safe check (Issue #2 Fix)
        with self._objects_lock:
            if obj_name in self.selected_objects:
                messagebox.showinfo("Already Added", f"{obj_name} is already in the selected list")
                return
            
            # Issue #16 Fix: Check if currently being added
            if obj_name in self._adding_objects:
                messagebox.showinfo("Please Wait", 
                    f"{obj_name} is currently being added. Please wait...")
                return
            
            # Mark as being added
            self._adding_objects.add(obj_name)
        
        with self._operation_lock:
            if self._is_loading or self._is_backing_up:
                self._adding_objects.discard(obj_name)  # Issue #16 Fix
                messagebox.showwarning("Operation in Progress", "Please wait for current operation to complete")
                return
            self._is_loading = True
        
        sf = self.get_connection()
        if not sf:
            self._is_loading = False
            self._adding_objects.discard(obj_name)  # Issue #16 Fix
            return
        
        self._cancel_event.clear()
        self.after(0, lambda name=obj_name: self.progress_var.set(f"Loading {name}..."))
        self.after(0, lambda: self.cancel_btn.config(state='normal'))
        
        def add_thread():
            fields = None
            record_count = 0
            error = None
            
            try:
                if self._cancel_event.is_set():
                    return
                
                backup_mgr = BackupManager(sf)
                field_list = backup_mgr.get_object_fields(obj_name)
                
                if self._cancel_event.is_set():
                    return
                
                fields = [f['name'] for f in field_list if f['createable'] or f['name'] == 'Id']
                record_count = backup_mgr.get_record_count(obj_name)
            except Exception as e:
                if not self._cancel_event.is_set():
                    error = str(e)
            finally:
                with self._operation_lock:
                    self._is_loading = False
                # Issue #16 Fix: Always remove from adding set
                self._adding_objects.discard(obj_name)
            
            # Update in main thread (Issue #1 Fix - explicit capture)
            if self._cancel_event.is_set():
                self.after(0, lambda: self._on_add_cancelled())
            elif fields:
                # Thread-safe update (Issue #2 Fix)
                with self._objects_lock:
                    self.selected_objects[obj_name] = {
                        'fields': fields,
                        'record_count': record_count
                    }
                
                self.after(0, lambda name=obj_name, fc=len(fields), rc=record_count: 
                          self.objects_listbox.insert(tk.END, f"{name} | {fc} fields | {rc} records"))
                self.after(0, lambda name=obj_name: self.progress_var.set(f"Added {name}"))
            else:
                self.after(0, lambda err=error: messagebox.showerror("Error", f"Failed to add {obj_name}:\n{err}"))
                self.after(0, lambda: self.progress_var.set("Ready to backup"))
            
            self.after(0, lambda: self.cancel_btn.config(state='disabled'))
        
        thread = threading.Thread(target=add_thread, daemon=True)
        self._active_threads.append(thread)
        thread.start()
    
    def _on_add_cancelled(self):
        """Handle cancelled add - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        self.cancel_btn.config(state='disabled')
        self.progress_var.set("Add cancelled")
    
    def remove_object(self):
        """Remove selected object"""
        selection = self.objects_listbox.curselection()
        if selection:
            obj_name = self.objects_listbox.get(selection[0]).split(' | ')[0]
            
            # Thread-safe removal (Issue #2 Fix)
            with self._objects_lock:
                if obj_name in self.selected_objects:
                    del self.selected_objects[obj_name]
            
            self.objects_listbox.delete(selection[0])
            self.progress_var.set(f"Removed {obj_name}")
    
    def start_backup(self):
        """Start backup with cancellation support (Issue #4 Fix)"""
        # Thread-safe check (Issue #2 Fix)
        with self._objects_lock:
            if not self.selected_objects:
                messagebox.showwarning("No Objects", "Please select at least one object to backup")
                return
            objects_copy = self.selected_objects.copy()
        
        with self._operation_lock:
            if self._is_backing_up or self._is_loading:
                messagebox.showwarning("Operation in Progress", "Please wait for current operation to complete")
                return
            self._is_backing_up = True
        
        sf = self.get_connection()
        if not sf:
            self._is_backing_up = False
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        custom_name = self.backup_name_entry.get().strip()
        
        if custom_name:
            backup_name = f"{custom_name}_{timestamp}"
        else:
            backup_name = f"backup_{timestamp}"
        
        # Clear cancel event
        self._cancel_event.clear()
        
        # Issue #14 Fix: Calculate total progress
        total_objects = len(objects_copy)
        
        # Update UI (Issue #3 Fix)
        self.after(0, lambda: self.backup_btn.config(state='disabled'))
        self.after(0, lambda: self.cancel_btn.config(state='normal'))
        # Issue #14 Fix: Set determinate progress instead of spinning
        self.after(0, lambda t=total_objects: self.progress_bar.config(maximum=t, value=0))
        self.after(0, lambda t=total_objects: self.progress_var.set(f"Backing up 0/{t} objects..."))
        self.after(0, lambda: self.results_text.delete(1.0, tk.END))
        
        def backup_thread():
            final_path = None
            error = None
            
            # Define progress callback function (Issue #14 Fix - Progressive Updates)
            def update_progress(obj_name, completed, total):
                """Update progress bar after each object is backed up"""
                # OPTIMIZED: Single self.after call instead of two (prevents UI freeze)
                def _update():
                    self.progress_bar.config(value=completed)
                    self.progress_var.set(f"Backed up {obj_name} ({completed}/{total} objects)")
                
                self.after(0, _update)
            
            try:
                if self._cancel_event.is_set():
                    return
                
                backup_mgr = BackupManager(sf)
                objects_config = {obj: data['fields'] for obj, data in objects_copy.items()}
                
                # Check for cancellation before backup
                if self._cancel_event.is_set():
                    return
                
                # Issue #14 Fix: Pass progress callback to get real-time updates
                final_path = backup_mgr.create_backup(
                    objects_config, 
                    backup_name, 
                    str(self.backup_location),
                    progress_callback=update_progress
                )
                
                # Issue #14 Fix: Update to 100% on completion
                self.after(0, lambda t=total_objects: self.progress_bar.config(value=t))
                self.after(0, lambda t=total_objects: self.progress_var.set(f"Completed {t}/{t} objects"))
                
            except Exception as e:
                if not self._cancel_event.is_set():
                    error = str(e)
            finally:
                with self._operation_lock:
                    self._is_backing_up = False
            
            # Update in main thread (Issue #1 Fix - explicit capture)
            if self._cancel_event.is_set():
                self.after(0, lambda: self._on_backup_cancelled())
            elif final_path:
                self.after(0, lambda path=final_path, objs=objects_copy: self.on_backup_complete(path, objs))
            else:
                self.after(0, lambda err=error: self.on_backup_error(err))
        
        thread = threading.Thread(target=backup_thread, daemon=True)
        self._active_threads.append(thread)
        thread.start()
    
    def _on_backup_cancelled(self):
        """Handle cancelled backup - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        # Issue #14 Fix: No need to stop() in determinate mode, just reset value
        self.progress_bar.config(value=0)
        self.backup_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.progress_var.set("Backup cancelled")
        self.results_text.insert(tk.END, "Backup cancelled by user\n")
    
    def on_backup_complete(self, backup_path, selected_objects_snapshot):
        """Handle successful backup - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            # Issue #14 Fix: No need to stop() in determinate mode
            self.backup_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            self.progress_var.set("Backup completed!")
            
            self.results_text.insert(tk.END, f"✓ Backup completed successfully!\n")
            self.results_text.insert(tk.END, f"Location: {backup_path}\n\n")
            self.results_text.insert(tk.END, f"Backed up objects:\n")
            
            total_records = 0
            for obj, data in selected_objects_snapshot.items():
                fields_count = len(data['fields'])
                records_count = data['record_count']
                total_records += records_count
                self.results_text.insert(tk.END, f"  • {obj}: {fields_count} fields, {records_count} records\n")
            
            self.results_text.insert(tk.END, f"\nTotal: {len(selected_objects_snapshot)} objects, {total_records} records\n")
            
            messagebox.showinfo("Success", f"Backup completed!\n\nSaved to:\n{backup_path}")
        except Exception as e:
            print(f"Error in on_backup_complete: {e}")
    
    def on_backup_error(self, error_msg):
        """Handle backup error - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            # Issue #14 Fix: No need to stop() in determinate mode, reset to 0
            self.progress_bar.config(value=0)
            self.backup_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            self.progress_var.set("Backup failed")
            self.results_text.insert(tk.END, f"✗ Backup failed:\n{error_msg}\n")
            messagebox.showerror("Backup Error", f"Backup failed:\n{error_msg}")
        except Exception as e:
            print(f"Error in on_backup_error: {e}")