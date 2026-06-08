// STANRIS - Tetris clone using raylib + WebAssembly
// Build with emscripten for /game
#include "raylib.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>

#if defined(__EMSCRIPTEN__)
#include <emscripten/emscripten.h>
#endif

// --- Config ---
#define COLS 10
#define ROWS 20
#define BLOCK 32
#define SCREEN_W 800
#define SCREEN_H 720
#define BOARD_X 240
#define BOARD_Y 40
#define BOARD_W (COLS * BLOCK)
#define BOARD_H (ROWS * BLOCK)

// --- Types ---
typedef struct {
    int x, y;
    int type;   // 0..6
    int rot;    // 0..3
} Piece;

typedef struct {
    int grid[ROWS][COLS]; // 0 empty, 1-7 = piece type+1
    Piece current;
    Piece hold;
    int next[5];          // lookahead
    int bag[7];
    int bagIndex;

    int score;
    int lines;
    int level;
    float fallTimer;      // seconds until next gravity drop
    float lockTimer;      // lock delay when resting
    bool canHold;
    bool gameOver;
    bool paused;

    // DAS / ARR (delayed auto-shift)
    int moveDir;
    float dasTimer;
    float arrTimer;
} GameState;

static GameState game;
static Texture2D blockTex[8];      // 1-7 + 0 unused
static Texture2D ghostTex;
static Texture2D boardBgTex;

// Tetromino 4x4 shapes [type][rot][row][col]  0/1
static const int SHAPES[7][4][4][4] = {
    // I (0) cyan
    {
        {{0,0,0,0},{1,1,1,1},{0,0,0,0},{0,0,0,0}},
        {{0,1,0,0},{0,1,0,0},{0,1,0,0},{0,1,0,0}},
        {{0,0,0,0},{1,1,1,1},{0,0,0,0},{0,0,0,0}},
        {{0,1,0,0},{0,1,0,0},{0,1,0,0},{0,1,0,0}},
    },
    // O (1) yellow
    {
        {{0,0,0,0},{0,1,1,0},{0,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,1,0},{0,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,1,0},{0,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,1,0},{0,1,1,0},{0,0,0,0}},
    },
    // T (2) purple
    {
        {{0,0,0,0},{0,1,0,0},{1,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,0,0},{0,1,1,0},{0,1,0,0}},
        {{0,0,0,0},{0,0,0,0},{1,1,1,0},{0,1,0,0}},
        {{0,0,0,0},{0,1,0,0},{1,1,0,0},{0,1,0,0}},
    },
    // S (3) green
    {
        {{0,0,0,0},{0,1,1,0},{1,1,0,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,0,0},{0,1,1,0},{0,0,1,0}},
        {{0,0,0,0},{0,0,0,0},{0,1,1,0},{1,1,0,0}},
        {{0,0,0,0},{1,0,0,0},{1,1,0,0},{0,1,0,0}},
    },
    // Z (4) red
    {
        {{0,0,0,0},{1,1,0,0},{0,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,0,1,0},{0,1,1,0},{0,1,0,0}},
        {{0,0,0,0},{0,0,0,0},{1,1,0,0},{0,1,1,0}},
        {{0,0,0,0},{0,1,0,0},{1,1,0,0},{1,0,0,0}},
    },
    // J (5) blue
    {
        {{0,0,0,0},{1,0,0,0},{1,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,1,0},{0,1,0,0},{0,1,0,0}},
        {{0,0,0,0},{0,0,0,0},{1,1,1,0},{0,0,1,0}},
        {{0,0,0,0},{0,1,0,0},{0,1,0,0},{1,1,0,0}},
    },
    // L (6) orange
    {
        {{0,0,0,0},{0,0,1,0},{1,1,1,0},{0,0,0,0}},
        {{0,0,0,0},{0,1,0,0},{0,1,0,0},{0,1,1,0}},
        {{0,0,0,0},{0,0,0,0},{1,1,1,0},{1,0,0,0}},
        {{0,0,0,0},{1,1,0,0},{0,1,0,0},{0,1,0,0}},
    },
};

// Colors for UI labels (index = type+1)
static const Color PIECE_COLORS[8] = {
    {0}, // unused
    {0, 240, 240, 255},   // I cyan
    {240, 240, 0, 255},   // O yellow
    {160, 0, 240, 255},   // T purple
    {0, 240, 0, 255},     // S green
    {240, 0, 0, 255},     // Z red
    {0, 0, 240, 255},     // J blue
    {240, 160, 0, 255},   // L orange
};

// --- Forward decls ---
static void InitGame(void);
static void NewPiece(Piece *p);
static void SpawnPiece(void);
static bool CanPlace(const Piece *p);
static void PlacePiece(const Piece *p);
static void RotatePiece(Piece *p, int dir);
static bool MovePiece(Piece *p, int dx, int dy);
static int HardDrop(void);
static void HoldPiece(void);
static int ClearLines(void);
static void UpdateGame(float dt);
static void DrawGame(void);
static int GetGhostY(void);
static void ShuffleBag(void);
static void RefillNext(void);

// --- 7-bag randomizer ---
static void ShuffleBag(void) {
    for (int i = 0; i < 7; i++) game.bag[i] = i;
    for (int i = 6; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = game.bag[i]; game.bag[i] = game.bag[j]; game.bag[j] = tmp;
    }
    game.bagIndex = 0;
}

static int NextFromBag(void) {
    if (game.bagIndex >= 7) {
        ShuffleBag();
    }
    return game.bag[game.bagIndex++];
}

static void RefillNext(void) {
    for (int i = 0; i < 5; i++) {
        if (game.next[i] == -1) {
            game.next[i] = NextFromBag();
        }
    }
}

// --- Core game ---
static void InitGame(void) {
    memset(&game, 0, sizeof(GameState));
    memset(game.grid, 0, sizeof(game.grid));

    game.level = 1;
    game.score = 0;
    game.lines = 0;
    game.canHold = true;
    game.hold.type = -1;
    game.moveDir = 0;
    game.dasTimer = 0.0f;
    game.arrTimer = 0.0f;

    for (int i = 0; i < 5; i++) game.next[i] = -1;

    srand((unsigned)time(NULL));
    ShuffleBag();
    RefillNext();

    SpawnPiece();
}

static void NewPiece(Piece *p) {
    p->type = game.next[0];
    p->rot = 0;
    // Standard spawn positions (top center, slight offset per piece)
    p->x = 3;
    p->y = -1; // allow pieces to spawn partly off top for I/J/L etc.

    if (p->type == 0) { // I
        p->x = 3;
        p->y = -1;
    } else if (p->type == 1) { // O
        p->x = 4;
        p->y = 0;
    }

    // Shift the queue
    for (int i = 0; i < 4; i++) game.next[i] = game.next[i + 1];
    game.next[4] = -1;
    RefillNext();
}

static void SpawnPiece(void) {
    NewPiece(&game.current);
    game.fallTimer = 0.0f;
    game.lockTimer = 0.0f;
    game.canHold = true;

    if (!CanPlace(&game.current)) {
        game.gameOver = true;
    }
}

static bool IsValid(int x, int y, int t, int r) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (!SHAPES[t][r][i][j]) continue;
            int gx = x + j;
            int gy = y + i;
            if (gx < 0 || gx >= COLS || gy >= ROWS) return false;
            if (gy >= 0 && game.grid[gy][gx] != 0) return false;
        }
    }
    return true;
}

static bool CanPlace(const Piece *p) {
    return IsValid(p->x, p->y, p->type, p->rot);
}

static void PlacePiece(const Piece *p) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (!SHAPES[p->type][p->rot][i][j]) continue;
            int gx = p->x + j;
            int gy = p->y + i;
            if (gy >= 0 && gy < ROWS && gx >= 0 && gx < COLS) {
                game.grid[gy][gx] = p->type + 1;
            }
        }
    }
}

static bool MovePiece(Piece *p, int dx, int dy) {
    int nx = p->x + dx;
    int ny = p->y + dy;
    if (IsValid(nx, ny, p->type, p->rot)) {
        p->x = nx;
        p->y = ny;
        return true;
    }
    return false;
}

static void RotatePiece(Piece *p, int dir) {
    int nr = (p->rot + (dir > 0 ? 1 : 3)) % 4; // +1 or -1 mod 4

    // Simple wall kicks (left, right, up). Good enough for fun play.
    int kicks[5][2] = {{0,0}, {-1,0}, {1,0}, {0,-1}, {0,1}};

    for (int k = 0; k < 5; k++) {
        int tx = p->x + kicks[k][0];
        int ty = p->y + kicks[k][1];
        if (IsValid(tx, ty, p->type, nr)) {
            p->x = tx;
            p->y = ty;
            p->rot = nr;
            return;
        }
    }
    // rotation failed
}

static int HardDrop(void) {
    int dist = 0;
    Piece tmp = game.current;
    while (IsValid(tmp.x, tmp.y + 1, tmp.type, tmp.rot)) {
        tmp.y++;
        dist++;
    }
    game.current = tmp;
    PlacePiece(&game.current);
    int cleared = ClearLines();
    SpawnPiece();
    return dist * 2; // score bonus per cell dropped
}

static void HoldPiece(void) {
    if (!game.canHold) return;

    if (game.hold.type == -1) {
        game.hold = game.current;
        game.hold.rot = 0;
        SpawnPiece();
    } else {
        Piece tmp = game.current;
        game.current = game.hold;
        game.current.x = (game.current.type == 1) ? 4 : 3;
        game.current.y = (game.current.type == 1) ? 0 : -1;
        game.current.rot = 0;
        game.hold = tmp;
        game.hold.rot = 0;
    }
    game.canHold = false;
    game.lockTimer = 0.0f;
}

static int ClearLines(void) {
    int cleared = 0;
    for (int r = ROWS - 1; r >= 0; r--) {
        bool full = true;
        for (int c = 0; c < COLS; c++) {
            if (game.grid[r][c] == 0) { full = false; break; }
        }
        if (full) {
            cleared++;
            // Shift everything down
            for (int rr = r; rr > 0; rr--) {
                for (int c = 0; c < COLS; c++) {
                    game.grid[rr][c] = game.grid[rr - 1][c];
                }
            }
            for (int c = 0; c < COLS; c++) game.grid[0][c] = 0;
            r++; // recheck same row index after shift
        }
    }

    if (cleared > 0) {
        // Classic-ish scoring
        int base[] = {0, 100, 300, 500, 800};
        int add = base[cleared] * game.level;
        game.score += add;

        game.lines += cleared;
        int newLevel = (game.lines / 10) + 1;
        if (newLevel > game.level) {
            game.level = newLevel;
        }
    }
    return cleared;
}

static int GetGhostY(void) {
    Piece g = game.current;
    while (IsValid(g.x, g.y + 1, g.type, g.rot)) {
        g.y++;
    }
    return g.y;
}

// --- Update ---
static void UpdateGame(float dt) {
    if (game.gameOver || game.paused) return;

    // --- Input: DAS / horizontal movement ---
    int desiredDir = 0;
    if (IsKeyDown(KEY_LEFT)) desiredDir = -1;
    if (IsKeyDown(KEY_RIGHT)) desiredDir = 1;

    if (desiredDir != 0) {
        if (desiredDir != game.moveDir) {
            // New direction pressed
            game.moveDir = desiredDir;
            game.dasTimer = 0.0f;
            if (MovePiece(&game.current, desiredDir, 0)) {
                game.lockTimer = 0.0f; // reset lock on move
            }
        } else {
            // Holding same direction
            game.dasTimer += dt;
            const float DAS = 0.12f;
            const float ARR = 0.045f;

            if (game.dasTimer > DAS) {
                game.arrTimer += dt;
                if (game.arrTimer > ARR) {
                    game.arrTimer = 0.0f;
                    if (MovePiece(&game.current, game.moveDir, 0)) {
                        game.lockTimer = 0.0f;
                    }
                }
            }
        }
    } else {
        game.moveDir = 0;
        game.dasTimer = 0.0f;
        game.arrTimer = 0.0f;
    }

    // Rotation (edge triggered)
    if (IsKeyPressed(KEY_UP) || IsKeyPressed(KEY_X)) {
        RotatePiece(&game.current, 1);
        game.lockTimer = 0.0f;
    }
    if (IsKeyPressed(KEY_Z)) {
        RotatePiece(&game.current, -1);
        game.lockTimer = 0.0f;
    }

    // Soft drop
    bool softDropping = IsKeyDown(KEY_DOWN);
    float gravity = 0.85f - (game.level - 1) * 0.06f;
    if (gravity < 0.05f) gravity = 0.05f;

    if (softDropping) {
        gravity = 0.04f; // much faster
    }

    game.fallTimer += dt;
    if (game.fallTimer >= gravity) {
        game.fallTimer = 0.0f;
        if (!MovePiece(&game.current, 0, 1)) {
            // Cannot go down
        }
    }

    // Lock delay logic
    bool resting = !IsValid(game.current.x, game.current.y + 1, game.current.type, game.current.rot);
    if (resting) {
        game.lockTimer += dt;
        const float LOCK_DELAY = 0.55f;
        if (game.lockTimer >= LOCK_DELAY) {
            PlacePiece(&game.current);
            int cleared = ClearLines();
            if (cleared == 0) {
                // small score for soft landing not needed
            }
            SpawnPiece();
            game.lockTimer = 0.0f;
        }
    } else {
        game.lockTimer = 0.0f;
    }

    // Hard drop
    if (IsKeyPressed(KEY_SPACE)) {
        int dropDist = HardDrop();
        game.score += dropDist;
        game.lockTimer = 0.0f;
    }

    // Hold
    if (IsKeyPressed(KEY_C) || IsKeyPressed(KEY_LEFT_SHIFT) || IsKeyPressed(KEY_RIGHT_SHIFT)) {
        HoldPiece();
    }

    // Pause
    if (IsKeyPressed(KEY_P)) {
        game.paused = !game.paused;
    }

    // Restart anytime
    if (IsKeyPressed(KEY_R)) {
        InitGame();
    }
}

// --- Drawing helpers ---
static void DrawBlock(int gx, int gy, int t, float alpha) {
    if (t <= 0 || t > 7) return;
    int px = BOARD_X + gx * BLOCK;
    int py = BOARD_Y + gy * BLOCK;
    Color c = PIECE_COLORS[t];
    if (alpha < 1.0f) {
        c.a = (unsigned char)(255 * alpha);
        DrawTexture(ghostTex, px, py, c); // use ghost tex as base for tint
    } else {
        DrawTexture(blockTex[t], px, py, WHITE);
    }
}

static void DrawPiece(const Piece *p, int ox, int oy, bool isGhost) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (!SHAPES[p->type][p->rot][i][j]) continue;
            int gx = p->x + j;
            int gy = p->y + i;
            if (gy < 0) continue; // don't draw above board
            int px = ox + gx * BLOCK;
            int py = oy + gy * BLOCK;
            if (isGhost) {
                Color tint = {255, 255, 255, 110};
                DrawTexture(ghostTex, px, py, tint);
            } else {
                DrawTexture(blockTex[p->type + 1], px, py, WHITE);
            }
        }
    }
}

static void DrawMiniPiece(int type, int px, int py) {
    if (type < 0) return;
    int s = 18; // mini block
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (!SHAPES[type][0][i][j]) continue;
            int x = px + j * s;
            int y = py + i * s;
            // Use the normal block texture scaled down by drawing rect + tint
            Color c = PIECE_COLORS[type + 1];
            DrawRectangle(x, y, s-1, s-1, c);
            DrawRectangleLines(x, y, s-1, s-1, (Color){20,20,20,255});
        }
    }
}

static void DrawGame(void) {
    ClearBackground((Color){12, 12, 18, 255});

    // Title
    DrawText("STANRIS", 40, 12, 32, (Color){255, 40, 90, 255});
    DrawText("TETRIS", 40, 42, 18, (Color){180, 180, 200, 255});

    // Left panel - HOLD
    DrawRectangle(30, 90, 170, 140, (Color){20, 20, 28, 255});
    DrawRectangleLines(30, 90, 170, 140, (Color){60, 60, 80, 255});
    DrawText("HOLD", 85, 98, 18, (Color){200, 200, 220, 255});
    if (game.hold.type >= 0) {
        DrawMiniPiece(game.hold.type, 55, 125);
    }

    // Right panel - NEXT
    DrawRectangle(600, 90, 170, 220, (Color){20, 20, 28, 255});
    DrawRectangleLines(600, 90, 170, 220, (Color){60, 60, 80, 255});
    DrawText("NEXT", 655, 98, 18, (Color){200, 200, 220, 255});
    for (int i = 0; i < 3; i++) {
        if (game.next[i] >= 0) {
            DrawMiniPiece(game.next[i], 625, 130 + i * 58);
        }
    }

    // Stats
    DrawRectangle(600, 330, 170, 160, (Color){20, 20, 28, 255});
    DrawRectangleLines(600, 330, 170, 160, (Color){60, 60, 80, 255});
    char buf[64];
    snprintf(buf, sizeof(buf), "SCORE\n%d", game.score);
    DrawText(buf, 615, 345, 16, (Color){255, 255, 255, 255});
    snprintf(buf, sizeof(buf), "LEVEL\n%d", game.level);
    DrawText(buf, 615, 400, 16, (Color){180, 255, 180, 255});
    snprintf(buf, sizeof(buf), "LINES\n%d", game.lines);
    DrawText(buf, 615, 455, 16, (Color){180, 200, 255, 255});

    // Board background + border
    DrawTexture(boardBgTex, BOARD_X, BOARD_Y, WHITE);
    DrawRectangleLinesEx((Rectangle){BOARD_X-2, BOARD_Y-2, BOARD_W+4, BOARD_H+4}, 4, (Color){70, 70, 90, 255});

    // Locked blocks
    for (int y = 0; y < ROWS; y++) {
        for (int x = 0; x < COLS; x++) {
            int t = game.grid[y][x];
            if (t > 0) {
                DrawBlock(x, y, t, 1.0f);
            }
        }
    }

    // Ghost piece
    if (!game.gameOver) {
        int gy = GetGhostY();
        if (gy != game.current.y) {
            Piece g = game.current;
            g.y = gy;
            DrawPiece(&g, BOARD_X, BOARD_Y, true);
        }
    }

    // Current piece
    if (!game.gameOver) {
        DrawPiece(&game.current, BOARD_X, BOARD_Y, false);
    }

    // Side lines / decoration
    DrawRectangle(BOARD_X - 8, BOARD_Y, 6, BOARD_H, (Color){40, 40, 55, 255});
    DrawRectangle(BOARD_X + BOARD_W + 2, BOARD_Y, 6, BOARD_H, (Color){40, 40, 55, 255});

    // Overlays
    if (game.paused) {
        DrawRectangle(BOARD_X, BOARD_Y, BOARD_W, BOARD_H, (Color){0,0,0,160});
        DrawText("PAUSED", BOARD_X + 90, BOARD_Y + 280, 36, WHITE);
        DrawText("P to resume", BOARD_X + 95, BOARD_Y + 330, 18, (Color){200,200,200,255});
    }

    if (game.gameOver) {
        DrawRectangle(BOARD_X, BOARD_Y, BOARD_W, BOARD_H, (Color){0,0,0,175});
        DrawText("GAME OVER", BOARD_X + 55, BOARD_Y + 260, 32, (Color){255, 60, 80, 255});
        DrawText("Press R to restart", BOARD_X + 70, BOARD_Y + 310, 18, (Color){220, 220, 230, 255});
    }

    // Controls footer
    DrawText("Arrows: Move  |  UP/X: Rotate  |  DOWN: Soft  |  SPACE: Hard Drop  |  C/SHIFT: Hold  |  P: Pause  |  R: Restart",
             40, SCREEN_H - 28, 13, (Color){140, 140, 160, 255});
}

// --- Main loop glue ---
static void MainLoop(void) {
    float dt = GetFrameTime();
    UpdateGame(dt);

    BeginDrawing();
    DrawGame();
    EndDrawing();
}

int main(void) {
    InitWindow(SCREEN_W, SCREEN_H, "STANRIS");
    SetTargetFPS(60);

    // Load textures.
    // - Web: --preload-file puts them at /textures/...
    // - Native: try several likely relative locations so you can run the binary
    //   from the repo root, screen/game/, or screen/game/src/.
    const char *candidates[] = {
        "textures/",            // run from screen/game/
        "screen/game/textures/",// run from repo root
        "game/textures/",       // run from screen/
        "../textures/",         // run from src/
        "./textures/",
        NULL
    };

    char path[256];
    const char *base = NULL;
    for (int ci = 0; candidates[ci]; ci++) {
        snprintf(path, sizeof(path), "%sblock_I.png", candidates[ci]);
        if (FileExists(path)) { base = candidates[ci]; break; }
    }
    if (!base) base = "textures/"; // last chance, let raylib error if missing

    snprintf(path, sizeof(path), "%sblock_I.png", base); blockTex[1] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_O.png", base); blockTex[2] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_T.png", base); blockTex[3] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_S.png", base); blockTex[4] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_Z.png", base); blockTex[5] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_J.png", base); blockTex[6] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_L.png", base); blockTex[7] = LoadTexture(path);
    snprintf(path, sizeof(path), "%sblock_ghost.png", base); ghostTex = LoadTexture(path);
    snprintf(path, sizeof(path), "%sboard_bg.png", base); boardBgTex = LoadTexture(path);

    // Make sure textures are filtered nicely for crisp pixels
    for (int i = 1; i <= 7; i++) {
        SetTextureFilter(blockTex[i], TEXTURE_FILTER_POINT);
    }
    SetTextureFilter(ghostTex, TEXTURE_FILTER_POINT);
    SetTextureFilter(boardBgTex, TEXTURE_FILTER_POINT);

    InitGame();

#if defined(__EMSCRIPTEN__)
    emscripten_set_main_loop(MainLoop, 0, 1);
#else
    while (!WindowShouldClose()) {
        MainLoop();
    }
#endif

    // Cleanup (only reached on desktop)
    for (int i = 1; i <= 7; i++) UnloadTexture(blockTex[i]);
    UnloadTexture(ghostTex);
    UnloadTexture(boardBgTex);
    CloseWindow();
    return 0;
}