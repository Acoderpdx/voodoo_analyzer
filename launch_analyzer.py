#!/usr/bin/env python3
"""
Launcher script that keeps the analyzer running without timeout
"""

import subprocess
import sys
import os
import time

def launch_analyzer():
    """Launch the analyzer in a way that won't timeout"""
    print("="*60)
    print("🚀 Launching Plugin Analyzer")
    print("="*60)
    print("\nThe analyzer will stay running in the background.")
    print("Look for the 'Plugin Parameter Discovery' window on your screen.")
    print("\nTo stop the analyzer, press Ctrl+C in this terminal.")
    print("="*60)
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Launch the main app
        process = subprocess.Popen([sys.executable, "main.py"])
        
        print(f"\n✅ Analyzer launched with PID: {process.pid}")
        print("\nThe app is now running. You can:")
        print("  - Use Quick Load buttons for test plugins")
        print("  - Browse for any VST3 plugin on your system")
        print("  - Check the Discovery Log for progress")
        print("\nThis terminal will stay active. Press Ctrl+C to quit.")
        
        # Keep the script running
        while True:
            # Check if process is still running
            if process.poll() is not None:
                print("\n❌ Analyzer has closed.")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping analyzer...")
        process.terminate()
        print("✅ Analyzer stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    launch_analyzer()