"""
Intelligent parameter categorization system
Groups parameters by function and testing needs
"""

from typing import Dict, List, Any
from pathlib import Path
import json
import re

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
        self.load_effect_knowledge()
    
    def load_effect_knowledge(self):
        """Load comprehensive effect parameter knowledge"""
        knowledge_path = Path('data/effect_knowledge.json')
        if knowledge_path.exists():
            with open(knowledge_path, 'r') as f:
                content = f.read()
                # Extract JSON from the markdown file
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                knowledge_data = json.loads(content[json_start:json_end])
                self.effect_knowledge = knowledge_data['audio_effect_parameters']
        else:
            self.effect_knowledge = {}
    
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
    
    def categorize_with_intelligence(self, plugin_name: str, parameters: Dict) -> Dict:
        """Enhanced categorization using effect knowledge"""
        # First, try to detect effect type
        effect_type = self._detect_plugin_type(plugin_name, parameters)
        
        if effect_type and '.' in effect_type:
            # Use effect-specific categorization
            return self._categorize_by_effect_type(effect_type, parameters)
        else:
            # Fall back to generic categorization
            return self.categorize_parameters(parameters)
    
    def _detect_plugin_type(self, plugin_name: str, parameters: Dict) -> str:
        """Detect plugin type from name and parameters"""
        param_names = set(p.lower() for p in parameters.keys() if not p.startswith('_'))
        plugin_name_lower = plugin_name.lower()
        
        # Check plugin name for obvious indicators
        name_indicators = {
            'reverb': 'time_based_effects.reverb',
            'delay': 'time_based_effects.delay',
            'chorus': 'modulation_effects.chorus',
            'flanger': 'modulation_effects.flanger',
            'phaser': 'modulation_effects.phaser',
            'compressor': 'dynamics.compressor',
            'limiter': 'dynamics.limiter',
            'eq': 'frequency_effects.parametric_eq',
            'filter': 'frequency_effects.filter',
            'distortion': 'distortion_saturation.distortion',
            'overdrive': 'distortion_saturation.overdrive',
            'plate': 'time_based_effects.reverb',
            'room': 'time_based_effects.reverb',
            'hall': 'time_based_effects.reverb'
        }
        
        for indicator, effect_type in name_indicators.items():
            if indicator in plugin_name_lower:
                return effect_type
        
        # Check against effect knowledge signatures
        for effect_category, effects in self.effect_knowledge.items():
            if effect_category == 'metadata':
                continue
            
            for effect_type, effect_data in effects.items():
                if 'core_parameters' in effect_data:
                    core_params = set(p.lower() for p in effect_data['core_parameters'].keys())
                    
                    # Check for parameter matches including variations
                    matches = 0
                    for core_param in core_params:
                        if core_param in param_names:
                            matches += 1
                        else:
                            # Check naming variations
                            param_data = effect_data['core_parameters'].get(core_param, {})
                            if 'naming_variations' in param_data:
                                variations = [v.lower() for v in param_data['naming_variations']]
                                if any(var in param_names for var in variations):
                                    matches += 1
                    
                    # If 70% of core parameters match, likely this effect type
                    if matches >= len(core_params) * 0.7:
                        return f"{effect_category}.{effect_type}"
        
        return None
    
    def _categorize_by_effect_type(self, effect_type: str, parameters: Dict) -> Dict:
        """Categorize based on known effect type patterns"""
        categorized = {
            'effect_type': effect_type,
            'categories': {},
            'uncategorized': [],
            'parameter_details': parameters
        }
        
        # Get effect knowledge
        effect_parts = effect_type.split('.')
        if len(effect_parts) == 2:
            category, subtype = effect_parts
            if category in self.effect_knowledge and subtype in self.effect_knowledge[category]:
                effect_data = self.effect_knowledge[category][subtype]
                
                # Categorize core parameters
                if 'core_parameters' in effect_data:
                    categorized['categories']['core'] = {
                        'parameters': [],
                        'priority': 'critical'
                    }
                    for param, data in effect_data['core_parameters'].items():
                        # Match with discovered parameters (handle naming variations)
                        matched = self._match_parameter(param, parameters, data.get('naming_variations', []))
                        if matched:
                            categorized['categories']['core']['parameters'].append(matched)
                
                # Categorize advanced parameters
                if 'advanced_parameters' in effect_data:
                    categorized['categories']['advanced'] = {
                        'parameters': [],
                        'priority': 'secondary'
                    }
                    for param, data in effect_data['advanced_parameters'].items():
                        matched = self._match_parameter(param, parameters, data.get('naming_variations', []))
                        if matched:
                            categorized['categories']['advanced']['parameters'].append(matched)
                
                # Find uncategorized parameters
                categorized_params = set()
                for cat_data in categorized['categories'].values():
                    categorized_params.update(cat_data['parameters'])
                
                for param in parameters:
                    if not param.startswith('_') and param not in categorized_params:
                        categorized['uncategorized'].append(param)
        
        return categorized
    
    def _match_parameter(self, knowledge_param: str, discovered_params: Dict, variations: List[str]) -> str:
        """Match a knowledge parameter with discovered parameters"""
        # Direct match (case insensitive)
        for param in discovered_params:
            if param.lower() == knowledge_param.lower():
                return param
        
        # Check variations
        for variation in variations:
            for param in discovered_params:
                if param.lower() == variation.lower():
                    return param
        
        # Fuzzy matching for common patterns
        knowledge_lower = knowledge_param.lower()
        for param in discovered_params:
            param_lower = param.lower()
            # Check if one contains the other
            if knowledge_lower in param_lower or param_lower in knowledge_lower:
                return param
            # Check common abbreviations
            if self._is_abbreviation_match(knowledge_lower, param_lower):
                return param
        
        return None
    
    def _is_abbreviation_match(self, term1: str, term2: str) -> bool:
        """Check if terms are abbreviations of each other"""
        abbrev_map = {
            'freq': 'frequency',
            'mod': 'modulation',
            'fb': 'feedback',
            'hpf': 'highpass',
            'lpf': 'lowpass',
            'bpf': 'bandpass',
            'reso': 'resonance',
            'amp': 'amplitude',
            'env': 'envelope'
        }
        
        for short, full in abbrev_map.items():
            if (short in term1 and full in term2) or (short in term2 and full in term1):
                return True
        
        return False