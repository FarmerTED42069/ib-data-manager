"""
Feature Selection Dialog for Analysis
Allows users to pick and choose analysis features for Jupyter notebooks
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Set
from ib_data_manager.analysis import FEATURE_LIBRARY, FeatureCategory


class FeatureSelectorDialog:
    """Dialog for selecting analysis features"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.selected_features = set()
        
        self.create_dialog()
        
    def create_dialog(self):
        """Create the feature selection dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🧪 Select Analysis Features")
        self.dialog.geometry("800x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Select Analysis Features for Your Notebook",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Create paned window for categories and details
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Left panel: Feature categories and selection
        self.create_selection_panel(paned_window)
        
        # Right panel: Feature details
        self.create_details_panel(paned_window)
        
        # Bottom buttons
        self.create_buttons(main_frame)
        
        # Load features
        self.load_features()
        
    def create_selection_panel(self, parent):
        """Create the feature selection panel"""
        selection_frame = ttk.Frame(parent, padding="10")
        parent.add(selection_frame, weight=2)
        
        # Quick selection buttons
        quick_frame = ttk.LabelFrame(selection_frame, text="Quick Selection", padding="5")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        quick_row = ttk.Frame(quick_frame)
        quick_row.pack(fill=tk.X)
        
        ttk.Button(quick_row, text="📊 Basic Analysis", 
                  command=self.select_basic_features, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_row, text="📈 Technical Analysis", 
                  command=self.select_technical_features, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_row, text="🧠 Advanced ML", 
                  command=self.select_advanced_features, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_row, text="🔄 Clear All", 
                  command=self.clear_all_features, width=12).pack(side=tk.LEFT, padx=2)
        
        # Feature tree
        tree_frame = ttk.LabelFrame(selection_frame, text="Available Features", padding="5")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.feature_tree = ttk.Treeview(tree_frame, columns=("complexity",), show="tree headings")
        self.feature_tree.heading("#0", text="Feature")
        self.feature_tree.heading("complexity", text="Level")
        self.feature_tree.column("complexity", width=80)
        
        # Scrollbars
        tree_scroll_v = ttk.Scrollbar(tree_frame, orient="vertical", command=self.feature_tree.yview)
        tree_scroll_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.feature_tree.xview)
        self.feature_tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)
        
        # Pack tree and scrollbars
        self.feature_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.feature_tree.bind("<<TreeviewSelect>>", self.on_feature_select)
        self.feature_tree.bind("<Double-1>", self.toggle_feature)
        
    def create_details_panel(self, parent):
        """Create the feature details panel"""
        details_frame = ttk.Frame(parent, padding="10")
        parent.add(details_frame, weight=1)
        
        # Selected features
        selected_frame = ttk.LabelFrame(details_frame, text="Selected Features", padding="5")
        selected_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_listbox = tk.Listbox(selected_frame, height=6, font=("Arial", 9))
        self.selected_listbox.pack(fill=tk.X, pady=2)
        
        # Feature details
        info_frame = ttk.LabelFrame(details_frame, text="Feature Information", padding="5")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Feature name and description
        self.feature_name_label = ttk.Label(info_frame, text="Select a feature to view details", 
                                          font=("Arial", 11, "bold"))
        self.feature_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.feature_desc_label = ttk.Label(info_frame, text="", wraplength=250)
        self.feature_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Requirements
        req_frame = ttk.Frame(info_frame)
        req_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(req_frame, text="Requirements:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.requirements_label = ttk.Label(req_frame, text="", font=("Arial", 9))
        self.requirements_label.pack(anchor=tk.W)
        
        # Dependencies
        dep_frame = ttk.Frame(info_frame)
        dep_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dep_frame, text="Dependencies:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.dependencies_label = ttk.Label(dep_frame, text="", font=("Arial", 9))
        self.dependencies_label.pack(anchor=tk.W)
        
        # Add/Remove buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill=tk.X)
        
        self.add_button = ttk.Button(button_frame, text="➕ Add Feature", 
                                   command=self.add_current_feature, width=15)
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.remove_button = ttk.Button(button_frame, text="➖ Remove", 
                                      command=self.remove_selected_feature, width=15)
        self.remove_button.pack(side=tk.LEFT)
        
    def create_buttons(self, parent):
        """Create dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # Info label
        info_label = ttk.Label(button_frame, 
                             text=f"Selected: 0 features", 
                             font=("Arial", 9))
        info_label.pack(side=tk.LEFT)
        
        self.info_label = info_label
        
        # Action buttons
        ttk.Button(button_frame, text="Generate Notebook", 
                  command=self.generate_notebook, width=15).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        
    def load_features(self):
        """Load features into the tree"""
        # Clear existing items
        for item in self.feature_tree.get_children():
            self.feature_tree.delete(item)
        
        # Add categories and features
        for category in FeatureCategory:
            # Add category node
            category_id = self.feature_tree.insert("", "end", text=category.value, 
                                                 values=("",), tags=("category",))
            
            # Add features in this category
            features = FEATURE_LIBRARY.get_features_by_category(category)
            for feature in features:
                feature_id = self.feature_tree.insert(category_id, "end", 
                                                    text=feature.name,
                                                    values=(feature.complexity,),
                                                    tags=("feature",))
        
        # Expand all categories
        for item in self.feature_tree.get_children():
            self.feature_tree.item(item, open=True)
    
    def on_feature_select(self, event):
        """Handle feature selection in tree"""
        selection = self.feature_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        tags = self.feature_tree.item(item, "tags")
        
        if "feature" in tags:
            feature_name = self.feature_tree.item(item, "text")
            feature = FEATURE_LIBRARY.get_feature(feature_name)
            
            if feature:
                self.show_feature_details(feature)
    
    def show_feature_details(self, feature):
        """Show details for selected feature"""
        self.current_feature = feature
        
        self.feature_name_label.config(text=feature.name)
        self.feature_desc_label.config(text=feature.description)
        self.requirements_label.config(text=", ".join(feature.requirements))
        self.dependencies_label.config(text=", ".join(feature.dependencies))
        
        # Update button state
        if feature.name in self.selected_features:
            self.add_button.config(state="disabled", text="✅ Added")
        else:
            self.add_button.config(state="normal", text="➕ Add Feature")
    
    def toggle_feature(self, event):
        """Toggle feature selection on double-click"""
        selection = self.feature_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        tags = self.feature_tree.item(item, "tags")
        
        if "feature" in tags:
            feature_name = self.feature_tree.item(item, "text")
            
            if feature_name in self.selected_features:
                self.selected_features.remove(feature_name)
            else:
                self.selected_features.add(feature_name)
            
            self.update_selected_display()
    
    def add_current_feature(self):
        """Add currently selected feature"""
        if hasattr(self, 'current_feature'):
            self.selected_features.add(self.current_feature.name)
            self.update_selected_display()
            self.add_button.config(state="disabled", text="✅ Added")
    
    def remove_selected_feature(self):
        """Remove selected feature from list"""
        selection = self.selected_listbox.curselection()
        if selection:
            feature_name = self.selected_listbox.get(selection[0])
            self.selected_features.discard(feature_name)
            self.update_selected_display()
            
            # Update add button if this is the current feature
            if hasattr(self, 'current_feature') and self.current_feature.name == feature_name:
                self.add_button.config(state="normal", text="➕ Add Feature")
    
    def update_selected_display(self):
        """Update the selected features display"""
        self.selected_listbox.delete(0, tk.END)
        for feature_name in sorted(self.selected_features):
            self.selected_listbox.insert(tk.END, feature_name)
        
        # Update info label
        count = len(self.selected_features)
        self.info_label.config(text=f"Selected: {count} features")
    
    def select_basic_features(self):
        """Select basic analysis features"""
        basic_features = ["Moving Averages", "RSI Indicator", "Returns Analysis"]
        for feature_name in basic_features:
            if FEATURE_LIBRARY.get_feature(feature_name):
                self.selected_features.add(feature_name)
        self.update_selected_display()
    
    def select_technical_features(self):
        """Select technical analysis features"""
        tech_features = ["Moving Averages", "RSI Indicator", "Returns Analysis", "Value at Risk (VaR)"]
        for feature_name in tech_features:
            if FEATURE_LIBRARY.get_feature(feature_name):
                self.selected_features.add(feature_name)
        self.update_selected_display()
    
    def select_advanced_features(self):
        """Select advanced ML features"""
        advanced_features = ["GARCH Volatility Model", "Price Prediction ML"]
        for feature_name in advanced_features:
            if FEATURE_LIBRARY.get_feature(feature_name):
                self.selected_features.add(feature_name)
        self.update_selected_display()
    
    def clear_all_features(self):
        """Clear all selected features"""
        self.selected_features.clear()
        self.update_selected_display()
        if hasattr(self, 'current_feature'):
            self.add_button.config(state="normal", text="➕ Add Feature")
    
    def generate_notebook(self):
        """Generate notebook with selected features"""
        if not self.selected_features:
            messagebox.showwarning("No Features Selected", 
                                 "Please select at least one analysis feature.")
            return
        
        if self.callback:
            self.callback(list(self.selected_features))
        
        self.dialog.destroy()


def show_feature_selector(parent, callback=None):
    """Convenience function to show feature selector dialog"""
    return FeatureSelectorDialog(parent, callback)
