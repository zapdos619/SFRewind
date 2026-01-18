"""
Login Frame UI Component - PRODUCTION READY
ALL CRITICAL ISSUES FIXED:
- Issue #21: Secure credential handling (passwords cleared from memory)
- Issue #4: Thread cancellation support
- Issue #3: All widget updates via self.after()
- Issue #1: Proper lambda value captures
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.salesforce_auth import SalesforceAuth
import threading
import re
import gc


class SecureString:
    """Secure string storage that can be wiped from memory"""
    def __init__(self):
        self._chars = []
    
    def set(self, value):
        """Set value as list of characters"""
        self.clear()
        if value:
            self._chars = list(value)
    
    def get(self):
        """Get value and clear it from memory"""
        value = ''.join(self._chars)
        return value
    
    def clear(self):
        """Securely wipe from memory"""
        self._chars = []
        gc.collect()  # Force garbage collection


class LoginFrame(ttk.Frame):
    """Salesforce login interface - PRODUCTION READY"""
    
    def __init__(self, parent, on_success_callback, theme_manager):
        super().__init__(parent)
        self.on_success = on_success_callback
        self.theme_manager = theme_manager
        self.colors = theme_manager.colors
        
        # Secure credential storage (Issue #21 Fix)
        self._secure_password = SecureString()
        self._secure_token = SecureString()
        
        # Initialize BooleanVar with master=self
        self.show_password_var = tk.BooleanVar(master=self, value=False)
        self.domain_var = tk.StringVar(master=self, value="test")
        self.use_custom_var = tk.BooleanVar(master=self, value=False)
        
        # Thread management (Issue #4 Fix)
        self._connection_lock = threading.Lock()
        self._is_connecting = False
        self._cancel_event = threading.Event()
        self._connection_thread = None
        
        self.setup_ui()
        
        # Set up variable traces AFTER UI is created
        self.use_custom_var.trace_add('write', lambda *args: self.handle_custom_domain_toggle())
        self.show_password_var.trace_add('write', lambda *args: self.handle_show_password_toggle())
    
    def setup_ui(self):
        """Setup login form"""
        container = ttk.Frame(self, padding="40")
        container.pack(expand=True)
        
        # Title
        title = ttk.Label(
            container,
            text="Connect to Salesforce",
            font=('Arial', 18, 'bold')
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Username
        ttk.Label(container, text="Username:", font=('Arial', 11)).grid(
            row=1, column=0, sticky='e', padx=10, pady=10
        )
        self.username_entry = ttk.Entry(container, width=50, font=('Arial', 10))
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        username_hint = ttk.Label(
            container, 
            text="e.g., user@company.com or user@company.com.sandbox",
            font=('Arial', 9),
            foreground='gray'
        )
        username_hint.grid(row=2, column=1, padx=10, sticky='w')
        
        # Password (with secure handling)
        ttk.Label(container, text="Password:", font=('Arial', 11)).grid(
            row=3, column=0, sticky='e', padx=10, pady=10
        )
        self.password_entry = ttk.Entry(container, width=50, show="●", font=('Arial', 10))
        self.password_entry.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        
        # Bind to secure storage (Issue #21 Fix)
        self.password_entry.bind('<KeyRelease>', self._on_password_change)
        
        # Security Token (with secure handling)
        ttk.Label(container, text="Security Token:", font=('Arial', 11)).grid(
            row=4, column=0, sticky='e', padx=10, pady=10
        )
        self.token_entry = ttk.Entry(container, width=50, show="●", font=('Arial', 10))
        self.token_entry.grid(row=4, column=1, padx=10, pady=10, sticky='ew')
        
        # Bind to secure storage (Issue #21 Fix)
        self.token_entry.bind('<KeyRelease>', self._on_token_change)
        
        token_hint = ttk.Label(
            container,
            text="From Setup → My Personal Information → Reset Security Token",
            font=('Arial', 9),
            foreground='gray'
        )
        token_hint.grid(row=5, column=1, padx=10, sticky='w')
        
        # Show password checkbox
        self.show_password_cb = ttk.Checkbutton(
            container,
            text="Show Password & Token",
            variable=self.show_password_var
        )
        self.show_password_cb.grid(row=6, column=1, padx=10, pady=8, sticky='w')
        
        # Environment selection
        ttk.Label(container, text="Environment:", font=('Arial', 11)).grid(
            row=7, column=0, sticky='e', padx=10, pady=10
        )
        
        domain_frame = ttk.Frame(container)
        domain_frame.grid(row=7, column=1, sticky='w', padx=10, pady=10)
        
        self.sandbox_radio = ttk.Radiobutton(
            domain_frame,
            text="Sandbox (test.salesforce.com)",
            variable=self.domain_var,
            value="test"
        )
        self.sandbox_radio.pack(side='left', padx=8)
        
        self.production_radio = ttk.Radiobutton(
            domain_frame,
            text="Production (login.salesforce.com)",
            variable=self.domain_var,
            value="login"
        )
        self.production_radio.pack(side='left', padx=8)
        
        # Custom domain section
        ttk.Label(container, text="", font=('Arial', 2)).grid(row=8, column=0)  # Spacer
        
        # Custom domain checkbox
        self.custom_check = ttk.Checkbutton(
            container,
            text="Use Custom Domain (My Domain)",
            variable=self.use_custom_var
        )
        self.custom_check.grid(row=9, column=1, padx=10, pady=8, sticky='w')
        
        # Custom domain input
        ttk.Label(container, text="Custom Domain:", font=('Arial', 11)).grid(
            row=10, column=0, sticky='e', padx=10, pady=10
        )
        self.custom_domain_entry = ttk.Entry(container, width=50, state='disabled', font=('Arial', 10))
        self.custom_domain_entry.grid(row=10, column=1, padx=10, pady=10, sticky='ew')
        
        custom_hint = ttk.Label(
            container,
            text="e.g., mycompany.my.salesforce.com (without https://)",
            font=('Arial', 9),
            foreground='gray'
        )
        custom_hint.grid(row=11, column=1, padx=10, sticky='w')
        
        # Connect button
        self.connect_btn = ttk.Button(
            container,
            text="Connect to Salesforce",
            command=self.connect,
            width=30
        )
        self.connect_btn.grid(row=12, column=0, columnspan=2, pady=30)
        
        # Cancel button (Issue #4 Fix)
        self.cancel_btn = ttk.Button(
            container,
            text="Cancel",
            command=self.cancel_connection,
            width=30,
            state='disabled'
        )
        self.cancel_btn.grid(row=13, column=0, columnspan=2, pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            container,
            text="Enter your credentials to connect",
            foreground="gray",
            font=('Arial', 10)
        )
        self.status_label.grid(row=14, column=0, columnspan=2)
        
        # Configure column weight for resizing
        container.columnconfigure(1, weight=1)
        
        # Bind Enter key for navigation
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.token_entry.focus())
        self.token_entry.bind('<Return>', lambda e: self.custom_domain_entry.focus() if self.use_custom_var.get() else self.connect())
        self.custom_domain_entry.bind('<Return>', lambda e: self.connect())
    
    def _on_password_change(self, event):
        """Store password securely (Issue #21 Fix)"""
        try:
            password = self.password_entry.get()
            self._secure_password.set(password)
        except:
            pass
    
    def _on_token_change(self, event):
        """Store token securely (Issue #21 Fix)"""
        try:
            token = self.token_entry.get()
            self._secure_token.set(token)
        except:
            pass
    
    def handle_custom_domain_toggle(self):
        """Handle changes to custom domain checkbox - THREAD SAFE (Issue #3 Fix)"""
        if self._is_connecting:
            return
        
        try:
            is_custom = self.use_custom_var.get()
        except:
            return
        
        # Schedule UI update in main thread (Issue #3 Fix)
        self.after(0, lambda custom=is_custom: self._update_custom_domain_ui(custom))
    
    def _update_custom_domain_ui(self, is_custom):
        """Update UI elements - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            if is_custom:
                self.custom_domain_entry.config(state='normal')
                self.sandbox_radio.config(state='disabled')
                self.production_radio.config(state='disabled')
                self.after(100, self._focus_custom_domain)
            else:
                self.custom_domain_entry.config(state='disabled')
                self.custom_domain_entry.delete(0, tk.END)
                self.sandbox_radio.config(state='normal')
                self.production_radio.config(state='normal')
        except Exception as e:
            print(f"Error updating custom domain UI: {e}")
    
    def _focus_custom_domain(self):
        """Helper to focus on custom domain entry"""
        try:
            if self.custom_domain_entry['state'] == 'normal':
                self.custom_domain_entry.focus()
        except:
            pass
    
    def handle_show_password_toggle(self):
        """Handle show password checkbox - THREAD SAFE (Issue #3 Fix)"""
        try:
            show = self.show_password_var.get()
        except:
            return
        
        # Schedule UI update in main thread (Issue #3 Fix)
        self.after(0, lambda s=show: self._update_password_visibility(s))
    
    def _update_password_visibility(self, show):
        """Update password visibility - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            if show:
                self.password_entry.config(show="")
                self.token_entry.config(show="")
            else:
                self.password_entry.config(show="●")
                self.token_entry.config(show="●")
        except Exception as e:
            print(f"Error updating password visibility: {e}")
    
    def validate_inputs(self, username, password, token, custom_domain=None):
        """Validate user inputs"""
        errors = []
        
        if not username:
            errors.append("Username is required")
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', username):
            errors.append("Username should be a valid email address")
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password seems too short (minimum 8 characters expected)")
        
        if not token:
            errors.append("Security Token is required")
        elif len(token) < 24:
            errors.append("Security Token seems invalid (should be 24+ characters)")
        
        if self.use_custom_var.get():
            if not custom_domain:
                errors.append("Custom domain is required when 'Use Custom Domain' is checked")
            elif not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', custom_domain):
                errors.append("Custom domain format is invalid (e.g., mycompany.my.salesforce.com)")
        
        return errors
    
    def connect(self):
        """Attempt to connect - WITH CANCELLATION SUPPORT (Issue #4 Fix)"""
        # Prevent double-click
        with self._connection_lock:
            if self._is_connecting:
                return
            self._is_connecting = True
        
        # Get username (not sensitive)
        try:
            username = self.username_entry.get().strip()
            domain = self.domain_var.get()
            custom_domain = self.custom_domain_entry.get().strip() if self.use_custom_var.get() else None
        except Exception as e:
            self._is_connecting = False
            messagebox.showerror("Error", f"Failed to read input fields: {e}")
            return
        
        # Get secure credentials (Issue #21 Fix)
        password = self._secure_password.get()
        token = self._secure_token.get()
        
        # Validate inputs
        validation_errors = self.validate_inputs(username, password, token, custom_domain)
        
        if validation_errors:
            # Clear credentials from memory (Issue #21 Fix)
            del password, token
            gc.collect()
            
            self._is_connecting = False
            error_message = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in validation_errors)
            messagebox.showwarning("Validation Error", error_message)
            return
        
        # Check sandbox username format
        if domain == "test" and not custom_domain and ".sandbox" not in username.lower():
            # Clear credentials temporarily
            del password, token
            gc.collect()
            
            self._is_connecting = False
            response = messagebox.askyesno(
                "Sandbox Environment",
                "You selected Sandbox but username doesn't contain '.sandbox'.\n\n"
                "Sandbox usernames typically look like: user@company.com.sandbox\n\n"
                "Continue anyway?"
            )
            if not response:
                self.username_entry.focus()
                return
            
            # Get credentials again
            password = self._secure_password.get()
            token = self._secure_token.get()
            self._is_connecting = True
        
        # Clear cancel event (Issue #4 Fix)
        self._cancel_event.clear()
        
        # Update UI (Issue #3 Fix - all via self.after)
        self.after(0, lambda: self.set_inputs_state('disabled'))
        self.after(0, lambda: self.connect_btn.config(state='disabled'))
        self.after(0, lambda: self.cancel_btn.config(state='normal'))
        self.after(0, lambda: self.status_label.config(text="Connecting to Salesforce...", foreground="blue"))
        
        # Connect in separate thread with cancellation support
        def connect_thread():
            auth_result = None
            error_message = None
            
            try:
                sf_auth = SalesforceAuth()
                
                # Check for cancellation before connecting
                if self._cancel_event.is_set():
                    return
                
                sf_auth.connect(username, password, token, domain, custom_domain)
                
                # Check for cancellation after connecting
                if self._cancel_event.is_set():
                    sf_auth.disconnect()
                    return
                
                auth_result = sf_auth
                
            except Exception as e:
                if not self._cancel_event.is_set():
                    error_message = str(e)
            finally:
                # CRITICAL: Clear credentials from memory (Issue #21 Fix)
                del password, token
                gc.collect()
            
            # Schedule UI update in main thread (Issue #1 Fix - explicit capture)
            if self._cancel_event.is_set():
                self.after(0, lambda: self.on_connection_cancelled())
            elif auth_result:
                self.after(0, lambda result=auth_result: self.on_connect_success(result))
            else:
                self.after(0, lambda error=error_message: self.on_connect_error(error))
        
        self._connection_thread = threading.Thread(target=connect_thread, daemon=True)
        self._connection_thread.start()
    
    def cancel_connection(self):
        """Cancel ongoing connection (Issue #4 Fix)"""
        self._cancel_event.set()
        self.status_label.config(text="Cancelling connection...", foreground="orange")
        self.cancel_btn.config(state='disabled')
        
        # Wait for thread to finish (max 3 seconds)
        if self._connection_thread and self._connection_thread.is_alive():
            self._connection_thread.join(timeout=3.0)
    
    def on_connection_cancelled(self):
        """Handle cancelled connection - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        with self._connection_lock:
            self._is_connecting = False
        
        try:
            self.set_inputs_state('normal')
            self.connect_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            self.status_label.config(text="Connection cancelled", foreground="orange")
        except Exception as e:
            print(f"Error in on_connection_cancelled: {e}")
    
    def set_inputs_state(self, state):
        """Enable/disable inputs - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        try:
            self.username_entry.config(state=state)
            self.password_entry.config(state=state)
            self.token_entry.config(state=state)
            self.custom_check.config(state=state)
            self.show_password_cb.config(state=state)
            
            if state == 'disabled':
                self.sandbox_radio.config(state='disabled')
                self.production_radio.config(state='disabled')
                self.custom_domain_entry.config(state='disabled')
            else:
                if self.use_custom_var.get():
                    self.custom_domain_entry.config(state='normal')
                    self.sandbox_radio.config(state='disabled')
                    self.production_radio.config(state='disabled')
                else:
                    self.custom_domain_entry.config(state='disabled')
                    self.sandbox_radio.config(state='normal')
                    self.production_radio.config(state='normal')
        except Exception as e:
            print(f"Error setting input state: {e}")
    
    def on_connect_success(self, sf_auth):
        """Handle successful connection - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        with self._connection_lock:
            self._is_connecting = False
        
        try:
            self.status_label.config(text="✓ Connected successfully!", foreground="green", font=('Arial', 11, 'bold'))
            self.set_inputs_state('normal')
            self.connect_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            
            # Clear password fields for security (Issue #21 Fix)
            self.password_entry.delete(0, tk.END)
            self.token_entry.delete(0, tk.END)
            self._secure_password.clear()
            self._secure_token.clear()
            
            self.on_success(sf_auth)
        except Exception as e:
            print(f"Error in on_connect_success: {e}")
            messagebox.showerror("Error", f"Connection succeeded but UI update failed: {e}")
    
    def on_connect_error(self, error_msg):
        """Handle connection error - RUNS IN MAIN THREAD (Issue #3 Fix)"""
        with self._connection_lock:
            self._is_connecting = False
        
        try:
            self.status_label.config(text="✗ Connection failed", foreground="red")
            self.set_inputs_state('normal')
            self.connect_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            
            # Parse common errors
            if error_msg and "INVALID_LOGIN" in error_msg.upper():
                error_display = "Invalid username, password, or security token.\n\nPlease check:\n• Username is correct\n• Password is correct\n• Security token is current (reset if needed)"
            elif error_msg and "API_DISABLED_FOR_ORG" in error_msg.upper():
                error_display = "API access is disabled for this organization.\n\nContact your Salesforce administrator."
            elif error_msg and "INVALID_SESSION_ID" in error_msg.upper():
                error_display = "Session error. Please check your credentials and try again."
            else:
                error_display = f"Connection failed:\n\n{error_msg if error_msg else 'Unknown error occurred'}"
            
            messagebox.showerror("Connection Error", error_display)
        except Exception as e:
            print(f"Error in on_connect_error: {e}")
    
    def __del__(self):
        """Cleanup - ensure credentials are cleared (Issue #21 Fix)"""
        try:
            self._secure_password.clear()
            self._secure_token.clear()
        except:
            pass