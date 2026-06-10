import unittest
from pathlib import Path


class BuildExeScriptTests(unittest.TestCase):
    def test_native_commands_fail_when_exit_code_is_nonzero(self):
        script = Path("build_exe.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-NativeCommand", script)
        self.assertIn("$LASTEXITCODE", script)
        self.assertIn("throw \"Command failed", script)

        executable_lines = [line.strip() for line in script.splitlines()]
        self.assertNotIn("python --version", executable_lines)
        self.assertFalse(any(line.startswith("python -m pip install") for line in executable_lines))
        self.assertFalse(any(line.startswith("python -m PyInstaller") for line in executable_lines))

        self.assertIn("Invoke-NativeCommand \"python\" @(\"--version\")", script)
        self.assertIn("Invoke-NativeCommand \"python\" @('-m', 'pip', 'install', '-r', $Requirements)", script)
        self.assertIn("Invoke-NativeCommand \"python\" @('-m', 'pip', 'install', 'pyinstaller')", script)
        self.assertIn("Invoke-NativeCommand \"python\" @('-m', 'PyInstaller'", script)


if __name__ == "__main__":
    unittest.main()
