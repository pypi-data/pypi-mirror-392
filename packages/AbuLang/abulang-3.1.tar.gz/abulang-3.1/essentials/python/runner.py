import re
import builtins
import math
import statistics
try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("[AbuLang Warning] sympy not installed. Calculus operations will not be available.")

try:
    from .abu_core import AbuLang
    from .gui_aliases import GUIAliasManager
    from .abu_packages import AbuSmart, AbuINSTALL, AbuFILES, AbuChess
    from .format_context import FormatContext
    from .file_operations import FileOperations
except ImportError:
    from abu_core import AbuLang
    from gui_aliases import GUIAliasManager
    try:
        from abu_packages import AbuSmart, AbuINSTALL, AbuFILES, AbuChess
    except ImportError:
        # Abu packages not available
        AbuSmart = None
        AbuINSTALL = None
        AbuFILES = None
        AbuChess = None
    try:
        from format_context import FormatContext
        from file_operations import FileOperations
    except ImportError:
        # Format context and file operations not available
        FormatContext = None
        FileOperations = None


class AbuRunner:
    """Main AbuLang interpreter and runtime handler (v1.4)."""

    def __init__(self):
        self.lang = AbuLang()
        self.gui_aliases = GUIAliasManager()
        # runtime context for variables and libraries
        self.context = {
            "math": math,
            "statistics": statistics,
            "stat": statistics,   # alias for statistics
            # GUI helper functions
            "def_box": self.gui_aliases.def_box,
            "def_circle": self.gui_aliases.def_circle,
            "get_coords": self.gui_aliases.get_coords,
        }
        # Track constants (variables marked with "always")
        self.constants = set()
        
        # Symbolic variable registry for calculus operations
        self.symbolic_vars = {}
        
        # Value type tracking system
        # Maps variable names to their type metadata
        # Format: {var_name: {'base_type': str, 'sign_type': str or None}}
        self.value_types = {}
        
        # Initialize format context and file operations for multi-format blocks
        if FormatContext and FileOperations:
            self.format_context = FormatContext()
            self.file_ops = FileOperations(self.context)
            # Add get_line as a callable function in context for use in functions
            self.context['get_line'] = self._get_line_function
        else:
            self.format_context = None
            self.file_ops = None
        
        # Initialize sympy if available
        if SYMPY_AVAILABLE:
            self._init_sympy()

    # ----------------------------------------------------
    #  VALUE TYPE TRACKING SYSTEM
    # ----------------------------------------------------
    def _track_variable_type(self, var_name, value):
        """
        Track the type metadata for a variable
        
        Stores both base type (int, float, str, etc.) and sign type
        (pos_value, neg_value) for numeric values.
        
        Args:
            var_name (str): The variable name
            value: The value being assigned
        """
        # Determine base type
        base_type = type(value).__name__
        
        # Determine sign type for numeric values
        sign_type = None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value > 0:
                sign_type = 'pos_value'
            elif value < 0:
                sign_type = 'neg_value'
            # value == 0 has no sign type
        
        # Store type metadata
        self.value_types[var_name] = {
            'base_type': base_type,
            'sign_type': sign_type
        }
    
    def _get_variable_types(self, var_name):
        """
        Get all applicable types for a variable
        
        Args:
            var_name (str): The variable name
            
        Returns:
            str: Comma-separated list of types (e.g., "int, pos_value")
        """
        if var_name not in self.value_types:
            # Variable not tracked, try to get from context
            if var_name in self.context:
                value = self.context[var_name]
                self._track_variable_type(var_name, value)
            else:
                return None
        
        type_info = self.value_types[var_name]
        types = [type_info['base_type']]
        
        if type_info['sign_type']:
            types.append(type_info['sign_type'])
        
        return ', '.join(types)
    
    def _check_value_type(self, var_name, type_check):
        """
        Check if a variable has a specific value type
        
        Args:
            var_name (str): The variable name
            type_check (str): The type to check ('pos_value' or 'neg_value')
            
        Returns:
            bool: True if the variable has the specified type
        """
        if var_name not in self.value_types:
            # Try to track it first
            if var_name in self.context:
                value = self.context[var_name]
                self._track_variable_type(var_name, value)
            else:
                return False
        
        type_info = self.value_types[var_name]
        return type_info['sign_type'] == type_check
    
    # ----------------------------------------------------
    #  SYMPY INITIALIZATION AND HELPERS
    # ----------------------------------------------------
    def _init_sympy(self):
        """Initialize sympy and add common symbolic variables"""
        if not SYMPY_AVAILABLE:
            return
        
        # Add sympy to context
        self.context['sympy'] = sympy
        
        # Pre-create common symbolic variables
        common_vars = ['x', 'y', 'z', 't', 'a', 'b', 'c', 'n']
        for var_name in common_vars:
            self.symbolic_vars[var_name] = sympy.Symbol(var_name)
            self.context[var_name] = self.symbolic_vars[var_name]
    
    def _get_or_create_symbol(self, var_name):
        """Get or create a symbolic variable"""
        if not SYMPY_AVAILABLE:
            return None
        
        if var_name not in self.symbolic_vars:
            self.symbolic_vars[var_name] = sympy.Symbol(var_name)
            self.context[var_name] = self.symbolic_vars[var_name]
        
        return self.symbolic_vars[var_name]
    
    def _parse_math_expression(self, expr_str):
        """
        Parse a mathematical expression string into a sympy expression
        
        Args:
            expr_str (str): The expression string (e.g., "x^2", "sin(x)", "2*x + 3")
        
        Returns:
            sympy expression or None if parsing fails
        """
        if not SYMPY_AVAILABLE:
            return None
        
        try:
            # Replace ^ with ** for exponentiation
            expr_str = expr_str.replace("^", "**")
            
            # Parse the expression using sympy
            # sympify will handle most mathematical expressions
            expr = sympy.sympify(expr_str, locals=self.symbolic_vars)
            
            return expr
        except Exception as e:
            print(f"[AbuLang Error] Could not parse expression '{expr_str}': {e}")
            return None
    


    # ----------------------------------------------------
    #  CALCULUS OPERATIONS
    # ----------------------------------------------------
    def _handle_derivative(self, line):
        """
        Handle derivative operator d/dx, d/dt, d/dy, etc.
        
        Pattern: d/dx expression or d/dt expression
        Example: d/dx x^2 -> 2*x
        
        Args:
            line (str): The line containing derivative operation
        
        Returns:
            bool: True if derivative was handled, False otherwise
        """
        if not SYMPY_AVAILABLE:
            print("[AbuLang Error] sympy not installed. Cannot compute derivatives.")
            return False
        
        # Match pattern: d/d<var> <expression>
        match = re.match(r'd/d(\w+)\s+(.+)', line.strip())
        if not match:
            return False
        
        var_name = match.group(1)
        expr_str = match.group(2).strip()
        
        # Get or create the symbolic variable
        var_symbol = self._get_or_create_symbol(var_name)
        
        # Parse the expression
        expr = self._parse_math_expression(expr_str)
        if expr is None:
            return True  # Error already printed
        
        # Compute the derivative
        try:
            derivative = sympy.diff(expr, var_symbol)
            # Simplify the result
            derivative = sympy.simplify(derivative)
            
            # Print the result
            print(derivative)
            
            return True
        except Exception as e:
            print(f"[AbuLang Error] Could not compute derivative: {e}")
            return True
    
    def _handle_integral(self, line):
        """
        Handle integral operator dx, dt, dy, etc.
        
        Pattern: dx expression or dt expression (antiderivative)
        Example: dx 2*x -> x^2 + C
        
        Args:
            line (str): The line containing integral operation
        
        Returns:
            bool: True if integral was handled, False otherwise
        """
        if not SYMPY_AVAILABLE:
            print("[AbuLang Error] sympy not installed. Cannot compute integrals.")
            return False
        
        # Match pattern: d<var> <expression>
        match = re.match(r'd(\w+)\s+(.+)', line.strip())
        if not match:
            return False
        
        var_name = match.group(1)
        expr_str = match.group(2).strip()
        
        # Get or create the symbolic variable
        var_symbol = self._get_or_create_symbol(var_name)
        
        # Parse the expression
        expr = self._parse_math_expression(expr_str)
        if expr is None:
            return True  # Error already printed
        
        # Compute the integral (antiderivative)
        try:
            integral = sympy.integrate(expr, var_symbol)
            # Simplify the result
            integral = sympy.simplify(integral)
            
            # Print the result with constant of integration
            print(f"{integral} + C")
            
            return True
        except Exception as e:
            print(f"[AbuLang Error] Could not compute integral: {e}")
            return True
    
    def _handle_calculus_helpers(self, line):
        """
        Handle calculus helper commands: simplify, expand, factor
        
        Commands:
        - simplify expression
        - expand expression
        - factor expression
        
        Args:
            line (str): The line containing helper command
        
        Returns:
            bool: True if command was handled, False otherwise
        """
        if not SYMPY_AVAILABLE:
            print("[AbuLang Error] sympy not installed. Cannot perform symbolic operations.")
            return False
        
        # Check for simplify command
        if line.startswith("simplify "):
            expr_str = line[9:].strip()
            expr = self._parse_math_expression(expr_str)
            if expr is not None:
                result = sympy.simplify(expr)
                print(result)
            return True
        
        # Check for expand command
        if line.startswith("expand "):
            expr_str = line[7:].strip()
            expr = self._parse_math_expression(expr_str)
            if expr is not None:
                result = sympy.expand(expr)
                print(result)
            return True
        
        # Check for factor command
        if line.startswith("factor "):
            expr_str = line[7:].strip()
            expr = self._parse_math_expression(expr_str)
            if expr is not None:
                result = sympy.factor(expr)
                print(result)
            return True
        
        return False
    
    def _handle_velocity_components(self, line):
        """
        Handle velocity component auto-definition
        
        Pattern: obj.velocity(x, y) or obj.velocity(vx, vy)
        Automatically creates dx and dy variables with the velocity components
        
        Args:
            line (str): The line containing velocity definition
        
        Returns:
            bool: True if velocity was handled, False otherwise
        """
        # Match pattern: <obj>.velocity(<x_val>, <y_val>)
        match = re.search(r'(\w+)\.velocity\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', line)
        if not match:
            return False
        
        obj_name = match.group(1)
        x_component = match.group(2).strip()
        y_component = match.group(3).strip()
        
        # Evaluate the components (don't try to evaluate the object name)
        try:
            x_value = self.eval_expr(x_component)
            y_value = self.eval_expr(y_component)
            
            # Set dx and dy variables
            self.context['dx'] = x_value
            self.context['dy'] = y_value
            
            # Optionally print confirmation
            # print(f"[Velocity] dx = {x_value}, dy = {y_value}")
            
            return True
        except Exception as e:
            # If evaluation fails, try to parse as literal numbers
            try:
                # Try direct conversion for simple numeric values
                x_value = float(x_component) if '.' in x_component else int(x_component)
                y_value = float(y_component) if '.' in y_component else int(y_component)
                
                self.context['dx'] = x_value
                self.context['dy'] = y_value
                
                return True
            except:
                print(f"[AbuLang Error] Could not set velocity components: {e}")
                return True
    
    # ----------------------------------------------------
    #  FILE OPERATIONS
    # ----------------------------------------------------
    def _get_line_function(self, line_number, filename):
        """
        Callable get_line function for use in functions and expressions
        
        This is added to the context so it can be called like:
        result = get_line(5, "file.txt")
        
        Args:
            line_number: Line number (1-indexed)
            filename: Source filename or variable name
        
        Returns:
            str: Line content or None on error
        """
        if not self.file_ops:
            print("[AbuLang Error] File operations not available")
            return None
        
        return self.file_ops.get_line(line_number, filename)
    
    def _handle_get_line(self, line):
        """
        Handle get_line command to retrieve specific lines from files
        
        Pattern: get_line <line_number> <filename>
        Example: get_line 5 data.txt
        Example: get_line 10 myfile (where myfile is a variable)
        
        Args:
            line (str): The line containing get_line command
        
        Returns:
            bool: True if get_line was handled, False otherwise
        """
        if not self.file_ops:
            print("[AbuLang Error] File operations not available")
            return False
        
        # Match pattern: get_line <line_number> <filename>
        match = re.match(r'get_line\s+(\d+)\s+(.+)', line.strip())
        if not match:
            # If pattern doesn't match, show usage help
            if line.strip().startswith('get_line'):
                print("[AbuLang Error] Invalid get_line syntax")
                print("[AbuLang] Usage: get_line <line_number> <filename>")
                print("[AbuLang] Examples:")
                print("  get_line 5 data.txt")
                print("  get_line 10 myfile  (where myfile is a variable)")
                return True
            return False
        
        line_number = int(match.group(1))
        filename = match.group(2).strip()
        
        # Call file_ops.get_line() which handles all error cases
        result = self.file_ops.get_line(line_number, filename)
        
        # Print the result if successful (errors are already printed by get_line)
        if result is not None:
            print(result)
        
        return True
    
    def _handle_switch(self, line):
        """
        Handle switch(format) command to change format context
        
        Pattern: switch(format) or switch format
        Example: switch(yaml), switch yaml
        
        Args:
            line (str): The line containing switch command
        
        Returns:
            bool: True if switch was handled, False otherwise
        """
        if not self.format_context:
            print("[AbuLang Error] Format context not available")
            return False
        
        # Match: switch(format) or switch format
        match = re.match(r'switch\s*\(?\s*(\w+)\s*\)?', line.strip())
        if not match:
            return False
        
        format_name = match.group(1)
        
        try:
            self.format_context.switch_format(format_name)
            print(f"[AbuLang] Switched to {format_name} mode")
            return True
        except ValueError as e:
            print(f"[AbuLang Error] {e}")
            print(f"[AbuLang] Supported formats: {', '.join(self.format_context.SUPPORTED_FORMATS.keys())}")
            return True
    
    def _handle_save_as(self, line):
        """
        Handle save_as(filename) command to save accumulated block
        
        Pattern: save_as(filename) or save_as filename
        Example: save_as(config.yaml), save_as data.csv
        
        Args:
            line (str): The line containing save_as command
        
        Returns:
            bool: True if save_as was handled, False otherwise
        """
        if not self.format_context or not self.file_ops:
            print("[AbuLang Error] Format context or file operations not available")
            return False
        
        # Match: save_as(filename) or save_as filename
        # Also handle variable assignment: var = save_as(filename)
        var_name = None
        if '=' in line and not line.startswith('if'):
            var_name, line = map(str.strip, line.split('=', 1))
        
        match = re.match(r'save_as\s*\(?\s*["\']?([^"\')\s]+)["\']?\s*\)?', line.strip())
        if not match:
            return False
        
        filename = match.group(1)
        
        # Get accumulated block content
        content = self.format_context.get_block()
        
        if not content:
            print("[AbuLang Error] No content to save")
            return True
        
        # Validate block according to current format
        valid, error = self.format_context.validate_block()
        if not valid:
            print(f"[AbuLang Error] Validation failed: {error}")
            return True
        
        # Save file
        result = self.file_ops.save_as(
            filename,
            content,
            self.format_context.current_format
        )
        
        # If variable assignment, store the filename
        if var_name and result:
            self.context[var_name] = result
            self._track_variable_type(var_name, result)
        
        # Reset to pythonAL mode with proper state management
        # This ensures proper context separation between format blocks
        self.format_context.reset_to_pythonal()
        
        return True
    
    def _handle_append_as(self, line):
        """
        Handle append_as(filename) command to append accumulated block
        
        Pattern: append_as(filename) or append_as filename
        Example: append_as(log.txt), append_as data.csv
        
        Args:
            line (str): The line containing append_as command
        
        Returns:
            bool: True if append_as was handled, False otherwise
        """
        if not self.format_context or not self.file_ops:
            print("[AbuLang Error] Format context or file operations not available")
            return False
        
        # Match: append_as(filename) or append_as filename
        # Also handle variable assignment: var = append_as(filename)
        var_name = None
        if '=' in line and not line.startswith('if'):
            var_name, line = map(str.strip, line.split('=', 1))
        
        match = re.match(r'append_as\s*\(?\s*["\']?([^"\')\s]+)["\']?\s*\)?', line.strip())
        if not match:
            return False
        
        filename = match.group(1)
        
        # Get accumulated block content
        content = self.format_context.get_block()
        
        if not content:
            print("[AbuLang Error] No content to append")
            return True
        
        # Append to file
        result = self.file_ops.append_as(filename, content)
        
        # If variable assignment, store the filename
        if var_name and result:
            self.context[var_name] = result
            self._track_variable_type(var_name, result)
        
        # Reset to pythonAL mode with proper state management
        # This ensures proper context separation between format blocks
        self.format_context.reset_to_pythonal()
        
        return True
    
    # ----------------------------------------------------
    #  Core execution dispatcher
    # ----------------------------------------------------
    def execute_line(self, line):
        # Store original line before stripping for indentation preservation
        original_line = line
        line = line.strip()
        
        # === BLOCK ACCUMULATION LOGIC ===
        # Check if we're in a format block (non-pythonAL format)
        # Use is_accumulating() for proper state checking
        if self.format_context and self.format_context.is_accumulating():
            # Check for block termination commands
            
            # Check for save_as (terminates block)
            if 'save_as' in line:
                # Don't accumulate this line, handle it as termination
                # This will be handled below in the save_as handler
                pass
            # Check for append_as (terminates block)
            elif 'append_as' in line:
                # Don't accumulate this line, handle it as termination
                # This will be handled below in the append_as handler
                pass
            # Check for switch (terminates current block and starts new one)
            elif line.startswith('switch'):
                # Don't accumulate this line, handle it as termination
                # This will be handled below in the switch handler
                pass
            else:
                # We're in a block and this is not a termination command
                # Accumulate the line with original indentation and whitespace
                # Preserve empty lines by checking original_line before stripping
                # If original line was empty or only whitespace, add empty string
                if not original_line.strip():
                    self.format_context.add_line('')
                else:
                    # Use original_line but strip only the trailing newline if present
                    line_to_accumulate = original_line.rstrip('\n\r')
                    self.format_context.add_line(line_to_accumulate)
                return
        
        # If line is empty after stripping, return early
        if not line:
            return
        
        # === GET_LINE HANDLING (BEFORE TRANSLATION) ===
        # Handle get_line commands before syntax translation to avoid eval errors
        
        # Handle standalone get_line command
        if line.startswith("get_line") and "=" not in line:
            if self._handle_get_line(line):
                return
        
        # Handle get_line in assignment (e.g., var = get_line 5 file.txt)
        if "=" in line and "get_line" in line and not line.startswith("if"):
            var, expr = map(str.strip, line.split("=", 1))
            
            # Check if trying to reassign a constant
            if var in self.constants:
                print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                return
            
            # Extract get_line parameters
            match = re.match(r'get_line\s+(\d+)\s+(.+)', expr.strip())
            if match:
                line_number = int(match.group(1))
                filename = match.group(2).strip()
                
                # Get the line content (don't print it)
                if self.file_ops:
                    result = self.file_ops.get_line(line_number, filename)
                    if result is not None:
                        self.context[var] = result
                        # Track type metadata
                        self._track_variable_type(var, result)
                else:
                    print("[AbuLang Error] File operations not available")
                return
        
        # === FORMAT BLOCK COMMANDS (BEFORE TRANSLATION) ===
        # Handle switch command (format switching)
        if line.startswith('switch'):
            if self.format_context:
                if self._handle_switch(line):
                    return
        
        # Handle save_as command (save block and terminate)
        if 'save_as' in line:
            if self.format_context:
                if self._handle_save_as(line):
                    return
        
        # Handle append_as command (append block and terminate)
        if 'append_as' in line:
            if self.format_context:
                if self._handle_append_as(line):
                    return
        
        # Translate only syntax enhancements, not GUI aliases
        # Since AbuLang supports normal Python, we don't need to translate
        # tkinter/pygame code - it works as-is!
        line = self.gui_aliases.translate_syntax_enhancements(line)
        
        # === VALUE TYPE CHECKING ===
        # Handle __CHECK_VALUE_TYPE__(var, type) markers from syntax translation
        if "__CHECK_VALUE_TYPE__" in line:
            # Extract the variable and type check
            match = re.search(r'__CHECK_VALUE_TYPE__\((\w+),\s*"(\w+)"\)', line)
            if match:
                var = match.group(1)
                type_check = match.group(2)
                # Perform the type check
                result = self._check_value_type(var, type_check)
                # Replace the marker with the boolean result
                line = line[:match.start()] + str(result) + line[match.end():]
        
        # === VELOCITY COMPONENT AUTO-DEFINITION ===
        # Check for obj.velocity(x, y) pattern BEFORE removing parentheses
        if ".velocity(" in line:
            if self._handle_velocity_components(line):
                return
        
        # === CALCULUS OPERATIONS ===
        # Check for derivative operator (d/dx, d/dt, etc.)
        if line.startswith("d/d"):
            if self._handle_derivative(line):
                return
        
        # Check for integral operator (dx, dt, etc.)
        # Must check this carefully to avoid matching variable names starting with 'd'
        # and to avoid matching variable assignments like "dx = -10"
        if re.match(r'^d[a-z]\s+[^=]', line):
            if self._handle_integral(line):
                return
        
        # Check for calculus helper commands (simplify, expand, factor)
        if line.startswith(("simplify ", "expand ", "factor ")):
            if self._handle_calculus_helpers(line):
                return
        
        # Handle =: operator (assign and compare)
        # Pattern: variable = value  # __COMPARE_TO_other_var__
        compare_match = re.search(r'(\w+)\s*=\s*(\S+)\s*#\s*__COMPARE_TO_(\w+)__', line)
        if compare_match:
            var = compare_match.group(1)
            value = compare_match.group(2)
            compare_var = compare_match.group(3)
            
            # Assign the value
            self.context[var] = self.eval_expr(value)
            
            # Compare and print result
            var_value = self.context[var]
            compare_value = self.context.get(compare_var, None)
            
            if compare_value is not None:
                if var_value > compare_value:
                    print(f"{var}>{compare_var} {var_value}")
                elif var_value < compare_value:
                    print(f"{var}<{compare_var} {var_value}")
                else:
                    print(f"{var}=={compare_var} {var_value}")
            return
        


        # === HELP ===
        if line.startswith("help"):
            # Handle both help(section) and help section
            if "help(" in line and line.endswith(")"):
                line = line.replace("help(", "help ").rstrip(")")
            self._handle_help(line)
            return

        # === LIBRA ===
        if line.startswith("libra") or "libra(" in line:
            # Handle both libra(module) and libra module
            if "libra(" in line and ")" in line:
                line = line.replace("libra(", "libra ").replace(")", "")
            self._handle_libra(line)
            return

        # === SHOW ===
        if line.startswith("show"):
            expr = line[4:].strip()
            
            # Handle both show("hello") and show "hello"
            # Only strip outer parentheses if they wrap the entire expression
            # Don't strip if there are parentheses inside strings
            if expr.startswith("(") and expr.endswith(")"):
                # Check if this is a simple wrapper or part of the content
                # Count parentheses to ensure we're only removing outer wrapper
                paren_count = 0
                is_wrapper = True
                for i, char in enumerate(expr[1:-1]):  # Skip first and last paren
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    # If we go negative, the closing paren isn't at the end
                    if paren_count < 0:
                        is_wrapper = False
                        break
                
                # Only strip if it's truly a wrapper (paren_count == 0 at end)
                if is_wrapper and paren_count == 0:
                    expr = expr[1:-1].strip()
            
            value = self.eval_expr(expr)

            # re-evaluate code-like strings such as stat.mean(nums)
            # Only try if it looks like a complete function call (starts with identifier and has parens)
            # Don't try if it's clearly just text with parentheses in it
            if isinstance(value, str) and re.match(r'^[a-zA-Z_][\w.]*\(.*\)$', value.strip()):
                try:
                    value = eval(value, self.context, self.context)
                except Exception:
                    # If eval fails, just keep the string value
                    # Don't print error since this is an optional re-evaluation
                    pass

            print(value)
            return

        # === ASK / SYSASK (INPUT) ===
        if line.startswith("ask") or line.startswith("sysask"):
            self._handle_ask(line)
            return
        
        # === VARIABLE ASSIGNMENT ===
        if "=" in line and not line.startswith("if"):
            # Check for constant marker
            if "# __CONSTANT__" in line:
                line = line.replace("# __CONSTANT__", "").strip()
                var, expr = map(str.strip, line.split("=", 1))
                
                # Check if trying to reassign a constant
                if var in self.constants:
                    print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                    return
                
                # Mark as constant and assign
                self.constants.add(var)
                value = self.eval_expr(expr)
                self.context[var] = value
                # Track type metadata
                self._track_variable_type(var, value)
                return
            
            var, expr = map(str.strip, line.split("=", 1))
            
            # Check if trying to reassign a constant
            if var in self.constants:
                print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                return
            
            value = self.eval_expr(expr)
            self.context[var] = value
            # Track type metadata
            self._track_variable_type(var, value)
            return

        # === TYPE INTROSPECTION ===
        # Check if user entered just a variable name (for type query)
        if re.match(r'^\w+$', line) and line in self.context:
            # Check if it's a variable (not a module or function)
            value = self.context[line]
            if not callable(value) and not hasattr(value, '__module__'):
                types = self._get_variable_types(line)
                if types:
                    print(types)
                    return
        
        # === FALLBACK RAW PYTHON ===
        try:
            exec(line, self.context, self.context)
        except Exception as e:
            print(f"[AbuLang Error] {e}")

    # ----------------------------------------------------
    #  HELP SYSTEM
    # ----------------------------------------------------
    def _handle_help(self, line):
        parts = line.split()
        if len(parts) == 1:  # plain 'help'
            sections = sorted(
                {info.get("section", "misc") for info in self.lang.commands.values()}
            )
            gui_categories = self.gui_aliases.get_all_help_categories()
            
            print("\n[HELP] AbuLang Help System v1.5")
            print("\n=== Core Command Sections ===")
            print(" " + ", ".join(sections))
            print("\n=== GUI & Library Sections ===")
            print(" " + ", ".join(gui_categories))
            print("\nType 'help <section>' to see commands in that section")
            print("Type 'help all' to see everything")
            print("\nFor complete reference, see: .kiro/specs/gui-friendly-aliases/NEW_ALIASES.md")
            return

        arg = parts[1].replace("(", "").replace(")", "")
        
        if arg.lower() == "all":
            print("\n[HELP] AbuLang Complete Reference\n")
            
            # Display all core command sections
            sections = sorted(
                {info.get("section", "misc") for info in self.lang.commands.values()}
            )
            
            for section in sections:
                found = [
                    (cmd, info)
                    for cmd, info in self.lang.commands.items()
                    if info.get("section", "") == section
                ]
                if found:
                    print(f"\n{'='*60}")
                    print(f"  {section.upper()}")
                    print(f"{'='*60}")
                    for cmd, info in found:
                        aliases_str = ""
                        if info.get('aliases'):
                            aliases_str = f" (aliases: {', '.join(info['aliases'])})"
                        print(f"  {cmd:10} - {info['desc']}{aliases_str}")
            
            # Display all GUI categories
            print(f"\n\n{'='*60}")
            print("  GUI & LIBRARY ALIASES")
            print(f"{'='*60}")
            gui_categories = self.gui_aliases.get_all_help_categories()
            for category in gui_categories:
                gui_help = self.gui_aliases.get_help_category(category)
                if gui_help:
                    print(f"\n--- {category.upper()} ---")
                    print(f"{gui_help['description']}")
                    if 'aliases' in gui_help:
                        count = len(gui_help['aliases'])
                        print(f"  ({count} aliases available - type 'help {category}' for details)")
            
            print(f"\n{'='*60}")
            print("\nFor complete reference with examples, see:")
            print("  .kiro/specs/gui-friendly-aliases/NEW_ALIASES.md")
            return

        section = arg.lower()
        
        # Check if it's a GUI help category
        gui_help = self.gui_aliases.get_help_category(section)
        if gui_help:
            self._display_gui_help(section, gui_help)
            return
        
        # Otherwise, check core commands
        found = [
            (cmd, info)
            for cmd, info in self.lang.commands.items()
            if info.get("section", "") == section
        ]
        if not found:
            print(f"No commands found for section: {section}")
            print(f"Available sections: {', '.join(sorted({info.get('section', 'misc') for info in self.lang.commands.values()}))}")
            print(f"GUI categories: {', '.join(self.gui_aliases.get_all_help_categories())}")
            return
        
        # Display section header
        print(f"\n{'='*60}")
        print(f"  {section.upper()}")
        print(f"{'='*60}")
        
        # Display commands with aliases
        for cmd, info in found:
            aliases_str = ""
            if info.get('aliases'):
                aliases_str = f" (aliases: {', '.join(info['aliases'])})"
            print(f"  {cmd:10} - {info['desc']}{aliases_str}")
        
        print(f"{'='*60}\n")
    
    def _display_gui_help(self, category, help_info):
        """Display formatted help for GUI alias categories"""
        print(f"\n{'='*60}")
        print(f"  {category.upper()} - {help_info['description']}")
        print(f"{'='*60}")
        
        # Display info if available
        if 'info' in help_info:
            print(f"\n[INFO] {help_info['info']}")
        
        # Display aliases
        if 'aliases' in help_info:
            print("\n--- Aliases ---")
            for alias, details in help_info['aliases'].items():
                if isinstance(details, dict):
                    target = details.get('target', '')
                    desc = details.get('desc', '')
                    print(f"  {alias:20} -> {target:20} {desc}")
                else:
                    print(f"  {alias:20} -> {details}")
        
        # Display parameters if available
        if 'parameters' in help_info:
            print("\n--- Parameters ---")
            for param, desc in help_info['parameters'].items():
                print(f"  {param:20} -> {desc}")
        
        # Display helpers if available
        if 'helpers' in help_info:
            print("\n--- Helper Methods ---")
            for helper, desc in help_info['helpers'].items():
                print(f"  {helper:20} -> {desc}")
        
        # Display examples
        if 'examples' in help_info:
            print("\n--- Examples ---")
            for example in help_info['examples']:
                print(f"  {example}")
        
        # Display common usage if available
        if 'common_usage' in help_info:
            print("\n--- Common Usage ---")
            for usage in help_info['common_usage']:
                print(f"  {usage}")
        
        # Display see also if available
        if 'see_also' in help_info:
            print(f"\n[TIP] {help_info['see_also']}")
        
        print(f"{'='*60}\n")

    # ----------------------------------------------------
    #  ASK (INPUT) HANDLER
    # ----------------------------------------------------
    def _handle_ask(self, line):
        """Handle ask/sysask commands - supports both ask("prompt") and ask "prompt" """
        # Remove the command prefix
        if line.startswith("ask"):
            rest = line[3:].strip()
        else:  # sysask
            rest = line[6:].strip()
        
        # Handle both ask("prompt") and ask "prompt"
        if rest.startswith("(") and rest.endswith(")"):
            rest = rest[1:-1].strip()
        
        # Check if it's an assignment: var = ask "prompt"
        if "=" in rest:
            var, prompt_expr = map(str.strip, rest.split("=", 1))
            prompt = self.eval_expr(prompt_expr)
            user_input = input(str(prompt))
            # Auto-convert numeric input
            try:
                if '.' in user_input:
                    self.context[var] = float(user_input)
                else:
                    self.context[var] = int(user_input)
            except:
                self.context[var] = user_input
        else:
            # Just ask without assignment
            prompt = self.eval_expr(rest)
            result = input(str(prompt))
            print(f"[Input received: {result}]")

    # ----------------------------------------------------
    #  LIBRA (IMPORT) HANDLER
    # ----------------------------------------------------
    def _handle_libra(self, line):
        parts = line.split()
        if len(parts) < 2:
            print("[AbuLang Error] No module specified")
            return

        module_name = parts[1].strip()
        alias = None
        if "as" in parts:
            idx = parts.index("as")
            if idx + 1 < len(parts):
                alias = parts[idx + 1].strip()

        # smart aliases: normal + creative mappings
        module_aliases = {
            "stat": "statistics",
            "maths": "math",
            "osys": "os",
            "req": "requests",
            "jsons": "json",
            "path": "os.path",
            "web": "requests",
            # visual/UI engines
            "DISPLAY": "pygame",
            "UI": "tkinter",
            "arrow": "turtle",
            # Abu packages
            "AbuSmart": "abu_packages.AbuSmart",
            "AbuINSTALL": "abu_packages.AbuINSTALL",
            "AbuFILES": "abu_packages.AbuFILES",
            "AbuChess": "abu_packages.AbuChess",
        }

        real_module = module_aliases.get(module_name, module_name)

        try:
            # Handle Abu packages specially
            if real_module.startswith("abu_packages."):
                pkg_name = real_module.split(".")[-1]
                if pkg_name == "AbuSmart" and AbuSmart:
                    imported = AbuSmart
                    self.context["smart"] = AbuSmart.smart if hasattr(AbuSmart, 'smart') else AbuSmart()
                elif pkg_name == "AbuINSTALL" and AbuINSTALL:
                    imported = AbuINSTALL
                    self.context["installer"] = AbuINSTALL.installer if hasattr(AbuINSTALL, 'installer') else AbuINSTALL()
                    self.context["install"] = AbuINSTALL.install
                elif pkg_name == "AbuFILES" and AbuFILES:
                    imported = AbuFILES
                    self.context["files"] = AbuFILES.files if hasattr(AbuFILES, 'files') else AbuFILES()
                elif pkg_name == "AbuChess" and AbuChess:
                    imported = AbuChess
                    self.context["chess"] = AbuChess.chess if hasattr(AbuChess, 'chess') else AbuChess()
                else:
                    print(f"[AbuLang Error] Abu package {pkg_name} not available")
                    return
                
                self.context[module_name] = imported
                print(f"[libra] imported Abu package {module_name}")
            else:
                imported = __import__(real_module)
                self.context[real_module] = imported

                # Always add the AbuLang alias name if different from real module
                if module_name != real_module:
                    self.context[module_name] = imported

                # user alias
                if alias:
                    self.context[alias] = imported
                    print(f"[libra] imported {real_module} as {alias}")
                else:
                    print(f"[libra] imported {real_module}")

            # auto-add shortcuts using GUIAliasManager
            if real_module == "statistics":
                self.context["stat"] = imported
            elif real_module == "math":
                self.context["maths"] = imported
            elif real_module == "pygame":
                self.context["ds"] = imported
            elif real_module == "tkinter":
                self.context["ui"] = imported
            elif real_module == "turtle":
                self.context["ar"] = imported
            
            # Check for auto-aliases from GUIAliasManager
            auto_aliases = self.gui_aliases.get_auto_aliases(module_name)
            for auto_alias in auto_aliases:
                if auto_alias not in self.context:
                    self.context[auto_alias] = imported

        except ImportError:
            print(f"[AbuLang Error] could not import {real_module}")

    # ----------------------------------------------------
    #  EXPRESSION EVALUATION
    # ----------------------------------------------------
    def eval_expr(self, expr):
        expr = expr.strip()

        # Check for explicit str"x" syntax
        if expr.startswith('str"') and expr.endswith('"'):
            return expr[4:-1]  # Return the string content without str" and "
        
        # Check for explicit int"x" or float"x" syntax
        if expr.startswith('int"') and expr.endswith('"'):
            content = expr[4:-1]
            try:
                return int(eval(content, self.context, self.context))
            except:
                return int(content)
        
        if expr.startswith('float"') and expr.endswith('"'):
            content = expr[6:-1]
            try:
                return float(eval(content, self.context, self.context))
            except:
                return float(content)

        # Auto-convert numeric strings to int/float
        if re.match(r"^['\"].*['\"]$", expr):
            string_content = expr.strip("\"'")
            
            # Only try to evaluate if it looks like a numeric expression
            # Check if it contains only numbers, operators, and whitespace
            if re.match(r'^[\d\s+\-*/().]+$', string_content):
                try:
                    # First try to evaluate it (handles "7+4", "2*3", etc.)
                    result = eval(string_content, self.context, self.context)
                    # If it's a number, return it
                    if isinstance(result, (int, float)):
                        return result
                except:
                    pass
            
            # Try direct int/float conversion for simple numeric strings
            try:
                if '.' in string_content:
                    return float(string_content)
                else:
                    return int(string_content)
            except:
                # Not numeric, return as string
                return string_content

        # variable lookup
        if expr in self.context:
            return self.context[expr]

        # math shorthand
        expr = expr.replace("^", "**")
        expr = re.sub(r"(\d+)%", r"(\1/100)", expr)  # 50% → (50/100)

        try:
            return eval(expr, self.context, self.context)
        except Exception:
            return expr

    # ----------------------------------------------------
    #  COMMENT STRIPPING
    # ----------------------------------------------------
    def _strip_comments(self, line: str) -> str:
        """
        Remove comments (# or //) from a line while preserving them inside string literals.
        
        Args:
            line (str): The line to process
            
        Returns:
            str: The line with comments removed
        """
        # Track whether we're inside a string literal
        in_string = False
        quote_char = None
        comment_pos = -1
        
        for i, char in enumerate(line):
            # Check for quote characters (handle escaped quotes)
            if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
            # Check for comment markers outside of strings
            elif not in_string:
                if char == '#':
                    comment_pos = i
                    break
                elif i < len(line) - 1 and line[i:i+2] == '//':
                    comment_pos = i
                    break
        
        # Remove comment if found
        if comment_pos >= 0:
            line = line[:comment_pos]
        
        return line

    # ----------------------------------------------------
    #  MAIN RUNTIME LOOP
    # ----------------------------------------------------
    def run(self, code: str):
        for line in code.splitlines():
            # Strip comments while preserving them inside strings
            line = self._strip_comments(line)
            
            line = line.strip()
            if not line:
                continue

            self.execute_line(line)
# ----------------------------------------------------
#  END OF AbuRunner