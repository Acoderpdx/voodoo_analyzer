"""
Export learning data and patterns for analysis
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class LearningExporter:
    """Export learned patterns and discoveries"""
    
    def __init__(self):
        self.discoveries_dir = Path('data/discoveries')
        self.discoveries_dir.mkdir(exist_ok=True)
    
    def export_learning_report(self, all_discoveries: Dict) -> str:
        """Generate comprehensive learning report"""
        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_plugins': len(all_discoveries),
                'version': '2.0',
                'system': 'Voodoo Analyzer Pattern Learning System'
            },
            'pattern_summary': self._summarize_patterns(all_discoveries),
            'effect_types_discovered': self._summarize_effect_types(all_discoveries),
            'format_requirements': self._extract_format_requirements(all_discoveries),
            'parameter_statistics': self._calculate_statistics(all_discoveries),
            'learning_insights': self._generate_insights(all_discoveries)
        }
        
        # Save report
        report_path = self.discoveries_dir / f'learning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save a "latest" copy for easy access
        latest_path = self.discoveries_dir / 'learning_report_latest.json'
        with open(latest_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
    
    def _summarize_patterns(self, discoveries: Dict) -> Dict:
        """Summarize discovered patterns across all plugins"""
        patterns = {
            'common_parameters': {},
            'parameter_ranges': {},
            'format_patterns': {},
            'naming_conventions': []
        }
        
        # Analyze parameter frequency
        param_count = {}
        for plugin_name, discovery in discoveries.items():
            if 'parameters' in discovery:
                for param_name in discovery['parameters']:
                    if not param_name.startswith('_'):
                        param_count[param_name] = param_count.get(param_name, 0) + 1
        
        # Find common parameters (appear in >30% of plugins)
        threshold = len(discoveries) * 0.3
        patterns['common_parameters'] = {
            param: count for param, count in param_count.items() 
            if count >= threshold
        }
        
        # Extract format patterns
        for plugin_name, discovery in discoveries.items():
            if 'validation_results' in discovery:
                for param, validation in discovery['validation_results'].items():
                    if 'working_formats' in validation and validation['working_formats']:
                        if param not in patterns['format_patterns']:
                            patterns['format_patterns'][param] = []
                        patterns['format_patterns'][param].extend(validation['working_formats'])
        
        # Deduplicate format patterns
        for param in patterns['format_patterns']:
            patterns['format_patterns'][param] = list(set(patterns['format_patterns'][param]))
        
        return patterns
    
    def _summarize_effect_types(self, discoveries: Dict) -> Dict:
        """Summarize discovered effect types"""
        effect_types = {
            'identified': {},
            'distribution': {},
            'confidence_scores': {}
        }
        
        for plugin_name, discovery in discoveries.items():
            if 'effect_type' in discovery and discovery['effect_type']:
                effect_type = discovery['effect_type']
                effect_types['identified'][plugin_name] = effect_type
                
                # Track distribution
                category = effect_type.split('.')[0] if '.' in effect_type else effect_type
                effect_types['distribution'][category] = effect_types['distribution'].get(category, 0) + 1
        
        return effect_types
    
    def _extract_format_requirements(self, discoveries: Dict) -> Dict:
        """Extract validated format requirements"""
        formats = {
            'string_numeric': {},
            'numeric': {},
            'choice': {},
            'special_cases': []
        }
        
        for plugin_name, discovery in discoveries.items():
            if 'format_requirements' in discovery:
                for param, format_type in discovery['format_requirements'].items():
                    if param not in formats['string_numeric']:
                        formats['string_numeric'][param] = []
                    formats['string_numeric'][param].append({
                        'plugin': plugin_name,
                        'format': format_type
                    })
        
        return formats
    
    def _calculate_statistics(self, discoveries: Dict) -> Dict:
        """Calculate comprehensive statistics"""
        stats = {
            'total_parameters_discovered': 0,
            'average_parameters_per_plugin': 0,
            'parameter_type_distribution': {},
            'validation_success_rate': 0,
            'categorization_rate': 0
        }
        
        total_params = 0
        validated_params = 0
        categorized_params = 0
        
        for plugin_name, discovery in discoveries.items():
            if 'parameters' in discovery:
                plugin_params = len([p for p in discovery['parameters'] if not p.startswith('_')])
                total_params += plugin_params
                
                # Count validated parameters
                if 'validation_results' in discovery:
                    validated_params += len(discovery['validation_results'])
                
                # Count categorized parameters
                if 'categorized' in discovery:
                    for category, params in discovery['categorized'].get('categories', {}).items():
                        categorized_params += len(params.get('parameters', []))
        
        stats['total_parameters_discovered'] = total_params
        stats['average_parameters_per_plugin'] = total_params / len(discoveries) if discoveries else 0
        
        if total_params > 0:
            stats['validation_success_rate'] = (validated_params / total_params) * 100
            stats['categorization_rate'] = (categorized_params / total_params) * 100
        
        return stats
    
    def _generate_insights(self, discoveries: Dict) -> List[Dict]:
        """Generate learning insights from discoveries"""
        insights = []
        
        # Insight: Most common parameter names
        param_frequency = {}
        for plugin_name, discovery in discoveries.items():
            if 'parameters' in discovery:
                for param in discovery['parameters']:
                    if not param.startswith('_'):
                        param_frequency[param] = param_frequency.get(param, 0) + 1
        
        if param_frequency:
            most_common = sorted(param_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            insights.append({
                'type': 'common_parameters',
                'title': 'Most Common Parameter Names',
                'data': dict(most_common)
            })
        
        # Insight: Format patterns
        format_patterns = {}
        for plugin_name, discovery in discoveries.items():
            if 'format_requirements' in discovery:
                for param, fmt in discovery['format_requirements'].items():
                    if fmt not in format_patterns:
                        format_patterns[fmt] = 0
                    format_patterns[fmt] += 1
        
        if format_patterns:
            insights.append({
                'type': 'format_distribution',
                'title': 'Parameter Format Distribution',
                'data': format_patterns
            })
        
        # Insight: Effect type accuracy
        effect_types = {}
        for plugin_name, discovery in discoveries.items():
            if 'effect_type' in discovery and discovery['effect_type']:
                category = discovery['effect_type'].split('.')[0]
                effect_types[category] = effect_types.get(category, 0) + 1
        
        if effect_types:
            insights.append({
                'type': 'effect_classification',
                'title': 'Effect Type Classification',
                'data': effect_types
            })
        
        return insights
    
    def export_individual_discovery(self, plugin_name: str, discovery_data: Dict) -> str:
        """Export individual plugin discovery with learning annotations"""
        enhanced_data = {
            'plugin': plugin_name,
            'timestamp': datetime.now().isoformat(),
            'discovery': discovery_data,
            'learning_version': '2.0'
        }
        
        # Clean plugin name for filename
        safe_name = plugin_name.replace('/', '_').replace('\\', '_')
        filename = f'{safe_name}_enhanced_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        filepath = self.discoveries_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(enhanced_data, f, indent=2)
        
        return str(filepath)
    
    def create_markdown_report(self, report_data: Dict) -> str:
        """Create a human-readable markdown report"""
        md_lines = [
            "# Voodoo Analyzer Learning Report",
            f"\nGenerated: {report_data['metadata']['generated']}",
            f"Total Plugins Analyzed: {report_data['metadata']['total_plugins']}",
            "\n## Pattern Summary",
            "\n### Most Common Parameters"
        ]
        
        if 'common_parameters' in report_data['pattern_summary']:
            for param, count in sorted(report_data['pattern_summary']['common_parameters'].items(), 
                                      key=lambda x: x[1], reverse=True)[:10]:
                md_lines.append(f"- **{param}**: found in {count} plugins")
        
        md_lines.extend([
            "\n## Effect Types Discovered",
            f"\nTotal effect types identified: {len(report_data['effect_types_discovered']['identified'])}"
        ])
        
        if 'distribution' in report_data['effect_types_discovered']:
            md_lines.append("\n### Effect Type Distribution")
            for effect, count in report_data['effect_types_discovered']['distribution'].items():
                md_lines.append(f"- **{effect}**: {count} plugins")
        
        md_lines.extend([
            "\n## Statistics",
            f"- Total parameters discovered: {report_data['parameter_statistics']['total_parameters_discovered']}",
            f"- Average parameters per plugin: {report_data['parameter_statistics']['average_parameters_per_plugin']:.1f}",
            f"- Validation success rate: {report_data['parameter_statistics']['validation_success_rate']:.1f}%",
            f"- Categorization rate: {report_data['parameter_statistics']['categorization_rate']:.1f}%"
        ])
        
        if 'learning_insights' in report_data:
            md_lines.append("\n## Learning Insights")
            for insight in report_data['learning_insights']:
                md_lines.append(f"\n### {insight['title']}")
                if isinstance(insight['data'], dict):
                    for key, value in insight['data'].items():
                        md_lines.append(f"- {key}: {value}")
        
        md_content = '\n'.join(md_lines)
        
        # Save markdown report
        md_path = self.discoveries_dir / f'learning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(md_path, 'w') as f:
            f.write(md_content)
        
        return str(md_path)