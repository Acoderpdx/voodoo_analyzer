"""
Parameter inspector component
"""

import tkinter as tk
from tkinter import ttk
import json

class ParameterInspector(ttk.Frame):
    """Inspect and display plugin parameters"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        """Create inspector widgets"""
        # Notebook for categories
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Overview tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")
        
        # Create overview text
        self.overview_text = tk.Text(self.overview_frame, wrap=tk.WORD)
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Category tabs will be added dynamically
        self.category_tabs = {}
    
    def clear(self):
        """Clear all parameter data"""
        self.overview_text.delete(1.0, tk.END)
        
        # Remove category tabs
        for tab_id in list(self.category_tabs.keys()):
            self.notebook.forget(self.category_tabs[tab_id])
        self.category_tabs.clear()
    
    def load_parameters(self, categorized_data):
        """Load and display categorized parameters"""
        if not categorized_data:
            return
        
        # Update overview
        self._update_overview(categorized_data)
        
        # Create tabs for each category
        for category, info in categorized_data['categories'].items():
            self._create_category_tab(category, info, categorized_data['parameter_details'])
        
        # Create uncategorized tab if needed
        if categorized_data['uncategorized']:
            self._create_uncategorized_tab(
                categorized_data['uncategorized'], 
                categorized_data['parameter_details']
            )
    
    def _update_overview(self, data):
        """Update overview tab"""
        self.overview_text.delete(1.0, tk.END)
        
        # Count parameters
        total_params = len(data['parameter_details'])
        categorized_count = sum(len(info['parameters']) for info in data['categories'].values())
        
        # Display summary
        self.overview_text.insert(tk.END, "PARAMETER DISCOVERY OVERVIEW\n", 'header')
        self.overview_text.insert(tk.END, "="*40 + "\n\n")
        
        self.overview_text.insert(tk.END, f"Total Parameters: {total_params}\n")
        self.overview_text.insert(tk.END, f"Categorized: {categorized_count}\n")
        self.overview_text.insert(tk.END, f"Uncategorized: {len(data['uncategorized'])}\n\n")
        
        # Category breakdown
        self.overview_text.insert(tk.END, "Categories:\n", 'header')
        for category, info in data['categories'].items():
            count = len(info['parameters'])
            priority = info['priority']
            self.overview_text.insert(tk.END, f"  • {category}: {count} params ({priority} priority)\n")
        
        # Configure tags
        self.overview_text.tag_config('header', font=('Arial', 12, 'bold'))
    
    def _create_category_tab(self, category: str, info: dict, param_details: dict):
        """Create tab for a parameter category"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=category.replace('_', ' ').title())
        self.category_tabs[category] = frame
        
        # Create treeview for parameters
        tree = ttk.Treeview(frame, columns=('Type', 'Range', 'Default', 'Unit'), show='tree headings')
        tree.heading('#0', text='Parameter')
        tree.heading('Type', text='Type')
        tree.heading('Range', text='Range/Values')
        tree.heading('Default', text='Default')
        tree.heading('Unit', text='Unit')
        
        # Configure columns
        tree.column('#0', width=200)
        tree.column('Type', width=100)
        tree.column('Range', width=150)
        tree.column('Default', width=100)
        tree.column('Unit', width=60)
        
        # Add parameters
        for param_name in info['parameters']:
            param_info = param_details.get(param_name, {})
            
            # Format range/values
            if param_info.get('valid_values'):
                range_str = f"{len(param_info['valid_values'])} values"
            elif param_info.get('range'):
                range_str = f"{param_info['range'][0]} - {param_info['range'][1]}"
            else:
                range_str = "N/A"
            
            tree.insert('', 'end', 
                       text=param_name,
                       values=(
                           param_info.get('type', 'unknown'),
                           range_str,
                           param_info.get('default', 'N/A'),
                           param_info.get('unit', '')
                       ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
    
    def _create_uncategorized_tab(self, params: list, param_details: dict):
        """Create tab for uncategorized parameters"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Uncategorized")
        self.category_tabs['uncategorized'] = frame
        
        # Create text widget
        text = tk.Text(frame, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text.insert(tk.END, "UNCATEGORIZED PARAMETERS\n", 'header')
        text.insert(tk.END, "These parameters need manual categorization:\n\n")
        
        for param in params:
            param_info = param_details.get(param, {})
            text.insert(tk.END, f"• {param}\n")
            text.insert(tk.END, f"  Type: {param_info.get('type', 'unknown')}\n")
            if param_info.get('range'):
                text.insert(tk.END, f"  Range: {param_info['range']}\n")
            text.insert(tk.END, "\n")
        
        text.tag_config('header', font=('Arial', 12, 'bold'))