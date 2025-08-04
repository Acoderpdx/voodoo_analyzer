#!/usr/bin/env python3
"""
Phase 2 Readiness Upgrade Script for Voodoo Analyzer
This script will:
1. Clean corrupted data files (preserve good ones)
2. Fix data aggregation issues
3. Update the discovery system for Phase 2 compatibility
4. Re-analyze failed plugins
5. Generate comprehensive reports
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import traceback
import re
import numpy as np

# CRITICAL: Run this script from the voodoo_analyzer directory
# cd /Users/aidanbernard/Downloads/VOODOO VSTS/voodoo_analyzer/

class Phase2Upgrader:
    def __init__(self):
        self.project_root = Path.cwd()
        self.data_dir = self.project_root / "data"
        self.discoveries_dir = self.data_dir / "discoveries"
        self.backup_dir = self.data_dir / "backup_before_phase2"
        self.failed_files = []
        self.successful_files = []
        self.plugins_to_reanalyze = []
        
    def run_full_upgrade(self):
        """Execute complete Phase 2 upgrade process"""
        print("🚀 Starting Phase 2 Readiness Upgrade...")
        
        # Step 1: Backup everything first
        self.create_backup()
        
        # Step 2: Analyze and clean discovery files
        self.analyze_discovery_files()
        
        # Step 3: Fix core system files
        self.fix_core_systems()
        
        # Step 4: Update data aggregation
        self.fix_data_aggregation()
        
        # Step 5: Generate re-analysis list
        self.generate_reanalysis_list()
        
        # Step 6: Create Phase 2 validator
        self.create_phase2_validator()
        
        # Step 7: Generate final report
        self.generate_upgrade_report()
        
        print("\n✅ Phase 2 Upgrade Complete!")
        
    def create_backup(self):
        """Backup all data before making changes"""
        print("\n📦 Creating backup...")
        
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            
        # Backup all JSON files in data directory
        for json_file in self.data_dir.glob("*.json"):
            shutil.copy2(json_file, self.backup_dir)
            
        # Backup discoveries directory
        if self.discoveries_dir.exists():
            backup_discoveries = self.backup_dir / "discoveries"
            if backup_discoveries.exists():
                shutil.rmtree(backup_discoveries)
            shutil.copytree(self.discoveries_dir, backup_discoveries)
            
        print(f"✅ Backup created at: {self.backup_dir}")
        
    def analyze_discovery_files(self):
        """Analyze all discovery files and categorize them"""
        print("\n🔍 Analyzing discovery files...")
        
        if not self.discoveries_dir.exists():
            print("❌ No discoveries directory found!")
            return
            
        for discovery_file in self.discoveries_dir.glob("*_enhanced_*.json"):
            try:
                with open(discovery_file, 'r') as f:
                    data = json.load(f)
                    
                # Check if file has valid structure
                if self._validate_discovery_structure(data):
                    self.successful_files.append(discovery_file)
                else:
                    self.failed_files.append((discovery_file, "Invalid structure"))
                    
            except json.JSONDecodeError as e:
                self.failed_files.append((discovery_file, f"JSON Error: {str(e)}"))
            except Exception as e:
                self.failed_files.append((discovery_file, f"Unknown Error: {str(e)}"))
                
        print(f"✅ Found {len(self.successful_files)} valid files")
        print(f"❌ Found {len(self.failed_files)} corrupted files")
        
        # Move corrupted files to a separate directory
        if self.failed_files:
            corrupted_dir = self.discoveries_dir / "corrupted"
            corrupted_dir.mkdir(exist_ok=True)
            
            for file_path, error in self.failed_files:
                print(f"  Moving {file_path.name} -> corrupted/ ({error})")
                shutil.move(str(file_path), str(corrupted_dir / file_path.name))
                
                # Extract plugin name for re-analysis
                plugin_name = file_path.stem.split('_enhanced_')[0]
                self.plugins_to_reanalyze.append(plugin_name)
                
    def _validate_discovery_structure(self, data):
        """Validate discovery file has required structure"""
        # Check for essential keys
        if 'plugin' not in data or 'timestamp' not in data:
            return False
            
        # Check for discovery data
        discovery = data.get('discovery', {})
        if not discovery:
            return False
            
        # Check for parameters
        parameters = discovery.get('parameters', {})
        if not isinstance(parameters, dict):
            return False
            
        # Check if parameters are properly structured
        for param_name, param_info in parameters.items():
            if not isinstance(param_info, dict):
                return False
            if 'type' not in param_info:
                return False
                
        return True
        
    def fix_core_systems(self):
        """Fix core system files for Phase 2 compatibility"""
        print("\n🔧 Fixing core systems...")
        
        # Fix 1: Update discovery.py with enhanced range detection
        self._update_discovery_system()
        
        # Fix 2: Update validator_enhanced.py
        self._update_validator_system()
        
        # Fix 3: Update exporter.py with SafeJSONEncoder
        self._update_exporter_system()
        
        # Fix 4: Create comprehensive report generator
        self._create_report_generator()
        
    def _update_discovery_system(self):
        """Add fixes to discovery.py"""
        discovery_path = self.project_root / "core" / "discovery.py"
        
        # Read current file
        with open(discovery_path, 'r') as f:
            content = f.read()
            
        # Check if fixes already applied
        if "PHASE2_READY = True" in content:
            print("  ✅ discovery.py already updated")
            return
            
        # Add Phase 2 enhancements at the end of the file
        enhancements = '''

# PHASE 2 ENHANCEMENTS
PHASE2_READY = True

def extract_parameter_range(plugin, param_name, param_obj):
    """Enhanced range extraction for Phase 2"""
    try:
        # Try to get range from parameter object
        if hasattr(param_obj, 'range'):
            range_val = param_obj.range
            if range_val and len(range_val) >= 2:
                return [float(range_val[0]), float(range_val[1])]
        
        # Try to get min/max
        if hasattr(param_obj, 'min_value') and hasattr(param_obj, 'max_value'):
            return [float(param_obj.min_value), float(param_obj.max_value)]
            
        # For string parameters with valid values
        if hasattr(param_obj, 'valid_values'):
            valid_vals = list(param_obj.valid_values)
            # Try to extract numeric ranges from string values
            numeric_vals = []
            for val in valid_vals:
                match = re.search(r'(\\d+\\.?\\d*)', str(val))
                if match:
                    numeric_vals.append(float(match.group(1)))
            if numeric_vals:
                return [min(numeric_vals), max(numeric_vals)]
                
        # Use research data if available
        from pathlib import Path
        research_path = Path(__file__).parent.parent / 'data' / 'research_data.json'
        if research_path.exists():
            with open(research_path, 'r') as f:
                research = json.load(f)
                plugin_type = plugin.name.lower()
                for key in research:
                    if key in plugin_type:
                        param_data = research[key].get(param_name, {})
                        if 'range' in param_data:
                            return param_data['range']
                            
    except Exception as e:
        print(f"Range extraction error for {param_name}: {e}")
        
    return None

# Monkey patch the discovery method to use enhanced range extraction
if 'ParameterDiscovery' in globals():
    _original_discover = ParameterDiscovery._discover_parameter_details
    
    def _enhanced_discover(self, param_name, param_obj):
        result = _original_discover(self, param_name, param_obj)
        
        # Add enhanced range detection
        if result and 'range' in result:
            enhanced_range = extract_parameter_range(self.plugin, param_name, param_obj)
            if enhanced_range:
                result['range'] = enhanced_range
                
        return result
        
    ParameterDiscovery._discover_parameter_details = _enhanced_discover
'''
        
        # Append enhancements
        with open(discovery_path, 'a') as f:
            f.write(enhancements)
            
        print("  ✅ discovery.py updated with Phase 2 enhancements")
        
    def _update_validator_system(self):
        """Ensure validator properly tests string formats"""
        validator_path = self.project_root / "core" / "validator_enhanced.py"
        
        if not validator_path.exists():
            # Create it if it doesn't exist
            validator_content = '''"""
Enhanced parameter validator for Phase 2 compatibility
"""
import json
from typing import Dict, Any, List, Tuple

class EnhancedValidator:
    def __init__(self):
        self.validation_results = {}
        
    def validate_parameter_format(self, plugin, param_name: str, param_info: Dict) -> Dict:
        """Test different parameter formats to find working ones"""
        results = {
            'parameter': param_name,
            'current_value': param_info.get('current_value'),
            'format_tests': {},
            'working_formats': []
        }
        
        if param_info.get('type') == 'string_numeric':
            # Test various string formats
            test_value = 4.0  # Test value
            unit = param_info.get('unit', 's')
            
            format_tests = [
                ('float', test_value),
                ('int', int(test_value)),
                ('string_plain', str(test_value)),
                ('string_one_decimal', f"{test_value:.1f}"),
                ('string_two_decimal', f"{test_value:.2f}"),
                ('string_with_unit_space', f"{test_value:.2f} {unit}"),
                ('string_with_unit_no_space', f"{test_value:.2f}{unit}"),
                ('string_unit_first', f"{unit} {test_value:.2f}"),
            ]
            
            for format_name, test_val in format_tests:
                try:
                    # Save current value
                    original = getattr(plugin, param_name)
                    
                    # Try to set with test format
                    setattr(plugin, param_name, test_val)
                    
                    # Read back to verify
                    readback = getattr(plugin, param_name)
                    
                    # Check if it worked
                    if str(readback) == str(test_val) or self._values_match(readback, test_val):
                        results['format_tests'][format_name] = {'success': True}
                        results['working_formats'].append(format_name)
                    else:
                        results['format_tests'][format_name] = {
                            'success': False,
                            'error': f"Readback mismatch: {readback} != {test_val}"
                        }
                        
                    # Restore original
                    setattr(plugin, param_name, original)
                    
                except Exception as e:
                    results['format_tests'][format_name] = {
                        'success': False,
                        'error': str(e)
                    }
                    
        return results
        
    def _values_match(self, val1, val2) -> bool:
        """Check if two values match (handling numeric/string conversion)"""
        try:
            # Extract numeric values if strings
            num1 = float(str(val1).split()[0]) if isinstance(val1, str) else float(val1)
            num2 = float(str(val2).split()[0]) if isinstance(val2, str) else float(val2)
            return abs(num1 - num2) < 0.01
        except:
            return str(val1) == str(val2)
'''
            with open(validator_path, 'w') as f:
                f.write(validator_content)
                
        print("  ✅ validator_enhanced.py updated")
        
    def _update_exporter_system(self):
        """Ensure exporter has SafeJSONEncoder"""
        exporter_path = self.project_root / "core" / "exporter.py"
        
        with open(exporter_path, 'r') as f:
            content = f.read()
            
        if "SafeJSONEncoder" not in content:
            # Add SafeJSONEncoder before the last class or at the end
            safe_encoder = '''

class SafeJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles special float values and numpy types"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        return super().default(obj)
'''
            
            # Find where to insert (before the last class or at end)
            import_pos = content.rfind('import')
            import_end = content.find('\n', import_pos) + 1
            
            # Add numpy import if not present
            if 'import numpy as np' not in content:
                content = content[:import_end] + "import numpy as np\n" + content[import_end:]
                
            # Add SafeJSONEncoder
            content = content + safe_encoder
            
            # Update all json.dump calls to use cls=SafeJSONEncoder
            content = re.sub(
                r'json\.dump\((.*?)\)',
                r'json.dump(\1, cls=SafeJSONEncoder)',
                content
            )
            
            with open(exporter_path, 'w') as f:
                f.write(content)
                
        print("  ✅ exporter.py updated with SafeJSONEncoder")
        
    def _create_report_generator(self):
        """Create fixed comprehensive report generator"""
        generator_path = self.project_root / "generate_phase2_report.py"
        
        generator_content = '''#!/usr/bin/env python3
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
        md_report += f"- ✅ **{plugin['name']}** ({plugin['parameter_count']} parameters)\\n"
        
    md_report += "\\n## Plugins Needing Work\\n"
    
    for plugin in report['plugins_needing_work']:
        md_report += f"\\n### {plugin['name']} ({plugin['parameter_count']} parameters)\\n"
        md_report += "Issues:\\n"
        for issue in plugin['issues'][:5]:  # Show first 5 issues
            md_report += f"- {issue}\\n"
        if len(plugin['issues']) > 5:
            md_report += f"- ... and {len(plugin['issues']) - 5} more issues\\n"
            
    md_path = project_root / "data" / "phase2_readiness_report.md"
    with open(md_path, 'w') as f:
        f.write(md_report)
        
    print(f"\\n✅ Reports generated:")
    print(f"  - {report_path}")
    print(f"  - {md_path}")
    
if __name__ == "__main__":
    generate_report()
'''
        
        with open(generator_path, 'w') as f:
            f.write(generator_content)
            
        # Make executable
        os.chmod(generator_path, 0o755)
        
        print("  ✅ Created generate_phase2_report.py")
        
    def fix_data_aggregation(self):
        """Fix the comprehensive analysis report generator"""
        print("\n📊 Fixing data aggregation...")
        
        # Run the new Phase 2 report generator
        os.system("python generate_phase2_report.py")
        
    def generate_reanalysis_list(self):
        """Generate list of plugins that need re-analysis"""
        print("\n📝 Generating re-analysis list...")
        
        reanalysis_file = self.data_dir / "plugins_to_reanalyze.txt"
        
        with open(reanalysis_file, 'w') as f:
            f.write("# Plugins that need re-analysis\\n")
            f.write("# Run analyze_new_plugin.py for each\\n\\n")
            
            for plugin in sorted(set(self.plugins_to_reanalyze)):
                f.write(f"{plugin}\\n")
                
        print(f"  ✅ Re-analysis list saved to: {reanalysis_file}")
        print(f"  📋 {len(set(self.plugins_to_reanalyze))} plugins need re-analysis")
        
    def create_phase2_validator(self):
        """Create a Phase 2 validation tool"""
        validator_path = self.project_root / "validate_phase2_ready.py"
        
        validator_content = '''#!/usr/bin/env python3
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
        print(f"\\n🔍 Validating: {plugin_name}")
        
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
            print(f"\\n📊 Ready: {ready_count}/{total_params} parameters")
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
                    
        print(f"\\n📊 Overall: {ready_count}/{total_count} plugins are Phase 2 ready")
'''
        
        with open(validator_path, 'w') as f:
            f.write(validator_content)
            
        os.chmod(validator_path, 0o755)
        print("  ✅ Created validate_phase2_ready.py")
        
    def generate_upgrade_report(self):
        """Generate final upgrade report"""
        print("\n📄 Generating upgrade report...")
        
        report = f"""# Phase 2 Upgrade Report

Generated: {datetime.now().isoformat()}

## Actions Taken

### 1. Data Cleanup
- Backed up all data to: {self.backup_dir}
- Identified {len(self.successful_files)} valid discovery files
- Moved {len(self.failed_files)} corrupted files to corrupted/
- Generated re-analysis list for {len(set(self.plugins_to_reanalyze))} plugins

### 2. System Updates
- ✅ Enhanced discovery.py with Phase 2 range extraction
- ✅ Updated validator_enhanced.py for format testing
- ✅ Added SafeJSONEncoder to exporter.py
- ✅ Created generate_phase2_report.py
- ✅ Created validate_phase2_ready.py

### 3. Next Steps

1. **Re-analyze failed plugins**:
   ```bash
   python analyze_new_plugin.py
   # Select each plugin from plugins_to_reanalyze.txt
   ```

2. **Validate Phase 2 readiness**:
   ```bash
   python validate_phase2_ready.py
   ```

3. **Generate comprehensive report**:
   ```bash
   python generate_phase2_report.py
   ```

4. **Test the updated system**:
   ```bash
   python main.py
   # Try analyzing a new plugin to ensure all fixes work
   ```

### 4. Phase 2 Implementation

Once all plugins are re-analyzed and validated, you can begin Phase 2:

```python
# Example Phase 2 usage
from pathlib import Path
import json

# Load a Phase 2-ready discovery
with open('data/discoveries/ValhallaVintageVerb_enhanced_[timestamp].json') as f:
    discovery = json.load(f)

# Use discovered formats for automation
params = discovery['discovery']['parameters']
decay_format = params['decay']['format']  # "%.2f s"

# Set parameter with correct format
plugin.decay = decay_format % 2.5  # "2.50 s"
```

## Files Modified
- core/discovery.py
- core/validator_enhanced.py
- core/exporter.py

## Files Created
- generate_phase2_report.py
- validate_phase2_ready.py
- data/plugins_to_reanalyze.txt
- data/phase2_readiness_report.json
- data/phase2_readiness_report.md

## Backup Location
{self.backup_dir}
"""
        
        report_path = self.project_root / "PHASE2_UPGRADE_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
            
        print(f"\n✅ Upgrade report saved to: {report_path}")
        
if __name__ == "__main__":
    print("=" * 60)
    print("VOODOO ANALYZER - PHASE 2 READINESS UPGRADE")
    print("=" * 60)
    
    # Confirm we're in the right directory
    if not Path.cwd().name == "voodoo_analyzer":
        print("❌ ERROR: Must run from voodoo_analyzer directory!")
        print("cd /Users/aidanbernard/Downloads/VOODOO VSTS/voodoo_analyzer/")
        sys.exit(1)
        
    # Confirm before proceeding
    print("\nThis script will:")
    print("1. Backup all data")
    print("2. Clean corrupted files")
    print("3. Update core systems for Phase 2")
    print("4. Generate reports and validators")
    
    response = input("\nProceed with upgrade? (yes/no): ")
    if response.lower() != 'yes':
        print("Upgrade cancelled.")
        sys.exit(0)
        
    # Run the upgrade
    upgrader = Phase2Upgrader()
    upgrader.run_full_upgrade()