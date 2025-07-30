#!/usr/bin/env python3
"""
Test script for plugin discovery
"""

from core import UniversalPluginDiscovery, ParameterCategorizer, ResearchValidator, DiscoveryExporter
from pathlib import Path
import json

def test_plugin(plugin_path):
    """Test discovery on a single plugin"""
    print(f"\n{'='*60}")
    print(f"Testing: {Path(plugin_path).stem}")
    print('='*60)
    
    # Step 1: Discovery
    discovery = UniversalPluginDiscovery(plugin_path)
    params = discovery.discover_all()
    
    if not params:
        print("ERROR: No parameters discovered!")
        return
    
    # Print discovery log
    print("\nDiscovery Log:")
    for log in discovery.discovery_log[:5]:  # First 5 lines
        print(f"  {log}")
    
    # Count parameters
    param_count = len([p for p in params if not p.startswith('_')])
    print(f"\nDiscovered {param_count} parameters")
    
    # Step 2: Categorization
    categorizer = ParameterCategorizer()
    categorized = categorizer.categorize_parameters(params)
    
    print("\nCategories found:")
    if 'categories' in categorized:
        for category, params in categorized['categories'].items():
            print(f"  {category}: {len(params)} parameters")
    if categorized.get('uncategorized'):
        print(f"  uncategorized: {len(categorized['uncategorized'])} parameters")
    
    # Step 3: Validation (if available)
    validator = ResearchValidator()
    if Path(plugin_path).stem.lower() in ['valhallavintageverb', 'vintageverb']:
        validation_result = validator.validate(params, 'vintageverb')
        print(f"\nValidation Score: {validation_result['score']:.1f}%")
        if validation_result.get('issues'):
            print("Issues found:")
            for issue in validation_result['issues'][:3]:  # First 3 issues
                print(f"  - {issue}")
    
    # Print some parameter details
    print("\nSample Parameters:")
    for param_name, param_info in list(params.items())[:5]:
        if not param_name.startswith('_'):
            print(f"  {param_name}: {param_info.get('type')} "
                  f"[{param_info.get('current_value')}]")
    
    return params, categorized

def main():
    """Test all Valhalla plugins"""
    test_plugins = [
        "/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3",
        "/Library/Audio/Plug-Ins/VST3/ValhallaPlate.vst3",
        "/Library/Audio/Plug-Ins/VST3/ValhallaRoom.vst3",
        "/Library/Audio/Plug-Ins/VST3/ValhallaDelay.vst3"
    ]
    
    results = {}
    
    for plugin_path in test_plugins:
        try:
            params, categorized = test_plugin(plugin_path)
            results[Path(plugin_path).stem] = {
                'parameters': params,
                'categorized': categorized
            }
        except Exception as e:
            print(f"\nERROR testing {Path(plugin_path).stem}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Export results
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for plugin_name, data in results.items():
        param_count = len([p for p in data['parameters'] if not p.startswith('_')])
        print(f"{plugin_name}: {param_count} parameters")

if __name__ == "__main__":
    main()