import tempfile
import unittest
from pathlib import Path

from stress_core import (
    BuildConfig,
    StressPaths,
    compare_outputs,
    executable_name,
    make_diff,
    validate_cpp_path,
    validate_rounds,
)


class StressCoreTests(unittest.TestCase):
    def test_validate_rounds_accepts_positive_integer_text(self):
        self.assertEqual(validate_rounds("1"), 1)
        self.assertEqual(validate_rounds("1000"), 1000)
        self.assertEqual(validate_rounds(" 25 "), 25)

    def test_validate_rounds_rejects_invalid_text(self):
        with self.assertRaises(ValueError):
            validate_rounds("0")
        with self.assertRaises(ValueError):
            validate_rounds("-3")
        with self.assertRaises(ValueError):
            validate_rounds("abc")

    def test_validate_cpp_path_accepts_existing_cpp(self):
        with tempfile.TemporaryDirectory() as tmp:
            cpp = Path(tmp) / "main.cpp"
            cpp.write_text("int main(){return 0;}\n", encoding="utf-8")
            self.assertEqual(validate_cpp_path(cpp), cpp.resolve())

    def test_validate_cpp_path_rejects_non_cpp(self):
        with tempfile.TemporaryDirectory() as tmp:
            txt = Path(tmp) / "main.txt"
            txt.write_text("hello\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_cpp_path(txt)

    def test_compare_outputs_ignores_trailing_whitespace(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected = Path(tmp) / "expected.out"
            actual = Path(tmp) / "actual.out"
            expected.write_text("1\n2   \n3\n", encoding="utf-8")
            actual.write_text("1\n2\n3   \n", encoding="utf-8")
            self.assertTrue(compare_outputs(expected, actual))

    def test_compare_outputs_detects_different_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected = Path(tmp) / "expected.out"
            actual = Path(tmp) / "actual.out"
            expected.write_text("1\n2\n", encoding="utf-8")
            actual.write_text("1\n3\n", encoding="utf-8")
            self.assertFalse(compare_outputs(expected, actual))

    def test_make_diff_writes_unified_diff(self):
        diff = make_diff("1\n2\n", "1\n3\n")
        self.assertIn("--- expected", diff)
        self.assertIn("+++ actual", diff)
        self.assertIn("-2", diff)
        self.assertIn("+3", diff)

    def test_stress_paths_are_inside_work_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = StressPaths(Path(tmp))
            self.assertEqual(paths.input_file, Path(tmp) / "input.txt")
            self.assertEqual(paths.force_output, Path(tmp) / "force.out")
            self.assertEqual(paths.answer_output, Path(tmp) / "answer.out")
            self.assertEqual(paths.diff_output, Path(tmp) / "diff.out")

    def test_executable_name_uses_windows_suffix_only_on_windows(self):
        name = executable_name("force")
        self.assertTrue(name == "force" or name == "force.exe")

    def test_build_config_default_standard(self):
        config = BuildConfig()
        self.assertEqual(config.standard, "gnu++14")
        self.assertEqual(config.optimize, "-O2")


if __name__ == "__main__":
    unittest.main()
