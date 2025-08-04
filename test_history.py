#!/usr/bin/env python3
"""Test the history viewer functionality"""

import tkinter as tk
from ui.components import HistoryViewer

def test_history_viewer():
    """Create a test window to show the history viewer"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Create and show history viewer
    history = HistoryViewer(root)
    
    # Print summary of what was loaded
    print(f"History viewer loaded with {len(history.plugin_data)} analyses")
    print("\nAvailable plugins:")
    for display_str in list(history.plugin_data.keys())[:5]:
        print(f"  - {display_str}")
    if len(history.plugin_data) > 5:
        print(f"  ... and {len(history.plugin_data) - 5} more")
    
    # Close after a moment
    root.after(3000, root.quit)
    root.mainloop()

if __name__ == "__main__":
    test_history_viewer()