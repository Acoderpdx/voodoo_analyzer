"""
Enhanced plugin parameter discovery engine
Incorporates all learnings from VintageVerb analysis
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import numpy as np
from pedalboard import load_plugin
import json

class UniversalPluginDiscovery:
    """Professional plugin parameter discovery with format detection"""
    
    def __init__(self, plugin_path: str):
        self.plugin_path = plugin_path
        self.plugin_name = Path(plugin_path).stem
        self.plugin = None
        self.parameters = {}
        self.discovery_log = []
        
    def load_plugin(self) -> bool:
        """Load the plugin and perform initial discovery"""
        try:
            self.plugin = load_plugin(self.plugin_path)
            self.discovery_log.append(f"Successfully loaded: {self.plugin_name}")
            return True
        except Exception as e:
            self.discovery_log.append(f"Failed to load plugin: {str(e)}")
            return False
    
    def discover_all(self) -> Dict[str, Any]:
        """Discover all parameters with enhanced format detection"""
        if not self.plugin:
            if not self.load_plugin():
                return {}
        
        # Get basic parameter list
        param_names = self._get_parameter_names()
        
        for param_name in param_names:
            self.discovery_log.append(f"Discovering: {param_name}")
            param_info = self._analyze_parameter(param_name)
            if param_info:
                self.parameters[param_name] = param_info
        
        # Add plugin metadata
        self.parameters['_metadata'] = {
            'plugin_name': self.plugin_name,
            'plugin_path': self.plugin_path,
            'total_parameters': len(self.parameters) - 1,
            'discovery_complete': True
        }
        
        return self.parameters
    
    def _get_parameter_names(self) -> List[str]:
        """Extract all parameter names from the plugin"""
        param_names = []
        
        # System parameters to exclude
        SYSTEM_PARAMS_BLACKLIST = [
            'installed_plugins', 'parameters', 'name', 
            'is_effect', 'is_instrument', 'has_shared_container',
            'preset_data', 'state_information', 'bypass',
            'is_processing', 'can_process_replacing', 'latency_samples',
            'tail_samples', 'manufacturer', 'identifier', 'version'
        ]
        
        # Method 1: Use the parameters property if available (preferred method)
        if hasattr(self.plugin, 'parameters'):
            try:
                # Access the parameters dictionary
                params_dict = self.plugin.parameters
                for param_name in params_dict.keys():
                    if param_name not in SYSTEM_PARAMS_BLACKLIST:
                        param_names.append(param_name)
                self.discovery_log.append(f"Found {len(param_names)} parameters via parameters property")
                return param_names
            except Exception as e:
                self.discovery_log.append(f"Error accessing parameters property: {e}")
        
        # Method 2: Direct attribute inspection (fallback)
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
        
        # Method 3: Check for common parameter patterns
        common_params = [
            'mix', 'decay', 'predelay', 'size', 'mode', 'color',
            'modDepth', 'modRate', 'highFreq', 'lowFreq', 'feedback',
            'diffusion', 'damping', 'width', 'attack', 'release'
        ]
        
        for param in common_params:
            if hasattr(self.plugin, param) and param not in param_names:
                param_names.append(param)
            # Also check case variations
            for variant in [param.lower(), param.upper(), param.capitalize()]:
                if hasattr(self.plugin, variant) and variant not in param_names:
                    param_names.append(variant)
        
        return param_names
    
    def _analyze_parameter(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Deeply analyze a single parameter"""
        try:
            current_value = getattr(self.plugin, param_name)
            param_info = {
                'name': param_name,
                'current_value': current_value,
                'type': 'unknown',
                'format': None,
                'range': None,
                'valid_values': None,
                'unit': self._detect_unit(param_name),
                'default': current_value
            }
            
            # Check if we can get richer metadata from parameters property
            if hasattr(self.plugin, 'parameters') and param_name in self.plugin.parameters:
                try:
                    param_obj = self.plugin.parameters[param_name]
                    
                    # Extract metadata from the parameter object
                    if hasattr(param_obj, 'range'):
                        param_range = param_obj.range
                        if param_range:
                            param_info['range'] = list(param_range[:2])  # min, max
                            if len(param_range) > 2:
                                param_info['step'] = param_range[2]
                    
                    # Get the display name
                    if hasattr(param_obj, 'name'):
                        param_info['display_name'] = param_obj.name
                    
                    # Check for valid string values
                    param_repr = repr(param_obj)
                    if 'valid string values' in param_repr:
                        # Extract number of valid values
                        import re
                        match = re.search(r'(\d+) valid string values', param_repr)
                        if match:
                            param_info['num_string_values'] = int(match.group(1))
                            param_info['type'] = 'string_list'
                            # Try to get the actual values
                            string_values = self._detect_valid_string_values(param_name)
                            if string_values:
                                param_info['valid_values'] = string_values
                    
                    # Check if it's boolean
                    if 'boolean' in param_repr:
                        param_info['type'] = 'boolean'
                        param_info['valid_values'] = [False, True]
                    
                    # Extract unit from the representation
                    unit_patterns = [r'(\w+)\s+range=', r'value=[\d.]+\s+(\w+)\s+range=']
                    for pattern in unit_patterns:
                        match = re.search(pattern, param_repr)
                        if match and match.group(1) not in ['value', 'raw_value']:
                            param_info['unit'] = match.group(1)
                            break
                    
                except Exception as e:
                    self.discovery_log.append(f"Error extracting metadata from parameter object: {e}")
            
            # Fallback type detection if not already set
            if param_info['type'] == 'unknown':
                if isinstance(current_value, (int, float)):
                    param_info['type'] = 'numeric'
                    param_info.update(self._analyze_numeric_parameter(param_name, current_value))
                elif isinstance(current_value, str):
                    param_info['type'] = 'string'
                    param_info.update(self._analyze_string_parameter(param_name, current_value))
                elif isinstance(current_value, bool):
                    param_info['type'] = 'boolean'
                    param_info['valid_values'] = [True, False]
            
            # Special handling for parameters that might need string format
            if param_name.lower() in ['decay', 'reverb', 'time', 'delay']:
                string_format = self._detect_string_format_requirement(param_name)
                if string_format:
                    param_info['format'] = string_format
                    param_info['type'] = 'string_numeric'
            
            return param_info
            
        except Exception as e:
            self.discovery_log.append(f"Error analyzing {param_name}: {str(e)}")
            return None
    
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
    
    def _test_parameter_range(self, param_name: str, current_value: Union[int, float]) -> Dict:
        """Test parameter range by trying different values"""
        result = {}
        test_values = [0, 0.1, 0.5, 1, 10, 100, 1000, 10000]
        valid_values = []
        
        for test_val in test_values:
            try:
                setattr(self.plugin, param_name, test_val)
                actual_val = getattr(self.plugin, param_name)
                valid_values.append(actual_val)
            except:
                pass
        
        # Restore original value
        try:
            setattr(self.plugin, param_name, current_value)
        except:
            pass
        
        if valid_values:
            result['range'] = [min(valid_values), max(valid_values)]
        
        return result
    
    def _analyze_string_parameter(self, param_name: str, current_value: str) -> Dict:
        """Analyze string parameter - might be a list or formatted number"""
        result = {}
        
        # Check if it's a numeric string (like "1.00 s")
        if self._is_numeric_string(current_value):
            result['subtype'] = 'numeric_string'
            result['format'] = self._extract_string_format(current_value)
        else:
            # Try to get list of valid values
            result['subtype'] = 'list'
            valid_values = self._detect_valid_string_values(param_name)
            if valid_values:
                result['valid_values'] = valid_values
        
        return result
    
    def _detect_string_format_requirement(self, param_name: str) -> Optional[str]:
        """Detect if parameter requires specific string format"""
        # Based on VintageVerb learnings
        test_formats = [
            (1.0, "1.00 s"),
            (1.0, "1.0 s"),
            (1.0, "1 s"),
            (1.0, "1.00"),
            (1.0, "1"),
        ]
        
        for numeric_val, string_val in test_formats:
            try:
                # Try setting as string
                setattr(self.plugin, param_name, string_val)
                if getattr(self.plugin, param_name) == string_val:
                    # Extract format pattern
                    if " s" in string_val:
                        return "%.2f s"
                    elif " ms" in string_val:
                        return "%.0f ms"
                    elif " Hz" in string_val:
                        return "%.0f Hz"
                    else:
                        return "%.2f"
            except:
                pass
        
        return None
    
    def _detect_valid_string_values(self, param_name: str) -> Optional[List[str]]:
        """Try to detect valid values for list-type parameters"""
        # Common mode/type values to test
        common_values = [
            # Reverb modes
            ["Concert Hall", "Plate", "Room", "Chamber", "Ambience", 
             "Cathedral", "Spring", "Nonlin"],
            # Quality/color modes  
            ["1970s", "1980s", "Now", "Vintage", "Modern", "Classic"],
            # Generic
            ["1", "2", "3", "4", "5", "6", "7", "8"],
            ["Low", "Medium", "High"],
            ["On", "Off"]
        ]
        
        for value_set in common_values:
            valid = []
            for val in value_set:
                try:
                    setattr(self.plugin, param_name, val)
                    if getattr(self.plugin, param_name) == val:
                        valid.append(val)
                except:
                    pass
            
            if len(valid) >= 2:  # Found at least 2 valid values
                return valid
        
        return None
    
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
    
    def _is_numeric_string(self, value: str) -> bool:
        """Check if string represents a number"""
        # Remove common units
        cleaned = value.replace('s', '').replace('ms', '').replace('Hz', '').replace('%', '').strip()
        try:
            float(cleaned)
            return True
        except:
            return False
    
    def _extract_string_format(self, value: str) -> str:
        """Extract format pattern from string value"""
        if ' s' in value:
            decimals = len(value.split('.')[1].split()[0]) if '.' in value else 0
            return f"%.{decimals}f s"
        elif ' ms' in value:
            return "%.0f ms"
        elif ' Hz' in value:
            return "%.0f Hz"
        elif '%' in value:
            return "%.0f%%"
        else:
            return "%s"
    
    def get_discovery_log(self) -> List[str]:
        """Get the discovery process log"""
        return self.discovery_log

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
                match = re.search(r'(\d+\.?\d*)', str(val))
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
