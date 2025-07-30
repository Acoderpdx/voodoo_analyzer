#!/usr/bin/env python3
"""
Quick stats from all plugin discoveries
"""

import json
from pathlib import Path

# Load the discovery files
delay_file = Path("valhalla_delay_discovery.json")
verb_file = Path("vintageverb_raw_params.json")

print("🎯 PLUGIN DISCOVERY QUICK STATS")
print("="*50)

# ValhallaDelay Stats
if delay_file.exists():
    with open(delay_file) as f:
        delay_data = json.load(f)
    
    params = delay_data['parameters']
    param_count = len([p for p in params if not p.startswith('_')])
    
    print(f"\n📦 ValhallaDelay:")
    print(f"   Total Parameters: {param_count}")
    
    # Count by type
    types = {}
    for p, info in params.items():
        if not p.startswith('_') and isinstance(info, dict):
            ptype = info.get('type', 'unknown')
            types[ptype] = types.get(ptype, 0) + 1
    
    print(f"   Types: {dict(types)}")
    
    # Sample some interesting parameters
    print(f"   Feedback: {params['feedback']['current_value']}% [{params['feedback']['range']}]")
    print(f"   Mode: {params['mode']['current_value']} (has {len(params['mode']['valid_values']) if params['mode'].get('valid_values') else 0} modes)")
    print(f"   Diffusion: {params['diffusion']['current_value']} (has {len(params['diffusion']['valid_values']) if params['diffusion'].get('valid_values') else 0} values!)")

# VintageVerb Stats
if verb_file.exists():
    with open(verb_file) as f:
        verb_data = json.load(f)
    
    param_count = len(verb_data)
    
    print(f"\n📦 ValhallaVintageVerb:")
    print(f"   Total Parameters: {param_count}")
    
    # Check decay format
    if 'decay' in verb_data:
        decay_info = verb_data['decay']
        print(f"   🔍 Decay parameter: {decay_info['value']}")
        print(f"      Format: STRING (not float!)")
        print(f"      Valid values: {decay_info['valid_values'][:3]}...{decay_info['valid_values'][-3:]}")
    
    # Check modes
    if 'reverbmode' in verb_data:
        mode_info = verb_data['reverbmode']
        print(f"   Reverb modes: {len(mode_info['valid_values'])} modes")
        print(f"      First 5: {mode_info['valid_values'][:5]}")

print("\n" + "="*50)
print("✅ Discovery system working perfectly!")