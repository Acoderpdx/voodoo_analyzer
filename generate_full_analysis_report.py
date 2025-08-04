#!/usr/bin/env python3
"""
Generate comprehensive analysis report from all plugin discoveries
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re

def load_all_discoveries():
    """Load all discovery data from files"""
    data_dir = Path(__file__).parent / "data" / "discoveries"
    all_plugins = {}
    failed_files = []
    
    if not data_dir.exists():
        print(f"No discoveries directory found at {data_dir}")
        return all_plugins, failed_files
    
    # Get all JSON files
    json_files = list(data_dir.glob("*.json"))
    print(f"Found {len(json_files)} discovery files")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Try to fix common JSON errors
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Remove trailing commas
                fixed_content = re.sub(r',\s*([}\]])', r'\\1', content)
                data = json.loads(fixed_content)
            
            # Extract plugin name from filename
            filename = file_path.stem
            if '_enhanced_' in filename:
                plugin_name = filename.split('_enhanced_')[0]
            else:
                plugin_name = filename
            
            # Get timestamp
            timestamp = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Store data
            if plugin_name not in all_plugins:
                all_plugins[plugin_name] = []
            
            all_plugins[plugin_name].append({
                'file': str(file_path),
                'timestamp': timestamp,
                'data': data
            })
            
        except Exception as e:
            failed_files.append({
                'file': str(file_path),
                'error': str(e)
            })
            print(f"Failed to load {file_path.name}: {e}")
    
    return all_plugins, failed_files

def analyze_parameters(params):
    """Analyze parameter data and extract meaningful info"""
    if not isinstance(params, dict):
        return {"error": "Invalid parameter format"}
    
    analysis = {
        'total_count': 0,
        'by_type': {},
        'by_format': {},
        'unique_names': [],
        'ranges': []
    }
    
    for param_name, param_info in params.items():
        if param_name.startswith('_'):
            continue
            
        analysis['total_count'] += 1
        analysis['unique_names'].append(param_name)
        
        # Type analysis
        param_type = param_info.get('type', 'unknown')
        analysis['by_type'][param_type] = analysis['by_type'].get(param_type, 0) + 1
        
        # Format analysis
        if 'format' in param_info:
            fmt = param_info['format']
            analysis['by_format'][fmt] = analysis['by_format'].get(fmt, 0) + 1
        
        # Range analysis
        if 'range' in param_info:
            analysis['ranges'].append({
                'name': param_name,
                'range': param_info['range']
            })
    
    return analysis

def generate_plugin_summary(plugin_name, discoveries):
    """Generate summary for a single plugin"""
    summary = {
        'plugin_name': plugin_name,
        'analysis_count': len(discoveries),
        'latest_analysis': None,
        'parameters_discovered': {},
        'categories': {},
        'learning_insights': {},
        'validation_results': {}
    }
    
    # Use the latest discovery
    latest = max(discoveries, key=lambda x: x['timestamp'])
    summary['latest_analysis'] = latest['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    
    data = latest['data']
    
    # Parameters
    if 'parameters' in data:
        summary['parameters_discovered'] = analyze_parameters(data['parameters'])
    
    # Categories
    if 'categorized' in data and 'categories' in data['categorized']:
        for cat_name, cat_info in data['categorized']['categories'].items():
            summary['categories'][cat_name] = len(cat_info.get('parameters', []))
    
    # Learning insights
    if 'learning_annotations' in data:
        annotations = data['learning_annotations']
        summary['learning_insights'] = {
            'effect_type': annotations.get('effect_type', 'Unknown'),
            'confidence': annotations.get('confidence', 0),
            'patterns_applied': len(annotations.get('applied_patterns', []))
        }
    
    # Validation
    if 'validation_results' in data:
        validation = data['validation_results']
        summary['validation_results'] = {
            'format_requirements': validation.get('format_requirements', {}),
            'validated_count': len(validation.get('validated_parameters', []))
        }
    
    return summary

def generate_full_report():
    """Generate comprehensive analysis report"""
    print("Generating comprehensive analysis report...")
    print("="*60)
    
    # Load all discoveries
    all_plugins, failed_files = load_all_discoveries()
    
    # Load learning patterns
    patterns_path = Path(__file__).parent / "data" / "learned_patterns.json"
    learned_patterns = {}
    if patterns_path.exists():
        with open(patterns_path, 'r') as f:
            learned_patterns = json.load(f)
    
    # Generate report
    report = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'tool': 'Voodoo Analyzer',
            'version': '2.0'
        },
        'summary': {
            'total_plugins_analyzed': len(all_plugins),
            'total_analyses': sum(len(analyses) for analyses in all_plugins.values()),
            'failed_loads': len(failed_files),
            'learning_patterns': len(learned_patterns.get('parameter_patterns', {})),
            'effect_types_identified': len(learned_patterns.get('effect_types', {}))
        },
        'plugins': {},
        'failed_files': failed_files,
        'effectiveness_metrics': {}
    }
    
    # Process each plugin
    for plugin_name, discoveries in all_plugins.items():
        report['plugins'][plugin_name] = generate_plugin_summary(plugin_name, discoveries)
    
    # Calculate effectiveness metrics
    total_params = 0
    categorized_params = 0
    validated_params = 0
    
    for plugin_data in report['plugins'].values():
        params_info = plugin_data.get('parameters_discovered', {})
        total_params += params_info.get('total_count', 0)
        
        categories = plugin_data.get('categories', {})
        categorized_params += sum(categories.values())
        
        validation = plugin_data.get('validation_results', {})
        validated_params += validation.get('validated_count', 0)
    
    report['effectiveness_metrics'] = {
        'total_parameters_discovered': total_params,
        'categorization_rate': categorized_params / total_params if total_params > 0 else 0,
        'validation_rate': validated_params / total_params if total_params > 0 else 0,
        'plugins_with_learning': len([p for p in report['plugins'].values() 
                                     if p['learning_insights'].get('effect_type') != 'Unknown'])
    }
    
    # Save report
    report_path = Path(__file__).parent / "data" / "comprehensive_analysis_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate markdown report
    generate_markdown_report(report, report_path.with_suffix('.md'))
    
    # Print summary
    print(f"\nANALYSIS SUMMARY:")
    print(f"Total Plugins Analyzed: {report['summary']['total_plugins_analyzed']}")
    print(f"Total Analysis Sessions: {report['summary']['total_analyses']}")
    print(f"Failed File Loads: {report['summary']['failed_loads']}")
    print(f"\nEFFECTIVENESS METRICS:")
    print(f"Total Parameters Discovered: {report['effectiveness_metrics']['total_parameters_discovered']}")
    print(f"Categorization Rate: {report['effectiveness_metrics']['categorization_rate']:.1%}")
    print(f"Validation Rate: {report['effectiveness_metrics']['validation_rate']:.1%}")
    print(f"Plugins with Effect Type Learning: {report['effectiveness_metrics']['plugins_with_learning']}")
    
    print(f"\nDetailed report saved to: {report_path}")
    print(f"Markdown report saved to: {report_path.with_suffix('.md')}")
    
    return report

def generate_markdown_report(report, output_path):
    """Generate human-readable markdown report"""
    with open(output_path, 'w') as f:
        f.write("# Voodoo Analyzer - Comprehensive Analysis Report\n\n")
        f.write(f"Generated: {report['metadata']['generated']}\n\n")
        
        # Summary
        f.write("## Executive Summary\n\n")
        summary = report['summary']
        f.write(f"- **Total Plugins Analyzed**: {summary['total_plugins_analyzed']}\n")
        f.write(f"- **Total Analysis Sessions**: {summary['total_analyses']}\n")
        f.write(f"- **Learning Patterns Developed**: {summary['learning_patterns']}\n")
        f.write(f"- **Effect Types Identified**: {summary['effect_types_identified']}\n\n")
        
        # Effectiveness
        f.write("## Effectiveness Metrics\n\n")
        metrics = report['effectiveness_metrics']
        f.write(f"- **Total Parameters Discovered**: {metrics['total_parameters_discovered']}\n")
        f.write(f"- **Categorization Success Rate**: {metrics['categorization_rate']:.1%}\n")
        f.write(f"- **Validation Success Rate**: {metrics['validation_rate']:.1%}\n")
        f.write(f"- **Plugins with Learned Effect Types**: {metrics['plugins_with_learning']}\n\n")
        
        # Detailed plugin analysis
        f.write("## Detailed Plugin Analysis\n\n")
        
        for plugin_name, plugin_data in sorted(report['plugins'].items()):
            f.write(f"### {plugin_name}\n\n")
            f.write(f"- **Analysis Count**: {plugin_data['analysis_count']}\n")
            f.write(f"- **Latest Analysis**: {plugin_data['latest_analysis']}\n")
            
            # Parameters
            params = plugin_data['parameters_discovered']
            if params.get('total_count', 0) > 0:
                f.write(f"- **Parameters Discovered**: {params['total_count']}\n")
                
                if params['by_type']:
                    f.write("  - By Type:\n")
                    for ptype, count in params['by_type'].items():
                        f.write(f"    - {ptype}: {count}\n")
                
                if params['by_format']:
                    f.write("  - By Format:\n")
                    for fmt, count in params['by_format'].items():
                        f.write(f"    - {fmt}: {count}\n")
            
            # Categories
            if plugin_data['categories']:
                f.write("- **Parameter Categories**:\n")
                for cat, count in plugin_data['categories'].items():
                    f.write(f"  - {cat}: {count} parameters\n")
            
            # Learning insights
            insights = plugin_data['learning_insights']
            if insights:
                f.write(f"- **Effect Type**: {insights.get('effect_type', 'Unknown')}\n")
                if insights.get('confidence', 0) > 0:
                    f.write(f"- **Confidence**: {insights['confidence']:.1%}\n")
                if insights.get('patterns_applied', 0) > 0:
                    f.write(f"- **Patterns Applied**: {insights['patterns_applied']}\n")
            
            f.write("\n")
        
        # Failed files
        if report['failed_files']:
            f.write("## Failed File Loads\n\n")
            for failed in report['failed_files']:
                f.write(f"- {Path(failed['file']).name}: {failed['error']}\n")
            f.write("\n")
        
        # Recommendations
        f.write("## Recommendations for Tool Improvement\n\n")
        f.write("Based on the analysis results, here are key areas for improvement:\n\n")
        
        if metrics['categorization_rate'] < 0.8:
            f.write("1. **Improve Parameter Categorization**: Current rate is below 80%, suggesting need for better pattern recognition\n")
        
        if metrics['validation_rate'] < 0.9:
            f.write("2. **Enhance Validation Logic**: More parameters need format validation\n")
        
        if report['failed_files']:
            f.write(f"3. **Fix File Loading Issues**: {len(report['failed_files'])} files failed to load\n")
        
        if metrics['plugins_with_learning'] < summary['total_plugins_analyzed'] * 0.7:
            f.write("4. **Expand Effect Type Learning**: More plugins need effect type identification\n")

if __name__ == "__main__":
    generate_full_report()