"""
Enhanced History viewer component for displaying all analyzed plugins and their data
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from pathlib import Path
from datetime import datetime
import re

class HistoryViewer(tk.Toplevel):
    """Window for viewing complete analysis history"""
    
    def __init__(self, parent, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.title("Analysis History - Complete View")
        self.geometry("1200x800")
        
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
        title_label = ttk.Label(main_frame, text="Complete Plugin Analysis History", 
                               font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Plugin list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Plugin list header
        list_header = ttk.Label(left_frame, text="All Analyzed Plugins", 
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
        ttk.Button(button_frame, text="Generate Full Report", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", 
                  command=self.destroy).pack(side=tk.RIGHT)
        
    def load_history(self):
        """Load all plugin analysis history including errors"""
        self.plugin_listbox.delete(0, tk.END)
        self.plugin_data = {}
        self.failed_files = []
        
        # First, add current session discoveries from app instance if available
        if self.app_instance and hasattr(self.app_instance, 'all_discoveries'):
            for plugin_name, discovery_data in self.app_instance.all_discoveries.items():
                display_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                params = discovery_data.get('parameters', {})
                if isinstance(params, dict):
                    param_count = len([k for k in params.keys() if not k.startswith('_')])
                else:
                    param_count = 0
                    
                display_str = f"{plugin_name} (Current Session) - {param_count} params"
                
                self.plugin_listbox.insert(tk.END, display_str)
                self.plugin_data[display_str] = {
                    'name': plugin_name,
                    'timestamp': display_time,
                    'file_path': 'In Memory',
                    'data': discovery_data,
                    'source': 'session'
                }
        
        # Load ALL files from disk
        if self.discoveries_dir.exists():
            # Get ALL JSON files
            all_files = list(self.discoveries_dir.glob("*.json"))
            
            for file_path in sorted(all_files, key=lambda x: x.stat().st_mtime, reverse=True):
                filename = file_path.stem
                
                # Try to extract plugin name
                if '_enhanced_' in filename:
                    parts = filename.rsplit('_enhanced_', 1)
                    plugin_name = parts[0]
                    timestamp_str = parts[1] if len(parts) == 2 else 'unknown'
                else:
                    plugin_name = filename
                    timestamp_str = 'unknown'
                
                # Get file modification time
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                display_time = file_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Try to load the file
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Try to parse JSON
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as je:
                        # Try to fix common JSON errors
                        fixed_content = re.sub(r',\s*([}\]])', r'\\1', content)
                        try:
                            data = json.loads(fixed_content)
                        except:
                            # If still fails, create error entry
                            raise je
                    
                    # Count parameters
                    params = data.get('parameters', {})
                    if isinstance(params, dict):
                        param_count = len([k for k in params.keys() if not k.startswith('_')])
                    else:
                        param_count = 0
                    
                    # Handle nested structure if present
                    if 'discovery' in data and 'parameters' in data['discovery']:
                        params = data['discovery']['parameters']
                        param_count = len([k for k in params.keys() if not k.startswith('_')])
                        data['parameters'] = params  # Normalize structure
                    
                    display_str = f"{plugin_name} ({display_time}) - {param_count} params"
                    
                    # Add to listbox
                    self.plugin_listbox.insert(tk.END, display_str)
                    
                    # Store data
                    self.plugin_data[display_str] = {
                        'name': plugin_name,
                        'timestamp': display_time,
                        'file_path': str(file_path),
                        'data': data,
                        'source': 'file'
                    }
                    
                except Exception as e:
                    # Add failed file info
                    self.failed_files.append({
                        'path': str(file_path),
                        'name': plugin_name,
                        'error': str(e),
                        'time': display_time
                    })
                    
                    # Still add to list but mark as error
                    display_str = f"{plugin_name} ({display_time}) - [ERROR: {type(e).__name__}]"
                    
                    self.plugin_listbox.insert(tk.END, display_str)
                    self.plugin_data[display_str] = {
                        'name': plugin_name,
                        'timestamp': display_time,
                        'file_path': str(file_path),
                        'data': {'error': str(e), 'error_type': type(e).__name__},
                        'source': 'error'
                    }
        
        # Update statistics
        self.update_stats()
        
    def update_stats(self):
        """Update statistics display"""
        total_analyses = len(self.plugin_data)
        unique_plugins = len(set(p['name'] for p in self.plugin_data.values()))
        
        # Count by source
        session_count = len([p for p in self.plugin_data.values() if p.get('source') == 'session'])
        file_count = len([p for p in self.plugin_data.values() if p.get('source') == 'file'])
        error_count = len([p for p in self.plugin_data.values() if p.get('source') == 'error'])
        
        # Count total parameters discovered
        total_params = 0
        for p in self.plugin_data.values():
            if p.get('source') != 'error' and 'parameters' in p['data']:
                params = p['data']['parameters']
                if isinstance(params, dict):
                    total_params += len([k for k in params.keys() if not k.startswith('_')])
        
        stats_text = f"Total Analyses: {total_analyses}\\n"
        stats_text += f"Unique Plugins: {unique_plugins}\\n"
        stats_text += f"Total Parameters: {total_params}\\n\\n"
        stats_text += f"Current Session: {session_count}\\n"
        stats_text += f"From Files: {file_count}\\n"
        
        if error_count > 0:
            stats_text += f"Failed to Load: {error_count}\\n"
        
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
        overview += f"File: {plugin_info['file_path']}\\n"
        overview += f"Source: {plugin_info['source']}\\n\\n"
        
        if plugin_info['source'] == 'error':
            overview += f"ERROR: {plugin_data.get('error', 'Unknown error')}\\n"
            overview += f"Error Type: {plugin_data.get('error_type', 'Unknown')}\\n"
        else:
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
        if plugin_info['source'] != 'error' and 'parameters' in plugin_data:
            params_text = "DISCOVERED PARAMETERS:\\n\\n"
            params = plugin_data['parameters']
            
            if isinstance(params, dict):
                sorted_params = sorted(params.items())
                for param_name, param_info in sorted_params:
                    if not param_name.startswith('_') and isinstance(param_info, dict):
                        params_text += f"{param_name}:\\n"
                        for key, value in param_info.items():
                            params_text += f"  {key}: {value}\\n"
                        params_text += "\\n"
            else:
                params_text += "Invalid parameter format\\n"
                    
            self.params_text.insert(1.0, params_text)
            
        # Update categories
        self.categories_text.delete(1.0, tk.END)
        if 'categorized' in plugin_data:
            categories = plugin_data['categorized']
            cat_text = "PARAMETER CATEGORIES:\\n\\n"
            
            if isinstance(categories, dict) and 'categories' in categories:
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
        if plugin_info['source'] == 'error':
            self.raw_text.insert(1.0, f"File: {plugin_info['file_path']}\\n\\nError loading file:\\n{plugin_data.get('error', 'Unknown error')}")
        else:
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
                export_data = {
                    'export_date': datetime.now().isoformat(),
                    'plugin_info': plugin_info
                }
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                messagebox.showinfo("Export Complete", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
                
    def export_all(self):
        """Export all history data"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="complete_plugin_history.json"
        )
        
        if filename:
            try:
                export_data = {
                    'export_date': datetime.now().isoformat(),
                    'total_analyses': len(self.plugin_data),
                    'failed_files': self.failed_files,
                    'plugins': {}
                }
                
                # Organize by plugin name
                for display_str, info in self.plugin_data.items():
                    plugin_name = info['name']
                    if plugin_name not in export_data['plugins']:
                        export_data['plugins'][plugin_name] = []
                    
                    export_data['plugins'][plugin_name].append({
                        'timestamp': info['timestamp'],
                        'source': info['source'],
                        'file_path': info['file_path'],
                        'data': info['data']
                    })
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
                messagebox.showinfo("Export Complete", 
                                  f"Exported {len(self.plugin_data)} analyses to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
                
    def generate_report(self):
        """Generate comprehensive analysis report"""
        try:
            import subprocess
            script_path = Path(__file__).parent.parent.parent / "generate_full_analysis_report.py"
            
            result = subprocess.run(
                ['/opt/anaconda3/bin/python', str(script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                report_path = self.data_dir / "comprehensive_analysis_report.md"
                messagebox.showinfo("Report Generated", 
                                  f"Comprehensive report generated:\\n{report_path}")
            else:
                messagebox.showerror("Report Error", result.stderr)
                
        except Exception as e:
            messagebox.showerror("Report Error", str(e))