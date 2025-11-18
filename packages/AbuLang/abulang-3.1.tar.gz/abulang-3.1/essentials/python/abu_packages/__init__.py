"""
Abu Packages - Official AbuLang package collection
"""

from .AbuSmart import AbuSmart, smart
from .AbuINSTALL import AbuINSTALL, installer, install
from .AbuFILES import AbuFILES, files
from .AbuChess import AbuChess, chess, play, AIweb, train, info, status

__all__ = [
    'AbuSmart', 'smart',
    'AbuINSTALL', 'installer', 'install',
    'AbuFILES', 'files',
    'AbuChess', 'chess', 'play', 'AIweb', 'train', 'info', 'status',
]

__version__ = '1.0.0'
