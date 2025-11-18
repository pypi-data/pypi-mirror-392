"""
AbuLang REPL - Interactive shell for AbuLang in Python IDLE
"""

import sys
import code
from essentials.python.runner import AbuRunner


class AbuLangREPL(code.InteractiveConsole):
    """Interactive console that supports AbuLang syntax"""
    
    def __init__(self, locals=None):
        super().__init__(locals)
        self.runner = AbuRunner()
        self.abulang_mode = True
    
    def runsource(self, source, filename="<input>", symbol="single"):
        """Execute source code with AbuLang support"""
        
        # Check for mode switches
        if source.strip() == "switch(python)":
            self.abulang_mode = False
            print("[AbuLang] Switched to Python mode")
            return False
        
        if source.strip() == "switch(abulang)":
            self.abulang_mode = True
            print("[AbuLang] Switched to AbuLang mode")
            return False
        
        # If in AbuLang mode, try to execute as AbuLang
        if self.abulang_mode:
            try:
                self.runner.execute_line(source.strip())
                return False
            except Exception as e:
                # If AbuLang fails, try Python
                pass
        
        # Fall back to Python execution
        return super().runsource(source, filename, symbol)


def start_abulang_repl():
    """Start the AbuLang REPL"""
    print("AbuLang REPL v3.0.0")
    print("Type 'switch(python)' to switch to Python mode")
    print("Type 'switch(abulang)' to switch back to AbuLang mode")
    print()
    
    repl = AbuLangREPL()
    repl.interact(banner="")


if __name__ == "__main__":
    start_abulang_repl()
