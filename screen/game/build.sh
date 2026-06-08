#!/usr/bin/env bash
# Build STANRIS (Tetris) to WebAssembly for Django /game
#
# PREREQUISITES:
#   1. Install Emscripten SDK (emsdk):
#      git clone https://github.com/emscripten-core/emsdk.git
#      cd emsdk
#      ./emsdk install latest
#      ./emsdk activate latest
#      source ./emsdk_env.sh
#
#   2. Build raylib for WebAssembly:
#      git clone https://github.com/raysan5/raylib.git
#      cd raylib/src
#      make clean
#      make PLATFORM=PLATFORM_WEB -B -j4
#      # The libraylib.a for web is now in src/
#
#   3. Set RAYLIB_PATH env var to the raylib checkout root, e.g.:
#      export RAYLIB_PATH=/Users/chris/raylib
#
#   4. Run this script from the screen/game/ directory:
#      ./build.sh
#
# Output will be placed in:
#   screen/static/screen/game/
#     - tetris.js
#     - tetris.wasm
#     - tetris.data   (contains preloaded textures/)
#     - (optional index.html if you want the raw emscripten shell)
#
# Then visit http://127.0.0.1:8000/game/
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"   # stannews/
STATIC_GAME_DIR="$PROJECT_ROOT/screen/static/screen/game"

RAYLIB_PATH="${RAYLIB_PATH:-$HOME/raylib}"

if [ ! -d "$RAYLIB_PATH/src" ]; then
    echo "ERROR: RAYLIB_PATH is not set or invalid."
    echo "       Current: $RAYLIB_PATH"
    echo "Please export RAYLIB_PATH to your raylib source checkout."
    exit 1
fi

if ! command -v emcc >/dev/null 2>&1; then
    echo "ERROR: emcc not found. Activate emsdk first:"
    echo "  source /path/to/emsdk/emsdk_env.sh"
    exit 1
fi

echo "==> Using RAYLIB_PATH=$RAYLIB_PATH"
echo "==> Output dir: $STATIC_GAME_DIR"
mkdir -p "$STATIC_GAME_DIR"

# Clean previous
rm -f "$STATIC_GAME_DIR"/tetris.{js,wasm,data} "$STATIC_GAME_DIR"/*.html 2>/dev/null || true

cd "$SCRIPT_DIR"

echo "==> Compiling tetris.c -> WebAssembly (separate JS + WASM + preloaded data) ..."

emcc src/tetris.c \
  -o "$STATIC_GAME_DIR/tetris.js" \
  -I"$RAYLIB_PATH/src" \
  -L"$RAYLIB_PATH/src" \
  -lraylib \
  -s USE_GLFW=3 \
  -s ASYNCIFY=1 \
  -s TOTAL_MEMORY=128MB \
  -s FORCE_FILESYSTEM=1 \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s ASSERTIONS=0 \
  -s WASM=1 \
  --preload-file textures@/textures \
  -s 'EXPORTED_RUNTIME_METHODS=["ccall","cwrap"]' \
  -O3

echo "==> Build complete."
echo ""
echo "Artifacts in $STATIC_GAME_DIR :"
ls -lh "$STATIC_GAME_DIR"/tetris.* 2>/dev/null || true

echo ""
echo "Now run the Django server and visit:"
echo "  http://127.0.0.1:8000/game/"
echo ""
echo "Tip: You can also open the raw emscripten shell by temporarily adding a"
echo "     simple index.html, but the Django template at /game is preferred."