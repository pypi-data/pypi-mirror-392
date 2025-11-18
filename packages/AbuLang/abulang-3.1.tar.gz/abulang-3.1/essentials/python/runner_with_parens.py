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
except ImportError:
    from abu_core import AbuLang
    from gui_aliases import GUIAliasManager


class AbuRunner:
    """Main AbuLang interpreter with PARENTHESES SUPPORT for complex Python code."""

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
        self.value_types = {}
        
        # Initialize sympy if available
        if SYMPY_AVAILABLE:
            self._init_sympy()

    # ----------------------------------------------------
    #  VALUE TYPE TRACKING SYSTEM
    # ----------------------------------------------------
    def _track_variable_type(self, var_name, value):
        """Track the type metadata for a variable"""
        base_type = type(value).__name__
        sign_type = None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value > 0:
                sign_type = 'pos_value'
            elif value < 0:
                sign_type = 'neg_value'
        
        self.value_types[var_name] = {
            'base_type': base_type,
            'sign_type': sign_type
        }
    
    def _get_variable_types(self, var_name):
        """Get all applicable types for a variable"""
        if var_name not in self.value_types:
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
        """Check if a variable has a specific value type"""
        if var_name not in self.value_types:
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
        
        self.context['sympy'] = sympy
        
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
        """Parse a mathematical expression string into a sympy expression"""
        if not SYMPY_AVAILABLE:
            return None
        
        try:
            expr_str = expr_str.replace("^", "**")
            expr = sympy.sympify(expr_str, locals=self.symbolic_vars)
            return expr
        except Exception as e:
            print(f"[AbuLang Error] Could not parse expression '{expr_str}': {e}")
            return None
    
    # ----------------------------------------------------
    #  CALCULUS OPERATIONS
    # ----------------------------------------------------
    def _handle_derivative(self, line):
        """Handle derivative operator d/dx, d/dt, d/dy, etc."""
        if not SYMPY_AVAILABLE:
            print("[AbuLang Error] sympy not installed. Cannot compute derivatives.")
            return False
        
        match = re.match(r'd/d(\w+)\s+(.+)', line.strip())
        if not match:
            return False
        
        var_name = match.group(1)
        expr_str = match.group(2).strip()
        
        var_symbol = self._get_or_create_symbol(var_name)
        expr = self._parse_math_expression(expr_str)
        if expr is None:
            return True
        
        try:
            derivative = sympy.diff(expr, var_symbol)
            derivative = sympy.simplify(derivative)
            print(derivative)
            return True
        except Exception as e:
            print(f"[AbuLang Error] Could not compute derivative: {e}")
            return True
    
    def _handle_integral(self, line):
        """Handle integral operator dx, dt, dy, etc."""
        if not SYMPY_AVAILABLE:
            print("[AbuLang Error] sympy not installed. Cannot compute integrals.")
            return False
        
        match = re.match(r'd(\w+)\s+(.+)', line.strip())
        if not match:
            return False
        
        var_name = match.group(1)
        expr_str = match.group(2).strip()
        
        var_symbol = self._get_or_create_symbol(var_name)
        expr = self._parse_math_expression(expr_str)
        if expr is None:
            return True
        
        try:
            integral = sympy.integrate(expr, var_symbol)
            integral = sympy.simplify(integral)
            print(f"{integral} + C")
            return True
        except Exception as e:
            print(f"[AbuLang Error] Could not compute integral: {e}")
            return True
    
    def _handle_calculus_helpers(self, line):
        """Handle calculus helper commands: simplify, expand, factor"""
        if not SYMPY_AVAILABLE:
            print("[AbuLang Error] sympy not installed. Cannot perform symbolic operations.")
            return False
        
        if line.startswith("simplify "):
            expr_str = line[9:].strip()
            expr = self._parse_math_expression(expr_str)
            if expr is not None:
                result = sympy.simplify(expr)
                print(result)
            return True
        
        if line.startswith("expand "):
            expr_str = line[7:].strip()
            expr = self._parse_math_expression(expr_str)
            if expr is not None:
                result = sympy.expand(expr)
                print(result)
            return True
        
        if line.startswith("factor "):
            expr_str = line[7:].strip()
            expr = self._parse_math_expression(expr_str)
            if expr is not None:
                result = sympy.factor(expr)
                print(result)
            return True
        
        return False
    
    def _handle_velocity_components(self, line):
        """Handle velocity component auto-definition"""
        match = re.search(r'(\w+)\.velocity\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', line)
        if not match:
            return False
        
        obj_name = match.group(1)
        x_component = match.group(2).strip()
        y_component = match.group(3).strip()
        
        try:
            x_value = self.eval_expr(x_component)
            y_value = self.eval_expr(y_component)
            
            self.context['dx'] = x_value
            self.context['dy'] = y_value
            
            return True
        except Exception as e:
            try:
                x_value = float(x_component) if '.' in x_component else int(x_component)
                y_value = float(y_component) if '.' in y_component else int(y_component)
                
                self.context['dx'] = x_value
                self.context['dy'] = y_value
                
                return True
            except:
                print(f"[AbuLang Error] Could not set velocity components: {e}")
                return True
    
    # ----------------------------------------------------
    #  Core execution dispatcher (NO PARENTHESES REMOVAL!)
    # ----------------------------------------------------
    def execute_line(self, line):
        line = line.strip()
        if not line:
            return
        
        # Translate GUI aliases before processing (includes syntax enhancements)
        line = self.gui_aliases.translate_line(line)
        
        # === VALUE TYPE CHECKING ===
        if "__CHECK_VALUE_TYPE__" in line:
            match = re.search(r'__CHECK_VALUE_TYPE__\((\w+),\s*"(\w+)"\)', line)
            if match:
                var = match.group(1)
                type_check = match.group(2)
                result = self._check_value_type(var, type_check)
                line = line[:match.start()] + str(result) + line[match.end():]
        
        # === VELOCITY COMPONENT AUTO-DEFINITION ===
        if ".velocity(" in line:
            if self._handle_velocity_components(line):
                return
        
        # === CALCULUS OPERATIONS ===
        if line.startswith("d/d"):
            if self._handle_derivative(line):
                return
        
        if re.match(r'^d[a-z]\s+[^=]', line):
            if self._handle_integral(line):
                return
        
        if line.startswith(("simplify ", "expand ", "factor ")):
            if self._handle_calculus_helpers(line):
                return
        
        # Handle =: operator (assign and compare)
        compare_match = re.search(r'(\w+)\s*=\s*(\S+)\s*#\s*__COMPARE_TO_(\w+)__', line)
        if compare_match:
            var = compare_match.group(1)
            value = compare_match.group(2)
            compare_var = compare_match.group(3)
            
            self.context[var] = self.eval_expr(value)
            
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
        
        # NOTE: NO PARENTHESES REMOVAL HERE!
        # This allows complex Python code with function calls to work properly

        # === HELP ===
        if line.startswith("help"):
            self._handle_help(line)
            return

        # === LIBRA ===
        if line.startswith("libra "):
            self._handle_libra(line)
            return

        # === SHOW ===
        if line.startswith("show"):
            expr = line[4:].strip()
            value = self.eval_expr(expr)

            if isinstance(value, str) and re.search(r"[a-zA-Z_]+\(", value):
                try:
                    value = eval(value, self.context, self.context)
                except Exception as e:
                    print(f"[AbuLang Error] {e}")

            print(value)
            return

        # === ASK / SYSASK (INPUT) ===
        if line.startswith("ask ") or line.startswith("sysask "):
            self._handle_ask(line)
            return
        
        # === VARIABLE ASSIGNMENT ===
        if "=" in line and not line.startswith("if"):
            if "# __CONSTANT__" in line:
                line = line.replace("# __CONSTANT__", "").strip()
                var, expr = map(str.strip, line.split("=", 1))
                
                if var in self.constants:
                    print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                    return
                
                self.constants.add(var)
                value = self.eval_expr(expr)
                self.context[var] = value
                self._track_variable_type(var, value)
                return
            
            var, expr = map(str.strip, line.split("=", 1))
            
            if var in self.constants:
                print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                return
            
            value = self.eval_expr(expr)
            self.context[var] = value
            self._track_variable_type(var, value)
            return

        # === TYPE INTROSPECTION ===
        if re.match(r'^\w+$', line) and line in self.context:
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

    # Copy all the helper methods from original runner
    def _handle_help(self, line):
        """Help system - simplified version"""
        parts = line.split()
        if len(parts) == 1:
            print("\n[HELP] AbuLang Help System")
            print("Type 'help all' to see all commands")
            return
        
        if parts[1] == "all":
            print("\n[HELP] AbuLang Complete Reference")
            for cmd, info in self.lang.commands.items():
                print(f"  {cmd:10} - {info['desc']}")
            return
    
    def _handle_ask(self, line):
        """Handle ask/sysask commands for user input"""
        if line.startswith("ask "):
            rest = line[4:].strip()
        else:
            rest = line[7:].strip()
        
        if "=" in rest:
            var, prompt_expr = map(str.strip, rest.split("=", 1))
            prompt = self.eval_expr(prompt_expr)
            user_input = input(str(prompt))
            try:
                if '.' in user_input:
                    self.context[var] = float(user_input)
                else:
                    self.context[var] = int(user_input)
            except:
                self.context[var] = user_input
        else:
            prompt = self.eval_expr(rest)
            result = input(str(prompt))
            print(f"[Input received: {result}]")

    def _handle_libra(self, line):
        """Handle library imports"""
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

        module_aliases = {
            "stat": "statistics",
            "maths": "math",
            "osys": "os",
            "req": "requests",
            "jsons": "json",
            "path": "os.path",
            "web": "requests",
            "DISPLAY": "pygame",
            "UI": "tkinter",
            "arrow": "turtle",
        }

        real_module = module_aliases.get(module_name, module_name)

        try:
            imported = __import__(real_module)
            self.context[real_module] = imported

            if module_name != real_module:
                self.context[module_name] = imported

            if alias:
                self.context[alias] = imported
                print(f"[libra] imported {real_module} as {alias}")
            else:
                print(f"[libra] imported {real_module}")

            # Auto-add shortcuts
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

        except ImportError:
            print(f"[AbuLang Error] could not import {real_module}")

    def eval_expr(self, expr):
        """Evaluate expressions"""
        expr = expr.strip()

        if expr.startswith('str"') and expr.endswith('"'):
            return expr[4:-1]
        
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

        if re.match(r"^['\"].*['\"]$", expr):
            string_content = expr.strip("\"'")
            try:
                result = eval(string_content, self.context, self.context)
                if isinstance(result, (int, float)):
                    return result
                return string_content
            except:
                try:
                    if '.' in string_content:
                        return float(string_content)
                    else:
                        return int(string_content)
                except:
                    return string_content

        if expr in self.context:
            return self.context[expr]

        expr = expr.replace("^", "**")
        expr = re.sub(r"(\d+)%", r"(\1/100)", expr)

        try:
            return eval(expr, self.context, self.context)
        except Exception:
            return expr

    def run(self, code: str):
        """Main runtime loop"""
        for line in code.splitlines():
            if "#" in line:
                line = line.split("#", 1)[0]
            if "//" in line:
                line = line.split("//", 1)[0]

            line = line.strip()
            if not line:
                continue

            self.execute_line(line)
