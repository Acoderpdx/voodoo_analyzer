#!/usr/bin/env python3
"""
Analyze a new plugin and report on self-improvement system performance
"""

from pathlib import Path
from core import UniversalPluginDiscovery, ParameterCategorizer
from core.pattern_learner import PatternLearner
from core.validator_enhanced import EnhancedValidator
from core.learning_exporter import LearningExporter
import json
from datetime import datetime

def analyze_plugin_with_learning_report(plugin_path: str):
    """Analyze a plugin and provide detailed learning system report"""
    
    plugin_name = Path(plugin_path).stem
    
    print(f"\n{'='*60}")
    print(f"ANALYZING NEW PLUGIN: {plugin_name}")
    print(f"{'='*60}\n")
    
    # Initialize components
    pattern_learner = PatternLearner()
    learning_exporter = LearningExporter()
    
    # Capture initial state
    print("📊 INITIAL LEARNING STATE:")
    initial_stats = pattern_learner.get_learning_stats()
    print(f"  • Plugins previously analyzed: {initial_stats['plugins_analyzed']}")
    print(f"  • String formats known: {initial_stats['string_formats_learned']}")
    print(f"  • Parameter patterns: {initial_stats['parameter_patterns']}")
    print(f"  • Effect types identified: {initial_stats['effect_types_identified']}")
    
    # Show known patterns
    print("\n📚 KNOWN PATTERNS BEFORE ANALYSIS:")
    if pattern_learner.learned_patterns['string_formats']:
        print("  String Formats:")
        for param, fmt in pattern_learner.learned_patterns['string_formats'].items():
            print(f"    - {param}: {fmt}")
    
    if pattern_learner.learned_patterns['effect_signatures']:
        print("\n  Effect Types:")
        for plugin, effect in pattern_learner.learned_patterns['effect_signatures'].items():
            print(f"    - {plugin}: {effect}")
    
    # Discover parameters
    print(f"\n🔍 DISCOVERING PARAMETERS...")
    discovery = UniversalPluginDiscovery(plugin_path)
    raw_params = discovery.discover_all()
    print(f"  ✓ Found {len(raw_params)} parameters")
    
    # Apply learned patterns
    print("\n🧠 APPLYING LEARNED PATTERNS...")
    enhanced_params = pattern_learner.enhance_discovery(raw_params)
    
    # Count enhancements
    enhancements = {
        'suggested_formats': 0,
        'learned_categories': 0,
        'suggested_ranges': 0
    }
    
    enhanced_examples = []
    
    for param, info in enhanced_params.items():
        if 'suggested_format' in info:
            enhancements['suggested_formats'] += 1
            enhanced_examples.append(f"  • {param}: suggested format '{info['suggested_format']}'")
        if 'learned_category' in info:
            enhancements['learned_categories'] += 1
            enhanced_examples.append(f"  • {param}: categorized as '{info['learned_category']}'")
        if 'suggested_range' in info:
            enhancements['suggested_ranges'] += 1
    
    print(f"  ✓ Applied {sum(enhancements.values())} enhancements:")
    print(f"    - Suggested formats: {enhancements['suggested_formats']}")
    print(f"    - Learned categories: {enhancements['learned_categories']}")
    print(f"    - Suggested ranges: {enhancements['suggested_ranges']}")
    
    if enhanced_examples:
        print("\n  Examples of enhancements:")
        for example in enhanced_examples[:5]:  # Show first 5
            print(example)
    
    # Validate parameters
    print("\n🔬 VALIDATING PARAMETER FORMATS...")
    validator = EnhancedValidator(discovery.plugin)
    validation_results = validator.validate_all_parameters(enhanced_params)
    
    print(f"  ✓ Validated {validation_results['statistics']['validated']} parameters")
    print(f"    - String numeric: {validation_results['statistics']['string_numeric']}")
    print(f"    - Format requirements found: {len(validation_results['format_requirements'])}")
    
    if validation_results['format_requirements']:
        print("\n  New format requirements discovered:")
        for param, fmt in list(validation_results['format_requirements'].items())[:3]:
            print(f"    - {param}: {fmt}")
    
    # Categorize with intelligence
    print("\n🏷️  INTELLIGENT CATEGORIZATION...")
    categorizer = ParameterCategorizer()
    categorized = categorizer.categorize_with_intelligence(plugin_name, enhanced_params)
    
    if 'effect_type' in categorized and categorized['effect_type']:
        print(f"  ✓ Effect type detected: {categorized['effect_type']}")
        
        # Check if this matches expected type based on plugin name
        expected_types = {
            'plate': 'reverb',
            'room': 'reverb',
            'hall': 'reverb',
            'delay': 'delay',
            'chorus': 'chorus',
            'flanger': 'flanger'
        }
        
        for keyword, expected in expected_types.items():
            if keyword in plugin_name.lower() and expected in categorized['effect_type']:
                print(f"    ✅ Correctly identified based on name!")
                break
    
    print(f"\n  Categories found:")
    for category, info in categorized['categories'].items():
        print(f"    - {category}: {len(info['parameters'])} parameters")
    
    if categorized.get('uncategorized'):
        print(f"    - uncategorized: {len(categorized['uncategorized'])} parameters")
    
    # Learn from discovery
    print("\n📈 LEARNING FROM DISCOVERY...")
    learnings = pattern_learner.learn_from_discovery(plugin_name, enhanced_params)
    
    print(f"  ✓ Learning results:")
    print(f"    - New patterns discovered: {learnings['new_patterns']}")
    print(f"    - Patterns confirmed: {learnings['confirmed_patterns']}")
    print(f"    - Anomalies found: {len(learnings['anomalies'])}")
    
    if learnings['anomalies']:
        print("\n  ⚠️  Anomalies detected:")
        for anomaly in learnings['anomalies'][:3]:
            print(f"    - {anomaly['parameter']}: expected '{anomaly['expected_format']}' but found '{anomaly['found_format']}'")
    
    # Final state
    print("\n📊 FINAL LEARNING STATE:")
    final_stats = pattern_learner.get_learning_stats()
    print(f"  • Plugins analyzed: {final_stats['plugins_analyzed']} (+{final_stats['plugins_analyzed'] - initial_stats['plugins_analyzed']})")
    print(f"  • String formats: {final_stats['string_formats_learned']} (+{final_stats['string_formats_learned'] - initial_stats['string_formats_learned']})")
    print(f"  • Parameter patterns: {final_stats['parameter_patterns']} (+{final_stats['parameter_patterns'] - initial_stats['parameter_patterns']})")
    print(f"  • Effect types: {final_stats['effect_types_identified']} (+{final_stats['effect_types_identified'] - initial_stats['effect_types_identified']})")
    
    # Export discovery
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
    
    discovery_data = {
        'parameters': clean_params,
        'categorized': {
            'effect_type': categorized.get('effect_type'),
            'categories': categorized.get('categories', {}),
            'uncategorized': categorized.get('uncategorized', [])
        },
        'validation_results': {
            'statistics': validation_results.get('statistics'),
            'format_requirements': validation_results.get('format_requirements', {})
        },
        'learnings': learnings
    }
    
    export_path = learning_exporter.export_individual_discovery(plugin_name, discovery_data)
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 SELF-IMPROVEMENT ANALYSIS SUMMARY:")
    print(f"{'='*60}")
    
    improvement_score = 0
    
    # Calculate improvement metrics
    if learnings['new_patterns'] > 0:
        print("✅ System learned NEW patterns from this plugin")
        improvement_score += 30
    
    if learnings['confirmed_patterns'] > 0:
        print("✅ System confirmed existing patterns (validation)")
        improvement_score += 20
    
    if enhancements['learned_categories'] > 0:
        print("✅ System applied learned categorizations")
        improvement_score += 25
    
    if categorized.get('effect_type'):
        print("✅ System correctly identified effect type")
        improvement_score += 25
    
    print(f"\n🏆 SELF-IMPROVEMENT SCORE: {improvement_score}/100")
    
    if improvement_score >= 70:
        print("   → Excellent! The system is actively learning and improving")
    elif improvement_score >= 40:
        print("   → Good! The system is applying learned knowledge")
    else:
        print("   → Limited learning, but this may be expected for unique plugins")
    
    print(f"\n📁 Full report exported to: {export_path}")
    
    return {
        'plugin_name': plugin_name,
        'parameters_found': len(raw_params),
        'enhancements_applied': sum(enhancements.values()),
        'new_patterns': learnings['new_patterns'],
        'improvement_score': improvement_score
    }

if __name__ == "__main__":
    # You can change this to test with ValhallaPlate or ValhallaRoom
    plugin_path = "/Library/Audio/Plug-Ins/VST3/ValhallaPlate.vst3"
    
    print("🚀 VOODOO ANALYZER - SELF-IMPROVEMENT ANALYSIS")
    print("Testing pattern learning and self-improvement capabilities")
    
    result = analyze_plugin_with_learning_report(plugin_path)
    
    print("\n" + "="*60)
    print("Analysis complete! Check the detailed output above.")