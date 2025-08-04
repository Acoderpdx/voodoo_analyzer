# Batch Plugin Analyzer

Automatically analyze all VST, VST3, and AU plugins on your system and compile comprehensive parameter information.

## Features

- **Automatic Discovery**: Scans all standard plugin directories
- **Parallel Processing**: Analyzes multiple plugins simultaneously for speed
- **Smart Caching**: Skips already-analyzed plugins (can be overridden)
- **Comprehensive Reports**: Generates JSON, CSV, and Markdown reports
- **Learning Integration**: Uses and improves the pattern learning system
- **Error Handling**: Continues even if individual plugins fail

## Usage

### Basic Usage
```bash
# Analyze all plugins in standard directories
python batch_analyze_all_plugins.py
```

### Advanced Options
```bash
# Re-analyze all plugins (don't skip existing)
python batch_analyze_all_plugins.py --no-skip

# Use more parallel workers for faster processing
python batch_analyze_all_plugins.py --workers 8

# Add custom directories to scan
python batch_analyze_all_plugins.py --dirs /custom/plugin/path /another/path
```

## Standard Plugin Directories Scanned

### System-wide:
- `/Library/Audio/Plug-Ins/VST`
- `/Library/Audio/Plug-Ins/VST3`
- `/Library/Audio/Plug-Ins/Components` (AU)

### User-specific:
- `~/Library/Audio/Plug-Ins/VST`
- `~/Library/Audio/Plug-Ins/VST3`
- `~/Library/Audio/Plug-Ins/Components` (AU)

## Output Files

All results are saved in the `exports/` directory:

1. **`batch_analysis_results.json`** - Main results file (updated with each run)
2. **`batch_analysis_TIMESTAMP.json`** - Timestamped backup of each run
3. **`all_parameters_TIMESTAMP.csv`** - CSV with all parameters for spreadsheet analysis
4. **`batch_analysis_report_TIMESTAMP.md`** - Human-readable markdown report

## Report Contents

### JSON Report Includes:
- Complete parameter information for each plugin
- Parameter categorization (Core, Modulation, Advanced, etc.)
- Validation results and format requirements
- Learning insights and patterns discovered
- Failed plugins with error details
- Processing statistics

### CSV Report Includes:
- Plugin name
- Parameter name
- Parameter type (float, int, string, etc.)
- Min/Max/Default values
- Units (Hz, dB, ms, etc.)
- Category

### Markdown Report Includes:
- Summary statistics
- Plugin rankings by parameter count
- Category breakdowns
- Failed plugin details
- Learning insights

## Performance Tips

1. **First Run**: The first run will take longer as it analyzes all plugins
2. **Subsequent Runs**: Will be faster as they skip already-analyzed plugins
3. **Workers**: Increase `--workers` if you have a powerful system (default: 4)
4. **Large Collections**: For 100+ plugins, expect 5-30 minutes depending on complexity

## Troubleshooting

### Common Issues:

1. **"No plugins found"**
   - Check that plugins are installed in standard directories
   - Use `--dirs` to specify custom plugin locations

2. **Individual plugin failures**
   - Normal - some plugins may not be analyzable
   - Check the failed plugins section in reports

3. **Slow performance**
   - Reduce workers if system becomes unresponsive
   - Some complex plugins take longer to analyze

## Example Output

```
🔍 BATCH PLUGIN ANALYZER
========================

Searching for plugins...

Found 156 plugins to analyze
Found 23 previously analyzed plugins

Analyzing 133 new plugins...

============================================================
Analyzing: Serum
Path: /Library/Audio/Plug-Ins/VST3/Serum.vst3
Type: VST3
  Discovering parameters...
  Applying learned patterns...
  Validating parameters...
  Categorizing parameters...
  Learning from discovery...
  ✅ Success: 487 parameters discovered

[... continues for all plugins ...]

💾 Saving results...
  ✅ Full report: exports/batch_analysis_results.json
  ✅ Backup: exports/batch_analysis_20250730_224532.json
  ✅ Parameter CSV: exports/all_parameters_20250730_224532.csv
  ✅ Markdown report: exports/batch_analysis_report_20250730_224532.md
  ✅ Learned patterns updated

============================================================
📊 ANALYSIS COMPLETE
============================================================

Total plugins found: 156
Successfully analyzed: 148
Failed: 8
Skipped (already analyzed): 23

Total parameters discovered: 12,847
Average parameters per plugin: 86.8

Total time: 342.7 seconds
Average time per plugin: 2.2 seconds

🏆 Top 5 Plugins by Parameter Count:
  - Serum: 487 parameters
  - Omnisphere: 423 parameters
  - Kontakt: 387 parameters
  - Massive X: 356 parameters
  - Diva: 298 parameters

✅ Results saved to exports/ directory
```