import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from utils.checker import RuleChainChecker, Rule, ZeroSizeRule, MediaInfoDurationRule

class DummyRulePass(Rule):
    def check(self, value):
        return True

class DummyRuleFail(Rule):
    def check(self, value):
        return False

class TestRuleChainChecker(unittest.TestCase):
    def test_register_rule_type_error(self):
        checker = RuleChainChecker()
        with self.assertRaises(TypeError):
            checker.register_rule(object())  # Not a Rule instance

    def test_apply_rules_all_pass(self):
        checker = RuleChainChecker()
        checker.register_rule(DummyRulePass())
        checker.register_rule(DummyRulePass())
        result = checker.apply_rules("dummy")
        self.assertFalse(result)  # Not broken

    def test_apply_rules_first_fail(self):
        checker = RuleChainChecker()
        checker.register_rule(DummyRuleFail())
        checker.register_rule(DummyRulePass())
        result = checker.apply_rules("dummy")
        self.assertTrue(result)  # Broken

    def test_apply_rules_second_fail(self):
        checker = RuleChainChecker()
        checker.register_rule(DummyRulePass())
        checker.register_rule(DummyRuleFail())
        result = checker.apply_rules("dummy")
        self.assertTrue(result)  # Broken

class TestZeroSizeRule(unittest.TestCase):
    @patch("os.path.getsize")
    def test_zero_size(self, mock_getsize):
        mock_getsize.return_value = 0
        rule = ZeroSizeRule()
        self.assertFalse(rule.check("file.mp4"))

    @patch("os.path.getsize")
    def test_nonzero_size(self, mock_getsize):
        mock_getsize.return_value = 123
        rule = ZeroSizeRule()
        self.assertTrue(rule.check("file.mp4"))

class TestMediaInfoDurationRule(unittest.TestCase):
    @patch("subprocess.run")
    def test_duration_valid(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = b"12345"
        mock_run.return_value = mock_proc
        rule = MediaInfoDurationRule()
        self.assertTrue(rule.check("file.mp4"))

    @patch("subprocess.run")
    def test_duration_empty(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = b""
        mock_run.return_value = mock_proc
        rule = MediaInfoDurationRule()
        self.assertFalse(rule.check("file.mp4"))

    @patch("subprocess.run")
    def test_duration_na(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = b"N/A"
        mock_run.return_value = mock_proc
        rule = MediaInfoDurationRule()
        self.assertFalse(rule.check("file.mp4"))

    @patch("subprocess.run", side_effect=Exception("fail"))
    def test_duration_exception(self, mock_run):
        rule = MediaInfoDurationRule()
        self.assertFalse(rule.check("file.mp4"))

if __name__ == "__main__":
    unittest.main()