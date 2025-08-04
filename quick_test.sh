#!/bin/bash
# Quick test commands for Voodoo Analyzer

echo "=== VOODOO ANALYZER QUICK TEST ==="
echo

# Change to app directory
cd "$(dirname "$0")"

# Test options
echo "Choose test option:"
echo "1) Run main app (GUI)"
echo "2) Test single plugin analysis"
echo "3) Generate analysis report"
echo "4) Show all discoveries"
echo "5) Run with specific plugin path"
echo

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "Starting main app..."
        /opt/anaconda3/bin/python main.py
        ;;
    2)
        echo "Testing single plugin analysis..."
        /opt/anaconda3/bin/python analyze_new_plugin.py
        ;;
    3)
        echo "Generating comprehensive report..."
        /opt/anaconda3/bin/python generate_full_analysis_report.py
        ;;
    4)
        echo "Showing all discoveries..."
        /opt/anaconda3/bin/python show_discoveries.py
        ;;
    5)
        read -p "Enter plugin path: " plugin_path
        /opt/anaconda3/bin/python -c "
from core import UniversalPluginDiscovery
from pprint import pprint
discovery = UniversalPluginDiscovery('$plugin_path')
results = discovery.discover_all()
print(f'\\nDiscovered {len(results)-1} parameters:')
for name, info in results.items():
    if not name.startswith('_'):
        print(f'  {name}: {info.get(\"type\")} - {info.get(\"unit\", \"no unit\")} - range: {info.get(\"range\", \"unknown\")}')
"
        ;;
    *)
        echo "Invalid choice. Running main app..."
        /opt/anaconda3/bin/python main.py
        ;;
esac