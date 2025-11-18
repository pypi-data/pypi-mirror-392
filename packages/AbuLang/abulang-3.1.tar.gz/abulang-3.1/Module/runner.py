"""
AbuLang Runner - Main interpreter
"""

import re
import builtins
import math
import statistics

try:
    from .abu_core import AbuLang
    from .gui_aliases import GUIAliasManager
except ImportError:
    from abu_core import AbuLang
    from gui_aliases import GUIAliasManager


class AbuRunner:
    """Main AbuLang interpreter and runtime handler"""

    def __init__(self):
        self.lang = AbuLang()
        self.gui_aliases = GUIAliasManager()
        self.context = {
            "math": math,
            "statistics": statistics,
            "stat": statistics,
        }
        self.constants = set()

    def execute_line(self, line):
        """Execute a single line of AbuLang code"""
        line = line.strip()
        if not line:
            return

        # Translate syntax enhancements
        line = self.gui_aliases.translate_syntax_enhancements(line)

        # === HELP ===
        if line.startswith("help"):
            self._handle_help(line)
            return

        # === LIBRA ===
        if line.startswith("libra"):
            self._handle_libra(line)
            return

        # === SHOW ===
        if line.startswith("show"):
            expr = line[4:].strip()
            if expr.startswith("(") and expr.endswith(")"):
                expr = expr[1:-1].strip()
            
            value = self.eval_expr(expr)

            if isinstance(value, str) and re.search(r"[a-zA-Z_]+\(", value):
                try:
                    value = eval(value, self.context, self.context)
                except Exception as e:
                    print(f"[AbuLang Error] {e}")

            print(value)
            return

        # === VARIABLE ASSIGNMENT ===
        # Check for "is" operator first (before "=")
        if " is " in line and not line.startswith("if"):
            var, expr = map(str.strip, line.split(" is ", 1))
            
            if var in self.constants:
                print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                return
            
            value = self.eval_expr(expr)
            self.context[var] = value
            return
        
        # Check for "=" operator
        if "=" in line and not line.startswith("if"):
            var, expr = map(str.strip, line.split("=", 1))
            
            if var in self.constants:
                print(f"[AbuLang Error] Cannot reassign constant '{var}'")
                return
            
            value = self.eval_expr(expr)
            self.context[var] = value
            return

        # === FALLBACK RAW PYTHON ===
        try:
            exec(line, self.context, self.context)
        except Exception as e:
            print(f"[AbuLang Error] {e}")

    def _handle_help(self, line):
        """Handle help command"""
        parts = line.split()
        if len(parts) == 1:
            sections = sorted(
                {info.get("section", "misc") for info in self.lang.commands.values()}
            )
            print("\n📘 AbuLang Help System")
            print("Available sections:\n " + ", ".join(sections))
            print("Type 'help <section>' or 'help all'")
            return

        arg = parts[1].replace("(", "").replace(")", "")
        if arg.lower() == "all":
            print("\n📘 AbuLang Full Command List\n")
            for cmd, info in self.lang.commands.items():
                print(f"{cmd:8} | {info.get('section','misc'):10} | {info['desc']}")
            return

        section = arg.lower()
        found = [
            (cmd, info)
            for cmd, info in self.lang.commands.items()
            if info.get("section", "") == section
        ]
        if not found:
            print(f"No commands found for section: {section}")
            return
        print(f"\nCommands in section '{section}':")
        for cmd, info in found:
            print(f"  {cmd:8} - {info['desc']}")

    def _handle_libra(self, line):
        """Handle library import"""
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
            # Import the module properly
            import importlib
            imported = importlib.import_module(real_module)
            self.context[real_module] = imported

            if module_name != real_module:
                self.context[module_name] = imported

            if alias:
                self.context[alias] = imported
                print(f"[libra] imported {real_module} as {alias}")
            else:
                print(f"[libra] imported {real_module}")

            if real_module == "statistics":
                self.context["stat"] = imported
            elif real_module == "math":
                self.context["maths"] = imported

        except ImportError:
            print(f"[AbuLang Error] could not import {real_module}")

    def eval_expr(self, expr):
        """Evaluate an expression"""
        expr = expr.strip()

        # Handle string literals
        if re.match(r"^['\"].*['\"]$", expr):
            return expr.strip("\"'")

        # Handle variable lookup
        if expr in self.context:
            return self.context[expr]

        # Handle math shortcuts
        expr = expr.replace("^", "**")
        expr = re.sub(r"(\d+)%", r"(\1/100)", expr)

        try:
            # Try to evaluate as Python expression
            result = eval(expr, self.context, self.context)
            return result
        except Exception as e:
            # If evaluation fails, return as string
            return expr

    def run(self, code: str):
        """Run AbuLang code"""
        for line in code.splitlines():
            # Handle comments
            if "#" in line:
                line = line.split("#", 1)[0]
            if "//" in line:
                line = line.split("//", 1)[0]

            line = line.strip()
            if not line:
                continue

            self.execute_line(line)
