"""
History viewer component for displaying all analyzed plugins and their data
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from pathlib import Path
from datetime import datetime

class HistoryViewer(tk.Toplevel):
    """Window for viewing complete analysis history"""
    
    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.title("Analysis History")
        self.geometry("1000x700")
        
        # Data paths
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.discoveries_dir = self.data_dir / "discoveries"
        self.learned_patterns_path = self.data_dir / "learned_patterns.json"
        
        # Create UI
        self._create_ui()
        
        # Load and display history
        self.load_history()
        
    def _create_ui(self):
        """Create the history viewer UI"""
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Plugin Analysis History", 
                               font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Plugin list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Plugin list header
        list_header = ttk.Label(left_frame, text="Analyzed Plugins", 
                               font=('Helvetica', 12, 'bold'))
        list_header.pack(pady=(0, 5))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Plugin list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.plugin_listbox = tk.Listbox(list_frame, 
                                         yscrollcommand=scrollbar.set,
                                         font=('Helvetica', 10))
        self.plugin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.plugin_listbox.yview)
        
        # Bind selection event
        self.plugin_listbox.bind('<<ListboxSelect>>', self._on_plugin_selected)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(left_frame, text="Statistics")
        stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="", font=('Helvetica', 9))
        self.stats_label.pack(padx=5, pady=5)
        
        # Right panel - Plugin details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # Details header
        self.details_header = ttk.Label(right_frame, text="Select a plugin to view details", 
                                       font=('Helvetica', 12, 'bold'))
        self.details_header.pack(pady=(0, 10))
        
        # Notebook for different views
        self.details_notebook = ttk.Notebook(right_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        overview_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(overview_frame, text="Overview")
        self.overview_text = scrolledtext.ScrolledText(overview_frame, wrap=tk.WORD)
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        
        # Parameters tab
        params_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(params_frame, text="Parameters")
        self.params_text = scrolledtext.ScrolledText(params_frame, wrap=tk.WORD)
        self.params_text.pack(fill=tk.BOTH, expand=True)
        
        # Categories tab
        categories_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(categories_frame, text="Categories")
        self.categories_text = scrolledtext.ScrolledText(categories_frame, wrap=tk.WORD)
        self.categories_text.pack(fill=tk.BOTH, expand=True)
        
        # Raw Data tab
        raw_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(raw_frame, text="Raw Data")
        self.raw_text = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD, font=('Courier', 9))
        self.raw_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Export Selected", 
                  command=self.export_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Export All History", 
                  command=self.export_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", 
                  command=self.destroy).pack(side=tk.RIGHT)
        
    def load_history(self):
        """Load all plugin analysis history"""
        self.plugin_listbox.delete(0, tk.END)
        self.plugin_data = {}
        
        # Load discovery files
        if self.discoveries_dir.exists():
            discovery_files = list(self.discoveries_dir.glob("*_enhanced_*.json"))
            
            for file_path in sorted(discovery_files, key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Extract plugin name and timestamp from filename
                    filename = file_path.stem
                    parts = filename.rsplit('_enhanced_', 1)
                    if len(parts) == 2:
                        plugin_name = parts[0]
                        timestamp_str = parts[1]
                        
                        # Parse timestamp
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            display_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            display_time = timestamp_str
                        
                        # Create display string
                        params = data.get('parameters', {})
                        # Handle case where parameters might not be a dict
                        if isinstance(params, dict):
                            param_count = len([k for k in params.keys() if not k.startswith('_')])
                        else:
                            param_count = 0
                            
                        display_str = f"{plugin_name} ({display_time}) - {param_count} params"
                        
                        # Add to listbox
                        self.plugin_listbox.insert(tk.END, display_str)
                        
                        # Store data
                        self.plugin_data[display_str] = {
                            'name': plugin_name,
                            'timestamp': display_time,
                            'file_path': str(file_path),
                            'data': data
                        }
                        
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        # Update statistics
        self.update_stats()
        
    def update_stats(self):
        """Update statistics display"""
        total_plugins = len(self.plugin_data)
        unique_plugins = len(set(p['name'] for p in self.plugin_data.values()))
        
        stats_text = f"Total Analyses: {total_plugins}\\nUnique Plugins: {unique_plugins}"
        
        # Add learning stats if available
        try:
            if self.learned_patterns_path.exists():
                with open(self.learned_patterns_path, 'r') as f:
                    patterns = json.load(f)
                
                if 'plugin_history' in patterns:
                    stats_text += f"\\nLearning History: {len(patterns['plugin_history'])}"
                if 'parameter_patterns' in patterns:
                    stats_text += f"\\nLearned Patterns: {len(patterns['parameter_patterns'])}"
        except:
            pass
        
        self.stats_label.config(text=stats_text)
        
    def _on_search_changed(self, *args):
        """Handle search text changes"""
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate listbox
        self.plugin_listbox.delete(0, tk.END)
        
        for display_str, data in self.plugin_data.items():
            if search_text in display_str.lower():
                self.plugin_listbox.insert(tk.END, display_str)
                
    def _on_plugin_selected(self, event):
        """Handle plugin selection"""
        selection = self.plugin_listbox.curselection()
        if not selection:
            return
            
        # Get selected plugin
        display_str = self.plugin_listbox.get(selection[0])
        if display_str not in self.plugin_data:
            return
            
        plugin_info = self.plugin_data[display_str]
        plugin_data = plugin_info['data']
        
        # Update header
        self.details_header.config(text=f"{plugin_info['name']} - {plugin_info['timestamp']}")
        
        # Update overview
        self.overview_text.delete(1.0, tk.END)
        overview = f"Plugin: {plugin_info['name']}\\n"
        overview += f"Analysis Date: {plugin_info['timestamp']}\\n"
        overview += f"File: {plugin_info['file_path']}\\n\\n"
        
        if 'metadata' in plugin_data:
            meta = plugin_data['metadata']
            overview += "METADATA:\\n"
            for key, value in meta.items():
                overview += f"  {key}: {value}\\n"
            overview += "\\n"
            
        if 'learning_annotations' in plugin_data:
            annotations = plugin_data['learning_annotations']
            overview += "LEARNING INSIGHTS:\\n"
            overview += f"  Effect Type: {annotations.get('effect_type', 'Unknown')}\\n"
            overview += f"  Confidence: {annotations.get('confidence', 0):.2%}\\n"
            
            if 'applied_patterns' in annotations:
                overview += f"  Applied Patterns: {len(annotations['applied_patterns'])}\\n"
                
        self.overview_text.insert(1.0, overview)
        
        # Update parameters
        self.params_text.delete(1.0, tk.END)
        if 'parameters' in plugin_data:
            params_text = "DISCOVERED PARAMETERS:\\n\\n"
            params = plugin_data['parameters']
            
            for param_name, param_info in sorted(params.items()):
                if not param_name.startswith('_'):
                    params_text += f"{param_name}:\\n"
                    for key, value in param_info.items():
                        params_text += f"  {key}: {value}\\n"
                    params_text += "\\n"
                    
            self.params_text.insert(1.0, params_text)
            
        # Update categories
        self.categories_text.delete(1.0, tk.END)
        if 'categorized' in plugin_data:
            categories = plugin_data['categorized']
            cat_text = "PARAMETER CATEGORIES:\\n\\n"
            
            if 'categories' in categories:
                for cat_name, cat_info in categories['categories'].items():
                    cat_text += f"{cat_name.upper()}:\\n"
                    if 'description' in cat_info:
                        cat_text += f"  {cat_info['description']}\\n"
                    if 'parameters' in cat_info:
                        cat_text += f"  Parameters: {', '.join(cat_info['parameters'])}\\n"
                    cat_text += "\\n"
                    
            if 'uncategorized' in categories and categories['uncategorized']:
                cat_text += f"UNCATEGORIZED:\\n"
                cat_text += f"  {', '.join(categories['uncategorized'])}\\n"
                
            self.categories_text.insert(1.0, cat_text)
            
        # Update raw data
        self.raw_text.delete(1.0, tk.END)
        self.raw_text.insert(1.0, json.dumps(plugin_data, indent=2))
        
    def export_selected(self):
        """Export selected plugin data"""
        selection = self.plugin_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin to export")
            return
            
        display_str = self.plugin_listbox.get(selection[0])
        plugin_info = self.plugin_data[display_str]
        
        # Ask for save location
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{plugin_info['name']}_export.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(plugin_info['data'], f, indent=2)
                messagebox.showinfo("Export Complete", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
                
    def export_all(self):
        """Export all history data"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="plugin_history_export.json"
        )
        
        if filename:
            try:
                export_data = {
                    'export_date': datetime.now().isoformat(),
                    'total_analyses': len(self.plugin_data),
                    'plugins': {}
                }
                
                for display_str, info in self.plugin_data.items():
                    plugin_name = info['name']
                    if plugin_name not in export_data['plugins']:
                        export_data['plugins'][plugin_name] = []
                    
                    export_data['plugins'][plugin_name].append({
                        'timestamp': info['timestamp'],
                        'data': info['data']
                    })
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
                messagebox.showinfo("Export Complete", 
                                  f"Exported {len(self.plugin_data)} analyses to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
                
    def clear_history(self):
        """Clear analysis history (with confirmation)"""
        result = messagebox.askyesno(
            "Clear History", 
            "Are you sure you want to clear all analysis history?\\n\\n"
            "This will delete all discovery files but preserve learned patterns."
        )
        
        if result:
            try:
                # Delete discovery files
                for file_path in self.discoveries_dir.glob("*_enhanced_*.json"):
                    file_path.unlink()
                    
                # Reload
                self.load_history()
                messagebox.showinfo("History Cleared", "Analysis history has been cleared")
            except Exception as e:
                messagebox.showerror("Clear Error", str(e))