"""
Enhanced validator that tests parameter behaviors and formats
"""
from typing import Dict, List, Any, Optional
import logging

class EnhancedValidator:
    """Validate and test parameter behaviors"""
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.test_results = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
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
    
    def _validate_numeric_parameter(self, param_name: str, param_info: Dict) -> Dict:
        """Validate numeric parameter ranges and behavior"""
        result = {
            'range_valid': True,
            'edge_cases': {}
        }
        
        try:
            original = getattr(self.plugin, param_name)
            
            # Test minimum
            if 'min' in param_info:
                try:
                    setattr(self.plugin, param_name, param_info['min'])
                    actual = getattr(self.plugin, param_name)
                    result['edge_cases']['min'] = {
                        'set': param_info['min'],
                        'actual': actual,
                        'valid': abs(actual - param_info['min']) < 0.001
                    }
                except:
                    result['edge_cases']['min'] = {'valid': False}
            
            # Test maximum
            if 'max' in param_info:
                try:
                    setattr(self.plugin, param_name, param_info['max'])
                    actual = getattr(self.plugin, param_name)
                    result['edge_cases']['max'] = {
                        'set': param_info['max'],
                        'actual': actual,
                        'valid': abs(actual - param_info['max']) < 0.001
                    }
                except:
                    result['edge_cases']['max'] = {'valid': False}
            
            # Restore
            setattr(self.plugin, param_name, original)
            
        except Exception as e:
            result['error'] = str(e)
            result['range_valid'] = False
        
        return result
    
    def _validate_choice_parameter(self, param_name: str, param_info: Dict) -> Dict:
        """Validate choice parameter options"""
        result = {
            'all_options_valid': True,
            'invalid_options': []
        }
        
        if 'options' not in param_info:
            result['error'] = 'No options found'
            return result
        
        try:
            original = getattr(self.plugin, param_name)
            
            for option in param_info['options']:
                try:
                    setattr(self.plugin, param_name, option)
                    actual = getattr(self.plugin, param_name)
                    if str(actual) != str(option):
                        result['invalid_options'].append(option)
                        result['all_options_valid'] = False
                except:
                    result['invalid_options'].append(option)
                    result['all_options_valid'] = False
            
            # Restore
            setattr(self.plugin, param_name, original)
            
        except Exception as e:
            result['error'] = str(e)
            result['all_options_valid'] = False
        
        return result
    
    def validate_all_parameters(self, parameters: Dict) -> Dict:
        """Validate all parameters and return comprehensive report"""
        validation_report = {
            'plugin_name': self.plugin.__class__.__name__,
            'total_parameters': len(parameters),
            'validation_results': {},
            'format_requirements': {},
            'anomalies': [],
            'statistics': {
                'validated': 0,
                'string_numeric': 0,
                'numeric': 0,
                'choice': 0,
                'boolean': 0
            }
        }
        
        for param_name, param_info in parameters.items():
            if param_name.startswith('_'):
                continue
            
            # Validate format
            format_result = self.validate_parameter_format(param_name, param_info)
            validation_report['validation_results'][param_name] = format_result
            validation_report['statistics']['validated'] += 1
            
            # Track parameter types
            param_type = param_info.get('type', 'unknown')
            if param_type in validation_report['statistics']:
                validation_report['statistics'][param_type] += 1
            
            # Determine required format for string_numeric
            if param_type == 'string_numeric' and format_result.get('working_formats'):
                # Prefer the most specific working format
                preferred_order = [
                    'string_with_unit_space',
                    'string_two_decimal',
                    'string_one_decimal',
                    'string_plain',
                    'float'
                ]
                
                for fmt in preferred_order:
                    if fmt in format_result['working_formats']:
                        validation_report['format_requirements'][param_name] = fmt
                        break
            
            # Flag anomalies
            if format_result.get('format_tests'):
                failed_tests = [fmt for fmt, res in format_result['format_tests'].items() 
                               if not res.get('success', False)]
                if len(failed_tests) > len(format_result['format_tests']) / 2:
                    validation_report['anomalies'].append({
                        'parameter': param_name,
                        'issue': 'Most format tests failed',
                        'failed_formats': failed_tests
                    })
        
        return validation_report
    
    def test_parameter_interaction(self, param1: str, param2: str, parameters: Dict) -> Dict:
        """Test if parameters interact with each other"""
        result = {
            'parameters': [param1, param2],
            'interaction_detected': False,
            'details': {}
        }
        
        try:
            # Store original values
            orig1 = getattr(self.plugin, param1)
            orig2 = getattr(self.plugin, param2)
            
            # Test if changing param1 affects param2
            if 'min' in parameters[param1] and 'max' in parameters[param1]:
                test_val = (parameters[param1]['min'] + parameters[param1]['max']) / 2
                setattr(self.plugin, param1, test_val)
                new_val2 = getattr(self.plugin, param2)
                
                if str(new_val2) != str(orig2):
                    result['interaction_detected'] = True
                    result['details']['param1_affects_param2'] = True
            
            # Restore
            setattr(self.plugin, param1, orig1)
            setattr(self.plugin, param2, orig2)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result