#!/usr/bin/env python3
"""
Validation script - compares research expectations vs actual discoveries
"""

from core import UniversalPluginDiscovery, ResearchValidator
from pathlib import Path
import json

def compare_vintageverb():
    """Compare research data vs actual discovery for VintageVerb"""
    print("="*60)
    print("VINTAGEVERB: Research vs Discovery Validation")
    print("="*60)
    
    # Load research data
    with open('data/research_data.json', 'r') as f:
        research = json.load(f)
    
    vintageverb_research = research.get('vintageverb', {})
    
    # Perform discovery
    discovery = UniversalPluginDiscovery("/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")
    discovered = discovery.discover_all()
    
    # Compare each research parameter
    print("\nParameter Validation:")
    print("-"*50)
    
    matches = 0
    mismatches = []
    
    for param_name, expected in vintageverb_research.items():
        print(f"\n{param_name}:")
        print(f"  Expected type: {expected.get('type')}")
        
        # Find in discovered (case-insensitive)
        discovered_param = None
        for disc_name, disc_info in discovered.items():
            if disc_name.lower() == param_name.lower():
                discovered_param = disc_info
                break
        
        if discovered_param:
            print(f"  Discovered type: {discovered_param.get('type')}")
            
            # Check type match
            if expected.get('type') == discovered_param.get('type'):
                print("  ✅ Type matches!")
                matches += 1
            else:
                print("  ❌ Type mismatch!")
                mismatches.append(f"{param_name}: expected {expected.get('type')} but got {discovered_param.get('type')}")
            
            # Check range if numeric
            if expected.get('range') and discovered_param.get('range'):
                exp_range = expected['range']
                disc_range = discovered_param['range']
                if exp_range == disc_range[:2]:  # Compare min/max only
                    print("  ✅ Range matches!")
                else:
                    print(f"  ⚠️  Range difference: expected {exp_range} got {disc_range[:2]}")
            
            # Check valid values for lists
            if expected.get('valid_values') and discovered_param.get('valid_values'):
                exp_values = set(expected['valid_values'])
                disc_values = set(discovered_param['valid_values'])
                if exp_values == disc_values:
                    print("  ✅ Valid values match!")
                else:
                    print(f"  ❌ Valid values differ!")
                    print(f"     Expected: {expected['valid_values']}")
                    print(f"     Got: {discovered_param['valid_values'][:5]}...")
                    
        else:
            print("  ❌ Parameter not found in discovery!")
            mismatches.append(f"{param_name}: not found")
    
    # Summary
    print("\n" + "="*50)
    print(f"VALIDATION SUMMARY:")
    print(f"  Matches: {matches}/{len(vintageverb_research)}")
    print(f"  Success rate: {matches/len(vintageverb_research)*100:.1f}%")
    
    if mismatches:
        print(f"\nMismatches found:")
        for mismatch in mismatches:
            print(f"  - {mismatch}")
    
    # Show discovered params not in research
    research_params = {p.lower() for p in vintageverb_research.keys()}
    discovered_params = {p.lower() for p in discovered.keys() if not p.startswith('_')}
    extra_params = discovered_params - research_params
    
    if extra_params:
        print(f"\nExtra parameters discovered (not in research):")
        for param in sorted(extra_params):
            print(f"  - {param}")

def main():
    compare_vintageverb()

if __name__ == "__main__":
    main()