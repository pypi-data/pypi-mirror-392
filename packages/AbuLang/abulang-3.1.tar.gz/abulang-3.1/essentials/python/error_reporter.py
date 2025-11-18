"""
Enhanced Error Reporter for AbuLang

This module provides detailed error reporting with line numbers, context,
command suggestions, and variable suggestions to help developers quickly
identify and fix issues.
"""

import traceback
from difflib import get_close_matches


class ErrorReporter:
    """
    Enhanced error reporter that provides:
    - Line numbers and context for errors
    - Stack traces in debug mode
    - Command suggestions for misspelled commands
    - Variable suggestions for undefined variables
    """
    
    def __init__(self, runner):
        """
        Initialize the error reporter.
        
        Args:
            runner: The AbuRunner instance (for accessing context and commands)
        """
        self.runner = runner
    
    def report_error(self, error, line, line_number=None):
        """
        Report an error with detailed context and suggestions.
        
        Args:
            error (Exception): The error that occurred
            line (str): The line of code where the error occurred
            line_number (int): Optional line number
        """
        print(f"\n{'='*60}")
        print(f"[AbuLang Error]")
        print(f"{'='*60}")
        
        # Show line number and context
        if line_number:
            print(f"Line {line_number}: {line}")
        else:
            print(f"Line: {line}")
        
        # Show error type and message
        error_type = type(error).__name__
        error_msg = str(error)
        print(f"\n{error_type}: {error_msg}")
        
        # Provide context-specific suggestions
        if isinstance(error, NameError):
            self.suggest_variable(error_msg, line)
        elif isinstance(error, ValueError) and "Unknown AbuLang command" in error_msg:
            self.suggest_command(line)
        elif isinstance(error, AttributeError):
            self._suggest_attribute(error_msg)
        elif isinstance(error, KeyError):
            self._suggest_key(error_msg)
        
        # Show stack trace in debug mode
        if self.runner.debug_mode:
            print(f"\n{'-'*60}")
            print("Stack Trace (Debug Mode):")
            print(f"{'-'*60}")
            traceback.print_exc()
        
        print(f"{'='*60}\n")
    
    def suggest_command(self, line):
        """
        Suggest similar commands for misspelled commands.
        
        Args:
            line (str): The line containing the unknown command
        """
        words = line.split()
        if not words:
            return
        
        first_word = words[0]
        
        # Get all available commands
        available_commands = list(self.runner.lang.lookup.keys())
        
        # Find close matches using fuzzy matching
        matches = get_close_matches(first_word, available_commands, n=3, cutoff=0.6)
        
        if matches:
            print(f"\nDid you mean one of these commands?")
            for match in matches:
                desc = self.runner.lang.explain(match)
                print(f"  • {match} - {desc}")
        else:
            print(f"\nNo similar commands found. Type 'help' to see all available commands.")
    
    def suggest_variable(self, error_msg, line):
        """
        Suggest available variables for undefined variable errors.
        
        Args:
            error_msg (str): The error message
            line (str): The line containing the undefined variable
        """
        # Extract variable name from error message
        # NameError format: "name 'variable_name' is not defined"
        var_name = None
        if "'" in error_msg:
            parts = error_msg.split("'")
            if len(parts) >= 2:
                var_name = parts[1]
        
        # Get available variables (filter out internal ones)
        available_vars = [
            name for name in self.runner.context.keys()
            if not name.startswith('__') and not callable(self.runner.context[name])
        ]
        
        if var_name and available_vars:
            # Try to find similar variable names
            matches = get_close_matches(var_name, available_vars, n=3, cutoff=0.6)
            
            if matches:
                print(f"\nDid you mean one of these variables?")
                for match in matches:
                    value = self.runner.context[match]
                    print(f"  • {match} = {repr(value)}")
            else:
                print(f"\nAvailable variables:")
                for var in available_vars[:10]:  # Show first 10
                    value = self.runner.context[var]
                    print(f"  • {var} = {repr(value)}")
                if len(available_vars) > 10:
                    print(f"  ... and {len(available_vars) - 10} more")
        elif available_vars:
            print(f"\nAvailable variables:")
            for var in available_vars[:10]:
                value = self.runner.context[var]
                print(f"  • {var} = {repr(value)}")
            if len(available_vars) > 10:
                print(f"  ... and {len(available_vars) - 10} more")
        else:
            print(f"\nNo variables are currently defined.")
    
    def _suggest_attribute(self, error_msg):
        """
        Provide helpful message for attribute errors.
        
        Args:
            error_msg (str): The error message
        """
        print(f"\nTip: Check that the object has the attribute you're trying to access.")
        print(f"     Use dir(object) to see available attributes.")
    
    def _suggest_key(self, error_msg):
        """
        Provide helpful message for key errors.
        
        Args:
            error_msg (str): The error message
        """
        print(f"\nTip: The key doesn't exist in the dictionary.")
        print(f"     Use .get(key, default) to avoid KeyError, or check .keys().")
