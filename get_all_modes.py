#!/usr/bin/env python3
"""Get all valid values for VintageVerb modes"""

from pedalboard import load_plugin

plugin = load_plugin("/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")

# Get colormode values
colormode_param = plugin.parameters['colormode']
print("ColorMode valid values:")
for val in colormode_param.valid_values:
    print(f"  - {val}")

# Get reverbmode values  
reverbmode_param = plugin.parameters['reverbmode']
print("\nReverbMode valid values:")
for val in reverbmode_param.valid_values:
    print(f"  - {val}")

print(f"\nTotal reverb modes: {len(reverbmode_param.valid_values)}")