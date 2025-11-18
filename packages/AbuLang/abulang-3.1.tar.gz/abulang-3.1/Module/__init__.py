"""
AbuLang Module - A friendly programming language with IDLE GUI
"""

from .runner import AbuRunner
from .idle_gui import AbuIDLEGUI

__version__ = "3.0.0"
__author__ = "Abu"
__license__ = "MIT"

__all__ = [
    'AbuRunner',
    'AbuIDLEGUI',
    'run',
    'run_file',
    'idle',
]

# Create default runner instance
_runner = AbuRunner()

def run(code: str):
    """Run AbuLang code"""
    _runner.run(code)

def run_file(filename: str):
    """Run an AbuLang file"""
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    run(code)

def idle():
    """Launch AbuLang IDLE GUI"""
    gui = AbuIDLEGUI()
    gui.run()
