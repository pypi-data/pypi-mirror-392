"""
AbuLangModule - Complete AbuLang Integration for Python IDLE
Enables all AbuLang commands and syntax in Python environment
"""

import builtins
import sys
import os
import yaml
from pathlib import Path

__version__ = "3.2.1"
__author__ = "Abu"

# Store original builtins
_original_builtins = {}

# Storage for multi-format blocks and local variables
_current_format = None
_format_buffer = []
_local_vars = {}  # Store local variables from functions

def load_commands():
    """Load commands from commands.yaml"""
    # Try multiple locations
    possible_paths = [
        Path(__file__).parent / "commands.yaml",
        Path("essentials/python/commands.yaml"),
        Path("../essentials/python/commands.yaml"),
    ]
    
    for path in possible_paths:
        if path.exists():
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('commands', {})
    
    return {}

def enable_abulang():
    """
    Enable ALL AbuLang commands in Python IDLE
    Makes AbuLang syntax work natively in Python
    """
    print("[AbuLang] Initializing AbuLang Module...")
    
    # Import necessary modules
    import math
    import statistics
    import time
    import logging
    import socket
    import requests
    
    # === BASIC I/O ===
    def show(*args, **kwargs):
        """AbuLang show command - display output"""
        print(*args, **kwargs)
    
    def ask(prompt=""):
        """AbuLang ask command - get user input"""
        return input(str(prompt))
    
    # === IMPORTS ===
    def libra(module_name):
        """AbuLang libra command - import library"""
        try:
            # Handle special AbuLang packages
            if module_name == "AbuSmart":
                from . import abu_smart
                builtins.smart = abu_smart
            elif module_name == "AbuFILES":
                from . import abu_files
                builtins.files = abu_files
            elif module_name == "AbuINSTALL":
                from . import abu_install
                builtins.installer = abu_install
            elif module_name == "AbuChess":
                from . import abu_chess
                builtins.chess = abu_chess
            else:
                # Standard Python import
                module = __import__(module_name)
                builtins.__dict__[module_name] = module
                print(f"[AbuLang] Imported {module_name}")
        except ImportError as e:
            print(f"[AbuLang] Could not import {module_name}: {e}")
    
    # === STRUCTURE / DEFINITION ===
    class defin:
        """AbuLang defin command - define function"""
        def __init__(self, func):
            self.func = func
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
    
    define = defin  # Alias
    
    # === DATA HANDLING ===
    def setva(var_name, value):
        """Set variable value"""
        frame = sys._getframe(1)
        frame.f_globals[var_name] = value
    
    def delet(var_name):
        """Delete variable"""
        frame = sys._getframe(1)
        if var_name in frame.f_globals:
            del frame.f_globals[var_name]
    
    # === MATH OPERATIONS ===
    def plus(a, b):
        """Add two numbers"""
        return a + b
    
    def minus(a, b):
        """Subtract two numbers"""
        return a - b
    
    def multi(a, b):
        """Multiply two numbers"""
        return a * b
    
    def divid(a, b):
        """Divide two numbers"""
        return a / b
    
    def expon(a, b):
        """Exponentiation"""
        return a ** b
    
    def modul(a, b):
        """Modulo"""
        return a % b
    
    def absof(x):
        """Absolute value"""
        return abs(x)
    
    def sumup(data):
        """Sum of list"""
        return sum(data)
    
    def avera(data):
        """Average of list"""
        return sum(data) / len(data)
    
    # === STRING OPERATIONS ===
    def strip(text):
        """Trim spaces"""
        return str(text).strip()
    
    def lower(text):
        """Lowercase"""
        return str(text).lower()
    
    def upper(text):
        """Uppercase"""
        return str(text).upper()
    
    def replc(text, old, new):
        """Replace text"""
        return str(text).replace(old, new)
    
    def findt(text, word):
        """Find substring"""
        return str(text).find(word)
    
    def lengt(text):
        """Length of string/list"""
        return len(text)
    
    # === SYSTEM OPERATIONS ===
    def pausi(seconds):
        """Pause for seconds"""
        time.sleep(seconds)
    
    def exitp():
        """Exit program"""
        sys.exit()
    
    # === FILE OPERATIONS ===
    def readf(filename):
        """Read file contents"""
        with open(filename, 'r') as f:
            return f.read()
    
    def write(filename, text):
        """Write to file"""
        with open(filename, 'w') as f:
            f.write(text)
    
    def get_line(line_num, filename):
        """Get specific line from file (1-indexed)"""
        with open(filename, 'r') as f:
            lines = f.readlines()
            if 1 <= line_num <= len(lines):
                return lines[line_num - 1].rstrip('\n')
            return None
    
    def save_as(filename):
        """Save current format buffer to file"""
        global _format_buffer
        if _format_buffer:
            with open(filename, 'w') as f:
                f.write('\n'.join(_format_buffer))
            _format_buffer = []
            return filename
        return None
    
    # === MULTI-FORMAT SUPPORT ===
    class FormatContext:
        """Context manager for multi-format blocks"""
        def __init__(self, format_type):
            self.format_type = format_type
            
        def __enter__(self):
            global _current_format, _format_buffer
            _current_format = self.format_type
            _format_buffer = []
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            global _current_format
            _current_format = None
            return False
        
        def add(self, line):
            """Add line to format buffer"""
            _format_buffer.append(str(line))
    
    def switch(format_type):
        """Switch to a different format (yaml, json, csv, etc.)"""
        return FormatContext(format_type)
    
    # === INVERSE WALRUS OPERATOR =: ===
    class CompareAssign:
        """Implements the =: operator (assign and compare)"""
        def __init__(self, value):
            self.value = value
        
        def __eq__(self, other):
            # Assign to caller's scope
            frame = sys._getframe(1)
            # Find the variable name being assigned
            import inspect
            code = frame.f_code
            # This is a simplified version - in real use, parse the line
            return self.value
        
        def compare_to(self, var_name, other_value):
            """Compare and assign: x =: 2*y assigns x=2*y and shows comparison"""
            frame = sys._getframe(2)
            frame.f_globals[var_name] = self.value
            
            if self.value < other_value:
                show(f"{var_name}<{other_value} {self.value}")
            elif self.value > other_value:
                show(f"{var_name}>{other_value} {self.value}")
            else:
                show(f"{var_name}=={other_value} {self.value}")
            
            return self.value
    
    def assign_compare(var_name, value, compare_to):
        """
        Inverse walrus: assigns and immediately compares
        Usage: assign_compare('x', 2*y, y) 
        Assigns x=2*y and shows x<y or x>y or x==y
        """
        frame = sys._getframe(1)
        frame.f_globals[var_name] = value
        
        if value < compare_to:
            show(f"{var_name}<{compare_to} {value}")
        elif value > compare_to:
            show(f"{var_name}>{compare_to} {value}")
        else:
            show(f"{var_name}=={compare_to} {value}")
        
        return value
    
    # === STRING INDEXING / FILTERING ===
    def isolate(filter_str, from_list):
        """
        Filter list to only include items containing the filter string
        Usage: isolate("abc", ["abc123", "def456", "abc789"]) -> ["abc123", "abc789"]
        """
        if isinstance(from_list, list):
            return [item for item in from_list if filter_str in str(item)]
        elif isinstance(from_list, str):
            # If it's a string, return characters that match
            return ''.join([char for char in from_list if char in filter_str])
        return []
    
    # === LOCAL VARIABLE MANAGEMENT ===
    class LocalArrow:
        """Implements the -> operator for local variable access"""
        def __init__(self, source):
            self.source = source
        
        def __gt__(self, target):
            # This gets called for ->
            # But we need custom handling
            return (self.source, target)
    
    def local(func_name):
        """
        Access local variables from a function
        Usage: local("my_func").dx returns the value of dx from my_func
        """
        class LocalAccessor:
            def __init__(self, func_name):
                self.func_name = func_name
            
            def __getattr__(self, var_name):
                key = f"{self.func_name}.{var_name}"
                if key in _local_vars:
                    return _local_vars[key]
                raise AttributeError(f"No local variable '{var_name}' in function '{self.func_name}'")
            
            def __setattr__(self, var_name, value):
                if var_name == 'func_name':
                    object.__setattr__(self, var_name, value)
                else:
                    key = f"{self.func_name}.{var_name}"
                    _local_vars[key] = value
        
        return LocalAccessor(func_name)
    
    def local_to_global(func_name, var_name):
        """
        Pull a local variable from a function to global scope
        Usage: local_to_global("my_func", "dx")
        Alternative syntax support: local->global("my_func", "dx")
        """
        key = f"{func_name}.{var_name}"
        if key in _local_vars:
            frame = sys._getframe(1)
            frame.f_globals[var_name] = _local_vars[key]
            return _local_vars[key]
        raise ValueError(f"No local variable '{var_name}' in function '{func_name}'")
    
    def save_local(func_name, var_name, value):
        """Save a local variable for later access"""
        key = f"{func_name}.{var_name}"
        _local_vars[key] = value
    
    # === ARROW OPERATOR -> ===
    class Arrow:
        """
        Implements -> operator for local->global
        Usage: Arrow("func_name") -> "var_name" pulls local to global
        """
        def __init__(self, func_name):
            self.func_name = func_name
        
        def __rshift__(self, target):
            """Handle >> as -> operator"""
            if isinstance(target, str):
                return local_to_global(self.func_name, target)
            elif hasattr(target, '__name__') and target.__name__ == 'global':
                # Return a callable that takes var_name
                def pull_to_global(var_name):
                    return local_to_global(self.func_name, var_name)
                return pull_to_global
            return None
    
    # Create a special 'global' marker for local->global syntax
    class GlobalMarker:
        def __call__(self, var_name):
            # This is called when used as local->global("var")
            pass
    
    global_marker = GlobalMarker()
    
    # Add all commands to builtins
    commands = {
        # I/O
        'show': show,
        'ask': ask,
        'input': ask,
        'displ': show,
        
        # Imports
        'libra': libra,
        'library': libra,
        
        # Structure
        'defin': defin,
        'define': define,
        
        # Data
        'setva': setva,
        'assign': setva,
        'delet': delet,
        'remove': delet,
        
        # Math
        'plus': plus,
        'minus': minus,
        'multi': multi,
        'divid': divid,
        'expon': expon,
        'modul': modul,
        'absof': absof,
        'sumup': sumup,
        'avera': avera,
        'mean': avera,
        
        # Strings
        'strip': strip,
        'trim': strip,
        'lower': lower,
        'upper': upper,
        'replc': replc,
        'replace': replc,
        'findt': findt,
        'search': findt,
        'lengt': lengt,
        'count': lengt,
        'isolate': isolate,
        
        # System
        'pausi': pausi,
        'wait': pausi,
        'exitp': exitp,
        'exit': exitp,
        'quit': exitp,
        
        # File
        'readf': readf,
        'readfile': readf,
        'write': write,
        'writi': write,
        'get_line': get_line,
        'save_as': save_as,
        
        # Multi-format
        'switch': switch,
        
        # Advanced operators
        'assign_compare': assign_compare,
        'CompareAssign': CompareAssign,
        
        # Local variables
        'local': local,
        'local_to_global': local_to_global,
        'save_local': save_local,
        'Arrow': Arrow,
        'global_marker': global_marker,
    }
    
    # Add to builtins
    for name, func in commands.items():
        if name not in _original_builtins:
            _original_builtins[name] = builtins.__dict__.get(name)
        builtins.__dict__[name] = func
    
    print("[AbuLang] ✓ Enabled!")
    print("[AbuLang] Available commands:")
    print("  I/O: show, ask, input")
    print("  Import: libra, library")
    print("  Math: plus, minus, multi, divid, expon, modul, absof, sumup, avera")
    print("  String: strip, lower, upper, replc, findt, lengt, isolate")
    print("  System: pausi, exitp")
    print("  File: readf, write, get_line, save_as")
    print("  Advanced: switch, assign_compare, local, local_to_global")
    print("\nType 'help_abulang()' for full command list")

def disable_abulang():
    """Disable AbuLang and restore original builtins"""
    for name, original in _original_builtins.items():
        if original is None:
            if name in builtins.__dict__:
                del builtins.__dict__[name]
        else:
            builtins.__dict__[name] = original
    _original_builtins.clear()
    print("[AbuLang] Disabled")

def help_abulang():
    """Show all available AbuLang commands"""
    print("""
=== AbuLang Commands ===

I/O Commands:
  show(...)       - Display output
  ask(prompt)     - Get user input
  
Import Commands:
  libra(module)   - Import library
  
Math Commands:
  plus(a, b)      - Add numbers
  minus(a, b)     - Subtract numbers
  multi(a, b)     - Multiply numbers
  divid(a, b)     - Divide numbers
  expon(a, b)     - Power (a^b)
  modul(a, b)     - Modulo (a%b)
  absof(x)        - Absolute value
  sumup(list)     - Sum of list
  avera(list)     - Average of list
  
String Commands:
  strip(text)     - Remove spaces
  lower(text)     - Lowercase
  upper(text)     - Uppercase
  replc(t,o,n)    - Replace text
  findt(text,w)   - Find substring
  lengt(text)     - Length
  isolate(str, list) - Filter list by string
  
System Commands:
  pausi(seconds)  - Pause/sleep
  exitp()         - Exit program
  
File Commands:
  readf(file)        - Read file
  write(file,txt)    - Write file
  get_line(n, file)  - Get line N from file
  save_as(file)      - Save format buffer to file

Multi-Format Commands:
  switch(format)     - Switch format (yaml, json, csv)
  save_as(file)      - Save current buffer

Advanced Operators:
  assign_compare(var, val, cmp) - Assign and compare (=: operator)
    Example: assign_compare('x', 2*y, y)
    Assigns x=2*y and shows "x<y 12" or "x>y 12"
  
Local Variable Management:
  local(func)           - Access local vars from function
    Example: dx = local("my_func").dx
  
  local_to_global(func, var) - Pull local to global
    Example: local_to_global("my_func", "dx")
  
  save_local(func, var, val) - Save local variable
    Example: save_local("my_func", "dx", 4)

String Filtering:
  isolate(filter, list) - Keep only items containing filter
    Example: isolate("abc", ["abc1", "def2", "abc3"]) -> ["abc1", "abc3"]

AbuLang Packages:
  libra("AbuSmart")    - System utilities
  libra("AbuFILES")    - File operations
  libra("AbuINSTALL")  - Package manager
  libra("AbuChess")    - Chess AI

Note: In IDLE, you must use parentheses: show("text")
For no-parentheses syntax, use .abu files: python cli.py file.abu
""")

# Auto-enable on import
enable_abulang()

# Exports
__all__ = [
    'enable_abulang',
    'disable_abulang',
    'help_abulang',
]
