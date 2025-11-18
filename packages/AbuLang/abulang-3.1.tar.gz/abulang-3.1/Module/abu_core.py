"""
AbuLang Core - Language definitions
"""

import yaml
from pathlib import Path


class AbuLang:
    """Core AbuLang language definitions"""

    def __init__(self):
        # Basic command definitions
        self.commands = {
            # I/O
            "show": {
                "section": "io",
                "aliases": ["display", "print"],
                "desc": "Display output"
            },
            "ask": {
                "section": "io",
                "aliases": ["input", "read"],
                "desc": "Get user input"
            },
            
            # Variables
            "libra": {
                "section": "system",
                "aliases": ["import", "library"],
                "desc": "Import a library"
            },
            
            # Control Flow
            "if": {
                "section": "logic",
                "aliases": ["check"],
                "desc": "Conditional statement"
            },
            "for": {
                "section": "logic",
                "aliases": ["loop"],
                "desc": "For loop"
            },
            "while": {
                "section": "logic",
                "aliases": ["repeat"],
                "desc": "While loop"
            },
            "def": {
                "section": "structure",
                "aliases": ["function"],
                "desc": "Define a function"
            },
            
            # Math
            "plus": {
                "section": "math",
                "aliases": ["+"],
                "desc": "Addition"
            },
            "minus": {
                "section": "math",
                "aliases": ["-"],
                "desc": "Subtraction"
            },
            "multi": {
                "section": "math",
                "aliases": ["*"],
                "desc": "Multiplication"
            },
            "divid": {
                "section": "math",
                "aliases": ["/"],
                "desc": "Division"
            },
        }

    def translate(self, word, **kwargs):
        """Translate AbuLang keyword to Python"""
        if word not in self.commands:
            raise ValueError(f"Unknown command: {word}")
        return self.commands[word]

    def explain(self, word):
        """Explain what a command does"""
        if word not in self.commands:
            return "Unknown command"
        return self.commands[word]["desc"]
