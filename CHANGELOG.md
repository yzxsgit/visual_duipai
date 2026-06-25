# Changelog

All notable changes to VisualDuipai will be documented in this file.

## Unreleased

### Added

- Linux AppImage 打包支持，通过 `build_linux.sh` 一键生成 `VisualDuipai-x86_64.AppImage`
- 应用图标（二分叉再汇聚设计）

## v0.1.0 - 2026-06-10

### Added

- Initial VisualDuipai GUI for local algorithm stress testing.
- Support for selecting or dragging in brute-force solution, accepted/optimized solution, and generator C++ files.
- Local compile-run-compare workflow using `g++`.
- Failure artifacts for debugging mismatched outputs.
- Drag-and-drop support through `tkinterdnd2`.
- Windows PyInstaller packaging through `build_exe.ps1`.
- GitHub Release documentation for publishing `VisualDuipai.exe` as a zip asset.
