"""
Enhanced AbuLang Core

This module extends the base AbuLang class with additional features including
async support, module loading, and macro expansion capabilities.
"""

try:
    from .abu_core import AbuLang
except ImportError:
    from abu_core import AbuLang


class EnhancedAbuLang(AbuLang):
    """
    Enhanced version of AbuLang with support for:
    - Async/await operations
    - Module system
    - Macro expansion
    - Extended command registry
    """
    
    def __init__(self):
        super().__init__()
        self.event_loop = None
        self.loaded_modules = {}
        self.macros = {}
        
    def get_event_loop(self):
        """
        Get or create the asyncio event loop for async operations.
        
        Returns:
            asyncio.AbstractEventLoop: The event loop instance
        """
        if self.event_loop is None:
            import asyncio
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
        return self.event_loop
    
    def register_macro(self, name, definition, params=None):
        """
        Register a macro for later expansion.
        
        Args:
            name (str): Macro name
            definition (str): Macro code definition
            params (list): Optional parameter names
        """
        self.macros[name] = {
            'definition': definition,
            'params': params or []
        }
    
    def expand_macro(self, name, args=None):
        """
        Expand a macro with given arguments.
        
        Args:
            name (str): Macro name
            args (list): Arguments to substitute
            
        Returns:
            str: Expanded macro code
        """
        if name not in self.macros:
            raise ValueError(f"Unknown macro: {name}")
        
        macro = self.macros[name]
        code = macro['definition']
        
        if args and macro['params']:
            for param, arg in zip(macro['params'], args):
                code = code.replace(f"${param}", str(arg))
        
        return code
