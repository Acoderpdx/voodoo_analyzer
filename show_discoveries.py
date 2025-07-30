#!/usr/bin/env python3
"""
Show all discovered plugin parameters
"""

import json
import os
from pathlib import Path
from datetime import datetime

def show_all_discoveries():
    """Display all discovered plugin data"""
    print("="*60)
    print("🔍 PLUGIN DISCOVERY RESULTS")
    print("="*60)
    
    # Check different locations for discovery files
    locations = [
        Path("."),  # Current directory
        Path("data/discoveries"),  # Export directory
    ]
    
    discovery_files = []
    for location in locations:
        if location.exists():
            discovery_files.extend(location.glob("*.json"))
    
    # Filter for discovery-related files
    plugin_files = [f for f in discovery_files if any(x in f.name.lower() for x in ['discovery', 'param', 'valhalla', 'export'])]
    
    if not plugin_files:
        print("No discovery files found yet.")
        print("\nTo create discoveries:")
        print("1. Run the Plugin Analyzer UI")
        print("2. Load a plugin")
        print("3. Use File → Export Discovery")
        return
    
    for file_path in sorted(plugin_files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract plugin info
            plugin_name = (data.get('plugin') or 
                          data.get('metadata', {}).get('plugin_name') or 
                          file_path.stem)
            
            print(f"\n📦 Plugin: {plugin_name}")
            print(f"   File: {file_path.name}")
            
            # Show parameters
            params = data.get('parameters', {})
            if params:
                # Remove metadata entries
                param_list = [(k, v) for k, v in params.items() if not k.startswith('_')]
                
                print(f"   Parameters found: {len(param_list)}")
                print("\n   Parameter Details:")
                
                # Group by type
                by_type = {}
                for param_name, param_info in param_list:
                    if isinstance(param_info, dict):
                        param_type = param_info.get('type', 'unknown')
                        if param_type not in by_type:
                            by_type[param_type] = []
                        by_type[param_type].append((param_name, param_info))
                
                # Display by type
                for param_type, params_of_type in by_type.items():
                    print(f"\n   {param_type.upper()} Parameters ({len(params_of_type)}):")
                    for param_name, param_info in sorted(params_of_type)[:10]:  # Show first 10
                        value = param_info.get('current_value', 'N/A')
                        if param_info.get('range'):
                            range_str = f" [{param_info['range'][0]}-{param_info['range'][1]}]"
                        else:
                            range_str = ""
                        unit = param_info.get('unit', '')
                        if unit:
                            unit = f" {unit}"
                        print(f"      - {param_name}: {value}{unit}{range_str}")
                    
                    if len(params_of_type) > 10:
                        print(f"      ... and {len(params_of_type) - 10} more")
            
            # Show categories if available
            categories = data.get('categorized', {}).get('categories', {})
            if categories:
                print("\n   Categories:")
                for cat, params in categories.items():
                    print(f"      - {cat}: {len(params)} parameters")
                    
        except Exception as e:
            print(f"\n❌ Error reading {file_path.name}: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    show_all_discoveries()