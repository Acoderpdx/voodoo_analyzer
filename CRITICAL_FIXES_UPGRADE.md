# 🚨 CRITICAL FIXES FOR PARAMETER DISCOVERY SYSTEM

## Context
After analyzing 15 plugin discoveries, we found critical issues that need immediate fixing. The system is discovering parameters but with incorrect units, ranges, and pollution from system parameters.

## 🔧 URGENT FIXES NEEDED

### 1. Fix System Parameter Filtering
**File**: `core/discovery.py`

```python
# Add to _get_parameter_names() method:
SYSTEM_PARAMS_BLACKLIST = [
    'installed_plugins', 'parameters', 'name', 
    'is_effect', 'is_instrument', 'has_shared_container',
    'preset_data', 'state_information', 'bypass'
]

def _get_parameter_names(self) -> List[str]:
    """Extract all parameter names from the plugin"""
    param_names = []
    
    # Get actual plugin parameters (not system attributes)
    try:
        # If plugin has parameters dict/list
        if hasattr(self.plugin, 'parameters'):
            for param_name, param_obj in self.plugin.parameters.items():
                if param_name not in SYSTEM_PARAMS_BLACKLIST:
                    param_names.append(param_name)
        else:
            # Fallback to attribute inspection
            for attr in dir(self.plugin):
                if (not attr.startswith('_') and 
                    attr not in SYSTEM_PARAMS_BLACKLIST and
                    not callable(getattr(self.plugin, attr, None))):
                    try:
                        value = getattr(self.plugin, attr)
                        # Skip if it's a list of paths or complex object
                        if not isinstance(value, (list, dict)) or attr in ['type', 'mode']:
                            param_names.append(attr)
                    except:
                        pass
    except Exception as e:
        self.discovery_log.append(f"Error getting parameters: {str(e)}")
    
    return param_names
```

### 2. Fix Range Detection for Normalized Parameters
**File**: `core/discovery.py`

```python
def _analyze_numeric_parameter(self, param_name: str, current_value: Union[int, float]) -> Dict:
    """Analyze numeric parameter range and behavior"""
    result = {'subtype': 'float' if isinstance(current_value, float) else 'int'}
    
    # Get the actual parameter object if available
    param_obj = None
    if hasattr(self.plugin, 'parameters') and param_name in self.plugin.parameters:
        param_obj = self.plugin.parameters[param_name]
    
    # Try to get real range from parameter object
    if param_obj and hasattr(param_obj, 'range'):
        try:
            param_range = param_obj.range
            if isinstance(param_range, tuple) and len(param_range) >= 2:
                result['range'] = [float(param_range[0]), float(param_range[1])]
                if len(param_range) > 2:
                    result['step'] = float(param_range[2])
        except:
            pass
    
    # If no range found or it's normalized [0,1], try value testing
    if not result.get('range') or result['range'] == [0.0, 1.0]:
        # For normalized params, try to infer real range from param name
        real_range = self._infer_range_from_name(param_name, current_value)
        if real_range:
            result['range'] = real_range
        else:
            # Test actual values
            result.update(self._test_parameter_range(param_name, current_value))
    
    return result

def _infer_range_from_name(self, param_name: str, current_value: float) -> Optional[List[float]]:
    """Infer likely range from parameter name and current value"""
    param_lower = param_name.lower()
    
    # Common parameter patterns
    if 'freq' in param_lower or 'hz' in param_lower:
        if 'low' in param_lower or 'high_pass' in param_lower:
            return [20.0, 2000.0]
        elif 'high' in param_lower or 'low_pass' in param_lower:
            return [1000.0, 20000.0]
        else:
            return [20.0, 20000.0]
    
    elif 'gain' in param_lower or 'db' in param_lower:
        return [-24.0, 24.0]
    
    elif 'delay' in param_lower and 'ms' in param_lower:
        return [0.0, 1000.0]
    
    elif any(x in param_lower for x in ['mix', 'wet', 'dry', 'depth', 'width']):
        # These are often 0-100%
        if 0 <= current_value <= 1:
            return [0.0, 100.0]  # Convert from normalized
    
    return None
```

### 3. Fix Unit Detection
**File**: `core/discovery.py`

```python
def _detect_unit(self, param_name: str) -> Optional[str]:
    """Enhanced unit detection from parameter name and value"""
    param_lower = param_name.lower()
    
    # First try to get unit from parameter object
    if hasattr(self.plugin, 'parameters') and param_name in self.plugin.parameters:
        param_obj = self.plugin.parameters[param_name]
        # Check for unit in string representation
        param_str = str(param_obj)
        
        # Extract unit from string like "100.0 Hz" or "50 %"
        import re
        unit_match = re.search(r'\d+\.?\d*\s*([A-Za-z%]+)', param_str)
        if unit_match:
            unit = unit_match.group(1).lower()
            # Normalize common units
            unit_map = {
                'hz': 'Hz', 'khz': 'kHz', 'db': 'dB',
                'ms': 'ms', 's': 's', '%': '%',
                'cents': 'cents', 'semi': 'semitones'
            }
            return unit_map.get(unit, unit)
    
    # Enhanced pattern matching
    unit_patterns = {
        'Hz': ['freq', 'frequency', 'cutoff', 'crossover'],
        'ms': ['delay', 'predelay', 'attack', 'release', 'hold'],
        's': ['decay', 'time', 'reverb', 'rt60'],
        'dB': ['gain', 'level', 'volume', 'shelf', 'threshold'],
        '%': ['mix', 'depth', 'amount', 'width', 'feedback', 'wet', 'dry'],
        'cents': ['detune', 'fine'],
        'semitones': ['pitch', 'transpose', 'shift']
    }
    
    for unit, patterns in unit_patterns.items():
        for pattern in patterns:
            if pattern in param_lower:
                # Special case: if it has 'ms' in name, it's ms not s
                if unit == 's' and 'ms' in param_lower:
                    return 'ms'
                return unit
    
    return None
```

### 4. Fix JSON Export Errors
**File**: `core/exporter.py`

```python
import numpy as np
import json

class SafeJSONEncoder(json.JSONEncoder):
    """Handle special values in JSON export"""
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
            # Don't serialize complex objects
            return str(obj)
        return super().default(obj)

# Update export_to_json method:
def export_to_json(self, ...):
    # ... existing code ...
    
    # Clean data before export
    export_data = self._clean_export_data(export_data)
    
    # Write with safe encoder
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, cls=SafeJSONEncoder)
    
def _clean_export_data(self, data):
    """Remove problematic data before export"""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            # Skip system parameters
            if k in ['installed_plugins', 'parameters', 'preset_data']:
                continue
            cleaned[k] = self._clean_export_data(v)
        return cleaned
    elif isinstance(data, list):
        return [self._clean_export_data(item) for item in data]
    else:
        return data
```

### 5. Fix Validation Actually Running
**File**: `core/validator_enhanced.py`

```python
def validate_parameter_format(self, param_name: str, param_info: Dict) -> Dict:
    """Test which formats actually work"""
    results = {
        'parameter': param_name,
        'current_value': param_info.get('current_value'),
        'format_tests': {},
        'working_formats': []
    }
    
    # Only test string_numeric parameters
    if param_info.get('type') != 'string_numeric':
        return results
    
    # Save original value
    original_value = None
    try:
        original_value = getattr(self.plugin, param_name)
    except:
        return results
    
    # Test numeric value from current string
    import re
    numeric_match = re.search(r'([\d.]+)', str(param_info.get('current_value', '')))
    if numeric_match:
        test_value = float(numeric_match.group(1))
        
        # Comprehensive format tests
        test_formats = [
            ('float', test_value),
            ('int', int(test_value)),
            ('string_plain', str(test_value)),
            ('string_one_decimal', f"{test_value:.1f}"),
            ('string_two_decimal', f"{test_value:.2f}"),
        ]
        
        # Add unit-based tests if unit detected
        unit = param_info.get('unit', '')
        if unit:
            test_formats.extend([
                ('string_with_unit_space', f"{test_value:.2f} {unit}"),
                ('string_with_unit_no_space', f"{test_value:.2f}{unit}"),
                ('string_one_decimal_unit', f"{test_value:.1f} {unit}"),
            ])
        
        # Test each format
        for format_name, test_val in test_formats:
            try:
                setattr(self.plugin, param_name, test_val)
                actual = getattr(self.plugin, param_name)
                
                # Check if it worked
                success = True
                exact_match = str(test_val).strip() == str(actual).strip()
                
                results['format_tests'][format_name] = {
                    'success': success,
                    'set_value': str(test_val),
                    'actual_value': str(actual),
                    'exact_match': exact_match
                }
                
                if success and exact_match:
                    results['working_formats'].append(format_name)
                    
            except Exception as e:
                results['format_tests'][format_name] = {
                    'success': False,
                    'error': str(e)
                }
    
    # Restore original
    try:
        setattr(self.plugin, param_name, original_value)
    except:
        pass
    
    return results
```

## 📋 Implementation Checklist

1. [ ] **Update discovery.py** with system parameter filtering
2. [ ] **Fix range detection** for normalized parameters
3. [ ] **Enhance unit detection** with regex extraction
4. [ ] **Fix JSON export** with safe encoder
5. [ ] **Make validation actually run** and test formats

## 🧪 Test These Fixes

After implementing:
```bash
# Test on Nectar 4 Reverb (had unit detection issues)
python main.py
# Load Nectar 4 Reverb
# Check if units are now correct (Hz, dB, %, ms)

# Test on TAL-Reverb-2 (had normalized ranges)
# Check if ranges are now proper values not [0,1]

# Export and verify no JSON errors
```

## 🎯 Expected Results After Fixes

1. **Clean Parameters**: No more `installed_plugins` pollution
2. **Correct Units**: Hz for frequencies, dB for gains, % for mix
3. **Real Ranges**: Actual values like [20, 20000] not [0, 1]
4. **Working Validation**: `format_tests` populated with results
5. **Stable Exports**: No more JSON decode errors

## 🚀 Next Enhancement

Once these critical fixes are in place, the learning system can properly:
- Learn correct parameter patterns
- Build accurate effect knowledge
- Generate better test matrices
- Improve categorization accuracy

**Priority**: Fix these issues FIRST before any other enhancements!