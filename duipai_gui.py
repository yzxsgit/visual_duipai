from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

from stress_core import (
    BuildConfig,
    CommandError,
    StopRequested,
    compare_outputs,
    compile_cpp,
    ensure_work_dir,
    run_generator,
    run_solution,
    validate_cpp_path,
    validate_rounds,
    write_diff,
)

APP_DIR = Path(__file__).resolve().parent
WORK_DIR = APP_DIR / "duipai_work"


class DropCard(ctk.CTkFrame):
    def __init__(self, master: tk.Misc, title: str, on_selected):
        super().__init__(master, corner_radius=16, border_width=1)
        self.on_selected = on_selected
        self.path: Path | None = None

        self.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

        self.hint_label = ctk.CTkLabel(self, text="拖入 .cpp 文件或点击选择", text_color=("gray45", "gray70"))
        self.hint_label.grid(row=1, column=0, padx=18, pady=(0, 10), sticky="w")

        self.path_label = ctk.CTkLabel(
            self,
            text="未选择",
            anchor="w",
            justify="left",
            wraplength=260,
            text_color=("gray30", "gray85"),
        )
        self.path_label.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")

        for widget in (self, self.title_label, self.hint_label, self.path_label):
            widget.bind("<Button-1>", self._choose_file)
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._handle_drop)

    def set_enabled(self, enabled: bool) -> None:
        cursor = "hand2" if enabled else "arrow"
        for widget in (self, self.title_label, self.hint_label, self.path_label):
            widget.configure(cursor=cursor)
        self._enabled = enabled

    def set_path(self, path: Path) -> None:
        self.path = path
        self.path_label.configure(text=str(path))

    def clear_path(self) -> None:
        self.path = None
        self.path_label.configure(text="未选择")

    def _choose_file(self, _event=None) -> None:
        if not getattr(self, "_enabled", True):
            return
        selected = filedialog.askopenfilename(
            title="选择 C++ 源文件",
            filetypes=[("C++ source", "*.cpp"), ("All files", "*.*")],
        )
        if selected:
            self.on_selected(self, selected)

    def _handle_drop(self, event) -> None:
        if not getattr(self, "_enabled", True):
            return
        paths = self.tk.splitlist(event.data)
        if paths:
            self.on_selected(self, paths[0])


class DuipaiApp(TkinterDnD.Tk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("对拍可视化工具 - Modern Stress Tester")
        self.geometry("980x760")
        self.minsize(900, 680)

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None
        self.input_widgets: list[object] = []
        self.closing = False
        self.after_id: str | None = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after_id = self.after(100, self._drain_events)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkLabel(self, text="对拍可视化工具", font=ctk.CTkFont(size=30, weight="bold"))
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="w")
        subtitle = ctk.CTkLabel(self, text="选择三个 C++ 程序，自动编译、生成数据并比较输出。", text_color=("gray40", "gray75"))
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="w")

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="ew")
        for col in range(3):
            cards.grid_columnconfigure(col, weight=1, uniform="cards")

        self.force_card = DropCard(cards, "暴力程序", self._select_cpp)
        self.answer_card = DropCard(cards, "正解 / 待测", self._select_cpp)
        self.gen_card = DropCard(cards, "数据生成器", self._select_cpp)
        self.force_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.answer_card.grid(row=0, column=1, padx=10, sticky="nsew")
        self.gen_card.grid(row=0, column=2, padx=(10, 0), sticky="nsew")

        controls = ctk.CTkFrame(self, corner_radius=16)
        controls.grid(row=3, column=0, padx=24, pady=(0, 16), sticky="nsew")
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_rowconfigure(3, weight=1)

        options = ctk.CTkFrame(controls, fg_color="transparent")
        options.grid(row=0, column=0, padx=18, pady=(18, 12), sticky="ew")
        options.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(options, text="轮次").grid(row=0, column=0, padx=(0, 8), sticky="w")
        self.rounds_entry = ctk.CTkEntry(options, width=120)
        self.rounds_entry.insert(0, "1000")
        self.rounds_entry.grid(row=0, column=1, padx=(0, 24), sticky="w")

        ctk.CTkLabel(options, text="编译标准").grid(row=0, column=2, padx=(0, 8), sticky="w")
        self.standard_combo = ctk.CTkComboBox(options, values=["gnu++14", "gnu++17", "c++17", "c++14"], width=140)
        self.standard_combo.set("gnu++14")
        self.standard_combo.grid(row=0, column=3, padx=(0, 24), sticky="w")

        buttons = ctk.CTkFrame(controls, fg_color="transparent")
        buttons.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="ew")
        self.start_button = ctk.CTkButton(buttons, text="开始对拍", command=self._start)
        self.start_button.pack(side="left", padx=(0, 10))
        self.stop_button = ctk.CTkButton(buttons, text="停止", command=self._stop, state="disabled", fg_color="#8a1f2d", hover_color="#a52838")
        self.stop_button.pack(side="left", padx=(0, 10))
        self.open_button = ctk.CTkButton(buttons, text="打开工作目录", command=self._open_work_dir)
        self.open_button.pack(side="left")

        self.progress = ctk.CTkProgressBar(controls)
        self.progress.set(0)
        self.progress.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")

        self.log_text = ctk.CTkTextbox(controls, wrap="word")
        self.log_text.grid(row=3, column=0, padx=18, pady=(0, 18), sticky="nsew")

        self.input_widgets = [self.force_card, self.answer_card, self.gen_card, self.rounds_entry, self.standard_combo, self.start_button]
        self._set_inputs_enabled(True)

    def _select_cpp(self, card: DropCard, raw_path: str) -> None:
        try:
            card.set_path(validate_cpp_path(raw_path))
        except ValueError as exc:
            card.clear_path()
            self._log(f"无效文件，已清除选择: {exc}")

    def _start(self) -> None:
        try:
            rounds = validate_rounds(self.rounds_entry.get())
            force = self._require_path(self.force_card, "暴力程序")
            answer = self._require_path(self.answer_card, "正解 / 待测")
            gen = self._require_path(self.gen_card, "数据生成器")
        except ValueError as exc:
            self._log(f"参数错误: {exc}")
            messagebox.showerror("参数错误", str(exc))
            return

        self.stop_event.clear()
        self.progress.set(0)
        self._set_inputs_enabled(False)
        self.stop_button.configure(state="normal")
        config = BuildConfig(standard=self.standard_combo.get())
        self.worker_thread = threading.Thread(
            target=self._worker,
            args=(rounds, gen, force, answer, config),
            daemon=True,
        )
        self.worker_thread.start()

    def _require_path(self, card: DropCard, name: str) -> Path:
        if card.path is None:
            raise ValueError(f"请选择{name}")
        return validate_cpp_path(card.path)

    def _worker(self, rounds: int, gen: Path, force: Path, answer: Path, config: BuildConfig) -> None:
        try:
            paths = ensure_work_dir(WORK_DIR)
            self._emit("log", f"工作目录: {paths.work_dir}")
            self._check_stop()

            for label, source, output in (
                ("数据生成器", gen, paths.gen_exe),
                ("暴力程序", force, paths.force_exe),
                ("正解 / 待测", answer, paths.answer_exe),
            ):
                self._emit("log", f"编译{label}: {source}")
                compile_cpp(source, output, config, stop_event=self.stop_event)
                self._check_stop()

            for round_no in range(1, rounds + 1):
                self._check_stop()
                self._emit("log", f"Round {round_no}/{rounds}")
                run_generator(paths, config, stop_event=self.stop_event)
                self._check_stop()
                run_solution(paths.force_exe, paths.input_file, paths.force_output, paths, config, stop_event=self.stop_event)
                self._check_stop()
                run_solution(paths.answer_exe, paths.input_file, paths.answer_output, paths, config, stop_event=self.stop_event)

                if not compare_outputs(paths.force_output, paths.answer_output):
                    write_diff(paths.force_output, paths.answer_output, paths.diff_output)
                    self._emit("log", "Wrong Answer: 输出不一致")
                    self._emit("log", f"input.txt: {paths.input_file}")
                    self._emit("log", f"force.out: {paths.force_output}")
                    self._emit("log", f"answer.out: {paths.answer_output}")
                    self._emit("log", f"diff.out: {paths.diff_output}")
                    self._emit("progress", round_no / rounds)
                    return

                self._emit("progress", round_no / rounds)

            self._emit("log", f"Accepted: {rounds} 轮全部通过")
        except StopRequested:
            self._emit("log", "用户已停止")
        except CommandError as exc:
            self._emit("log", self._format_command_error(exc))
        except Exception as exc:  # Keep GUI alive and surface unexpected failures.
            self._emit("log", f"运行出错: {exc}")
        finally:
            self._emit("done", None)

    def _check_stop(self) -> None:
        if self.stop_event.is_set():
            raise StopRequested()

    def _format_command_error(self, exc: CommandError) -> str:
        lines = [str(exc)]
        result = getattr(exc, "result", None)
        if result is not None:
            lines.append(f"命令: {result.command_text}")
            lines.append(f"退出码: {result.returncode}")
            if result.stderr:
                lines.append(f"stderr:\n{result.stderr.rstrip()}")
        return "\n".join(lines)

    def _stop(self) -> None:
        self.stop_event.set()
        if not self.closing:
            self._log("正在停止，正在中断当前子进程...")
            self.stop_button.configure(state="disabled")

    def _on_close(self) -> None:
        self.closing = True
        self.stop_event.set()
        self._set_inputs_enabled(False)
        self.stop_button.configure(state="disabled")
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.after_id = self.after(100, self._wait_for_worker_close)
            return
        self._destroy_after_worker_exit()

    def _wait_for_worker_close(self) -> None:
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.after_id = self.after(100, self._wait_for_worker_close)
            return
        self._destroy_after_worker_exit()

    def _destroy_after_worker_exit(self) -> None:
        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        self.destroy()

    def _open_work_dir(self) -> None:
        paths = ensure_work_dir(WORK_DIR)
        try:
            import os

            os.startfile(paths.work_dir)  # type: ignore[attr-defined]
        except AttributeError:
            import subprocess

            subprocess.Popen(["xdg-open", str(paths.work_dir)])
        except Exception as exc:
            self._log(f"打开工作目录失败: {exc}")

    def _set_inputs_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for widget in self.input_widgets:
            if isinstance(widget, DropCard):
                widget.set_enabled(enabled)
            else:
                widget.configure(state=state)

    def _emit(self, event_type: str, payload: object) -> None:
        self.events.put((event_type, payload))

    def _drain_events(self) -> None:
        try:
            while True:
                event_type, payload = self.events.get_nowait()
                if self.closing:
                    if event_type == "done":
                        self._destroy_after_worker_exit()
                    continue
                if event_type == "log":
                    self._log(str(payload))
                elif event_type == "progress":
                    self.progress.set(float(payload))
                elif event_type == "done":
                    self._set_inputs_enabled(True)
                    self.stop_button.configure(state="disabled")
        except queue.Empty:
            pass
        if not self.closing:
            self.after_id = self.after(100, self._drain_events)

    def _log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")


if __name__ == "__main__":
    DuipaiApp().mainloop()
