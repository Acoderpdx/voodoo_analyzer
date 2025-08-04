#!/usr/bin/env python3
"""
Phase 2 Readiness Validator
Checks if a plugin discovery is ready for Phase 2
"""
import json
import sys
from pathlib import Path

def validate_discovery(filepath):
    """Validate a single discovery file for Phase 2 readiness"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        plugin_name = data.get('plugin', 'Unknown')
        print(f"\n🔍 Validating: {plugin_name}")
        
        discovery = data.get('discovery', data)
        parameters = discovery.get('parameters', {})
        
        if not parameters:
            print("❌ No parameters found!")
            return False
            
        issues = []
        ready_count = 0
        
        for param_name, param_info in parameters.items():
            param_type = param_info.get('type')
            
            # Check string numeric parameters
            if param_type == 'string_numeric':
                if not param_info.get('format'):
                    issues.append(f"  - {param_name}: Missing string format")
                else:
                    ready_count += 1
                    
            # Check ranges
            param_range = param_info.get('range', [None, None])
            if param_range == [None, None] or None in param_range:
                issues.append(f"  - {param_name}: Missing range values")
                
            # Check valid values for choice parameters
            if param_type == 'string_list' and not param_info.get('valid_values'):
                issues.append(f"  - {param_name}: Missing valid values list")
                
        # Report results
        total_params = len(parameters)
        if not issues:
            print(f"✅ PHASE 2 READY! All {total_params} parameters properly discovered.")
            return True
        else:
            print(f"❌ Not Phase 2 ready. {len(issues)} issues found:")
            for issue in issues[:10]:  # Show first 10 issues
                print(issue)
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more issues")
            print(f"\n📊 Ready: {ready_count}/{total_params} parameters")
            return False
            
    except Exception as e:
        print(f"❌ Error validating file: {e}")
        return False
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Validate specific file
        validate_discovery(sys.argv[1])
    else:
        # Validate all discoveries
        discoveries_dir = Path.cwd() / "data" / "discoveries"
        ready_count = 0
        total_count = 0
        
        for discovery_file in discoveries_dir.glob("*.json"):
            if 'corrupted' not in str(discovery_file):
                total_count += 1
                if validate_discovery(discovery_file):
                    ready_count += 1
                    
        print(f"\n📊 Overall: {ready_count}/{total_count} plugins are Phase 2 ready")
