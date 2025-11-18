"""
AbuLang - A friendly, Pythonic programming language for beginners and creative coders
"""

try:
    # Try importing from essentials (for development)
    from essentials.python.runner import AbuRunner
except ImportError:
    try:
        # Try importing from abulang.essentials (for PyPI)
        from abulang.essentials.python.runner import AbuRunner
    except ImportError:
        # Fallback: try from Module (local development)
        try:
            from Module.runner import AbuRunner
        except ImportError:
            raise ImportError("Could not import AbuRunner from any location")

__version__ = "3.0.0"
__author__ = "Abu"
__license__ = "MIT"

# Create default runner instance
_runner = AbuRunner()

def run(code: str):
    """
    Run AbuLang code
    
    Args:
        code (str): AbuLang code to execute
    
    Example:
        >>> from abulang import run
        >>> run('show "Hello, World!"')
        Hello, World!
    """
    _runner.run(code)

def run_file(filename: str):
    """
    Run an AbuLang file
    
    Args:
        filename (str): Path to .abu file
    
    Example:
        >>> from abulang import run_file
        >>> run_file("myprogram.abu")
    """
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    run(code)

def enable_abulang_mode():
    """Enable AbuLang syntax in Python IDLE"""
    import builtins
    
    # Create AbuLang command functions
    def show(*args):
        """AbuLang show command"""
        if args:
            print(*args)
    
    def ask(prompt=""):
        """AbuLang ask command"""
        return input(str(prompt))
    
    def libra(module_name):
        """AbuLang libra (import) command"""
        _runner.execute_line(f"libra {module_name}")
    
    # Add to builtins so they're available in IDLE
    builtins.show = show
    builtins.ask = ask
    builtins.libra = libra
    
    print("[AbuLang] Enabled! You can now use AbuLang syntax in Python IDLE")
    print("[AbuLang] Available commands: show, ask, libra")

# Exports
__all__ = [
    'run',
    'run_file',
    'AbuRunner',
]
