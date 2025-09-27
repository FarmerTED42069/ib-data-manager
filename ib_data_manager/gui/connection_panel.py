"""
Connection Panel Component
Streamlined connection management with visual status indicators
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import asyncio

class ConnectionPanel:
    """
    Clean, efficient connection management panel.
    Shows status at a glance and provides quick connection controls.
    """
    
    def __init__(self, parent, dashboard):
        self.parent = parent
        self.dashboard = dashboard
        self.status = "disconnected"
        self.last_connected = None
        
        self.create_panel()
        
    def create_panel(self):
        """Create the connection panel UI"""
        # Main connection frame
        self.conn_frame = ttk.LabelFrame(self.parent, text="🔌 Connection", padding="10")
        self.conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status display with large, clear indicator
        status_frame = ttk.Frame(self.conn_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connection status indicator (large, colorful)
        self.status_indicator = tk.Label(
            status_frame, 
            text="●", 
            font=("Arial", 24), 
            fg="red"
        )
        self.status_indicator.pack(side=tk.LEFT)
        
        # Status text
        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.status_label = ttk.Label(
            status_text_frame, 
            text="Not Connected", 
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(anchor=tk.W)
        
        self.status_detail = ttk.Label(
            status_text_frame, 
            text="Click Connect to start", 
            font=("Arial", 9),
            foreground="gray"
        )
        self.status_detail.pack(anchor=tk.W)
        
        # Connection controls
        controls_frame = ttk.Frame(self.conn_frame)
        controls_frame.pack(fill=tk.X)
        
        # Connect/Disconnect button (changes based on state)
        self.connect_btn = ttk.Button(
            controls_frame, 
            text="Connect to IB Gateway", 
            command=self.toggle_connection
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick settings button
        self.settings_btn = ttk.Button(
            controls_frame, 
            text="⚙️ Settings", 
            command=self.show_connection_settings,
            width=10
        )
        self.settings_btn.pack(side=tk.LEFT)
        
        # Auto-reconnect checkbox
        self.auto_reconnect = tk.BooleanVar(
            value=self.dashboard.settings.get("auto_reconnect", True)
        )
        ttk.Checkbutton(
            controls_frame, 
            text="Auto-reconnect", 
            variable=self.auto_reconnect,
            command=self.on_auto_reconnect_change
        ).pack(side=tk.RIGHT)
        
    def toggle_connection(self):
        """Toggle connection state"""
        if self.status == "disconnected":
            self.connect()
        else:
            self.disconnect()
            
    def connect(self):
        """Connect to IB Gateway"""
        self.update_status("connecting", "Connecting to IB Gateway...")
        self.connect_btn.config(state="disabled")
        
        async def do_connect():
            try:
                success = await self.dashboard.ib_conn.connect()
                if success:
                    self.dashboard.root.after(0, lambda: self.update_status(
                        "connected", 
                        f"Connected at {datetime.now().strftime('%H:%M:%S')}"
                    ))
                else:
                    self.dashboard.root.after(0, lambda: self.update_status(
                        "error", 
                        "Failed to connect - check IB Gateway"
                    ))
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.update_status(
                    "error", 
                    f"Connection error: {str(e)[:50]}..."
                ))
            finally:
                self.dashboard.root.after(0, lambda: self.connect_btn.config(state="normal"))
                
        future = self.dashboard.run_async_task(do_connect())
        
    def disconnect(self):
        """Disconnect from IB Gateway"""
        self.update_status("disconnecting", "Disconnecting...")
        self.connect_btn.config(state="disabled")
        
        async def do_disconnect():
            try:
                await self.dashboard.ib_conn.disconnect()
                self.dashboard.root.after(0, lambda: self.update_status(
                    "disconnected", 
                    "Disconnected"
                ))
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.update_status(
                    "error", 
                    f"Disconnect error: {str(e)[:50]}..."
                ))
            finally:
                self.dashboard.root.after(0, lambda: self.connect_btn.config(state="normal"))
                
        future = self.dashboard.run_async_task(do_disconnect())
        
    def update_status(self, status, detail_text):
        """Update connection status display"""
        self.status = status
        
        # Update indicator color and text
        status_config = {
            "disconnected": {"color": "red", "text": "Not Connected", "btn_text": "Connect to IB Gateway"},
            "connecting": {"color": "orange", "text": "Connecting...", "btn_text": "Connecting..."},
            "connected": {"color": "green", "text": "Connected", "btn_text": "Disconnect"},
            "disconnecting": {"color": "orange", "text": "Disconnecting...", "btn_text": "Disconnecting..."},
            "error": {"color": "red", "text": "Connection Error", "btn_text": "Retry Connection"}
        }
        
        config = status_config.get(status, status_config["disconnected"])
        
        self.status_indicator.config(fg=config["color"])
        self.status_label.config(text=config["text"])
        self.status_detail.config(text=detail_text)
        self.connect_btn.config(text=config["btn_text"])
        
        # Update dashboard connection status
        self.dashboard.connection_status = status
        
        if status == "connected":
            self.last_connected = datetime.now()
            
    def show_connection_settings(self):
        """Show connection settings dialog"""
        dialog = tk.Toplevel(self.dashboard.root)
        dialog.title("Connection Settings")
        dialog.geometry("400x300")
        dialog.transient(self.dashboard.root)
        dialog.grab_set()
        
        # Settings frame
        settings_frame = ttk.Frame(dialog, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # IB Gateway settings
        ttk.Label(settings_frame, text="IB Gateway Configuration", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Host and port
        host_frame = ttk.Frame(settings_frame)
        host_frame.pack(fill=tk.X, pady=5)
        ttk.Label(host_frame, text="Host:").pack(side=tk.LEFT)
        host_entry = ttk.Entry(host_frame, width=15)
        host_entry.pack(side=tk.LEFT, padx=(10, 20))
        host_entry.insert(0, self.dashboard.settings.get("ib_host", "127.0.0.1"))
        
        ttk.Label(host_frame, text="Port:").pack(side=tk.LEFT)
        port_entry = ttk.Entry(host_frame, width=8)
        port_entry.pack(side=tk.LEFT, padx=(10, 0))
        port_entry.insert(0, str(self.dashboard.settings.get("ib_port", 4002)))
        
        # Client ID
        client_frame = ttk.Frame(settings_frame)
        client_frame.pack(fill=tk.X, pady=5)
        ttk.Label(client_frame, text="Client ID:").pack(side=tk.LEFT)
        client_entry = ttk.Entry(client_frame, width=8)
        client_entry.pack(side=tk.LEFT, padx=(10, 0))
        client_entry.insert(0, str(self.dashboard.settings.get("client_id", 1)))
        
        # Auto-connect
        auto_connect = tk.BooleanVar(value=self.dashboard.settings.get("auto_connect", False))
        ttk.Checkbutton(settings_frame, text="Auto-connect on startup", 
                       variable=auto_connect).pack(anchor=tk.W, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_settings():
            self.dashboard.settings.update({
                "ib_host": host_entry.get(),
                "ib_port": int(port_entry.get()),
                "client_id": int(client_entry.get()),
                "auto_connect": auto_connect.get()
            })
            self.dashboard.save_settings()
            dialog.destroy()
            
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
    def on_auto_reconnect_change(self):
        """Handle auto-reconnect setting change"""
        self.dashboard.settings["auto_reconnect"] = self.auto_reconnect.get()
        self.dashboard.save_settings()
        
    def get_connection_info(self):
        """Get current connection information"""
        return {
            "status": self.status,
            "last_connected": self.last_connected,
            "auto_reconnect": self.auto_reconnect.get()
        }
