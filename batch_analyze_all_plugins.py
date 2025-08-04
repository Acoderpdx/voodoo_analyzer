#!/usr/bin/env python3
"""
Batch Plugin Analyzer - Automatically analyze all VST, VST3, and AU plugins
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import UniversalPluginDiscovery, ParameterCategorizer
from core.pattern_learner import PatternLearner
from core.validator_enhanced import EnhancedValidator
from core.learning_exporter import LearningExporter


class BatchPluginAnalyzer:
    """Analyze all plugins in standard directories"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.pattern_learner = PatternLearner()
        self.learning_exporter = LearningExporter()
        self.categorizer = ParameterCategorizer()
        
        # Statistics
        self.stats = {
            'total_plugins': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_parameters': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Results storage
        self.all_results = {}
        self.failed_plugins = []
        
        # Thread lock for shared data
        self.lock = threading.Lock()
        
    def get_plugin_directories(self):
        """Get standard plugin directories for macOS"""
        dirs = []
        
        # System-wide locations
        system_dirs = [
            "/Library/Audio/Plug-Ins/VST",
            "/Library/Audio/Plug-Ins/VST3",
            "/Library/Audio/Plug-Ins/Components",  # AU plugins
        ]
        
        # User-specific locations
        home = os.path.expanduser("~")
        user_dirs = [
            f"{home}/Library/Audio/Plug-Ins/VST",
            f"{home}/Library/Audio/Plug-Ins/VST3",
            f"{home}/Library/Audio/Plug-Ins/Components",
        ]
        
        # Check which directories exist
        for d in system_dirs + user_dirs:
            if os.path.exists(d):
                dirs.append(d)
                
        return dirs
    
    def find_all_plugins(self, directories=None):
        """Find all plugin files in given directories"""
        if directories is None:
            directories = self.get_plugin_directories()
            
        plugins = []
        
        for directory in directories:
            print(f"\nScanning: {directory}")
            
            for root, dirs, files in os.walk(directory):
                # For VST3 and AU, we want the bundle directory
                for d in dirs:
                    if d.endswith('.vst3') or d.endswith('.component'):
                        plugin_path = os.path.join(root, d)
                        plugins.append({
                            'path': plugin_path,
                            'name': Path(d).stem,
                            'type': 'vst3' if d.endswith('.vst3') else 'au'
                        })
                
                # For VST2, we want .vst bundles or .dll files
                for d in dirs:
                    if d.endswith('.vst'):
                        plugin_path = os.path.join(root, d)
                        plugins.append({
                            'path': plugin_path,
                            'name': Path(d).stem,
                            'type': 'vst'
                        })
                        
                # Some VST2 might be .dll files
                for f in files:
                    if f.endswith('.dll'):
                        plugin_path = os.path.join(root, f)
                        plugins.append({
                            'path': plugin_path,
                            'name': Path(f).stem,
                            'type': 'vst'
                        })
        
        # Remove duplicates
        seen = set()
        unique_plugins = []
        for p in plugins:
            if p['path'] not in seen:
                seen.add(p['path'])
                unique_plugins.append(p)
                
        return unique_plugins
    
    def analyze_plugin(self, plugin_info):
        """Analyze a single plugin"""
        plugin_path = plugin_info['path']
        plugin_name = plugin_info['name']
        
        print(f"\n{'='*60}")
        print(f"Analyzing: {plugin_name}")
        print(f"Path: {plugin_path}")
        print(f"Type: {plugin_info['type'].upper()}")
        
        try:
            # Create discovery instance
            discovery = UniversalPluginDiscovery(plugin_path)
            
            # Discover parameters
            print("  Discovering parameters...")
            parameters = discovery.discover_all()
            
            if not parameters or all(k.startswith('_') for k in parameters.keys()):
                print("  ⚠️  No parameters discovered")
                return None
            
            # Apply pattern learning
            print("  Applying learned patterns...")
            enhanced_params = self.pattern_learner.enhance_discovery(parameters)
            
            # Validate parameters
            print("  Validating parameters...")
            validator = EnhancedValidator(discovery.plugin)
            validation_results = validator.validate_all_parameters(enhanced_params)
            
            # Categorize parameters
            print("  Categorizing parameters...")
            categorized = self.categorizer.categorize_with_intelligence(plugin_name, enhanced_params)
            
            # Learn from discovery
            print("  Learning from discovery...")
            learnings = self.pattern_learner.learn_from_discovery(plugin_name, enhanced_params)
            
            # Count parameters
            param_count = len([k for k in enhanced_params.keys() if not k.startswith('_')])
            print(f"  ✅ Success: {param_count} parameters discovered")
            
            return {
                'plugin_name': plugin_name,
                'plugin_path': plugin_path,
                'plugin_type': plugin_info['type'],
                'parameter_count': param_count,
                'parameters': enhanced_params,
                'categorized': categorized,
                'validation': validation_results,
                'learnings': learnings,
                'discovery_log': discovery.get_discovery_log()
            }
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return {
                'plugin_name': plugin_name,
                'plugin_path': plugin_path,
                'plugin_type': plugin_info['type'],
                'error': str(e),
                'failed': True
            }
    
    def analyze_all_plugins(self, directories=None, skip_analyzed=True):
        """Analyze all plugins in parallel"""
        print("\n🔍 BATCH PLUGIN ANALYZER")
        print("========================\n")
        
        # Find all plugins
        print("Searching for plugins...")
        plugins = self.find_all_plugins(directories)
        
        if not plugins:
            print("No plugins found!")
            return
        
        print(f"\nFound {len(plugins)} plugins to analyze")
        
        # Check for existing results if skip_analyzed is True
        existing_results = {}
        if skip_analyzed and os.path.exists('exports/batch_analysis_results.json'):
            try:
                with open('exports/batch_analysis_results.json', 'r') as f:
                    existing_data = json.load(f)
                    existing_results = existing_data.get('plugins', {})
                    print(f"Found {len(existing_results)} previously analyzed plugins")
            except:
                pass
        
        # Filter plugins to analyze
        plugins_to_analyze = []
        for p in plugins:
            if skip_analyzed and p['name'] in existing_results:
                print(f"  Skipping {p['name']} (already analyzed)")
                self.stats['skipped'] += 1
                # Include existing results
                self.all_results[p['name']] = existing_results[p['name']]
            else:
                plugins_to_analyze.append(p)
        
        if not plugins_to_analyze:
            print("\nAll plugins already analyzed!")
            return
        
        print(f"\nAnalyzing {len(plugins_to_analyze)} new plugins...")
        
        self.stats['total_plugins'] = len(plugins)
        self.stats['start_time'] = time.time()
        
        # Analyze in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_plugin = {
                executor.submit(self.analyze_plugin, plugin): plugin 
                for plugin in plugins_to_analyze
            }
            
            # Process completed tasks
            for future in as_completed(future_to_plugin):
                plugin = future_to_plugin[future]
                try:
                    result = future.result()
                    
                    with self.lock:
                        if result:
                            if result.get('failed'):
                                self.stats['failed'] += 1
                                self.failed_plugins.append({
                                    'name': plugin['name'],
                                    'path': plugin['path'],
                                    'error': result.get('error', 'Unknown error')
                                })
                            else:
                                self.stats['successful'] += 1
                                if result.get('parameter_count', 0) > 0:
                                    self.stats['total_parameters'] += result['parameter_count']
                                    self.all_results[plugin['name']] = result
                                    
                except Exception as e:
                    print(f"\nUnexpected error analyzing {plugin['name']}: {e}")
                    with self.lock:
                        self.stats['failed'] += 1
                        self.failed_plugins.append({
                            'name': plugin['name'],
                            'path': plugin['path'],
                            'error': str(e)
                        })
        
        self.stats['end_time'] = time.time()
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary()
    
    def save_results(self):
        """Save all results to files"""
        print("\n💾 Saving results...")
        
        # Create exports directory
        os.makedirs('exports', exist_ok=True)
        
        # Save main results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Comprehensive JSON report
        report = {
            'metadata': {
                'timestamp': timestamp,
                'stats': self.stats,
                'duration_seconds': self.stats['end_time'] - self.stats['start_time'] if self.stats['end_time'] else 0
            },
            'plugins': self.all_results,
            'failed_plugins': self.failed_plugins,
            'learning_stats': self.pattern_learner.get_learning_stats()
        }
        
        # Save main report
        report_path = f'exports/batch_analysis_results.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  ✅ Full report: {report_path}")
        
        # Save timestamped backup
        backup_path = f'exports/batch_analysis_{timestamp}.json'
        with open(backup_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  ✅ Backup: {backup_path}")
        
        # Generate parameter summary CSV
        self.generate_parameter_csv(timestamp)
        
        # Generate markdown report
        self.generate_markdown_report(timestamp)
        
        # Save learned patterns
        self.pattern_learner.save_patterns()
        print(f"  ✅ Learned patterns updated")
    
    def generate_parameter_csv(self, timestamp):
        """Generate CSV with all parameters"""
        csv_path = f'exports/all_parameters_{timestamp}.csv'
        
        with open(csv_path, 'w') as f:
            # Header
            f.write("Plugin,Parameter,Type,Min,Max,Default,Unit,Category\n")
            
            # Data
            for plugin_name, data in self.all_results.items():
                if 'parameters' in data:
                    categorized = data.get('categorized', {})
                    categories = categorized.get('categories', {})
                    
                    # Build parameter to category mapping
                    param_to_category = {}
                    for cat_name, cat_info in categories.items():
                        for param in cat_info.get('parameters', []):
                            param_to_category[param] = cat_name
                    
                    # Write parameters
                    for param_name, param_info in data['parameters'].items():
                        if param_name.startswith('_'):
                            continue
                            
                        param_type = param_info.get('type', 'unknown')
                        min_val = param_info.get('min', '')
                        max_val = param_info.get('max', '')
                        default = param_info.get('default', '')
                        unit = param_info.get('unit', '')
                        category = param_to_category.get(param_name, 'uncategorized')
                        
                        # Escape commas in values
                        plugin_name_escaped = plugin_name.replace(',', ';')
                        param_name_escaped = param_name.replace(',', ';')
                        
                        f.write(f"{plugin_name_escaped},{param_name_escaped},{param_type},{min_val},{max_val},{default},{unit},{category}\n")
        
        print(f"  ✅ Parameter CSV: {csv_path}")
    
    def generate_markdown_report(self, timestamp):
        """Generate readable markdown report"""
        md_path = f'exports/batch_analysis_report_{timestamp}.md'
        
        with open(md_path, 'w') as f:
            f.write("# Batch Plugin Analysis Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Plugins Found**: {self.stats['total_plugins']}\n")
            f.write(f"- **Successfully Analyzed**: {self.stats['successful']}\n")
            f.write(f"- **Failed**: {self.stats['failed']}\n")
            f.write(f"- **Skipped**: {self.stats['skipped']}\n")
            f.write(f"- **Total Parameters Discovered**: {self.stats['total_parameters']}\n")
            
            if self.stats['end_time'] and self.stats['start_time']:
                duration = self.stats['end_time'] - self.stats['start_time']
                f.write(f"- **Analysis Duration**: {duration:.1f} seconds\n")
            
            f.write("\n## Successfully Analyzed Plugins\n\n")
            
            # Sort by parameter count
            sorted_plugins = sorted(
                [(k, v) for k, v in self.all_results.items() if not v.get('failed')],
                key=lambda x: x[1].get('parameter_count', 0),
                reverse=True
            )
            
            for plugin_name, data in sorted_plugins:
                param_count = data.get('parameter_count', 0)
                plugin_type = data.get('plugin_type', 'unknown').upper()
                f.write(f"### {plugin_name} ({plugin_type})\n")
                f.write(f"- Parameters: {param_count}\n")
                
                # Show categorized breakdown
                if 'categorized' in data:
                    categories = data['categorized'].get('categories', {})
                    if categories:
                        f.write("- Categories:\n")
                        for cat_name, cat_info in categories.items():
                            cat_count = len(cat_info.get('parameters', []))
                            f.write(f"  - {cat_name}: {cat_count}\n")
                
                f.write("\n")
            
            # Failed plugins
            if self.failed_plugins:
                f.write("\n## Failed Plugins\n\n")
                for failed in self.failed_plugins:
                    f.write(f"- **{failed['name']}**\n")
                    f.write(f"  - Path: {failed['path']}\n")
                    f.write(f"  - Error: {failed['error']}\n\n")
            
            # Learning insights
            f.write("\n## Learning Insights\n\n")
            stats = self.pattern_learner.get_learning_stats()
            f.write(f"- Total Plugins Analyzed: {stats.get('total_plugins_analyzed', 0)}\n")
            f.write(f"- Parameter Patterns Learned: {stats.get('total_parameter_patterns', 0)}\n")
            f.write(f"- String Formats Discovered: {stats.get('total_string_formats', 0)}\n")
            f.write(f"- Effect Types Identified: {stats.get('total_effect_types', 0)}\n")
        
        print(f"  ✅ Markdown report: {md_path}")
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("📊 ANALYSIS COMPLETE")
        print("="*60)
        
        print(f"\nTotal plugins found: {self.stats['total_plugins']}")
        print(f"Successfully analyzed: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Skipped (already analyzed): {self.stats['skipped']}")
        print(f"\nTotal parameters discovered: {self.stats['total_parameters']}")
        
        if self.stats['successful'] > 0:
            avg_params = self.stats['total_parameters'] / self.stats['successful']
            print(f"Average parameters per plugin: {avg_params:.1f}")
        
        if self.stats['end_time'] and self.stats['start_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            print(f"\nTotal time: {duration:.1f} seconds")
            
            if self.stats['successful'] > 0:
                avg_time = duration / (self.stats['successful'] + self.stats['failed'])
                print(f"Average time per plugin: {avg_time:.1f} seconds")
        
        # Top plugins by parameter count
        if self.all_results:
            print("\n🏆 Top 5 Plugins by Parameter Count:")
            sorted_plugins = sorted(
                [(k, v) for k, v in self.all_results.items() if not v.get('failed')],
                key=lambda x: x[1].get('parameter_count', 0),
                reverse=True
            )[:5]
            
            for plugin_name, data in sorted_plugins:
                count = data.get('parameter_count', 0)
                print(f"  - {plugin_name}: {count} parameters")
        
        print("\n✅ Results saved to exports/ directory")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Batch analyze all VST/VST3/AU plugins')
    parser.add_argument('--dirs', nargs='+', help='Additional directories to scan')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers (default: 4)')
    parser.add_argument('--no-skip', action='store_true', help='Re-analyze all plugins (don\'t skip existing)')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = BatchPluginAnalyzer(max_workers=args.workers)
    
    # Run analysis
    analyzer.analyze_all_plugins(
        directories=args.dirs,
        skip_analyzed=not args.no_skip
    )


if __name__ == '__main__':
    main()