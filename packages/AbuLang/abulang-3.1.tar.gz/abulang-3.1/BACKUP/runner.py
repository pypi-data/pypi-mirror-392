import re
import builtins
import math
import statistics
from .abu_core import AbuLang


class AbuRunner:
    """Main AbuLang interpreter and runtime handler (v1.4)."""

    def __init__(self):
        self.lang = AbuLang()
        # runtime context for variables and libraries
        self.context = {
            "math": math,
            "statistics": statistics,
            "stat": statistics,   # alias for statistics
        }

    # ----------------------------------------------------
    #  Core execution dispatcher
    # ----------------------------------------------------
    def execute_line(self, line):
        line = line.strip()
        if not line:
            return

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

            # re-evaluate code-like strings such as stat.mean(nums)
            if isinstance(value, str) and re.search(r"[a-zA-Z_]+\(", value):
                try:
                    value = eval(value, self.context, self.context)
                except Exception as e:
                    print(f"[AbuLang Error] {e}")

            print(value)
            return

        # === VARIABLE ASSIGNMENT ===
        if "=" in line and not line.startswith("if"):
            var, expr = map(str.strip, line.split("=", 1))
            self.context[var] = self.eval_expr(expr)
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
            print("\n📘 AbuLang Help System v1.4")
            print("Available sections:\n " + ", ".join(sections))
            print("Type help(section) or help all")
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
        }

        real_module = module_aliases.get(module_name, module_name)

        try:
            imported = __import__(real_module)
            self.context[real_module] = imported

            # user alias
            if alias:
                self.context[alias] = imported
                print(f"[libra] imported {real_module} as {alias}")
            else:
                if module_name != real_module:
                    self.context[module_name] = imported
                print(f"[libra] imported {real_module}")

            # auto-add shortcuts
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

    # ----------------------------------------------------
    #  EXPRESSION EVALUATION
    # ----------------------------------------------------
    def eval_expr(self, expr):
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

        try:
            return eval(expr, self.context, self.context)
        except Exception:
            return expr

    # ----------------------------------------------------
    #  MAIN RUNTIME LOOP
    # ----------------------------------------------------
    def run(self, code: str):
        for line in code.splitlines():
            # handle comments (# or //)
            if "#" in line:
                line = line.split("#", 1)[0]
            if "//" in line:
                line = line.split("//", 1)[0]

            line = line.strip()
            if not line:
                continue

            self.execute_line(line)
# ----------------------------------------------------
#  END OF AbuRunner
