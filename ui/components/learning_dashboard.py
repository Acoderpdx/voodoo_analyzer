"""
Dashboard to show learning progress and patterns
"""
import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from typing import Dict, Optional

class LearningDashboard(ttk.Frame):
    """Display learning progress and discovered patterns"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_learning_data()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Pattern Learning Progress", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=(0, 10))
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self._create_stats_view()
        
        # Patterns tab
        self.patterns_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.patterns_frame, text="Learned Patterns")
        self._create_patterns_view()
        
        # Insights tab
        self.insights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.insights_frame, text="Insights")
        self._create_insights_view()
    
    def _create_stats_view(self):
        """Create statistics view"""
        # Stats container
        stats_container = ttk.Frame(self.stats_frame, padding="10")
        stats_container.pack(fill='both', expand=True)
        
        # Overall statistics frame
        overall_frame = ttk.LabelFrame(stats_container, text="Overall Progress", padding="10")
        overall_frame.pack(fill='x', pady=(0, 10))
        
        self.stats_labels = {}
        stats_items = [
            ('plugins_analyzed', 'Plugins Analyzed:'),
            ('total_parameters', 'Total Parameters:'),
            ('patterns_learned', 'Patterns Learned:'),
            ('effect_types', 'Effect Types Identified:'),
            ('validation_rate', 'Validation Success Rate:')
        ]
        
        for i, (key, label) in enumerate(stats_items):
            ttk.Label(overall_frame, text=label).grid(row=i, column=0, sticky='w', padx=(0, 10))
            self.stats_labels[key] = ttk.Label(overall_frame, text="0", font=('Arial', 10, 'bold'))
            self.stats_labels[key].grid(row=i, column=1, sticky='w')
        
        # Recent discoveries frame
        recent_frame = ttk.LabelFrame(stats_container, text="Recent Discoveries", padding="10")
        recent_frame.pack(fill='both', expand=True)
        
        # Create text widget for recent discoveries
        self.recent_text = tk.Text(recent_frame, height=10, width=60, wrap='word')
        self.recent_text.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, command=self.recent_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.recent_text.config(yscrollcommand=scrollbar.set)
    
    def _create_patterns_view(self):
        """Create patterns view with treeview"""
        patterns_container = ttk.Frame(self.patterns_frame, padding="10")
        patterns_container.pack(fill='both', expand=True)
        
        # Pattern tree
        columns = ('Type', 'Count', 'Examples')
        self.pattern_tree = ttk.Treeview(patterns_container, columns=columns, show='tree headings')
        
        # Configure columns
        self.pattern_tree.heading('#0', text='Pattern Category')
        self.pattern_tree.heading('Type', text='Type')
        self.pattern_tree.heading('Count', text='Count')
        self.pattern_tree.heading('Examples', text='Examples')
        
        self.pattern_tree.column('#0', width=200)
        self.pattern_tree.column('Type', width=150)
        self.pattern_tree.column('Count', width=80)
        self.pattern_tree.column('Examples', width=300)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(patterns_container, orient='vertical', command=self.pattern_tree.yview)
        x_scroll = ttk.Scrollbar(patterns_container, orient='horizontal', command=self.pattern_tree.xview)
        self.pattern_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Pack elements
        self.pattern_tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        patterns_container.grid_rowconfigure(0, weight=1)
        patterns_container.grid_columnconfigure(0, weight=1)
    
    def _create_insights_view(self):
        """Create insights view"""
        insights_container = ttk.Frame(self.insights_frame, padding="10")
        insights_container.pack(fill='both', expand=True)
        
        # Insights text
        self.insights_text = tk.Text(insights_container, height=20, width=70, wrap='word')
        self.insights_text.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(insights_container, command=self.insights_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.insights_text.config(yscrollcommand=scrollbar.set)
        
        # Configure text tags for formatting
        self.insights_text.tag_configure('heading', font=('Arial', 12, 'bold'))
        self.insights_text.tag_configure('subheading', font=('Arial', 10, 'bold'))
        self.insights_text.tag_configure('highlight', foreground='blue')
    
    def load_learning_data(self):
        """Load and display learning data"""
        patterns_file = Path('data/learned_patterns.json')
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    self._update_from_patterns(data)
            except Exception as e:
                print(f"Error loading patterns: {e}")
        
        # Load latest report if available
        report_file = Path('data/discoveries/learning_report_latest.json')
        if report_file.exists():
            try:
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    self._update_from_report(report)
            except Exception as e:
                print(f"Error loading report: {e}")
    
    def _update_from_patterns(self, patterns: Dict):
        """Update display from patterns data"""
        # Update stats
        if 'plugin_history' in patterns:
            self.stats_labels['plugins_analyzed'].config(text=str(len(patterns['plugin_history'])))
        
        if 'string_formats' in patterns:
            self.stats_labels['patterns_learned'].config(
                text=str(len(patterns['string_formats']) + 
                        len(patterns.get('parameter_patterns', {})) +
                        len(patterns.get('range_patterns', {})))
            )
        
        if 'effect_signatures' in patterns:
            self.stats_labels['effect_types'].config(text=str(len(patterns['effect_signatures'])))
        
        # Update pattern tree
        self.pattern_tree.delete(*self.pattern_tree.get_children())
        
        # Add string formats
        if patterns.get('string_formats'):
            formats_node = self.pattern_tree.insert('', 'end', text='String Formats', 
                                                   values=('Format Patterns', 
                                                          len(patterns['string_formats']), ''))
            for param, fmt in list(patterns['string_formats'].items())[:5]:
                self.pattern_tree.insert(formats_node, 'end', text=param,
                                       values=('string', 1, fmt))
        
        # Add parameter patterns
        if patterns.get('parameter_patterns'):
            param_node = self.pattern_tree.insert('', 'end', text='Parameter Patterns',
                                                values=('Recognition Patterns',
                                                       len(patterns['parameter_patterns']), ''))
            for pattern, category in list(patterns['parameter_patterns'].items())[:5]:
                self.pattern_tree.insert(param_node, 'end', text=pattern,
                                       values=('regex', 1, category))
        
        # Add effect signatures
        if patterns.get('effect_signatures'):
            effect_node = self.pattern_tree.insert('', 'end', text='Effect Types',
                                                 values=('Plugin Classifications',
                                                        len(patterns['effect_signatures']), ''))
            for plugin, effect in list(patterns['effect_signatures'].items())[:5]:
                self.pattern_tree.insert(effect_node, 'end', text=plugin,
                                       values=('effect', 1, effect))
    
    def _update_from_report(self, report: Dict):
        """Update display from learning report"""
        # Update statistics
        if 'parameter_statistics' in report:
            stats = report['parameter_statistics']
            self.stats_labels['total_parameters'].config(
                text=str(stats.get('total_parameters_discovered', 0))
            )
            self.stats_labels['validation_rate'].config(
                text=f"{stats.get('validation_success_rate', 0):.1f}%"
            )
        
        # Update insights
        self.insights_text.delete(1.0, tk.END)
        
        if 'learning_insights' in report:
            for insight in report['learning_insights']:
                self.insights_text.insert(tk.END, f"{insight['title']}\n", 'heading')
                
                if isinstance(insight['data'], dict):
                    for key, value in insight['data'].items():
                        self.insights_text.insert(tk.END, f"  • {key}: {value}\n")
                
                self.insights_text.insert(tk.END, "\n")
    
    def update_dashboard(self, learning_data: Dict):
        """Update dashboard with new learning data"""
        # Update stats
        if 'new_patterns' in learning_data:
            current = self.stats_labels['patterns_learned'].cget('text')
            try:
                current_count = int(current)
                new_count = current_count + learning_data['new_patterns']
                self.stats_labels['patterns_learned'].config(text=str(new_count))
            except:
                pass
        
        # Add to recent discoveries
        if 'effect_type' in learning_data:
            discovery_text = f"Effect Type: {learning_data['effect_type']}\n"
            discovery_text += f"New Patterns: {learning_data.get('new_patterns', 0)}\n"
            discovery_text += f"Confirmed: {learning_data.get('confirmed_patterns', 0)}\n"
            
            if learning_data.get('anomalies'):
                discovery_text += f"Anomalies: {len(learning_data['anomalies'])}\n"
            
            discovery_text += "-" * 40 + "\n"
            
            self.recent_text.insert(1.0, discovery_text)
            
            # Limit text size
            lines = self.recent_text.get(1.0, tk.END).split('\n')
            if len(lines) > 100:
                self.recent_text.delete('100.0', tk.END)
        
        # Reload full data
        self.load_learning_data()
    
    def refresh(self):
        """Refresh the dashboard display"""
        self.load_learning_data()