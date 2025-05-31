import os
import sys
import subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Rule:
    """Base class for rules."""
    def check(self, value):
        """Override this method in subclasses. Return True if rule passes, else False."""
        raise NotImplementedError("Subclasses must implement check()")

class RuleChainChecker:
    def __init__(self, rules=None):
        self.rules = []
        if rules:
            for rule in rules:
                self.register_rule(rule)

    def register_rule(self, rule):
        """Register a Rule instance."""
        if not isinstance(rule, Rule):
            raise TypeError("rule must be an instance of Rule")
        self.rules.append(rule)

    def apply_rules(self, value):
        """Returns True if any rule fails (file is broken), else False."""
        for rule in self.rules:
            if not rule.check(value):
                return True  # Broken
        return False  # Not broken

class ZeroSizeRule(Rule):
    def check(self, file_path):
        return os.path.getsize(file_path) > 0

class MediaInfoDurationRule(Rule):
    def check(self, file_path):
        try:
            result = subprocess.run(
                ["mediainfo", "--Inform=Video;%Duration%", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            duration = result.stdout.decode("utf-8").strip()
            # Consider broken if duration is empty or contains N/A
            return bool(duration) and "N/A" not in duration
        except Exception:
            return False

