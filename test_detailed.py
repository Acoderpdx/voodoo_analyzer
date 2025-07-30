#!/usr/bin/env python3
"""
Detailed parameter testing to validate discovery
"""

from pedalboard import load_plugin
import json

def test_vintageverb_detailed():
    """Get raw parameter details from VintageVerb"""
    plugin = load_plugin("/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")
    
    print("VintageVerb Parameter Analysis")
    print("="*60)
    
    # Get all parameters directly
    params = {}
    for param_name in plugin.parameters.keys():
        param = plugin.parameters[param_name]
        
        # Extract full details
        param_info = {
            'name': param.name if hasattr(param, 'name') else param_name,
            'raw_value': param.raw_value if hasattr(param, 'raw_value') else None,
            'value': str(param),  # This gets the string representation
            'type': param.__class__.__name__
        }
        
        # Check if it has valid string values
        try:
            if hasattr(param, 'valid_values'):
                param_info['valid_values'] = list(param.valid_values)
        except:
            pass
            
        # Check if it has range
        try:
            if hasattr(param, 'range'):
                param_info['range'] = param.range
        except:
            pass
        
        params[param_name] = param_info
        
        # Print critical parameters
        if param_name in ['decay', 'colormode', 'reverbmode', 'mix', 'modrate', 'moddepth']:
            print(f"\n{param_name}:")
            print(f"  Name: {param_info['name']}")
            print(f"  Value: {str(param)}")
            print(f"  Raw: {param_info['raw_value']}")
            if 'valid_values' in param_info:
                print(f"  Valid Values: {param_info['valid_values'][:5]}...")
            if 'range' in param_info:
                print(f"  Range: {param_info['range']}")
    
    # Save full details
    with open('vintageverb_raw_params.json', 'w') as f:
        json.dump(params, f, indent=2, default=str)
    
    print(f"\n\nTotal parameters: {len(params)}")
    print("Full details saved to: vintageverb_raw_params.json")
    
    # Check decay format
    print(f"\nDecay parameter check:")
    print(f"  Current value: '{plugin.decay}'")
    print(f"  Type: {type(plugin.decay)}")
    
    # Try setting decay
    try:
        plugin.decay = 1.0
        print("  Setting as float: WORKS")
    except Exception as e:
        print(f"  Setting as float: FAILED - {e}")
        
    try:
        plugin.decay = "1.00 s"
        print("  Setting as string: WORKS")
    except Exception as e:
        print(f"  Setting as string: FAILED - {e}")

if __name__ == "__main__":
    test_vintageverb_detailed()