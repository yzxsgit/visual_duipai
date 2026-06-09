import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from stress_core import (
    BuildConfig,
    StopRequested,
    StressPaths,
    compare_outputs,
    compile_cpp,
    ensure_work_dir,
    executable_name,
    make_diff,
    run_command,
    run_generator,
    run_solution,
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

    def test_compare_outputs_detects_different_invalid_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            expected = Path(tmp) / "expected.out"
            actual = Path(tmp) / "actual.out"
            expected.write_bytes(b"\xff\n")
            actual.write_bytes(b"\xfe\n")
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

    def test_ensure_work_dir_returns_absolute_work_dir_for_relative_path(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            relative_work_dir = Path(tmp).relative_to(Path.cwd())
            paths = ensure_work_dir(relative_work_dir)
            self.assertTrue(paths.work_dir.is_absolute())

    def test_executable_name_uses_windows_suffix_only_on_windows(self):
        name = executable_name("force")
        self.assertTrue(name == "force" or name == "force.exe")

    def test_build_config_default_standard(self):
        config = BuildConfig()
        self.assertEqual(config.standard, "gnu++14")
        self.assertEqual(config.optimize, "-O2")

    def test_run_command_raises_stop_requested_when_stop_event_set(self):
        stop_event = threading.Event()
        timer = threading.Timer(0.2, stop_event.set)
        timer.start()
        started = time.monotonic()
        try:
            with self.assertRaises(StopRequested):
                run_command(
                    [sys.executable, "-c", "import time; time.sleep(10)"],
                    timeout_seconds=30,
                    stop_event=stop_event,
                )
        finally:
            timer.cancel()
        self.assertLess(time.monotonic() - started, 5)

    def test_compile_cpp_passes_stop_event_to_run_command(self):
        stop_event = threading.Event()
        config = BuildConfig(compiler="g++")
        with tempfile.TemporaryDirectory() as tmp, mock.patch("stress_core.require_compiler"), mock.patch("stress_core.run_command") as run:
            source = Path(tmp) / "main.cpp"
            output = Path(tmp) / executable_name("main")
            source.write_text("int main(){return 0;}\n", encoding="utf-8")
            compile_cpp(source, output, config, stop_event=stop_event)
        self.assertIs(run.call_args.kwargs["stop_event"], stop_event)

    def test_run_generator_and_solution_pass_stop_event_to_run_command(self):
        stop_event = threading.Event()
        config = BuildConfig()
        with tempfile.TemporaryDirectory() as tmp, mock.patch("stress_core.run_command") as run:
            paths = StressPaths(Path(tmp))
            run_generator(paths, config, stop_event=stop_event)
            run_solution(paths.answer_exe, paths.input_file, paths.answer_output, paths, config, stop_event=stop_event)
        self.assertIs(run.call_args_list[0].kwargs["stop_event"], stop_event)
        self.assertIs(run.call_args_list[1].kwargs["stop_event"], stop_event)


if __name__ == "__main__":
    unittest.main()
