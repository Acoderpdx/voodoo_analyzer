"""
VST Inspector component
"""

class VSTInspector:
    """Component for inspecting VST plugin details."""
    
    def __init__(self):
        self.current_plugin = None
        self.plugin_info = {}
    
    def inspect_plugin(self, plugin_path):
        """Inspect a VST plugin."""
        self.current_plugin = plugin_path
        # TODO: Extract plugin information
    
    def get_plugin_info(self):
        """Get current plugin information."""
        return self.plugin_info