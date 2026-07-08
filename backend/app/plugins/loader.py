import importlib
import os
import sys
from typing import List, Type

def discover_plugins(plugin_dir: str = "extensions", base_class: Type = None) -> List[Type]:
    """
    Dynamically loads Python modules from a directory and returns classes
    that inherit from the specified base_class.
    """
    plugins = []
    if not os.path.exists(plugin_dir):
        return plugins
        
    sys.path.insert(0, plugin_dir)
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, base_class) and attr is not base_class:
                        plugins.append(attr)
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")
                
    sys.path.pop(0)
    return plugins
