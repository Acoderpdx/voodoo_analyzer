"""
Main application UI for Plugin Parameter Discovery
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import json
import os
from pathlib import Path
import threading

from core import UniversalPluginDiscovery, ParameterCategorizer, ResearchValidator, DiscoveryExporter
from core.pattern_learner import PatternLearner
from core.validator_enhanced import EnhancedValidator
from core.learning_exporter import LearningExporter
from ui.components import ParameterInspector, LearningDashboard

class PluginAnalyzerApp:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Plugin Parameter Discovery - Stage 1")
        self.root.geometry("1200x800")
        
        # State
        self.current_plugin_path = None
        self.discovery_results = None
        self.categorized_results = None
        
        # Learning system
        self.pattern_learner = PatternLearner()
        self.learning_exporter = LearningExporter()
        self.all_discoveries = {}  # Store all discoveries for learning
        
        # Create UI
        self._create_menu()
        self._create_main_layout()
        
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Plugin", command=self.load_plugin)
        file_menu.add_command(label="Export Discovery", command=self.export_discovery)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate with Research", command=self.validate_discovery)
        tools_menu.add_command(label="Generate Test Matrix", command=self.generate_test_matrix)
        tools_menu.add_separator()
        tools_menu.add_command(label="Generate Learning Report", command=self.generate_learning_report)
        tools_menu.add_command(label="View Learning Stats", command=self.view_learning_stats)
    
    def _create_main_layout(self):
        """Create the main application layout"""
        # Create paned window
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Plugin browser and info
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Plugin info
        info_frame = ttk.LabelFrame(left_frame, text="Plugin Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.plugin_label = ttk.Label(info_frame, text="No plugin loaded")
        self.plugin_label.pack(padx=10, pady=5)
        
        # Plugin loading buttons
        load_frame = ttk.LabelFrame(left_frame, text="Load Plugin")
        load_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Manual path entry
        path_frame = ttk.Frame(load_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Plugin Path:").pack(side=tk.LEFT, padx=(0, 5))
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Add placeholder text
        self.path_entry.insert(0, "/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")
        
        load_btn = ttk.Button(path_frame, text="Load", 
                            command=self.load_from_entry)
        load_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Browse button - prominent
        browse_btn = ttk.Button(load_frame, text="Browse for Plugin...", 
                               command=lambda: self.load_plugin(),
                               style='Accent.TButton')
        browse_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Separator
        ttk.Separator(load_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)
        
        # Quick load section
        ttk.Label(load_frame, text="Quick Load:").pack(anchor=tk.W, padx=5)
        quick_frame = ttk.Frame(load_frame)
        quick_frame.pack(fill=tk.X, padx=5, pady=5)
        
        test_plugins = [
            ("VintageVerb", "/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3"),
            ("Plate", "/Library/Audio/Plug-Ins/VST3/ValhallaPlate.vst3"),
            ("Room", "/Library/Audio/Plug-Ins/VST3/ValhallaRoom.vst3"),
            ("Delay", "/Library/Audio/Plug-Ins/VST3/ValhallaDelay.vst3")
        ]
        
        for name, path in test_plugins:
            btn = ttk.Button(quick_frame, text=name, 
                           command=lambda p=path: self.load_plugin(p))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Discovery log
        log_frame = ttk.LabelFrame(left_frame, text="Discovery Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - Notebook with tabs
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # Create notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Parameter inspector tab
        self.param_inspector = ParameterInspector(self.notebook)
        self.notebook.add(self.param_inspector, text="Parameter Inspector")
        
        # Learning dashboard tab
        self.learning_dashboard = LearningDashboard(self.notebook)
        self.notebook.add(self.learning_dashboard, text="Learning Progress")
        
        # Bottom status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        
    def load_from_entry(self):
        """Load plugin from the path entry field"""
        plugin_path = self.path_entry.get().strip()
        if plugin_path:
            # Expand user path if needed
            plugin_path = os.path.expanduser(plugin_path)
            if os.path.exists(plugin_path):
                self.load_plugin(plugin_path)
            else:
                from tkinter import messagebox
                messagebox.showerror(
                    "Invalid Path",
                    f"Plugin not found at:\n{plugin_path}"
                )
        
    def load_plugin(self, plugin_path=None):
        """Load a plugin for discovery"""
        if not plugin_path:
            # Try to start in VST3 directory if it exists
            initial_dir = "/Library/Audio/Plug-Ins/VST3"
            if not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~/Library/Audio/Plug-Ins/VST3")
            if not os.path.exists(initial_dir):
                initial_dir = "/"
                
            # Use native macOS file dialog via osascript
            import subprocess
            import tempfile
            
            # Create AppleScript that allows bundle selection
            script = '''
            set startFolder to POSIX file "{}"
            set selectedFile to choose file of type {{}} ¬
                with prompt "Select a VST3, VST, or AU Plugin:" ¬
                default location startFolder ¬
                without invisibles and multiple selections allowed
            return POSIX path of selectedFile
            '''.format(initial_dir)
            
            try:
                # Write script to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
                    f.write(script)
                    script_path = f.name
                
                # Execute AppleScript
                result = subprocess.run(
                    ['osascript', script_path],
                    capture_output=True,
                    text=True
                )
                
                # Clean up temp file
                os.unlink(script_path)
                
                if result.returncode == 0:
                    plugin_path = result.stdout.strip()
                    if plugin_path:
                        print(f"Selected: {plugin_path}")
                        # Update the path entry field with the selected path
                        self.path_entry.delete(0, tk.END)
                        self.path_entry.insert(0, plugin_path)
                else:
                    plugin_path = None
                    
            except Exception as e:
                print(f"File selection error: {e}")
                # Fallback to askdirectory
                from tkinter import messagebox
                messagebox.showinfo(
                    "Select Plugin Bundle",
                    "Please navigate to the plugin and click 'Choose'"
                )
                plugin_path = filedialog.askdirectory(
                    title="Select Plugin Bundle",
                    initialdir=initial_dir
                )
        
        if not plugin_path:
            return
        
        self.current_plugin_path = plugin_path
        self.plugin_label.config(text=f"Plugin: {Path(plugin_path).name}")
        self.status_bar.config(text="Discovering parameters...")
        
        # Clear previous results
        self.log_text.delete(1.0, tk.END)
        self.param_inspector.clear()
        
        # Show progress
        self.progress.pack(side=tk.BOTTOM, fill=tk.X)
        self.progress.start()
        
        # Run discovery in thread
        thread = threading.Thread(target=self._run_discovery)
        thread.daemon = True
        thread.start()
    
    def _run_discovery(self):
        """Run parameter discovery in background thread"""
        try:
            # Create discovery instance
            discovery = UniversalPluginDiscovery(self.current_plugin_path)
            
            # Log updates
            def log_callback(msg):
                self.root.after(0, lambda: self.log_text.insert(tk.END, msg + "\n"))
                self.root.after(0, lambda: self.log_text.see(tk.END))
            
            # Discover parameters
            log_callback("Starting parameter discovery...")
            self.discovery_results = discovery.discover_all()
            
            # Apply pattern learning enhancement
            log_callback("\nApplying learned patterns...")
            enhanced_params = self.pattern_learner.enhance_discovery(self.discovery_results)
            
            # Validate parameters with enhanced validator
            log_callback("\nValidating parameter formats...")
            plugin = discovery.plugin
            validator = EnhancedValidator(plugin)
            validation_results = validator.validate_all_parameters(enhanced_params)
            
            # Log discovery process
            for log_entry in discovery.get_discovery_log():
                log_callback(log_entry)
            
            # Categorize parameters with intelligence
            log_callback("\nCategorizing parameters with effect knowledge...")
            categorizer = ParameterCategorizer()
            plugin_name = Path(self.current_plugin_path).stem
            self.categorized_results = categorizer.categorize_with_intelligence(plugin_name, enhanced_params)
            
            # Learn from this discovery
            log_callback("\nLearning from discovery...")
            learnings = self.pattern_learner.learn_from_discovery(plugin_name, enhanced_params)
            
            # Store discovery for learning report
            self.all_discoveries[plugin_name] = {
                'parameters': enhanced_params,
                'categorized': self.categorized_results,
                'validation_results': validation_results,
                'effect_type': learnings.get('effect_type'),
                'format_requirements': validation_results.get('format_requirements', {})
            }
            
            # Export individual discovery
            export_path = self.learning_exporter.export_individual_discovery(plugin_name, self.all_discoveries[plugin_name])
            log_callback(f"\nExported discovery to: {export_path}")
            
            # Update learning dashboard
            self.root.after(0, lambda: self.learning_dashboard.update_dashboard(learnings))
            
            # Update UI
            self.root.after(0, self._discovery_complete)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Discovery Error", error_msg))
        finally:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
    
    def _discovery_complete(self):
        """Handle discovery completion"""
        self.status_bar.config(text="Discovery complete")
        self.param_inspector.load_parameters(self.categorized_results)
        
        # Log summary
        self.log_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.log_text.insert(tk.END, "DISCOVERY SUMMARY\n")
        self.log_text.insert(tk.END, "="*50 + "\n")
        
        if self.discovery_results:
            total = len([k for k in self.discovery_results.keys() if not k.startswith('_')])
            self.log_text.insert(tk.END, f"Total parameters discovered: {total}\n")
            
            if self.categorized_results:
                for category, info in self.categorized_results['categories'].items():
                    count = len(info['parameters'])
                    self.log_text.insert(tk.END, f"{category}: {count} parameters\n")
                
                if self.categorized_results['uncategorized']:
                    count = len(self.categorized_results['uncategorized'])
                    self.log_text.insert(tk.END, f"Uncategorized: {count} parameters\n")
        
        self.log_text.see(tk.END)
    
    def validate_discovery(self):
        """Validate discovery against research data"""
        if not self.discovery_results:
            messagebox.showwarning("No Discovery", "Please load and discover a plugin first")
            return
        
        validator = ResearchValidator()
        plugin_name = Path(self.current_plugin_path).stem
        validation = validator.validate_discovery(plugin_name, self.discovery_results)
        
        # Show validation results
        result_window = tk.Toplevel(self.root)
        result_window.title("Validation Results")
        result_window.geometry("600x400")
        
        text = scrolledtext.ScrolledText(result_window)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, f"Plugin: {validation['plugin_name']}\n")
        text.insert(tk.END, f"Validation Score: {validation['validation_score']:.2%}\n\n")
        
        if validation['validation_score'] < 0:
            text.insert(tk.END, "No research data available for this plugin\n")
        else:
            text.insert(tk.END, f"Matched Parameters ({len(validation['matched_parameters'])}):\n")
            for param in validation['matched_parameters']:
                text.insert(tk.END, f"  ✓ {param}\n")
            
            if validation['missing_parameters']:
                text.insert(tk.END, f"\nMissing Parameters ({len(validation['missing_parameters'])}):\n")
                for param in validation['missing_parameters']:
                    text.insert(tk.END, f"  ✗ {param}\n")
            
            if validation['format_mismatches']:
                text.insert(tk.END, f"\nFormat Mismatches ({len(validation['format_mismatches'])}):\n")
                for mismatch in validation['format_mismatches']:
                    text.insert(tk.END, f"  ! {mismatch}\n")
    
    def generate_test_matrix(self):
        """Generate test matrix from categorized parameters"""
        if not self.categorized_results:
            messagebox.showwarning("No Discovery", "Please discover parameters first")
            return
        
        categorizer = ParameterCategorizer()
        test_matrix = categorizer.generate_test_matrix(self.categorized_results)
        
        # Show test matrix
        matrix_window = tk.Toplevel(self.root)
        matrix_window.title("Test Matrix")
        matrix_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(matrix_window)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, "GENERATED TEST MATRIX\n")
        text.insert(tk.END, "="*40 + "\n\n")
        
        for phase, tests in test_matrix.items():
            if tests:
                text.insert(tk.END, f"{phase}:\n")
                for test in tests:
                    text.insert(tk.END, f"  • {test}\n")
                text.insert(tk.END, "\n")
    
    def export_discovery(self):
        """Export discovery results"""
        if not self.discovery_results:
            messagebox.showwarning("No Discovery", "Please discover parameters first")
            return
        
        # Validate first
        validator = ResearchValidator()
        plugin_name = Path(self.current_plugin_path).stem
        validation = validator.validate_discovery(plugin_name, self.discovery_results)
        
        # Generate test matrix
        categorizer = ParameterCategorizer()
        test_matrix = categorizer.generate_test_matrix(self.categorized_results)
        
        # Export
        exporter = DiscoveryExporter()
        export_path = exporter.export_to_json(
            plugin_name,
            self.discovery_results,
            self.categorized_results,
            test_matrix,
            validation
        )
        
        messagebox.showinfo("Export Complete", f"Discovery exported to:\n{export_path}")
    
    def generate_learning_report(self):
        """Generate comprehensive learning report"""
        if not self.all_discoveries:
            messagebox.showinfo("No Data", "No plugins have been analyzed yet")
            return
        
        # Generate report
        report_path = self.learning_exporter.export_learning_report(self.all_discoveries)
        
        # Also generate markdown report
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        md_path = self.learning_exporter.create_markdown_report(report_data)
        
        messagebox.showinfo("Report Generated", 
                          f"Learning report generated:\n\nJSON: {report_path}\nMarkdown: {md_path}")
    
    def view_learning_stats(self):
        """View current learning statistics"""
        stats = self.pattern_learner.get_learning_stats()
        
        # Create stats window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Learning Statistics")
        stats_window.geometry("400x300")
        
        text = scrolledtext.ScrolledText(stats_window)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, "PATTERN LEARNING STATISTICS\n")
        text.insert(tk.END, "="*40 + "\n\n")
        
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            text.insert(tk.END, f"{formatted_key}: {value}\n")
        
        # Add recent discoveries
        if self.pattern_learner.learned_patterns.get('plugin_history'):
            text.insert(tk.END, "\n\nRecent Plugin Discoveries:\n")
            text.insert(tk.END, "-"*40 + "\n")
            for plugin, info in list(self.pattern_learner.learned_patterns['plugin_history'].items())[-5:]:
                text.insert(tk.END, f"• {plugin}: {info['parameter_count']} parameters\n")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PluginAnalyzerApp()
    app.run()