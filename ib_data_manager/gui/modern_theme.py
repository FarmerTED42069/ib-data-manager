"""
Modern theme and styling for IB Data Manager GUI
"""

import tkinter as tk
from tkinter import ttk

class ModernTheme:
    """Modern color theme and styling constants"""
    
    # Colors
    PRIMARY = "#2E86AB"      # Blue
    SECONDARY = "#A23B72"    # Purple  
    SUCCESS = "#F18F01"      # Orange
    DANGER = "#C73E1D"       # Red
    WARNING = "#F4A261"      # Yellow
    INFO = "#264653"         # Dark Green
    
    # Grays
    DARK = "#2D3748"
    MEDIUM = "#4A5568"
    LIGHT = "#E2E8F0"
    WHITE = "#FFFFFF"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 14
    FONT_SIZE_MEDIUM = 11
    FONT_SIZE_SMALL = 9
    
    @classmethod
    def configure_styles(cls, root):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        
        # Configure main styles
        style.configure('Title.TLabel', 
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE_LARGE, 'bold'),
                       foreground=cls.DARK)
        
        style.configure('Heading.TLabel',
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE_MEDIUM, 'bold'),
                       foreground=cls.MEDIUM)
        
        style.configure('Status.TLabel',
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE_MEDIUM),
                       padding=(5, 2))
        
        # Button styles
        style.configure('Primary.TButton',
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE_MEDIUM),
                       padding=(10, 5))
        
        style.configure('Success.TButton',
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE_MEDIUM),
                       padding=(8, 4))
        
        # Frame styles
        style.configure('Card.TFrame',
                       relief='solid',
                       borderwidth=1,
                       padding=10)

class ProgressDialog:
    """Modern progress dialog with cancellation support"""
    
    def __init__(self, parent, title="Processing", message="Please wait..."):
        self.parent = parent
        self.cancelled = False
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Create widgets
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        self.message_label = ttk.Label(main_frame, text=message, 
                                     font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_MEDIUM))
        self.message_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        self.progress.start()
        
        # Cancel button
        self.cancel_btn = ttk.Button(main_frame, text="Cancel", 
                                   command=self.cancel)
        self.cancel_btn.pack()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
    def update_message(self, message: str):
        """Update progress message"""
        self.message_label.config(text=message)
        self.dialog.update_idletasks()
        
    def cancel(self):
        """Cancel operation"""
        self.cancelled = True
        self.close()
        
    def close(self):
        """Close dialog"""
        self.progress.stop()
        self.dialog.destroy()
