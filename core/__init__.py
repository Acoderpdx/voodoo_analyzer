"""
Core module for Voodoo Analyzer
"""
from .discovery import UniversalPluginDiscovery
from .categorizer import ParameterCategorizer
from .validator import ResearchValidator
from .exporter import DiscoveryExporter

__all__ = ['UniversalPluginDiscovery', 'ParameterCategorizer', 'ResearchValidator', 'DiscoveryExporter']