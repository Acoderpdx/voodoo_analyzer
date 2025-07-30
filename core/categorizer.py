"""
Intelligent parameter categorization system
Groups parameters by function and testing needs
"""

from typing import Dict, List, Any

class ParameterCategorizer:
    """Categorize parameters by type and function"""
    
    def __init__(self):
        self.categories = {
            'reverb_core': {
                'keywords': ['mix', 'decay', 'size', 'room', 'predelay'],
                'priority': 'critical'
            },
            'tone_shaping': {
                'keywords': ['freq', 'frequency', 'cut', 'shelf', 'eq', 'filter', 'damp'],
                'priority': 'secondary'
            },
            'modulation': {
                'keywords': ['mod', 'rate', 'depth', 'lfo', 'chorus', 'vibrato'],
                'priority': 'modulation'
            },
            'diffusion': {
                'keywords': ['diff', 'diffusion', 'density', 'thick'],
                'priority': 'secondary'
            },
            'algorithm': {
                'keywords': ['mode', 'type', 'color', 'model', 'algorithm'],
                'priority': 'critical'
            },
            'dynamics': {
                'keywords': ['attack', 'release', 'envelope', 'compress'],
                'priority': 'secondary'
            },
            'spatial': {
                'keywords': ['width', 'stereo', 'pan', 'spread'],
                'priority': 'secondary'
            }
        }
    
    def categorize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize all parameters by function"""
        categorized = {
            'categories': {},
            'uncategorized': [],
            'parameter_details': {}
        }
        
        # Skip metadata
        param_items = [(k, v) for k, v in parameters.items() if not k.startswith('_')]
        
        for param_name, param_info in param_items:
            category = self._find_category(param_name, param_info)
            
            if category:
                if category not in categorized['categories']:
                    categorized['categories'][category] = {
                        'parameters': [],
                        'priority': self.categories[category]['priority']
                    }
                categorized['categories'][category]['parameters'].append(param_name)
            else:
                categorized['uncategorized'].append(param_name)
            
            # Store parameter details
            categorized['parameter_details'][param_name] = param_info
        
        return categorized
    
    def _find_category(self, param_name: str, param_info: Dict) -> str:
        """Find the best category for a parameter"""
        param_lower = param_name.lower()
        
        # Check each category's keywords
        for category, info in self.categories.items():
            for keyword in info['keywords']:
                if keyword in param_lower:
                    return category
        
        # Additional heuristics based on type/range
        if param_info.get('unit') == 'ms' and param_info.get('range'):
            if param_info['range'][1] > 100:  # Likely delay/reverb time
                return 'reverb_core'
        
        if param_info.get('type') == 'list':
            return 'algorithm'
        
        return None
    
    def generate_test_matrix(self, categorized: Dict) -> Dict[str, List]:
        """Generate optimal test sequences based on categories"""
        test_matrix = {
            'phase_1_core': [],
            'phase_2_modulation': [],
            'phase_3_tone': [],
            'phase_4_spatial': []
        }
        
        # Phase 1: Core reverb parameters
        if 'reverb_core' in categorized['categories']:
            test_matrix['phase_1_core'].extend([
                'baseline_measurement',
                'decay_sweep',
                'size_variations'
            ])
        
        # Phase 2: Modulation testing
        if 'modulation' in categorized['categories']:
            test_matrix['phase_2_modulation'].extend([
                'modulation_off',
                'modulation_sweep',
                'rate_variations'
            ])
        
        # Phase 3: Tone shaping
        if 'tone_shaping' in categorized['categories']:
            test_matrix['phase_3_tone'].extend([
                'frequency_sweep',
                'filter_variations'
            ])
        
        # Phase 4: Spatial parameters
        if 'spatial' in categorized['categories']:
            test_matrix['phase_4_spatial'].extend([
                'stereo_width_test',
                'panning_test'
            ])
        
        # Add algorithm testing if present
        if 'algorithm' in categorized['categories']:
            test_matrix['phase_1_core'].insert(0, 'mode_comparison')
        
        return test_matrix