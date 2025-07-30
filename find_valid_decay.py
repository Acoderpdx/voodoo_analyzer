#!/usr/bin/env python3
"""Find valid decay values around specific targets"""

from pedalboard import load_plugin

plugin = load_plugin("/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")
param = plugin.parameters['decay']
valid_values = list(param.valid_values)

print("Valid decay values around key points:")
print("="*50)

# Find values around 10s
print("\nAround 10 seconds:")
for val in valid_values:
    if '9.' in val or '10.' in val or '11.' in val:
        print(f"  {val}")

# Find values around 5s
print("\nAround 5 seconds:")
for val in valid_values:
    if val.startswith('4.') or val.startswith('5.') or val.startswith('6.'):
        if float(val.split()[0]) >= 4.5 and float(val.split()[0]) <= 5.5:
            print(f"  {val}")

# Test setting to valid values
print("\nTesting valid values:")
test_vals = ['10.03 s', '10.09 s', '5.01 s', '5.04 s']
for val in test_vals:
    if val in valid_values:
        try:
            plugin.decay = val
            print(f"  ✅ '{val}' works! Current: {plugin.decay}")
        except Exception as e:
            print(f"  ❌ '{val}' failed: {e}")
    else:
        print(f"  ❌ '{val}' not in valid list")