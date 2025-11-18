"""
Enhanced AbuLang Runner

This module extends the base AbuRunner class with advanced features including
multi-line support, debugging, profiling, and enhanced error handling.
"""

try:
    from .runner import AbuRunner
    from .enhanced_core import EnhancedAbuLang
    from .error_reporter import ErrorReporter
except ImportError:
    from runner import AbuRunner
    from enhanced_core import EnhancedAbuLang
    from error_reporter import ErrorReporter


class EnhancedAbuRunner(AbuRunner):
    """
    Enhanced version of AbuRunner with support for:
    - Multi-line code blocks (functions, classes, loops)
    - Debug mode with breakpoints
    - Performance profiling
    - Enhanced error reporting
    - Variable watching
    """
    
    def __init__(self, debug_mode=False, profile_mode=False, forgiving=False):
        """
        Initialize the enhanced runner.
        
        Args:
            debug_mode (bool): Enable debugging features
            profile_mode (bool): Enable performance profiling
            forgiving (bool): Enable forgiving mode (auto-fix common syntax errors)
        """
        super().__init__()
        
        # Replace base lang with enhanced version
        self.lang = EnhancedAbuLang()
        
        # Multi-line support
        self.multiline_buffer = []
        self.in_multiline = False
        self.multiline_indent_level = 0
        self.empty_line_count = 0
        
        # Debug and profiling
        self.debug_mode = debug_mode
        self.profile_mode = profile_mode
        self.profiler = None
        
        # Forgiving mode - auto-fix common syntax errors
        self.forgiving = forgiving
        self.breakpoints = set()
        self.step_mode = False
        
        # Variable watching
        self.watches = {}
        
        # Error reporter - initialize immediately
        self.error_reporter = ErrorReporter(self)
    
    def _parse_blocks(self, code: str) -> list:
        """
        Parse code into executable units (single lines or multi-line blocks).
        
        This method implements the core block parsing algorithm that:
        - Detects block headers (lines ending with ':')
        - Tracks indentation levels to determine block boundaries
        - Handles empty lines within blocks (preserves them)
        - Returns list of tuples: (code_string, line_number, is_block)
        
        Args:
            code (str): The complete AbuLang program as a string
            
        Returns:
            list: List of tuples (code_string, start_line_number, is_block)
                  where is_block is True for multi-line blocks, False for single lines
        """
        lines = code.splitlines()
        units = []
        current_block = []
        current_block_start = 0
        base_indent = None
        
        for line_num, line in enumerate(lines, 1):
            # Strip comments (preserving strings)
            cleaned_line = self._strip_comments(line)
            
            # Skip empty lines outside of blocks
            if not cleaned_line.strip():
                if current_block:
                    # Preserve empty lines within blocks
                    current_block.append(line)
                continue
            
            # Measure indentation (spaces/tabs)
            indent = len(cleaned_line) - len(cleaned_line.lstrip())
            
            # Check if this starts a new block (ends with :)
            if cleaned_line.rstrip().endswith(':') and not current_block:
                # Start accumulating a new block
                current_block = [line]
                current_block_start = line_num
                base_indent = indent
                continue
            
            # If we're currently in a block
            if current_block:
                # Check if this line is part of the block (indented more than base)
                if indent > base_indent or not cleaned_line.strip():
                    # Still in the block - accumulate this line
                    current_block.append(line)
                # Check if this is an elif/else continuation at the same level
                elif indent == base_indent and cleaned_line.strip().startswith(('elif ', 'else:')):
                    # This is a continuation of the current if block
                    current_block.append(line)
                else:
                    # Dedent detected - block is complete
                    # Check for incomplete block (header with no body)
                    if len(current_block) == 1:
                        # Only has the header line, no indented body
                        print(f"[AbuLang Error] Line {current_block_start}: Incomplete block")
                        print(f"  Block header '{current_block[0].strip()}' has no indented body")
                        print(f"\n  Did you mean to:")
                        print(f"    - Add indented lines after the ':' ?")
                        print(f"    - Remove the ':' if this is a single-line statement?")
                        current_block = []
                        base_indent = None
                        # Continue processing current line
                        if cleaned_line.rstrip().endswith(':'):
                            current_block = [line]
                            current_block_start = line_num
                            base_indent = indent
                        else:
                            units.append((cleaned_line, line_num, False))
                        continue
                    
                    block_code = '\n'.join(current_block)
                    units.append((block_code, current_block_start, True))
                    current_block = []
                    base_indent = None
                    
                    # Process current line (might start a new block or be a single line)
                    if cleaned_line.rstrip().endswith(':'):
                        # This line starts a new block
                        current_block = [line]
                        current_block_start = line_num
                        base_indent = indent
                    else:
                        # Single line command
                        units.append((cleaned_line, line_num, False))
            else:
                # Not in a block - check if this line starts one
                if cleaned_line.rstrip().endswith(':'):
                    # Start a new block
                    current_block = [line]
                    current_block_start = line_num
                    base_indent = indent
                else:
                    # Single line command
                    units.append((cleaned_line, line_num, False))
        
        # Handle any remaining block at end of file
        if current_block:
            block_code = '\n'.join(current_block)
            # Check for incomplete block (header with no body)
            if len(current_block) == 1:
                # Only has the header line, no indented body
                print(f"[AbuLang Error] Line {current_block_start}: Incomplete block")
                print(f"  Block header '{current_block[0].strip()}' has no indented body")
                print(f"\n  Did you mean to:")
                print(f"    - Add indented lines after the ':' ?")
                print(f"    - Remove the ':' if this is a single-line statement?")
                return units
            units.append((block_code, current_block_start, True))
        
        return units
    
    def _strip_comments(self, line: str) -> str:
        """
        Strip comments from a line while preserving # and // inside strings.
        
        Args:
            line (str): Line to process
            
        Returns:
            str: Line with comments removed
        """
        in_string = False
        quote_char = None
        comment_pos = -1
        
        for i, char in enumerate(line):
            # Handle string boundaries
            if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
            # Look for comments outside strings
            elif not in_string:
                if char == '#':
                    comment_pos = i
                    break
                elif i < len(line) - 1 and line[i:i+2] == '//':
                    comment_pos = i
                    break
        
        # Remove comment if found
        if comment_pos >= 0:
            return line[:comment_pos]
        
        return line
    
    def _execute_block(self, block_code: str, line_num: int):
        """
        Execute a multi-line code block.
        
        This method:
        - Applies AbuLang syntax translations to each line while preserving indentation
        - Executes the complete block using exec() with the shared context
        - Ensures variables and functions defined in blocks are available in context
        
        Args:
            block_code (str): The complete block as a string
            line_num (int): Starting line number for error reporting
        """
        # === BLOCK ACCUMULATION FOR FORMAT BLOCKS ===
        # If we're in a format block, accumulate all lines instead of executing
        if self.format_context and self.format_context.in_block and self.format_context.current_format != 'pythonAL':
            # Accumulate all lines in the block
            for line in block_code.splitlines():
                line_to_accumulate = line.rstrip('\n\r')
                self.format_context.add_line(line_to_accumulate)
            return
        
        try:
            # Check if we're in Python mode (pure Python, no AbuLang translation)
            in_python_mode = (self.format_context and 
                            self.format_context.current_format == 'python')
            
            if in_python_mode:
                # Python mode: Execute block as-is without AbuLang translation
                exec(block_code, self.context, self.context)
            else:
                # pythonAL mode: Apply AbuLang syntax translations to each line
                translated_lines = []
                for line in block_code.splitlines():
                    # Only translate non-empty, non-comment lines
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        # Preserve indentation while translating
                        indent = len(line) - len(line.lstrip())
                        
                        # Convert AbuLang commands to Python
                        # Handle 'show' command
                        if stripped.startswith('show '):
                            expr = stripped[5:].strip()
                            translated = f'print({expr})'
                        # Handle 'ask' or 'sysask' command
                        elif stripped.startswith('ask ') or stripped.startswith('sysask '):
                            if stripped.startswith('ask '):
                                rest = stripped[4:].strip()
                            else:
                                rest = stripped[7:].strip()
                            
                            # Check if it's an assignment
                            if '=' in rest and not rest.startswith('='):
                                var, prompt = map(str.strip, rest.split('=', 1))
                                translated = f'{var} = input({prompt})'
                            else:
                                translated = f'input({rest})'
                        else:
                            # Apply syntax enhancements for other lines
                            translated = self.gui_aliases.translate_line(stripped)
                        
                        translated_lines.append(' ' * indent + translated)
                    else:
                        # Preserve empty lines and comments as-is
                        translated_lines.append(line)
                
                translated_block = '\n'.join(translated_lines)
                
                # Execute the block with the shared context
                # This ensures variables and functions defined in blocks are available
                exec(translated_block, self.context, self.context)
            
        except IndentationError as e:
            self._handle_indentation_error(e, line_num, block_code)
        except SyntaxError as e:
            self._handle_syntax_error(e, line_num, block_code)
        except NameError as e:
            self._handle_name_error(e, line_num)
        except Exception as e:
            print(f"[AbuLang Error] Line {line_num}: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def _handle_indentation_error(self, error, line_num, code):
        """
        Handle indentation errors with helpful messages.
        
        Args:
            error (IndentationError): The indentation error
            line_num (int): Starting line number of the block
            code (str): The code block that caused the error
        """
        print(f"[AbuLang Error] Line {line_num}: Indentation error")
        print(f"  {error}")
        print(f"\n  Did you mean to:")
        print(f"    - Use consistent indentation (spaces or tabs, not both)?")
        print(f"    - Indent the line after ':' ?")
        print(f"    - Match the indentation of surrounding lines?")
    
    def _handle_syntax_error(self, error, line_num, code):
        """
        Handle syntax errors with helpful messages.
        
        Args:
            error (SyntaxError): The syntax error
            line_num (int): Starting line number of the block
            code (str): The code block that caused the error
        """
        print(f"[AbuLang Error] Line {line_num}: Syntax error")
        print(f"  {error}")
        
        # Check for common mistakes
        if ":" not in code and any(kw in code for kw in ['if', 'for', 'while', 'def', 'class']):
            print(f"\n  Did you mean to add ':' at the end of the line?")
        elif "elif" in code or "else" in code:
            print(f"\n  Did you mean to:")
            print(f"    - Match the indentation of the corresponding 'if' statement?")
            print(f"    - Add ':' at the end of the line?")
    
    def _handle_name_error(self, error, line_num):
        """
        Handle name errors with suggestions for similar variable names.
        
        Args:
            error (NameError): The name error
            line_num (int): Line number where the error occurred
        """
        import re
        
        # Extract variable name from error message
        match = re.search(r"name '(\w+)' is not defined", str(error))
        if match:
            undefined_var = match.group(1)
            # Find similar variable names in context
            similar = [var for var in self.context.keys() 
                       if not var.startswith('__') and not callable(self.context[var])
                       and var.lower().startswith(undefined_var[0].lower())]
            
            print(f"[AbuLang Error] Line {line_num}: {error}")
            if similar:
                print(f"\n  Did you mean: {', '.join(similar[:3])}?")
        else:
            print(f"[AbuLang Error] Line {line_num}: {error}")
    
    def enter_multiline_mode(self, line):
        """
        Enter multi-line mode when a line ends with colon.
        
        Args:
            line (str): The line that triggered multi-line mode
        """
        self.in_multiline = True
        self.multiline_buffer = [line]
        # Calculate initial indent level
        self.multiline_indent_level = len(line) - len(line.lstrip())
    
    def add_to_multiline(self, line):
        """
        Add a line to the multi-line buffer or execute if block is complete.
        
        Args:
            line (str): Line to add to buffer
            
        Returns:
            bool: True if block was executed, False if still collecting
        """
        # Check if line is dedented (back to original level or less)
        current_indent = len(line) - len(line.lstrip())
        
        # Empty line handling
        if not line.strip():
            self.empty_line_count += 1
            # Two consecutive empty lines end the block
            if self.empty_line_count >= 2:
                if self.multiline_buffer:
                    self.execute_multiline_block()
                self.in_multiline = False
                self.multiline_buffer = []
                self.empty_line_count = 0
                return True
            # Single empty line - add to buffer
            self.multiline_buffer.append(line)
            return False
        
        # Reset empty line counter when we see content
        self.empty_line_count = 0
        
        # Dedented line signals end of block
        if current_indent <= self.multiline_indent_level:
            # Execute the buffered block first
            if self.multiline_buffer:
                self.execute_multiline_block()
            self.in_multiline = False
            self.multiline_buffer = []
            # Execute the dedented line
            self.execute_line(line)
            return True
        
        # Still in the block, add to buffer
        self.multiline_buffer.append(line)
        return False
    
    def execute_multiline_block(self):
        """
        Execute the collected multi-line code block with error tracking.
        """
        if not self.multiline_buffer:
            return
        
        # Apply forgiving mode fixes and convert AbuLang commands to Python
        fixed_buffer = []
        for line in self.multiline_buffer:
            # Apply forgiving mode fixes if enabled
            if self.forgiving:
                line = self._fix_syntax_forgiving(line)
            
            # Convert AbuLang commands to Python
            line = self._convert_abulang_to_python(line)
            fixed_buffer.append(line)
        
        self.multiline_buffer = fixed_buffer
        
        code = '\n'.join(self.multiline_buffer)
        try:
            exec(code, self.context, self.context)
        except SyntaxError as e:
            # Report syntax error with line context
            self._report_multiline_error(e, code, e.lineno if hasattr(e, 'lineno') else None)
        except Exception as e:
            # Report runtime error with full block context
            self._report_multiline_error(e, code, None)
    
    def _convert_abulang_to_python(self, line):
        """
        Convert AbuLang commands to Python within a line while preserving indentation.
        
        Args:
            line (str): Line to convert
            
        Returns:
            str: Converted line
        """
        import re
        
        # Preserve leading whitespace
        leading_space = len(line) - len(line.lstrip())
        indent = line[:leading_space]
        stripped_line = line.strip()
        
        # Convert 'show' to 'print()'
        if stripped_line.startswith('show '):
            expr = stripped_line[5:].strip()
            return f"{indent}print({expr})"
        
        # Convert 'ask' or 'sysask' to 'input()'
        if stripped_line.startswith('ask ') or stripped_line.startswith('sysask '):
            if stripped_line.startswith('ask '):
                rest = stripped_line[4:].strip()
            else:
                rest = stripped_line[7:].strip()
            
            # Check if it's an assignment
            if '=' in rest and not rest.startswith('='):
                var, prompt = map(str.strip, rest.split('=', 1))
                return f"{indent}{var} = input({prompt})"
            else:
                return f"{indent}input({rest})"
        
        return line
    
    def _report_multiline_error(self, error, code, error_line=None):
        """
        Report an error that occurred in a multi-line block.
        
        Args:
            error (Exception): The error that occurred
            code (str): The full multi-line code block
            error_line (int): Line number within the block where error occurred
        """
        print(f"\n[AbuLang Multi-line Error] {type(error).__name__}: {error}")
        
        if error_line is not None:
            # Show the specific line where the error occurred
            lines = code.splitlines()
            if 0 < error_line <= len(lines):
                print(f"  At line {error_line} in block:")
                print(f"    {lines[error_line - 1]}")
        else:
            # Show the entire block for context
            print("  In code block:")
            for i, line in enumerate(code.splitlines(), 1):
                print(f"    {i}: {line}")
        
        # Use error reporter if available
        if self.error_reporter:
            if self.debug_mode:
                import traceback
                traceback.print_exc()
    
    def execute_line(self, line, line_number=None):
        """
        Execute a single line with enhanced features.
        
        This method is now called by the run() method for single-line commands only.
        Multi-line blocks are handled by _execute_block().
        
        Args:
            line (str): Line to execute (already cleaned by block parser)
            line_number (int): Optional line number for debugging
        """
        # Store original line before stripping for indentation preservation
        original_line = line
        
        # === BLOCK ACCUMULATION LOGIC ===
        # Check if we're in a format block (non-pythonAL format)
        if self.format_context and self.format_context.in_block and self.format_context.current_format != 'pythonAL':
            # Check for block termination commands
            stripped_line = line.strip()
            
            # Check for save_as (terminates block)
            if 'save_as' in stripped_line:
                # Don't accumulate this line, handle it as termination
                # This will be handled below in the save_as handler
                pass
            # Check for append_as (terminates block)
            elif 'append_as' in stripped_line:
                # Don't accumulate this line, handle it as termination
                # This will be handled below in the append_as handler
                pass
            # Check for switch (terminates current block and starts new one)
            elif stripped_line.startswith('switch'):
                # Don't accumulate this line, handle it as termination
                # This will be handled below in the switch handler
                pass
            else:
                # We're in a block and this is not a termination command
                # Accumulate the line with original indentation and whitespace
                # Use original_line but strip only the trailing newline if present
                line_to_accumulate = original_line.rstrip('\n\r')
                self.format_context.add_line(line_to_accumulate)
                return
        
        # Strip whitespace from single lines
        line = line.strip()
        if not line:
            return
        
        # Debug mode: check breakpoints
        if self.debug_mode and line_number and line_number in self.breakpoints:
            self.pause_for_debug(line, line_number)
        
        # Profiling: start timing
        if self.profile_mode and self.profiler and line_number:
            self.profiler.start_line(line_number)
        
        # Execute the line with enhanced error handling
        try:
            self._execute_with_error_handling(line)
            
            # Check watches for changes
            self._check_watches()
            
        except Exception as e:
            if self.error_reporter:
                self.error_reporter.report_error(e, line, line_number)
            else:
                print(f"[AbuLang Error] {type(e).__name__}: {e}")
        
        # Profiling: end timing
        if self.profile_mode and self.profiler and line_number:
            self.profiler.end_line(line_number)
    
    def _fix_syntax_forgiving(self, line):
        """
        Auto-fix common syntax errors when in forgiving mode.
        
        Args:
            line (str): Line to fix
            
        Returns:
            str: Fixed line
        """
        import re
        
        original_line = line
        
        # Preserve leading whitespace (indentation)
        leading_space = len(line) - len(line.lstrip())
        indent = line[:leading_space]
        stripped_line = line.strip()
        
        # Fix 1: Add colon to if/while/for/def/class statements
        # Pattern: if x=5 → if x==5:
        # Pattern: if x==5 → if x==5:
        if_while_for_pattern = r'^(if|while|elif)\s+(.+?)(?<!:)$'
        match = re.match(if_while_for_pattern, stripped_line)
        if match:
            keyword = match.group(1)
            condition = match.group(2).strip()
            
            # Fix single = to == in conditions
            # But not if it's already ==, !=, <=, >=
            if '=' in condition and not any(op in condition for op in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=']):
                # Replace single = with == (but be careful with assignments)
                parts = condition.split('=')
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    # If left side is a simple variable name, assume comparison
                    if left.replace('_', '').replace('.', '').isalnum():
                        condition = f"{left} == {right}"
            
            line = f"{indent}{keyword} {condition}:"
            if self.debug_mode:
                print(f"[Forgiving] Fixed: '{original_line.strip()}' → '{line.strip()}'")
        
        # Fix 2: Add colon to for loops
        for_pattern = r'^for\s+(.+?)\s+in\s+(.+?)(?<!:)$'
        match = re.match(for_pattern, stripped_line)
        if match:
            var = match.group(1)
            iterable = match.group(2)
            line = f"{indent}for {var} in {iterable}:"
            if self.debug_mode:
                print(f"[Forgiving] Fixed: '{original_line.strip()}' → '{line.strip()}'")
        
        # Fix 3: Add colon to def/class
        def_class_pattern = r'^(def|class)\s+(.+?)(?<!:)$'
        match = re.match(def_class_pattern, stripped_line)
        if match:
            keyword = match.group(1)
            rest = match.group(2)
            line = f"{indent}{keyword} {rest}:"
            if self.debug_mode:
                print(f"[Forgiving] Fixed: '{original_line.strip()}' → '{line.strip()}'")
        
        # Fix 4: Add colon to else
        if stripped_line == 'else':
            line = f'{indent}else:'
            if self.debug_mode:
                print(f"[Forgiving] Fixed: '{original_line.strip()}' → '{line.strip()}'")
        
        # Fix 5: Add colon to try/except/finally
        try_except_pattern = r'^(try|except|finally)(?:\s+(.+?))?(?<!:)$'
        match = re.match(try_except_pattern, stripped_line)
        if match:
            keyword = match.group(1)
            rest = match.group(2) if match.group(2) else ''
            if rest:
                line = f"{indent}{keyword} {rest}:"
            else:
                line = f"{indent}{keyword}:"
            if self.debug_mode:
                print(f"[Forgiving] Fixed: '{original_line.strip()}' → '{line.strip()}'")
        
        return line
    
    def _execute_with_error_handling(self, line):
        """
        Execute a line with proper error propagation for enhanced error reporting.
        
        Args:
            line (str): Line to execute
        """
        import re
        
        # Check if we're in Python mode (pure Python, no AbuLang translation)
        in_python_mode = (self.format_context and 
                         self.format_context.current_format == 'python')
        
        # Translate GUI aliases and syntax enhancements FIRST (unless in Python mode)
        original_line = line
        if not in_python_mode:
            line = self.gui_aliases.translate_line(line)
            if self.debug_mode and line != original_line:
                print(f"[Debug] Translated: '{original_line}' -> '{line}'")
        
        # Handle =: operator (assign and compare)
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
        
        # Apply forgiving mode fixes if enabled
        if self.forgiving:
            line = self._fix_syntax_forgiving(line)
        
        # === HELP ===
        if line.startswith("help"):
            self._handle_help(line)
            return

        # === LIBRA ===
        if line.startswith("libra "):
            self._handle_libra(line)
            return

        # === SHOW === (only in pythonAL mode)
        if not in_python_mode and line.startswith("show"):
            expr = line[4:].strip()
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

        # === ASK / SYSASK (INPUT) === (only in pythonAL mode)
        if not in_python_mode and (line.startswith("ask ") or line.startswith("sysask ")):
            self._handle_ask(line)
            return
        
        # === GET_LINE (FILE LINE RETRIEVAL) ===
        if line.startswith("get_line"):
            if self._handle_get_line(line):
                return
        
        # === FORMAT BLOCK COMMANDS ===
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

        # === VARIABLE ASSIGNMENT ===
        # In Python mode, skip custom assignment handling and use native Python
        # In pythonAL mode, handle special AbuLang assignment features
        if not in_python_mode and "=" in line and not line.startswith("if"):
            # Check if the = is inside parentheses (function call with keyword args)
            paren_depth = 0
            equals_in_parens = False
            for i, char in enumerate(line):
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == '=' and paren_depth > 0:
                    equals_in_parens = True
                    break
            
            # If = is inside parentheses, it's not an assignment
            if not equals_in_parens:
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
                    self.context[var] = self.eval_expr(expr)
                    return
                
                var, expr = map(str.strip, line.split("=", 1))
                
                # Check if trying to reassign a constant
                if var in self.constants:
                    print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                    return
                
                # Check if the expression contains ask/sysask
                if expr.startswith("ask ") or expr.startswith("sysask "):
                    # Handle ask in assignment
                    if expr.startswith("ask "):
                        prompt_expr = expr[4:].strip()
                    else:  # sysask
                        prompt_expr = expr[7:].strip()
                    
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
                    return
                
                # Check if the expression contains get_line
                if expr.startswith("get_line "):
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
                    else:
                        print("[AbuLang Error] Invalid get_line syntax in assignment")
                        print("[AbuLang] Usage: var = get_line <line_number> <filename>")
                        return
                
                self.context[var] = self.eval_expr(expr)
                return

        # === FALLBACK RAW PYTHON ===
        # Check if first word is a known AbuLang command
        words = line.split()
        if words:
            first_word = words[0]
            # Check if it looks like an AbuLang command but isn't recognized
            if first_word not in self.lang.lookup and not first_word.startswith(('if', 'for', 'while', 'def', 'class', 'import', 'from', 'return', 'try', 'except', 'with')):
                # Try to execute as Python first, if it fails with SyntaxError, report as unknown command
                try:
                    exec(line, self.context, self.context)
                    return
                except SyntaxError:
                    # Likely an unknown AbuLang command
                    raise ValueError(f"Unknown AbuLang command: {first_word}")
        
        exec(line, self.context, self.context)
    
    def pause_for_debug(self, line, line_number):
        """
        Pause execution for debugging.
        
        Args:
            line (str): Current line being executed
            line_number (int): Line number
        """
        print(f"\n[Debug] Breakpoint at line {line_number}: {line}")
        print("Commands: (c)ontinue, (s)tep, (v)ars, (p)rint <expr>, (q)uit")
        
        while True:
            try:
                cmd = input("(debug) ").strip()
                
                if cmd in ('c', 'continue'):
                    self.step_mode = False
                    break
                elif cmd in ('s', 'step'):
                    self.step_mode = True
                    break
                elif cmd in ('v', 'vars'):
                    self._show_variables()
                elif cmd.startswith('p '):
                    expr = cmd[2:].strip()
                    try:
                        result = eval(expr, self.context)
                        print(result)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd in ('q', 'quit'):
                    raise KeyboardInterrupt("Debug quit")
                else:
                    print("Unknown command")
            except EOFError:
                break
    
    def _show_variables(self):
        """Display all variables in the current context."""
        print("\nCurrent variables:")
        for name, value in sorted(self.context.items()):
            if not name.startswith('__') and not callable(value):
                print(f"  {name} = {repr(value)}")
    
    def _handle_ask(self, line):
        """Handle ask/sysask commands for user input."""
        # Remove the command prefix
        if line.startswith("ask "):
            rest = line[4:].strip()
        else:  # sysask
            rest = line[7:].strip()
        
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
    
    def _handle_help(self, line):
        """Handle help command - delegate to parent implementation."""
        super()._handle_help(line)
    
    def _handle_libra(self, line):
        """Handle libra (import) command - delegate to parent implementation."""
        super()._handle_libra(line)
    
    def eval_expr(self, expr):
        """
        Evaluate expression with proper error propagation.
        
        Args:
            expr (str): Expression to evaluate
            
        Returns:
            The evaluated result
            
        Raises:
            Exception: Any evaluation errors are propagated for error reporting
        """
        import re
        
        expr = expr.strip()

        # literal string
        if re.match(r"^['\"].*['\"]$", expr):
            return expr.strip("\"'")

        # variable lookup
        if expr in self.context:
            return self.context[expr]

        # math shorthand
        expr = expr.replace("^", "**")
        expr = re.sub(r"(\d+)%", r"(\1/100)", expr)  # 50% → (50/100)

        # Let errors propagate instead of catching them
        return eval(expr, self.context, self.context)
    
    def _check_watches(self):
        """Check watched variables for changes."""
        for var_name, old_value in list(self.watches.items()):
            if var_name in self.context:
                new_value = self.context[var_name]
                if new_value != old_value:
                    print(f"[Watch] {var_name} changed: {old_value} -> {new_value}")
                    self.watches[var_name] = new_value
    
    def set_breakpoint(self, line_number):
        """
        Set a breakpoint at the specified line number.
        
        Args:
            line_number (int): Line number for breakpoint
        """
        self.breakpoints.add(line_number)
        print(f"Breakpoint set at line {line_number}")
    
    def watch_variable(self, var_name):
        """
        Watch a variable for changes.
        
        Args:
            var_name (str): Variable name to watch
        """
        if var_name in self.context:
            self.watches[var_name] = self.context[var_name]
            print(f"Watching variable: {var_name}")
        else:
            print(f"Variable '{var_name}' not found in context")
    
    def run(self, code: str):
        """
        Execute AbuLang code with support for multi-line blocks.
        
        This method uses the block parser to identify executable units
        (single lines or complete blocks) and routes them to the appropriate
        execution method.
        
        Args:
            code (str): The complete AbuLang program as a string
        """
        try:
            # Parse code into executable units (single lines or blocks)
            units = self._parse_blocks(code)
            
            # Execute each unit with appropriate error handling
            for code_string, line_num, is_block in units:
                if is_block:
                    # Multi-line block - execute as a complete unit
                    self._execute_block(code_string, line_num)
                else:
                    # Single line - use existing execute_line method
                    try:
                        self.execute_line(code_string, line_num)
                    except NameError as e:
                        # Handle undefined variable errors with suggestions
                        self._handle_name_error(e, line_num)
                    except Exception as e:
                        # Handle other errors with line number context
                        print(f"[AbuLang Error] Line {line_num}: {e}")
                        if self.debug_mode:
                            import traceback
                            traceback.print_exc()
                            
        except Exception as e:
            # Handle any unexpected errors during parsing or execution
            print(f"[AbuLang Error] {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
