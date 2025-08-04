"""
Export discovery results for Stage 2 automated recording
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

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

class DiscoveryExporter:
    """Export parameter discoveries in various formats"""
    
    def __init__(self):
        self.export_dir = Path(__file__).parent.parent / 'data' / 'discoveries'
        self.export_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, 
                      plugin_name: str, 
                      parameters: Dict,
                      categorized: Dict,
                      test_matrix: Dict,
                      validation: Dict) -> str:
        """Export complete discovery to JSON format"""
        
        export_data = {
            'metadata': {
                'plugin_name': plugin_name,
                'discovery_date': datetime.now().isoformat(),
                'version': '1.0',
                'stage': 1
            },
            'parameters': parameters,
            'categorization': categorized,
            'test_matrix': test_matrix,
            'validation': validation,
            'recording_config': self._generate_recording_config(parameters, categorized)
        }
        
        # Clean data before export
        export_data = self._clean_export_data(export_data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{plugin_name}_{timestamp}_discovery.json"
        filepath = self.export_dir / filename
        
        # Write with safe encoder
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, cls=SafeJSONEncoder)
        
        return str(filepath)
    
    def _generate_recording_config(self, parameters: Dict, categorized: Dict) -> Dict:
        """Generate configuration for Stage 2 automated recording"""
        config = {
            'sample_rate': 48000,
            'bit_depth': 24,
            'recording_length_seconds': 3.0,
            'test_signals': [
                '01_impulse.wav',
                '04_exp_sweep_20_20k.wav',
                '07_white_noise.wav',
                '09_pink_burst_100ms.wav',
                '11_pure_tone_1000hz.wav'
            ],
            'parameter_settings': {}
        }
        
        # Generate parameter value sets for testing
        for category, info in categorized['categories'].items():
            if info['priority'] == 'critical':
                for param in info['parameters']:
                    param_info = parameters.get(param, {})
                    config['parameter_settings'][param] = self._generate_test_values(param_info)
        
        return config
    
    def _generate_test_values(self, param_info: Dict) -> List:
        """Generate test values for a parameter"""
        if param_info.get('type') == 'list' and param_info.get('valid_values'):
            return param_info['valid_values']
        elif param_info.get('range'):
            min_val, max_val = param_info['range']
            # Generate 5 test points
            return [
                min_val,
                min_val + (max_val - min_val) * 0.25,
                min_val + (max_val - min_val) * 0.5,
                min_val + (max_val - min_val) * 0.75,
                max_val
            ]
        else:
            return [param_info.get('current_value', 0)]
    
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