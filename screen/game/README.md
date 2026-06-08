# STANRIS — Tetris (C + raylib + WebAssembly)

A complete Tetris clone written in C using raylib, compiled to WebAssembly via Emscripten.

**URL**: `/game` (served from Django template + static files)

## Files

- `src/tetris.c` — full game (7-bag, DAS/ARR, ghost, hold, lock delay, scoring, levels)
- `textures/` — generated block art (I, O, T, S, Z, J, L + ghost + board bg)
- `generate_textures.py` — Python/PIL script that created the PNGs
- `build.sh` — the emscripten build that outputs to `screen/static/screen/game/`
- Built artifacts live in `../../static/screen/game/` (tetris.js, tetris.wasm, tetris.data)

## Build Instructions (one time setup)

### 1. Emscripten SDK

```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```

### 2. raylib for WebAssembly

```bash
git clone https://github.com/raysan5/raylib.git
cd raylib/src
make clean
make PLATFORM=PLATFORM_WEB -B -j4
```

You now have `libraylib.a` compiled for wasm inside `raylib/src`.

### 3. Set the path + build

```bash
export RAYLIB_PATH=/full/path/to/your/raylib
cd screen/game
./build.sh
```

The script will produce:
- `screen/static/screen/game/tetris.js`
- `screen/static/screen/game/tetris.wasm`
- `screen/static/screen/game/tetris.data` (contains all the textures preloaded into the virtual FS)

## Running

Start Django normally:

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/game/**

Click the canvas to focus, then use keyboard.

## Controls

| Key           | Action          |
|---------------|-----------------|
| ← →           | Move            |
| ↑ or X        | Rotate CW       |
| Z             | Rotate CCW      |
| ↓             | Soft drop       |
| SPACE         | Hard drop       |
| C / SHIFT     | Hold piece      |
| P             | Pause           |
| R             | Restart         |

## Desktop testing (optional)

If you have native raylib installed on macOS (`brew install raylib`), you can quickly test the logic without emscripten:

```bash
cd screen/game
cc -o /tmp/stanris src/tetris.c -lraylib -framework OpenGL -framework Cocoa -framework IOKit -framework CoreVideo
/tmp/stanris
```

## Notes

- Textures are point-filtered for crisp retro pixels.
- Uses 7-bag randomizer (no drought).
- Simple but effective wall kicks (good enough for real play).
- Lock delay + move/rotate reset.
- The `/game` route is public (no auth) so anyone on the lab network can play.
- If you see "BUILD REQUIRED" on the page, the static artifacts are missing — run `build.sh`.

Enjoy.  — stannews lab edition
