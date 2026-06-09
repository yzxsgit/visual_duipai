from __future__ import annotations

import difflib
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class BuildConfig:
    standard: str = "gnu++14"
    optimize: str = "-O2"
    compiler: str = "g++"
    compile_timeout_seconds: int = 60
    run_timeout_seconds: int = 10


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def command_text(self) -> str:
        return " ".join(self.args)


class CommandError(RuntimeError):
    def __init__(self, message: str, result: Optional[CommandResult] = None):
        super().__init__(message)
        self.result = result


class StopRequested(RuntimeError):
    pass


@dataclass(frozen=True)
class StressPaths:
    work_dir: Path

    @property
    def gen_exe(self) -> Path:
        return self.work_dir / executable_name("gen")

    @property
    def force_exe(self) -> Path:
        return self.work_dir / executable_name("force")

    @property
    def answer_exe(self) -> Path:
        return self.work_dir / executable_name("answer")

    @property
    def input_file(self) -> Path:
        return self.work_dir / "input.txt"

    @property
    def force_output(self) -> Path:
        return self.work_dir / "force.out"

    @property
    def answer_output(self) -> Path:
        return self.work_dir / "answer.out"

    @property
    def diff_output(self) -> Path:
        return self.work_dir / "diff.out"


def executable_name(stem: str) -> str:
    if sys.platform.startswith("win"):
        return f"{stem}.exe"
    return stem


def validate_rounds(text: str) -> int:
    value = text.strip()
    if not value.isdigit():
        raise ValueError("轮次必须是正整数")
    rounds = int(value)
    if rounds <= 0:
        raise ValueError("轮次必须大于 0")
    return rounds


def validate_cpp_path(path: os.PathLike[str] | str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"文件不存在: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"不是文件: {resolved}")
    if resolved.suffix.lower() != ".cpp":
        raise ValueError(f"请选择 .cpp 文件: {resolved}")
    return resolved


def ensure_work_dir(work_dir: Path) -> StressPaths:
    work_dir.mkdir(parents=True, exist_ok=True)
    return StressPaths(work_dir)


def require_compiler(compiler: str) -> None:
    if shutil.which(compiler) is None:
        raise CommandError(f"找不到编译器 `{compiler}`，请确认 g++ 已加入 PATH")


def run_command(
    args: Iterable[str],
    *,
    timeout_seconds: int,
    stdin_file: Optional[Path] = None,
    stdout_file: Optional[Path] = None,
    cwd: Optional[Path] = None,
) -> CommandResult:
    args_list = [str(arg) for arg in args]
    stdin_handle = None
    stdout_handle = None
    try:
        if stdin_file is not None:
            stdin_handle = stdin_file.open("r", encoding="utf-8", errors="replace")
        if stdout_file is not None:
            stdout_handle = stdout_file.open("w", encoding="utf-8", errors="replace")

        completed = subprocess.run(
            args_list,
            stdin=stdin_handle,
            stdout=stdout_handle if stdout_handle is not None else subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CommandError(f"命令超时: {' '.join(args_list)}") from exc
    finally:
        if stdin_handle is not None:
            stdin_handle.close()
        if stdout_handle is not None:
            stdout_handle.close()

    result = CommandResult(
        args=args_list,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )
    if result.returncode != 0:
        raise CommandError(f"命令失败: {result.command_text}", result)
    return result


def compile_cpp(source: Path, output: Path, config: BuildConfig) -> CommandResult:
    require_compiler(config.compiler)
    output.parent.mkdir(parents=True, exist_ok=True)
    args = [
        config.compiler,
        f"-std={config.standard}",
        config.optimize,
        str(source),
        "-o",
        str(output),
    ]
    return run_command(args, timeout_seconds=config.compile_timeout_seconds)


def read_text_lossy(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalized_output_lines(path: Path) -> list[str]:
    text = read_text_lossy(path)
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def compare_outputs(expected_file: Path, actual_file: Path) -> bool:
    return normalized_output_lines(expected_file) == normalized_output_lines(actual_file)


def make_diff(expected_text: str, actual_text: str) -> str:
    expected_lines = [line.rstrip() for line in expected_text.splitlines()]
    actual_lines = [line.rstrip() for line in actual_text.splitlines()]
    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile="expected",
        tofile="actual",
        lineterm="",
    )
    return "\n".join(diff) + "\n"


def write_diff(expected_file: Path, actual_file: Path, diff_file: Path) -> None:
    diff_file.write_text(
        make_diff(read_text_lossy(expected_file), read_text_lossy(actual_file)),
        encoding="utf-8",
    )


def run_generator(paths: StressPaths, config: BuildConfig) -> CommandResult:
    return run_command(
        [paths.gen_exe],
        timeout_seconds=config.run_timeout_seconds,
        stdout_file=paths.input_file,
        cwd=paths.work_dir,
    )


def run_solution(executable: Path, input_file: Path, output_file: Path, paths: StressPaths, config: BuildConfig) -> CommandResult:
    return run_command(
        [executable],
        timeout_seconds=config.run_timeout_seconds,
        stdin_file=input_file,
        stdout_file=output_file,
        cwd=paths.work_dir,
    )
