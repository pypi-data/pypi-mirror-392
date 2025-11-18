"""
AbuLang REPL (Read-Eval-Print Loop)

This module provides an interactive shell for AbuLang with features including:
- Command history with readline support
- Tab completion for commands and variables
- Multi-line input support
- Graceful error handling
"""

import sys
from pathlib import Path

try:
    from .enhanced_runner import EnhancedAbuRunner
except ImportError:
    from enhanced_runner import EnhancedAbuRunner


class AbuREPL:
    """
    Interactive REPL for AbuLang with readline support, history, and autocomplete.
    """
    
    def __init__(self, debug_mode=False, profile_mode=False):
        """
        Initialize the REPL.
        
        Args:
            debug_mode (bool): Enable debug mode
            profile_mode (bool): Enable profiling mode
        """
        self.runner = EnhancedAbuRunner(debug_mode=debug_mode, profile_mode=profile_mode)
        self.history_file = Path.home() / '.abulang_history'
        self.readline_available = False
        self.setup_readline()
    
    def setup_readline(self):
        """
        Set up readline for history and autocomplete support.
        Handles cases where readline is not available (e.g., Windows without pyreadline).
        """
        try:
            import readline
            self.readline_available = True
            
            # Enable tab completion
            readline.parse_and_bind('tab: complete')
            readline.set_completer(self.completer)
            
            # Set completer delimiters (exclude common characters in variable names)
            readline.set_completer_delims(' \t\n;')
            
            # Load history file if it exists
            if self.history_file.exists():
                try:
                    readline.read_history_file(str(self.history_file))
                except Exception as e:
                    print(f"Warning: Could not load history: {e}")
            
            # Set history length
            readline.set_history_length(1000)
            
        except ImportError:
            # readline not available (common on Windows)
            self.readline_available = False
            print("Note: readline not available. History and autocomplete disabled.")
            print("Install pyreadline3 for Windows or readline for Unix-like systems.")
    
    def save_history(self):
        """
        Save command history to disk.
        """
        if not self.readline_available:
            return
        
        try:
            import readline
            readline.write_history_file(str(self.history_file))
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def completer(self, text, state):
        """
        Autocomplete function for readline.
        Provides completions for AbuLang commands and variables.
        
        Args:
            text (str): The text to complete
            state (int): The completion state (0 for first call, incremented for each call)
            
        Returns:
            str or None: The completion option, or None if no more options
        """
        if state == 0:
            # First call - generate completion options
            self.completion_options = []
            
            # Add AbuLang commands
            for cmd in self.runner.lang.lookup.keys():
                if cmd.startswith(text):
                    self.completion_options.append(cmd)
            
            # Add variables from context
            for var in self.runner.context.keys():
                if var.startswith(text) and not var.startswith('__'):
                    self.completion_options.append(var)
            
            # Sort for consistent ordering
            self.completion_options.sort()
        
        # Return the next option
        if state < len(self.completion_options):
            return self.completion_options[state]
        return None
    
    def run(self):
        """
        Run the interactive REPL loop.
        Handles user input, multi-line mode, and graceful exit.
        """
        print("AbuLang REPL v2.0")
        print("Type 'help' for commands, 'exit' or 'quit' to exit")
        print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) to exit")
        print()
        
        while True:
            try:
                # Choose prompt based on multi-line mode
                if self.runner.in_multiline:
                    prompt = "... "
                else:
                    prompt = ">>> "
                
                # Get user input
                line = input(prompt)
                
                # Check for exit commands
                if line.strip() in ('exit', 'quit') and not self.runner.in_multiline:
                    print("Goodbye!")
                    break
                
                # Execute the line
                self.runner.execute_line(line)
                
            except EOFError:
                # Ctrl+D (Unix) or Ctrl+Z (Windows)
                print("\nGoodbye!")
                break
            
            except KeyboardInterrupt:
                # Ctrl+C - cancel current input/multi-line block
                print("\nKeyboardInterrupt")
                # Reset multi-line state
                self.runner.in_multiline = False
                self.runner.multiline_buffer = []
                self.runner.empty_line_count = 0
                continue
            
            except Exception as e:
                # Catch any unexpected errors to keep REPL running
                print(f"[REPL Error] {type(e).__name__}: {e}")
                # Reset multi-line state on error
                self.runner.in_multiline = False
                self.runner.multiline_buffer = []
                self.runner.empty_line_count = 0
        
        # Save history before exiting
        self.save_history()


def main():
    """
    Entry point for running REPL directly.
    """
    repl = AbuREPL()
    repl.run()


if __name__ == "__main__":
    main()
