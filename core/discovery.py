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
        
        # Method 1: Direct attribute inspection
        for attr in dir(self.plugin):
            if not attr.startswith('_') and not callable(getattr(self.plugin, attr, None)):
                try:
                    # Test if it's a parameter by trying to read it
                    value = getattr(self.plugin, attr)
                    param_names.append(attr)
                except:
                    pass
        
        # Method 2: Check for common parameter patterns
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
            
            # Detect parameter type and format
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
        
        # Try to find range by testing values
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
        """Detect parameter unit from name"""
        param_lower = param_name.lower()
        
        unit_patterns = {
            'hz': ['freq', 'frequency', 'cutoff', 'highfreq', 'lowfreq'],
            'ms': ['delay', 'predelay', 'attack', 'release', 'hold'],
            's': ['decay', 'time', 'reverb', 'rt60'],
            'db': ['gain', 'level', 'volume', 'shelf', 'boost', 'cut'],
            '%': ['mix', 'depth', 'amount', 'diffusion', 'feedback', 'width']
        }
        
        for unit, patterns in unit_patterns.items():
            for pattern in patterns:
                if pattern in param_lower:
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