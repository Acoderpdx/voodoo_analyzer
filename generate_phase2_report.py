#!/usr/bin/env python3
"""
Phase 2 Ready Comprehensive Report Generator
"""
import json
from pathlib import Path
from datetime import datetime

def load_discovery_safely(filepath):
    """Load discovery file handling both structures"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Handle both data structures
        if 'discovery' in data:
            discovery_data = data['discovery']
        else:
            discovery_data = data
            
        # Ensure we have parameters
        if 'parameters' not in discovery_data:
            discovery_data['parameters'] = {}
            
        return {
            'plugin_name': data.get('plugin', filepath.stem.split('_')[0]),
            'timestamp': data.get('timestamp', 'unknown'),
            'parameters': discovery_data.get('parameters', {}),
            'validation': discovery_data.get('validation_results', {}),
            'effect_type': discovery_data.get('effect_type', 'unknown'),
            'phase2_ready': check_phase2_ready(discovery_data)
        }
    except Exception as e:
        return None
        
def check_phase2_ready(discovery):
    """Check if discovery is Phase 2 ready"""
    issues = []
    params = discovery.get('parameters', {})
    
    for name, info in params.items():
        # Check string format discovery
        if info.get('type') == 'string_numeric' and not info.get('format'):
            issues.append(f"{name}: Missing string format")
            
        # Check range discovery
        range_val = info.get('range', [None, None])
        if not range_val or range_val == [None, None] or None in range_val:
            issues.append(f"{name}: Missing range")
            
        # Check valid values for choice parameters
        if info.get('type') == 'string_list' and not info.get('valid_values'):
            issues.append(f"{name}: Missing valid values")
            
    return len(issues) == 0, issues
    
def generate_report():
    """Generate comprehensive Phase 2 readiness report"""
    project_root = Path.cwd()
    discoveries_dir = project_root / "data" / "discoveries"
    
    report = {
        'generated': datetime.now().isoformat(),
        'phase2_ready_plugins': [],
        'plugins_needing_work': [],
        'total_parameters': 0,
        'ready_parameters': 0,
        'summary': {}
    }
    
    # Analyze each discovery
    for discovery_file in discoveries_dir.glob("*.json"):
        if 'corrupted' in str(discovery_file):
            continue
            
        data = load_discovery_safely(discovery_file)
        if not data:
            continue
            
        plugin_name = data['plugin_name']
        params = data['parameters']
        is_ready, issues = data['phase2_ready']
        
        plugin_info = {
            'name': plugin_name,
            'parameter_count': len(params),
            'phase2_ready': is_ready,
            'issues': issues,
            'timestamp': data['timestamp']
        }
        
        if is_ready:
            report['phase2_ready_plugins'].append(plugin_info)
        else:
            report['plugins_needing_work'].append(plugin_info)
            
        report['total_parameters'] += len(params)
        
        # Count ready parameters
        for param_info in params.values():
            if param_info.get('type') == 'string_numeric' and param_info.get('format'):
                report['ready_parameters'] += 1
            elif param_info.get('range') and None not in param_info['range']:
                report['ready_parameters'] += 1
                
    # Generate summary
    report['summary'] = {
        'total_plugins': len(report['phase2_ready_plugins']) + len(report['plugins_needing_work']),
        'ready_plugins': len(report['phase2_ready_plugins']),
        'completion_percentage': round(
            len(report['phase2_ready_plugins']) / 
            (len(report['phase2_ready_plugins']) + len(report['plugins_needing_work'])) * 100, 1
        ) if report['phase2_ready_plugins'] or report['plugins_needing_work'] else 0
    }
    
    # Save report
    report_path = project_root / "data" / "phase2_readiness_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Also create markdown report
    md_report = f"""# Phase 2 Readiness Report

Generated: {report['generated']}

## Summary
- **Total Plugins Analyzed**: {report['summary']['total_plugins']}
- **Phase 2 Ready**: {report['summary']['ready_plugins']} ({report['summary']['completion_percentage']}%)
- **Total Parameters**: {report['total_parameters']}
- **Ready Parameters**: {report['ready_parameters']}

## Phase 2 Ready Plugins
"""
    
    for plugin in report['phase2_ready_plugins']:
        md_report += f"- ✅ **{plugin['name']}** ({plugin['parameter_count']} parameters)\n"
        
    md_report += "\n## Plugins Needing Work\n"
    
    for plugin in report['plugins_needing_work']:
        md_report += f"\n### {plugin['name']} ({plugin['parameter_count']} parameters)\n"
        md_report += "Issues:\n"
        for issue in plugin['issues'][:5]:  # Show first 5 issues
            md_report += f"- {issue}\n"
        if len(plugin['issues']) > 5:
            md_report += f"- ... and {len(plugin['issues']) - 5} more issues\n"
            
    md_path = project_root / "data" / "phase2_readiness_report.md"
    with open(md_path, 'w') as f:
        f.write(md_report)
        
    print(f"\n✅ Reports generated:")
    print(f"  - {report_path}")
    print(f"  - {md_path}")
    
if __name__ == "__main__":
    generate_report()
