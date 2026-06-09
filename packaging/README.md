# VisualDuipai Packaging

This project is packaged with PyInstaller.

## Windows EXE

From PowerShell, run:

Replace <path-to-visual_duipai> with the folder where this repository is checked out.

```powershell
cd <path-to-visual_duipai>
.\build_exe.ps1
```

If PowerShell blocks script execution, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

The output is:

```text
dist/VisualDuipai.exe
```

Double-click `dist/VisualDuipai.exe` to launch the GUI.

## Requirements on the target machine

The packaged EXE includes the Python GUI and Python dependencies, but it does not include a C++ compiler.

The machine running the EXE must have `g++` installed and available in `PATH`:

```powershell
g++ --version
```

If `g++` is missing, the GUI can open, but stress testing will fail during compilation and show the compiler error in the log.

## Drag-and-drop support

The Windows build collects `tkinterdnd2` resources with PyInstaller:

```powershell
--collect-all tkinterdnd2
```

If the build fails because `--collect-all` is unsupported, upgrade PyInstaller:

```powershell
python -m pip install --upgrade pyinstaller
```

## macOS and Linux

Windows `.exe` files do not run natively on macOS or Linux.

Future platform builds should be created on the target OS:

- macOS: run PyInstaller on macOS and produce a macOS executable or `.app` bundle.
- Linux: run PyInstaller on Linux and produce a Linux executable, with optional AppImage packaging later.

This project does not cross-compile macOS or Linux builds from Windows.
