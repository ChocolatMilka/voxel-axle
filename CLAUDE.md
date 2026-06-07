# CLAUDE.md — voxel-axle

A Minecraft-style voxel game written in **Axle** and software-rendered into an
SDL2 window. Source under `src/**.axle`, config in `axle.toml`. See `README.md`
for the architecture and controls.

## Axle toolchain — REQUIRED: v0.2.11 or newer

This project must be compiled with **Axle v0.2.11+**. Always check the version
before building:

```powershell
axle --version        # must print 0.2.11 or higher
```

If the version is < 0.2.11 (or `axle: command not found`), install/upgrade the
compiler (see below) **before** compiling anything. Do not fall back to an
older version: codegen and the stdlib evolve between releases, and a 0.2.10
binary can surface errors that no longer exist in 0.2.11+.

## Install / upgrade Axle

The compiler lives in the sibling repo `../axle` (Rust + LLVM 18 backend).

### Windows (this machine)

The binary is installed via the MSI at `C:\Program Files (x86)\Axle\axle.exe`.
Two ways to get 0.2.11+:

1. **MSI release (recommended)** — install the Windows x64 `.msi` from the
   `v0.2.11` version, then reopen the terminal and
   recheck `axle --version`.
2. **Build from source** — from `../axle`:
   ```powershell
   # Prerequisites: Visual C++ Build Tools + LLVM 18 (see ../axle/SETUP-WINDOWS.md)
   $env:LLVM_SYS_181_PREFIX = "C:\Program Files\LLVM"
   cargo build --release -p axle_cli
   # binary: ../axle/target/release/axle.exe — add it to PATH or call it directly
   ```

### Linux / macOS

- **Linux (apt)**: official repo — `sudo apt install axle`, then
  `sudo apt upgrade` to move to 0.2.11+. Details in
  `../axle/docs/src/getting-started/install.md`.
- **macOS / no apt**: Docker image or build from source
  (`../axle/docs/src/getting-started/build.md`).

## Runtime prerequisites for THIS project (SDL2)

- SDL2 installed; `SDL2.dll` copied next to the binary (in `target/`).
- vcpkg: `vcpkg install sdl2:x64-windows` — `axle.toml` (`[link] paths`) points
  at its `lib` (machine-specific path).
- `atlas.raw` must sit next to the binary or in `target/` (loaded at runtime).

## Build & run

```powershell
axle --version        # 0.2.11+ required
axle run              # from the project root
```

Useful Axle commands: `axle build <in>`, `axle run <in>`,
`axle check <in>` (type-check only).
