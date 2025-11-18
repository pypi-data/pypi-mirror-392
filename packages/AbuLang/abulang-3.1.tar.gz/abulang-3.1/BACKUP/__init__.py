from .abu_core import AbuLang
from .runner import AbuRunner

# default runtime
_runner = AbuRunner()

def run(code: str):
    """Run AbuLang code directly."""
    _runner.run(code)

# Optional shortcut for global usage
run_code = run
execute = run

__all__ = ["run", "run_code", "execute", "AbuRunner", "AbuLang"]


