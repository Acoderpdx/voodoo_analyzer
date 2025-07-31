#!/usr/bin/env python3
"""
Test pattern learning with ValhallaDelay to see cross-plugin learning
"""

from pathlib import Path
from core import UniversalPluginDiscovery, ParameterCategorizer
from core.pattern_learner import PatternLearner
from core.validator_enhanced import EnhancedValidator
import json

def test_delay_learning():
    """Test learning system with delay plugin"""
    print("Testing Pattern Learning with ValhallaDelay")
    print("="*50)
    
    # Initialize components
    pattern_learner = PatternLearner()
    
    # Show current learning state
    print("\nCurrent Learning State:")
    stats = pattern_learner.get_learning_stats()
    print(f"  Plugins analyzed: {stats['plugins_analyzed']}")
    print(f"  Patterns learned: {stats['string_formats_learned']}")
    print(f"  Effect types: {stats['effect_types_identified']}")
    
    # Test with Delay
    plugin_path = "/Library/Audio/Plug-Ins/VST3/ValhallaDelay.vst3"
    plugin_name = "ValhallaDelay"
    
    print(f"\n1. Discovering {plugin_name}...")
    discovery = UniversalPluginDiscovery(plugin_path)
    params = discovery.discover_all()
    print(f"   Found {len(params)} parameters")
    
    # Enhance with patterns
    print("\n2. Applying learned patterns...")
    enhanced = pattern_learner.enhance_discovery(params)
    
    # Check if patterns were applied
    patterns_applied = 0
    for param, info in enhanced.items():
        if 'suggested_format' in info or 'learned_category' in info:
            patterns_applied += 1
    
    print(f"   Patterns applied to {patterns_applied} parameters")
    
    # Categorize
    print("\n3. Categorizing with intelligence...")
    categorizer = ParameterCategorizer()
    categorized = categorizer.categorize_with_intelligence(plugin_name, enhanced)
    
    if 'effect_type' in categorized:
        print(f"   Detected as: {categorized['effect_type']}")
    
    # Learn from this plugin
    print("\n4. Learning from discovery...")
    learnings = pattern_learner.learn_from_discovery(plugin_name, enhanced)
    print(f"   New patterns: {learnings['new_patterns']}")
    print(f"   Effect type: {learnings.get('effect_type')}")
    
    # Show what was learned
    print("\n5. Newly Learned Patterns:")
    if learnings['new_patterns'] > 0:
        # Check for new string formats
        for param, fmt in pattern_learner.learned_patterns['string_formats'].items():
            if param not in ['decay']:  # Skip already known
                print(f"   String format - {param}: {fmt}")
    
    # Final stats
    print("\n6. Updated Learning Statistics:")
    final_stats = pattern_learner.get_learning_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    test_delay_learning()