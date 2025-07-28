"""
Configuration Editor for IB Data Manager
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os

class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("IB Data Manager - Configuration Editor")
        self.root.geometry("500x400")
        
        # Default configuration
        self.default_config = {
            'ib_gateway': {
                'host': '127.0.0.1',
                'port': 4001,
                'client_id': 1
            },
            'connection': {
                'timeout': 15,
                'retry_attempts': 3,
                'retry_delay': 5
            },
            'data_settings': {
                'use_delayed_data': True,
                'market_data_type': 3  # 1=Live, 2=Frozen, 3=Delayed, 4=Delayed-Frozen
            }
        }
        
        self.config_file = 'config.json'
        self.config = self.load_config()
        
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            return False
    
    def create_widgets(self):
        """Create the configuration editor widgets"""
        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection settings tab
        conn_frame = ttk.Frame(notebook, padding="10")
        notebook.add(conn_frame, text="Connection Settings")
        
        # Host
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.host_var = tk.StringVar(value=self.config.get('ib_gateway', {}).get('host', '127.0.0.1'))
        host_entry = ttk.Entry(conn_frame, textvariable=self.host_var, width=30)
        host_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Port
        ttk.Label(conn_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.IntVar(value=self.config.get('ib_gateway', {}).get('port', 4001))
        port_entry = ttk.Entry(conn_frame, textvariable=self.port_var, width=30)
        port_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Client ID
        ttk.Label(conn_frame, text="Client ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.client_id_var = tk.IntVar(value=self.config.get('ib_gateway', {}).get('client_id', 1))
        client_id_entry = ttk.Entry(conn_frame, textvariable=self.client_id_var, width=30)
        client_id_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Connection timeout
        ttk.Label(conn_frame, text="Connection Timeout (seconds):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.IntVar(value=self.config.get('connection', {}).get('timeout', 15))
        timeout_entry = ttk.Entry(conn_frame, textvariable=self.timeout_var, width=30)
        timeout_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Retry attempts
        ttk.Label(conn_frame, text="Retry Attempts:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.retry_var = tk.IntVar(value=self.config.get('connection', {}).get('retry_attempts', 3))
        retry_entry = ttk.Entry(conn_frame, textvariable=self.retry_var, width=30)
        retry_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Data settings tab
        data_frame = ttk.Frame(notebook, padding="10")
        notebook.add(data_frame, text="Data Settings")
        
        # Use delayed data
        self.delayed_var = tk.BooleanVar(value=self.config.get('data_settings', {}).get('use_delayed_data', True))
        delayed_check = ttk.Checkbutton(data_frame, text="Use Delayed Market Data", variable=self.delayed_var)
        delayed_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Market data type
        ttk.Label(data_frame, text="Market Data Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_type_var = tk.StringVar(value=str(self.config.get('data_settings', {}).get('market_data_type', 3)))
        data_type_combo = ttk.Combobox(data_frame, textvariable=self.data_type_var, values=['1 - Live', '2 - Frozen', '3 - Delayed', '4 - Delayed-Frozen'])
        data_type_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        data_type_combo.set('3 - Delayed')
        
        # Help tab
        help_frame = ttk.Frame(notebook, padding="10")
        notebook.add(help_frame, text="Help")
        
        help_text = """Connection Settings Help:

Host: Usually '127.0.0.1' or 'localhost'
Port: 4001 for live trading, 4002 for paper trading
Client ID: Unique identifier for this connection (1-32)

Common Issues:
1. IB Gateway not running
2. API not enabled in IB Gateway
3. Wrong port number
4. Firewall blocking connection
5. Another application using the same Client ID

Recommended Settings:
- Use delayed data for testing
- Start with Client ID 1
- Use port 4002 for paper trading"""
        
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Configuration", command=self.save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
    
    def save_and_close(self):
        """Save configuration and close"""
        # Update config with current values
        self.config['ib_gateway'] = {
            'host': self.host_var.get(),
            'port': self.port_var.get(),
            'client_id': self.client_id_var.get()
        }
        
        self.config['connection'] = {
            'timeout': self.timeout_var.get(),
            'retry_attempts': self.retry_var.get(),
            'retry_delay': 5
        }
        
        # Extract market data type number
        data_type_value = self.data_type_var.get().split(' - ')[0]
        
        self.config['data_settings'] = {
            'use_delayed_data': self.delayed_var.get(),
            'market_data_type': int(data_type_value)
        }
        
        if self.save_config():
            self.root.destroy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            self.config = self.default_config.copy()
            
            # Update UI
            self.host_var.set(self.config['ib_gateway']['host'])
            self.port_var.set(self.config['ib_gateway']['port'])
            self.client_id_var.set(self.config['ib_gateway']['client_id'])
            self.timeout_var.set(self.config['connection']['timeout'])
            self.retry_var.set(self.config['connection']['retry_attempts'])
            self.delayed_var.set(self.config['data_settings']['use_delayed_data'])
            self.data_type_var.set(f"{self.config['data_settings']['market_data_type']} - Delayed")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
