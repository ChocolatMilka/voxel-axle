"""Bake the whole texture atlas (block tiles + mob tiles) into atlas.raw.

This is the SINGLE SOURCE OF TRUTH for tile ordering. The Axle side mirrors
this order in `src/world/tiles.axle` (keep them in sync!) and `config.atlasTiles`
must equal the total tile count printed at the end.

Block textures are pulled from the HD resource pack and COPIED into the repo
(`assets/textures/block/`) on first use, so the project stays self-contained. MC's
grass/leaves are greyscale and tinted per-biome at runtime; we have no runtime
tint, so the tint is baked here (luminance-recolour toward a target colour).
Mob tiles reuse the crops from the old bake_mobs.py, read from the repo's
`assets/textures/entity/` (the repaired creeper charge.png lives there).

Run:  python bake_atlas.py
"""
from PIL import Image
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
PACK = Path(r"C:\Users\users\AppData\Roaming\.minecraft\resourcepacks"
            r"\Default HD 128x Demo 1.8.2.4\assets\minecraft\textures\block")
BLOCK_OUT = ROOT / "assets" / "textures" / "block"
TEX = ROOT / "assets" / "textures" / "entity"
TILE = 64

# ── Per-biome / per-species tint colours (greyscale source → this hue) ──
T_PLAINS = (124, 189, 107)
T_SAVANNA = (180, 170, 70)
T_JUNGLE = (74, 168, 52)
T_SWAMP = (90, 122, 78)
T_TAIGA = (122, 170, 140)
L_OAK = (84, 152, 70)
L_BIRCH = (132, 178, 86)
L_SPRUCE = (66, 110, 78)
L_ACACIA = (120, 150, 56)
L_JUNGLE = (60, 150, 46)
L_DARKOAK = (74, 116, 58)

raw = bytearray()
_index = []   # (tile_index, label) for the printed map
_copied = set()


def src(name: str) -> Path:
    """Copy `<name>.png` from the pack into assets/textures/block/ (once) and return
    the repo path. Falls back to an already-present repo copy if the pack
    lacks it."""
    out = BLOCK_OUT / f"{name}.png"
    if name not in _copied:
        srcp = PACK / f"{name}.png"
        if srcp.exists():
            BLOCK_OUT.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(srcp, out)
        _copied.add(name)
    return out


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def mean_lum(im):
    px = [p for p in im.get_flattened_data() if p[3] >= 128]
    if not px:
        return 1.0
    return max(1.0, sum(lum(p) for p in px) / len(px))


def to64(im):
    return im.convert("RGBA").resize((TILE, TILE), Image.NEAREST)


def emit(im, base):
    """Append a 64x64 tile as BGRA, compositing transparent texels onto
    `base` so the world never shows holes."""
    im = to64(im)
    px = im.load()
    for y in range(TILE):
        for x in range(TILE):
            r, g, b, a = px[x, y]
            if a < 128:
                r, g, b = base
            raw.extend((b, g, r, 255))


def add(label, im, base):
    _index.append((len(raw) // (TILE * TILE * 4), label))
    emit(im, base)


def tinted(im, color):
    """Luminance-recolour a (greyscale) image toward `color`: the image's
    mean tone maps to `color`, brighter/darker texels scale around it."""
    im = im.convert("RGBA")
    base = mean_lum(im)
    px = im.load()
    w, h = im.size
    out = Image.new("RGBA", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            s = lum((r, g, b)) / base
            op[x, y] = (min(255, int(color[0] * s)),
                        min(255, int(color[1] * s)),
                        min(255, int(color[2] * s)), a)
    return out


def block(name):
    return Image.open(src(name)).convert("RGBA")


def grass_top(label, color):
    add(label, tinted(block("grass_block_top"), color), (90, 140, 70))


def grass_side(label, color):
    base = block("dirt").copy()
    ov = tinted(block("grass_block_side_overlay"), color)
    base.alpha_composite(ov)
    add(label, base, (110, 84, 56))


# ════════════════ BLOCK TILES (order == tiles.axle) ════════════════
grass_top("grass_top (plains)", T_PLAINS)        # 0
grass_side("grass_side (plains)", T_PLAINS)      # 1
add("dirt", block("dirt"), (120, 86, 58))        # 2
add("coarse_dirt", block("coarse_dirt"), (110, 80, 54))  # 3
add("podzol_top", block("podzol_top"), (90, 64, 32))     # 4
add("podzol_side", block("podzol_side"), (110, 80, 50))  # 5
add("mycelium_top", block("mycelium_top"), (114, 100, 110))  # 6
add("mycelium_side", block("mycelium_side"), (110, 84, 60))  # 7
add("sand", block("sand"), (218, 205, 145))      # 8
add("red_sand", block("red_sand"), (190, 110, 56))  # 9
add("gravel", block("gravel"), (122, 118, 112))  # 10
add("clay", block("clay"), (160, 165, 172))      # 11
add("snow", block("snow"), (236, 240, 246))      # 12
add("ice", block("ice"), (150, 180, 235))        # 13
add("packed_ice", block("packed_ice"), (140, 168, 222))  # 14
add("stone", block("stone"), (128, 128, 132))    # 15
add("cobblestone", block("cobblestone"), (122, 120, 120))  # 16
add("mossy_cobblestone", block("mossy_cobblestone"), (104, 116, 96))  # 17
add("granite", block("granite"), (154, 110, 92)) # 18
add("diorite", block("diorite"), (188, 188, 190))  # 19
add("andesite", block("andesite"), (136, 138, 138))  # 20
add("stone_bricks", block("stone_bricks"), (122, 122, 124))  # 21
add("bricks", block("bricks"), (150, 96, 80))    # 22
add("sandstone_top", block("sandstone_top"), (224, 212, 158))  # 23
add("sandstone_side", block("sandstone"), (220, 208, 152))     # 24
add("sandstone_bottom", block("sandstone_bottom"), (216, 204, 150))  # 25
add("red_sandstone_top", block("red_sandstone_top"), (190, 100, 40))  # 26
add("red_sandstone_side", block("red_sandstone"), (184, 96, 38))      # 27
add("terracotta", block("terracotta"), (150, 92, 66))   # 28
add("orange_terracotta", block("orange_terracotta"), (162, 84, 38))  # 29
add("white_terracotta", block("white_terracotta"), (208, 176, 156))  # 30
add("oak_log_side", block("oak_log"), (104, 80, 48))    # 31
add("oak_log_top", block("oak_log_top"), (152, 120, 72))  # 32
add("oak_leaves", tinted(block("oak_leaves"), L_OAK), (40, 78, 34))  # 33
add("oak_planks", block("oak_planks"), (150, 112, 66))  # 34
add("birch_log_side", block("birch_log"), (200, 200, 192))  # 35
add("birch_log_top", block("birch_log_top"), (180, 168, 120))  # 36
add("birch_leaves", tinted(block("birch_leaves"), L_BIRCH), (66, 92, 42))  # 37
add("spruce_log_side", block("spruce_log"), (66, 48, 28))  # 38
add("spruce_log_top", block("spruce_log_top"), (108, 82, 48))  # 39
add("spruce_leaves", tinted(block("spruce_leaves"), L_SPRUCE), (34, 58, 40))  # 40
add("acacia_log_side", block("acacia_log"), (104, 78, 64))  # 41
add("acacia_log_top", block("acacia_log_top"), (140, 100, 70))  # 42
add("acacia_leaves", tinted(block("acacia_leaves"), L_ACACIA), (62, 78, 28))  # 43
add("jungle_log_side", block("jungle_log"), (88, 68, 36))  # 44
add("jungle_log_top", block("jungle_log"), (120, 96, 56))  # 45 (no _top in pack)
add("jungle_leaves", tinted(block("jungle_leaves"), L_JUNGLE), (32, 78, 24))  # 46
add("dark_oak_log_side", block("dark_oak_log"), (66, 50, 32))  # 47
add("dark_oak_log_top", block("dark_oak_log_top"), (92, 70, 44))  # 48
add("dark_oak_leaves", tinted(block("dark_oak_leaves"), L_DARKOAK), (40, 62, 30))  # 49
add("cactus_side", block("cactus_side"), (78, 116, 50))  # 50
add("cactus_top", block("cactus_top"), (90, 124, 58))    # 51
add("pumpkin_side", block("pumpkin_side"), (190, 122, 38))  # 52
add("pumpkin_top", block("pumpkin_top"), (180, 130, 50))    # 53
add("melon_side", block("melon_side"), (110, 140, 40))   # 54
add("melon_top", block("melon_top"), (120, 150, 50))     # 55
add("glowstone", block("glowstone"), (180, 150, 92))     # 56
add("water", Image.open(src("water_still")).crop((0, 0, 16, 16)), (50, 90, 200))  # 57
add("coal_ore", block("coal_ore"), (70, 70, 72))         # 58
add("iron_ore", block("iron_ore"), (150, 132, 116))      # 59
add("gold_ore", block("gold_ore"), (160, 150, 96))       # 60
add("diamond_ore", block("diamond_ore"), (120, 170, 170))  # 61
add("redstone_ore", block("redstone_ore"), (140, 90, 88))  # 62
add("emerald_ore", block("emerald_ore"), (90, 150, 104))   # 63
add("lapis_ore", block("lapis_ore"), (90, 100, 140))       # 64
grass_top("grass_top (savanna)", T_SAVANNA)      # 65
grass_side("grass_side (savanna)", T_SAVANNA)    # 66
grass_top("grass_top (jungle)", T_JUNGLE)        # 67
grass_side("grass_side (jungle)", T_JUNGLE)      # 68
grass_top("grass_top (swamp)", T_SWAMP)          # 69
grass_side("grass_side (swamp)", T_SWAMP)        # 70
grass_top("grass_top (taiga)", T_TAIGA)          # 71
grass_side("grass_side (taiga)", T_TAIGA)        # 72
# ── Expansion: bamboo, cherry, giant mushrooms ──
add("bamboo_side", block("bamboo_stalk"), (110, 150, 70))        # 73
add("bamboo_top", block("bamboo_block_top"), (150, 170, 90))     # 74
add("cherry_log_side", block("cherry_log"), (96, 64, 74))        # 75
add("cherry_log_top", block("cherry_log_top"), (124, 92, 102))   # 76
add("cherry_leaves", block("cherry_leaves"), (236, 168, 206))    # 77
add("mushroom_stem", block("mushroom_stem"), (206, 200, 186))    # 78
add("red_mushroom_block", block("red_mushroom_block"), (180, 36, 36))    # 79
add("brown_mushroom_block", block("brown_mushroom_block"), (150, 112, 76))  # 80

BLOCK_TILES = len(_index)

# ════════════════ MOB TILES (after the blocks) ════════════════
# (source png, crop box in the 512x256 entity net, fallback base RGB)
MOBS = [
    (TEX / "chicken.png",          (16, 140, 176, 252), (236, 236, 232), "chicken_body"),
    (TEX / "chicken.png",          (20, 16, 116, 112),  (240, 240, 236), "chicken_head"),
    (TEX / "sheep" / "sheep.png",  (272, 36, 446, 208), (224, 222, 214), "sheep_wool"),
    (TEX / "sheep" / "sheep.png",  (64, 64, 112, 112),  (215, 205, 195), "sheep_head"),
    (TEX / "cow" / "cow.png",      (168, 40, 360, 200), (94, 74, 58),    "cow_body"),
    (TEX / "cow" / "cow.png",      (48, 48, 104, 112),  (110, 86, 66),   "cow_head"),
    (TEX / "creeper" / "creeper.png", (160, 160, 224, 256), (58, 140, 58), "creeper_skin"),
    (TEX / "creeper" / "creeper.png", (64, 64, 128, 128),   (40, 80, 40),  "creeper_face"),
    (TEX / "creeper" / "charge.png",  (128, 128, 192, 224), (228, 196, 40), "charge_skin"),
    (TEX / "creeper" / "charge.png",  (64, 64, 128, 128),   (200, 150, 30), "charge_face"),
    (TEX / "pig" / "pig.png", (84, 20, 180, 100), (222, 150, 150), "pig_body"),
    (TEX / "pig" / "pig.png", (24, 24, 52, 56),   (230, 162, 162), "pig_head"),
]
for path, box, base, label in MOBS:
    add(label, Image.open(path).convert("RGBA").crop(box), base)

# ════════════════ Write + report ════════════════
total = len(raw) // (TILE * TILE * 4)
(ROOT / "atlas.raw").write_bytes(raw)
tgt = ROOT / "target"
if tgt.is_dir():
    (tgt / "atlas.raw").write_bytes(raw)

print(f"baked {total} tiles ({BLOCK_TILES} block + {total - BLOCK_TILES} mob), "
      f"{len(raw)} bytes")
print("--- tile index map (mirror in src/world/tiles.axle) ---")
for i, label in _index:
    print(f"{i:3d}  {label}")
