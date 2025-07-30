"""
Validate discoveries against known research data
"""

import json
from typing import Dict, Any, List
from pathlib import Path

class ResearchValidator:
    """Validate parameter discoveries against research data"""
    
    def __init__(self):
        self.research_data = self._load_research_data()
    
    def _load_research_data(self) -> Dict:
        """Load known plugin parameters from research"""
        research_path = Path(__file__).parent.parent / 'data' / 'research_data.json'
        if research_path.exists():
            with open(research_path, 'r') as f:
                return json.load(f)
        return {}
    
    def validate_discovery(self, plugin_name: str, discovered_params: Dict) -> Dict[str, Any]:
        """Validate discovered parameters against research data"""
        validation_result = {
            'plugin_name': plugin_name,
            'validation_score': 0.0,
            'matched_parameters': [],
            'missing_parameters': [],
            'extra_parameters': [],
            'format_mismatches': []
        }
        
        # Check if we have research data for this plugin
        plugin_key = self._normalize_plugin_name(plugin_name)
        if plugin_key not in self.research_data:
            validation_result['validation_score'] = -1  # No research data
            return validation_result
        
        research_params = self.research_data[plugin_key]
        discovered_names = set(k for k in discovered_params.keys() if not k.startswith('_'))
        research_names = set(research_params.keys())
        
        # Find matches and differences
        matched = discovered_names & research_names
        missing = research_names - discovered_names
        extra = discovered_names - research_names
        
        validation_result['matched_parameters'] = list(matched)
        validation_result['missing_parameters'] = list(missing)
        validation_result['extra_parameters'] = list(extra)
        
        # Check format/type matches
        for param in matched:
            discovered = discovered_params[param]
            expected = research_params[param]
            
            # Check type match
            if discovered.get('type') != expected.get('type'):
                validation_result['format_mismatches'].append({
                    'parameter': param,
                    'discovered_type': discovered.get('type'),
                    'expected_type': expected.get('type')
                })
            
            # Check format for string parameters
            if expected.get('format') and discovered.get('format') != expected['format']:
                validation_result['format_mismatches'].append({
                    'parameter': param,
                    'discovered_format': discovered.get('format'),
                    'expected_format': expected['format']
                })
        
        # Calculate validation score
        total_params = len(research_names)
        if total_params > 0:
            correct_params = len(matched) - len(validation_result['format_mismatches'])
            validation_result['validation_score'] = correct_params / total_params
        
        return validation_result
    
    def _normalize_plugin_name(self, plugin_name: str) -> str:
        """Normalize plugin name for comparison"""
        # Remove version numbers and extensions
        normalized = plugin_name.lower()
        normalized = normalized.replace('.vst3', '').replace('.au', '')
        normalized = normalized.replace('vintage', '').replace('verb', '')
        
        # Map to known research keys
        name_map = {
            'valhalla': 'vintageverb',
            'valhallaplate': 'plate',
            'valhallaroom': 'room',
            'vallhalladelay': 'delay'
        }
        
        for key, value in name_map.items():
            if key in normalized:
                return value
        
        return normalized