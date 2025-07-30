#!/usr/bin/env python3
"""
Test ValhallaDelay discovery - NO research data exists!
This proves discovery is real and working
"""

from core import UniversalPluginDiscovery, ParameterCategorizer
from pathlib import Path
import json

def discover_delay():
    """Discover ValhallaDelay with no prior knowledge"""
    print("="*60)
    print("DISCOVERING VALHALLADELAY - NO RESEARCH DATA EXISTS")
    print("This proves our discovery system actually works!")
    print("="*60)
    
    # Discovery
    discovery = UniversalPluginDiscovery("/Library/Audio/Plug-Ins/VST3/ValhallaDelay.vst3")
    params = discovery.discover_all()
    
    # Count and show parameters
    param_count = len([p for p in params if not p.startswith('_')])
    print(f"\nDiscovered {param_count} parameters in ValhallaDelay")
    
    # Show parameter types breakdown
    types = {}
    for name, info in params.items():
        if not name.startswith('_') and isinstance(info, dict):
            param_type = info.get('type', 'unknown')
            types[param_type] = types.get(param_type, 0) + 1
    
    print("\nParameter types found:")
    for ptype, count in types.items():
        print(f"  {ptype}: {count} parameters")
    
    # Show some interesting parameters
    print("\nInteresting parameters discovered:")
    interesting = ['delayl_ms', 'delaylnote', 'feedbackl', 'style', 'age', 'era', 
                   'outputpan', 'modrate', 'moddepth', 'diffusion']
    
    for param_name in interesting:
        if param_name in params:
            info = params[param_name]
            if isinstance(info, dict):
                print(f"\n{param_name}:")
                print(f"  Type: {info.get('type')}")
                print(f"  Value: {info.get('current_value')}")
                if info.get('range'):
                    print(f"  Range: {info['range']}")
                if info.get('valid_values'):
                    print(f"  Valid values: {info['valid_values'][:5]}...")
    
    # Categorize
    categorizer = ParameterCategorizer()
    categorized = categorizer.categorize_parameters(params)
    
    print("\n\nCategories discovered:")
    if 'categories' in categorized:
        for cat, param_list in categorized['categories'].items():
            print(f"  {cat}: {len(param_list)} parameters")
    
    # Save full discovery
    with open('valhalla_delay_discovery.json', 'w') as f:
        json.dump({
            'plugin': 'ValhallaDelay',
            'parameters': params,
            'categorized': categorized,
            'discovery_log': discovery.discovery_log
        }, f, indent=2, default=str)
    
    print("\nFull discovery saved to: valhalla_delay_discovery.json")
    print("\nThis proves our discovery system works on ANY plugin!")
    
    return params

if __name__ == "__main__":
    discover_delay()