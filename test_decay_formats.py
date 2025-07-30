#!/usr/bin/env python3
"""
Test different decay parameter formats to verify which work
"""

from pedalboard import load_plugin

def test_decay_formats():
    """Test various formats for setting decay parameter"""
    print("="*60)
    print("DECAY PARAMETER FORMAT TESTING")
    print("="*60)
    
    plugin = load_plugin("/Library/Audio/Plug-Ins/VST3/ValhallaVintageVerb.vst3")
    
    # Get current value
    print(f"Current decay value: '{plugin.decay}'")
    print(f"Type: {type(plugin.decay)}")
    
    # Test different formats
    test_values = [
        # (value_to_set, description)
        (10.0, "Float 10.0"),
        ("10.0", "String '10.0'"),
        ("10", "String '10'"),
        ("10.00 s", "String '10.00 s' (correct format)"),
        ("10.0 s", "String '10.0 s'"),
        ("10 s", "String '10 s'"),
        (5.55, "Float 5.55"),
        ("5.55 s", "String '5.55 s' (correct format)"),
        ("5.5 s", "String '5.5 s'"),
        ("20.00 s", "String '20.00 s' (correct format)"),
    ]
    
    print("\nTesting different formats:")
    print("-"*50)
    
    for test_value, description in test_values:
        print(f"\nTesting: {description}")
        print(f"  Setting value: {repr(test_value)}")
        
        try:
            plugin.decay = test_value
            actual_value = plugin.decay
            print(f"  ✅ SUCCESS! Set to: '{actual_value}'")
            
            # Check if it matches expected format
            if isinstance(test_value, str) and test_value == actual_value:
                print(f"  ✅ Exact match!")
            elif isinstance(test_value, float):
                # Check if float was converted to string format
                expected_str = f"{test_value:.2f} s"
                if actual_value == expected_str:
                    print(f"  ✅ Float converted to '{expected_str}'")
                else:
                    print(f"  ⚠️  Float resulted in '{actual_value}'")
                    
        except Exception as e:
            print(f"  ❌ FAILED: {str(e)[:100]}...")
    
    # Test edge cases
    print("\n\nEdge case testing:")
    print("-"*50)
    
    edge_cases = [
        ("0.20 s", "Minimum value"),
        ("70.00 s", "Maximum value"),
        ("0.19 s", "Below minimum"),
        ("70.01 s", "Above maximum"),
        ("abc", "Invalid string"),
        (-1.0, "Negative float"),
    ]
    
    for test_value, description in edge_cases:
        print(f"\n{description}: {repr(test_value)}")
        try:
            plugin.decay = test_value
            print(f"  ✅ Set to: '{plugin.decay}'")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:80]}...")
    
    # Show all valid decay values sample
    print("\n\nSample of valid decay values:")
    print("-"*50)
    param = plugin.parameters['decay']
    valid_values = list(param.valid_values)
    print(f"First 10: {valid_values[:10]}")
    print(f"Last 10: {valid_values[-10:]}")
    print(f"Total valid values: {len(valid_values)}")

if __name__ == "__main__":
    test_decay_formats()