"""
Pattern learning system that improves with each discovery
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Set
import re
from datetime import datetime
from .learning_exporter import SafeJSONEncoder

class PatternLearner:
    """Learns and applies patterns from plugin discoveries"""
    
    def __init__(self):
        self.patterns_file = Path('data/learned_patterns.json')
        self.effect_knowledge_file = Path('data/effect_knowledge.json')
        self.load_all_knowledge()
    
    def load_all_knowledge(self):
        """Load both effect knowledge and learned patterns"""
        # Load comprehensive effect knowledge
        with open(self.effect_knowledge_file, 'r') as f:
            content = f.read()
            # Extract JSON from the markdown file
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            self.effect_knowledge = json.loads(content[json_start:json_end])
        
        # Load previously learned patterns
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                self.learned_patterns = json.load(f)
        else:
            self.learned_patterns = {
                'string_formats': {},      # e.g., "decay": "%.2f s"
                'parameter_patterns': {},  # e.g., "delay.*ms": "time_ms"
                'range_patterns': {},      # e.g., "feedback": [0, 100]
                'naming_maps': {},         # e.g., "moddepth": "modulation_depth"
                'effect_signatures': {},   # patterns that identify effect types
                'plugin_history': {}       # track analyzed plugins
            }
    
    def learn_from_discovery(self, plugin_name: str, parameters: Dict) -> Dict:
        """Extract patterns from a new discovery"""
        learnings = {
            'new_patterns': 0,
            'confirmed_patterns': 0,
            'anomalies': [],
            'effect_type': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Record plugin in history
        self.learned_patterns['plugin_history'][plugin_name] = {
            'timestamp': learnings['timestamp'],
            'parameter_count': len(parameters)
        }
        
        for param_name, param_info in parameters.items():
            if param_name.startswith('_'):
                continue
            
            # Learn string formats
            if param_info.get('format'):
                if param_name not in self.learned_patterns['string_formats']:
                    self.learned_patterns['string_formats'][param_name] = param_info['format']
                    learnings['new_patterns'] += 1
                elif self.learned_patterns['string_formats'][param_name] == param_info['format']:
                    learnings['confirmed_patterns'] += 1
                else:
                    learnings['anomalies'].append({
                        'parameter': param_name,
                        'expected_format': self.learned_patterns['string_formats'][param_name],
                        'found_format': param_info['format']
                    })
            
            # Learn parameter patterns
            self._learn_parameter_pattern(param_name, param_info)
            
            # Learn range patterns
            if 'min' in param_info and 'max' in param_info:
                range_key = f"{param_name}_range"
                if range_key not in self.learned_patterns['range_patterns']:
                    self.learned_patterns['range_patterns'][range_key] = [param_info['min'], param_info['max']]
                    learnings['new_patterns'] += 1
        
        # Detect effect type from parameters
        effect_type = self._detect_effect_type(plugin_name, parameters)
        if effect_type:
            self.learned_patterns['effect_signatures'][plugin_name] = effect_type
            learnings['effect_type'] = effect_type
        
        # Save updated patterns
        self.save_patterns()
        return learnings
    
    def _learn_parameter_pattern(self, param_name: str, param_info: Dict):
        """Learn patterns from parameter names and types"""
        lower_name = param_name.lower()
        
        # Common parameter pattern mappings
        pattern_mappings = {
            r'.*rate.*': 'modulation_rate',
            r'.*depth.*': 'modulation_depth',
            r'.*feedback.*': 'feedback',
            r'.*mix.*': 'wet_dry_mix',
            r'.*time.*': 'time_parameter',
            r'.*freq.*': 'frequency',
            r'.*gain.*': 'gain',
            r'.*threshold.*': 'threshold',
            r'.*attack.*': 'envelope_attack',
            r'.*release.*': 'envelope_release',
            r'.*decay.*': 'decay_time',
            r'.*cutoff.*': 'filter_cutoff',
            r'.*resonance.*': 'filter_resonance',
            r'.*drive.*': 'saturation_drive',
            r'.*width.*': 'stereo_width'
        }
        
        for pattern, category in pattern_mappings.items():
            if re.match(pattern, lower_name):
                if pattern not in self.learned_patterns['parameter_patterns']:
                    self.learned_patterns['parameter_patterns'][pattern] = category
                break
    
    def _detect_effect_type(self, plugin_name: str, parameters: Dict) -> str:
        """Detect effect type from parameters and name"""
        param_names = set(p.lower() for p in parameters.keys() if not p.startswith('_'))
        plugin_name_lower = plugin_name.lower()
        
        # Check plugin name first for obvious indicators
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
            'overdrive': 'distortion_saturation.overdrive'
        }
        
        for indicator, effect_type in name_indicators.items():
            if indicator in plugin_name_lower:
                return effect_type
        
        # Check against effect knowledge signatures
        for effect_category, effects in self.effect_knowledge['audio_effect_parameters'].items():
            if effect_category == 'metadata':
                continue
            
            for effect_type, effect_data in effects.items():
                if 'core_parameters' in effect_data:
                    core_params = set(p.lower() for p in effect_data['core_parameters'].keys())
                    
                    # Check parameter names and variations
                    matches = 0
                    for core_param in core_params:
                        # Check exact match
                        if core_param in param_names:
                            matches += 1
                        else:
                            # Check variations
                            if 'naming_variations' in effect_data['core_parameters'].get(core_param, {}):
                                variations = [v.lower() for v in effect_data['core_parameters'][core_param]['naming_variations']]
                                if any(var in param_names for var in variations):
                                    matches += 1
                    
                    # If 70% of core parameters match, likely this effect type
                    if matches >= len(core_params) * 0.7:
                        return f"{effect_category}.{effect_type}"
        
        return None
    
    def enhance_discovery(self, parameters: Dict) -> Dict:
        """Apply learned patterns to enhance parameter discovery"""
        enhanced = parameters.copy()
        
        for param_name, param_info in parameters.items():
            if param_name.startswith('_'):
                continue
                
            # Apply format patterns
            if param_name in self.learned_patterns['string_formats']:
                enhanced[param_name]['suggested_format'] = self.learned_patterns['string_formats'][param_name]
            
            # Apply range patterns
            range_key = f"{param_name}_range"
            if range_key in self.learned_patterns['range_patterns']:
                suggested_range = self.learned_patterns['range_patterns'][range_key]
                enhanced[param_name]['suggested_range'] = {
                    'min': suggested_range[0],
                    'max': suggested_range[1]
                }
            
            # Apply parameter categorization
            lower_name = param_name.lower()
            for pattern, category in self.learned_patterns['parameter_patterns'].items():
                if re.match(pattern, lower_name):
                    enhanced[param_name]['learned_category'] = category
                    break
        
        return enhanced
    
    def get_effect_knowledge(self, effect_type: str) -> Dict:
        """Get knowledge for a specific effect type"""
        if not effect_type or '.' not in effect_type:
            return {}
        
        category, subtype = effect_type.split('.', 1)
        
        if category in self.effect_knowledge['audio_effect_parameters']:
            if subtype in self.effect_knowledge['audio_effect_parameters'][category]:
                return self.effect_knowledge['audio_effect_parameters'][category][subtype]
        
        return {}
    
    def save_patterns(self):
        """Save learned patterns to file"""
        self.patterns_file.parent.mkdir(exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2, cls=SafeJSONEncoder)
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learned patterns"""
        return {
            'plugins_analyzed': len(self.learned_patterns['plugin_history']),
            'string_formats_learned': len(self.learned_patterns['string_formats']),
            'parameter_patterns': len(self.learned_patterns['parameter_patterns']),
            'range_patterns': len(self.learned_patterns['range_patterns']),
            'effect_types_identified': len(self.learned_patterns['effect_signatures'])
        }