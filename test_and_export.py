#!/usr/bin/env python3
"""
Test script that exports discovery results for review
"""

from core import UniversalPluginDiscovery, ParameterCategorizer, DiscoveryExporter
from pathlib import Path
import json
from datetime import datetime

def test_plugin_full(plugin_path):
    """Full test with export"""
    plugin_name = Path(plugin_path).stem
    print(f"\n{'='*60}")
    print(f"Testing: {plugin_name}")
    print('='*60)
    
    # Discovery
    discovery = UniversalPluginDiscovery(plugin_path)
    params = discovery.discover_all()
    
    if not params:
        print("ERROR: No parameters discovered!")
        return None
    
    # Count parameters
    param_count = len([p for p in params if not p.startswith('_')])
    print(f"Discovered {param_count} parameters")
    
    # Print all parameters with details
    print("\nAll Parameters:")
    for param_name, param_info in params.items():
        if not param_name.startswith('_'):
            if isinstance(param_info, dict):
                print(f"  {param_name}:")
                print(f"    Type: {param_info.get('type', 'unknown')}")
                print(f"    Value: {param_info.get('current_value', 'N/A')}")
                if param_info.get('range'):
                    print(f"    Range: {param_info['range']}")
                if param_info.get('valid_values'):
                    print(f"    Valid Values: {param_info['valid_values'][:5]}{'...' if len(param_info['valid_values']) > 5 else ''}")
    
    # Categorization
    categorizer = ParameterCategorizer()
    categorized = categorizer.categorize_parameters(params)
    
    # Export
    exporter = DiscoveryExporter()
    export_path = exporter.export_to_json(plugin_name, params, categorized, discovery.discovery_log)
    print(f"\nExported to: {export_path}")
    
    # Also save a detailed report
    report_path = Path(f"discovery_report_{plugin_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    report = {
        "plugin": plugin_name,
        "path": plugin_path,
        "timestamp": datetime.now().isoformat(),
        "parameter_count": param_count,
        "parameters": params,
        "categorized": categorized,
        "discovery_log": discovery.discovery_log
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Detailed report saved to: {report_path}")
    
    return params, categorized

def main():
    """Test VintageVerb first"""
    test_plugin_full("/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")

if __name__ == "__main__":
    main()