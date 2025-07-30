#!/usr/bin/env python3
"""
Plugin Parameter Discovery Tool - Stage 1
Professional parameter discovery and mapping for audio plugins
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.app import PluginAnalyzerApp

def main():
    app = PluginAnalyzerApp()
    app.run()

if __name__ == "__main__":
    main()