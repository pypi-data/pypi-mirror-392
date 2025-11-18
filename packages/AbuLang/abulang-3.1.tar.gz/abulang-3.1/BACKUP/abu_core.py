import yaml
from pathlib import Path

class AbuLang:
    def __init__(self):
        path = Path(__file__).parent / "commands.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.commands = data["commands"]

        # Build lookup table with aliases
        self.lookup = {}
        for cmd, info in self.commands.items():
            self.lookup[cmd] = info
            for alias in info.get("aliases", []):
                self.lookup[alias] = info

    def translate(self, word, **kwargs):
        """Translate AbuLang keyword → Python command."""
        if word not in self.lookup:
            raise ValueError(f"Unknown AbuLang command: {word}")
        pattern = self.lookup[word]["python"]
        return pattern.format(**kwargs)

    def explain(self, word):
        """Describe what a command does."""
        if word not in self.lookup:
            return "Unknown command"
        return self.lookup[word]["desc"]
