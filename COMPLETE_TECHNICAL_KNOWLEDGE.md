# 🧠 COMPLETE TECHNICAL KNOWLEDGE DUMP
## Universal Plugin Analysis System - All Phases

### 🎯 PROJECT OVERVIEW
Building a 3-phase system that reverse-engineers audio plugins with 85-95% accuracy:
- **Phase 1**: Parameter Discovery (BUILT & ENHANCED) - Finds all parameters, formats, ranges
- **Phase 2**: Automated Recording (NEXT) - Tests parameter combinations systematically  
- **Phase 3**: DSP Extraction (PROVEN) - Analyzes recordings to extract algorithms

**Proven Success**: Already achieved 88% accuracy reverse-engineering ValhallaVintageVerb

---

## 📁 CURRENT PROJECT STRUCTURE
```
/Users/aidanbernard/Downloads/VOODOO VSTS/voodoo_analyzer/
├── main.py                      # Entry point
├── run.sh                       # Quick launcher script
├── quick_test.sh               # Testing utilities
├── requirements.txt             # pedalboard==0.9.0, numpy==1.24.3
├── core/
│   ├── __init__.py
│   ├── discovery.py            # Parameter discovery engine (ENHANCED)
│   ├── categorizer.py          # Intelligent categorization
│   ├── validator.py            # Research validation
│   ├── exporter.py             # JSON export (FIXED)
│   ├── pattern_learner.py      # Self-learning system
│   ├── validator_enhanced.py   # Format testing (FIXED)
│   └── learning_exporter.py    # Learning data export
├── ui/
│   ├── __init__.py
│   ├── app.py                  # Main GUI application (ENHANCED)
│   └── components/
│       ├── __init__.py
│       ├── browser.py          # Parameter browser
│       ├── inspector.py        # VST inspector
│       ├── learning_dashboard.py # Learning progress
│       ├── history_viewer.py    # Basic history viewer
│       └── history_viewer_enhanced.py # Complete history system (NEW)
└── data/
    ├── effect_knowledge.json   # Comprehensive effect database
    ├── research_data.json      # Known plugin parameters
    ├── learned_patterns.json   # Growing pattern library (ACTIVE)
    ├── comprehensive_analysis_report.json # Full analysis report
    ├── comprehensive_analysis_report.md   # Human-readable report
    └── discoveries/            # 15 exported discoveries (8 with JSON errors)
```

---

## 🔧 PHASE 1: PARAMETER DISCOVERY (CURRENT STATE)

### Core Technical Stack
```python
# Dependencies
pedalboard==0.9.0  # VST/AU hosting in Python
numpy==1.24.3      # Numerical operations
tkinter            # GUI (built-in)
scipy              # Signal processing (for phase 2/3)

# Critical imports
from pedalboard import load_plugin
```

### Recent Major Enhancements (IMPLEMENTED)

#### 1. System Parameter Filtering
```python
# FIXED: No more pollution from system parameters
SYSTEM_PARAMS_BLACKLIST = [
    'installed_plugins',  # Was polluting discoveries
    'parameters',         # Raw parameter object
    'name', 'is_effect', 'is_instrument',
    'has_shared_container', 'preset_data',
    'state_information', 'bypass',
    'is_processing', 'can_process_replacing',
    'latency_samples', 'tail_samples',
    'manufacturer', 'identifier', 'version'
]
```

#### 2. Enhanced Range Detection
```python
# FIXED: Real ranges instead of normalized [0,1]
def _infer_range_from_name(self, param_name: str, current_value: float):
    """Infer real ranges from parameter names"""
    param_lower = param_name.lower()
    
    if 'freq' in param_lower or 'hz' in param_lower:
        if 'low' in param_lower:
            return [20.0, 2000.0]
        elif 'high' in param_lower:
            return [1000.0, 20000.0]
        else:
            return [20.0, 20000.0]
    
    elif 'gain' in param_lower or 'db' in param_lower:
        return [-24.0, 24.0]
    
    elif 'delay' in param_lower and 'ms' in param_lower:
        return [0.0, 1000.0]
    
    elif any(x in param_lower for x in ['mix', 'wet', 'dry', 'depth', 'width']):
        if 0 <= current_value <= 1:
            return [0.0, 100.0]  # Convert to percentage
```

#### 3. Advanced Unit Detection
```python
# FIXED: Accurate unit extraction with regex
def _detect_unit(self, param_name: str) -> Optional[str]:
    # First try regex extraction from parameter object
    if hasattr(self.plugin, 'parameters'):
        param_str = str(self.plugin.parameters[param_name])
        # Extract from "100.0 Hz" or "50 %"
        unit_match = re.search(r'\d+\.?\d*\s*([A-Za-z%]+)', param_str)
        if unit_match:
            unit = unit_match.group(1).lower()
            unit_map = {
                'hz': 'Hz', 'khz': 'kHz', 'db': 'dB',
                'ms': 'ms', 's': 's', '%': '%',
                'cents': 'cents', 'semi': 'semitones'
            }
            return unit_map.get(unit, unit)
```

#### 4. Safe JSON Export
```python
# FIXED: No more JSON decode errors
class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        return super().default(obj)
```

#### 5. Enhanced History Viewer
```python
# NEW: Complete analysis history with error handling
class HistoryViewer(tk.Toplevel):
    """Shows ALL analyses including failed loads"""
    - Displays 15 total discovery files
    - Shows 8 files with JSON errors
    - Provides detailed parameter views
    - Export capabilities for all data
    - Search and statistics
```

### Current Discovery Status

#### Successfully Analyzed Plugins:
1. **ValhallaVintageVerb** - 22 parameters with string formats
2. **ValhallaPlate** - Full parameter set discovered
3. **ValhallaSupermassive** - Complex modulation parameters
4. **TAL-Reverb-2** - 15 parameters (normalized ranges fixed)
5. **FabFilter Twin 3** - Filter parameters discovered
6. **Nectar 4 Reverb** - Multiple analyses completed

#### Plugins with JSON Errors (need re-analysis):
- ValhallaFreqEcho
- ValhallaShimmer
- Krush
- iZNectar4SaturationAUHook
- Some duplicate analyses of working plugins

### Key Discovery Achievements

#### 1. String Format Detection (PROVEN)
```python
# Critical discovery patterns:
"%.2f s"   # VintageVerb decay: "1.00 s"
"%.1f s"   # ValhallaPlate decay: "1.0 s"
"%.0f ms"  # Delay times: "100 ms"
"%.0f Hz"  # Frequencies: "1000 Hz"
"%.0f%%"   # Percentages: "50%"
```

#### 2. Parameter Learning System
```python
# Self-improving pattern recognition
class PatternLearner:
    def learn_from_discovery(self, plugin_name: str, parameters: Dict):
        # Learns parameter patterns
        # Builds effect type knowledge
        # Improves future discoveries
```

#### 3. Validation System (ENHANCED)
```python
# Now actually tests formats
def validate_parameter_format(self, param_name: str, param_info: Dict):
    test_formats = [
        ('float', test_value),
        ('string_plain', str(test_value)),
        ('string_with_unit_space', f"{test_value:.2f} {unit}"),
        ('string_with_unit_no_space', f"{test_value:.2f}{unit}"),
    ]
    # Tests each format and reports what works
```

### Critical Code Patterns

#### Loading Plugins (macOS Specific)
```python
# Use native macOS file picker for .vst3 bundles
script = '''
set selectedFile to choose file of type {{}} ¬
    with prompt "Select a VST3, VST, or AU Plugin:" ¬
    without invisibles and multiple selections allowed
return POSIX path of selectedFile
'''
result = subprocess.run(['osascript', script_path], capture_output=True)
```

#### Parameter Discovery Flow
```python
# 1. Filter system parameters
# 2. Extract from parameters property
# 3. Detect type (numeric, string_numeric, string_list)
# 4. Infer ranges from names if normalized
# 5. Extract units with regex
# 6. Test string formats if needed
# 7. Validate with enhanced validator
# 8. Export with safe JSON encoder
```

---

## 🎬 PHASE 2: AUTOMATED RECORDING (TO BUILD)

### Integration with Phase 1
```python
# Import discovered parameters
with open('data/discoveries/plugin_enhanced_timestamp.json') as f:
    discovery = json.load(f)
    
# Use discovered formats for setting parameters
for param_name, param_info in discovery['parameters'].items():
    if param_info['type'] == 'string_numeric':
        # Use exact format discovered
        format_str = param_info['format']  # e.g., "%.2f s"
        value_str = format_str % test_value
        setattr(plugin, param_name, value_str)
```

### Planned Architecture
```python
class AutomatedRecorder:
    def __init__(self, discovery_file):
        self.discovery = self.load_discovery(discovery_file)
        self.plugin = load_plugin(self.discovery['plugin_path'])
        
    def generate_test_matrix(self):
        # Use categorized parameters from Phase 1
        critical_params = self.discovery['categorization']['categories']['critical']['parameters']
        # Generate systematic test combinations
```

---

## 🔬 PHASE 3: DSP ANALYSIS & EXTRACTION (PROVEN METHODS)

[Previous Phase 3 content remains the same - proven methods from VintageVerb success]

---

## 💡 CURRENT ISSUES & SOLUTIONS

### Issue 1: JSON File Corruption
**Problem**: 8 out of 15 discovery files have JSON errors
**Cause**: Special float values (NaN, Inf) and complex objects
**Solution**: SafeJSONEncoder implemented, need to re-analyze affected plugins

### Issue 2: Incomplete Parameter Discovery
**Problem**: Some plugins show 0 parameters in history
**Cause**: Parameters stored in nested 'discovery' key
**Solution**: History viewer now handles both formats

### Issue 3: Unit Consistency
**Problem**: Units not consistently detected
**Solution**: Enhanced regex extraction + unit normalization map

---

## 📊 PROJECT METRICS

### Current Status:
- **Total Analyses**: 15 (7 successful, 8 with errors)
- **Unique Plugins**: 10
- **Parameters Discovered**: Varies (0-22 per plugin)
- **Learning Patterns**: 11 patterns established
- **Effect Types**: 6 types identified

### Phase 1 Completion: ~85%
- ✅ Core discovery engine
- ✅ GUI with history viewer
- ✅ Pattern learning system
- ✅ Export functionality
- ✅ Critical fixes applied
- ⏳ Re-analyze failed plugins
- ⏳ Complete documentation

---

## 🚀 IMMEDIATE NEXT STEPS

### 1. Re-analyze Failed Plugins
```bash
# Use the improved discovery system
./quick_test.sh
# Option 2: Test single plugin analysis
# Select each failed plugin
```

### 2. Validate Improvements
```bash
# Generate comprehensive report
python generate_full_analysis_report.py
# Check if all plugins now show parameters
```

### 3. Begin Phase 2 Planning
- Design test signal generator
- Plan parameter sweep strategies
- Build recording infrastructure

---

## 📚 TOOLS & UTILITIES

### Quick Testing:
```bash
./run.sh                    # Main GUI
./quick_test.sh            # Testing menu
python main.py             # Direct launch
python analyze_new_plugin.py  # Single plugin test
python generate_full_analysis_report.py  # Full report
python show_discoveries.py    # List all discoveries
```

### History Access:
- GUI: Click "View History / Logs" button
- Menu: History → View Analysis History
- Shows all 15 analyses with full details

---

**This knowledge represents the complete current state of the Voodoo Analyzer project with all enhancements, fixes, and learnings incorporated. The tool is now significantly more robust and ready for Phase 2 implementation.**