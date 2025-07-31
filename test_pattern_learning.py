#!/usr/bin/env python3
"""
Test the pattern learning system with ValhallaVintageVerb
"""

from pathlib import Path
from core import UniversalPluginDiscovery, ParameterCategorizer
from core.pattern_learner import PatternLearner
from core.validator_enhanced import EnhancedValidator
from core.learning_exporter import LearningExporter
import json

def test_pattern_learning():
    """Test the enhanced discovery with pattern learning"""
    print("Testing Pattern Learning System")
    print("="*50)
    
    # Initialize components
    pattern_learner = PatternLearner()
    learning_exporter = LearningExporter()
    
    # Test with VintageVerb
    plugin_path = "/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3"
    plugin_name = "ValhallaVintageVerb"
    
    print(f"\n1. Discovering parameters for {plugin_name}...")
    discovery = UniversalPluginDiscovery(plugin_path)
    params = discovery.discover_all()
    
    print(f"   Found {len(params)} parameters")
    
    # Apply pattern learning
    print("\n2. Enhancing with learned patterns...")
    enhanced_params = pattern_learner.enhance_discovery(params)
    
    # Validate parameters
    print("\n3. Validating parameter formats...")
    validator = EnhancedValidator(discovery.plugin)
    validation_results = validator.validate_all_parameters(enhanced_params)
    
    print(f"   Validated {validation_results['statistics']['validated']} parameters")
    print(f"   String numeric: {validation_results['statistics']['string_numeric']}")
    print(f"   Format requirements found: {len(validation_results['format_requirements'])}")
    
    # Categorize with intelligence
    print("\n4. Categorizing with effect knowledge...")
    categorizer = ParameterCategorizer()
    categorized = categorizer.categorize_with_intelligence(plugin_name, enhanced_params)
    
    if 'effect_type' in categorized:
        print(f"   Detected effect type: {categorized['effect_type']}")
    
    print(f"   Categories found: {list(categorized['categories'].keys())}")
    
    # Learn from discovery
    print("\n5. Learning from discovery...")
    learnings = pattern_learner.learn_from_discovery(plugin_name, enhanced_params)
    
    print(f"   New patterns: {learnings['new_patterns']}")
    print(f"   Confirmed patterns: {learnings['confirmed_patterns']}")
    if learnings.get('effect_type'):
        print(f"   Effect type learned: {learnings['effect_type']}")
    
    # Export results
    print("\n6. Exporting results...")
    # Extract only serializable data
    clean_params = {}
    for k, v in enhanced_params.items():
        if not k.startswith('_'):
            clean_params[k] = {
                'type': v.get('type'),
                'current_value': str(v.get('current_value', '')),
                'min': v.get('min'),
                'max': v.get('max'),
                'options': v.get('options'),
                'format': v.get('format'),
                'unit': v.get('unit')
            }
    
    # Clean categorized data
    clean_categorized = {
        'effect_type': categorized.get('effect_type'),
        'categories': categorized.get('categories', {}),
        'uncategorized': categorized.get('uncategorized', [])
    }
    
    discovery_data = {
        'parameters': clean_params,
        'categorized': clean_categorized,
        'validation_results': {
            'plugin_name': validation_results.get('plugin_name'),
            'total_parameters': validation_results.get('total_parameters'),
            'statistics': validation_results.get('statistics'),
            'format_requirements': validation_results.get('format_requirements', {}),
            'anomalies': validation_results.get('anomalies', [])
        },
        'effect_type': learnings.get('effect_type'),
        'format_requirements': validation_results.get('format_requirements', {})
    }
    
    export_path = learning_exporter.export_individual_discovery(plugin_name, discovery_data)
    print(f"   Exported to: {export_path}")
    
    # Show learning stats
    print("\n7. Learning Statistics:")
    stats = pattern_learner.get_learning_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Display some discovered patterns
    print("\n8. Sample Discovered Patterns:")
    if pattern_learner.learned_patterns['string_formats']:
        print("   String formats:")
        for param, fmt in list(pattern_learner.learned_patterns['string_formats'].items())[:3]:
            print(f"     {param}: {fmt}")
    
    # Test specific parameter - decay
    if 'decay' in params:
        print("\n9. Decay Parameter Analysis:")
        decay_info = params['decay']
        print(f"   Type: {decay_info.get('type')}")
        print(f"   Current value: {decay_info.get('current_value')}")
        print(f"   Format: {decay_info.get('format')}")
        
        if 'decay' in validation_results['validation_results']:
            decay_validation = validation_results['validation_results']['decay']
            if decay_validation.get('working_formats'):
                print(f"   Working formats: {decay_validation['working_formats']}")

if __name__ == "__main__":
    test_pattern_learning()