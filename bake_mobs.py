"""Append mob-texture tiles to the block atlas.

Reads the existing `atlas.raw` (11 block tiles, 64x64 BGRA) and appends
representative 64x64 tiles cropped from the Minecraft entity textures
(512x256 = the 64x32 UV net at 8x), then rewrites `atlas.raw` (and copies
it next to the built binary). The engine loads `atlas.raw` at runtime, so
there is no embedded-hex source to regenerate. Tile order after the 11
block tiles: 11 chicken-body, 12 chicken-head, 13 sheep-wool, 14
sheep-head, 15 cow-body, 16 cow-head.
"""
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "textures" / "entity"
TILE = 64

# (source png, crop box in 512x256 source coords, fallback base RGB)
# The "head" entries are the FRONT-FACE crops (the animal's face), used
# only on whichever box face points along the mob's heading; the "body"
# crops are the skin used on every other face. Source is the 64x32 MC UV
# net at 8x, so a logical (x,y,w,h) face maps to (8x, 8y, 8w, 8h).
TILES = [
    (TEX / "chicken.png",       (16, 140, 176, 252), (236, 236, 232)),  # 11 chicken body
    (TEX / "chicken.png",       (20, 16, 116, 112),  (240, 240, 236)),  # 12 chicken head
    (TEX / "sheep" / "sheep.png", (272, 36, 446, 208), (224, 222, 214)),  # 13 sheep wool
    (TEX / "sheep" / "sheep.png", (64, 64, 112, 112),  (215, 205, 195)),  # 14 sheep face (8,8,6,6)
    (TEX / "cow" / "cow.png",   (168, 40, 360, 200), (94, 74, 58)),     # 15 cow body
    (TEX / "cow" / "cow.png",   (48, 48, 104, 112),  (110, 86, 66)),    # 16 cow face (6,6,7,8)
]


def bake_tile(path: Path, box, base) -> bytes:
    im = Image.open(path).convert("RGBA").crop(box).resize((TILE, TILE), Image.NEAREST)
    px = im.load()
    out = bytearray()
    for y in range(TILE):
        for x in range(TILE):
            r, g, b, a = px[x, y]
            if a < 128:  # composite transparent texels onto the base colour
                r, g, b = base
            out += bytes((b, g, r, 255))  # atlas is little-endian 0x00RRGGBB → B,G,R,A
    return bytes(out)


BLOCK_TILES = 11  # the leading block-face tiles; mob tiles are appended after


def main() -> None:
    # Keep only the block tiles, then (re)append the mob tiles, so the
    # script is idempotent however many times it runs.
    raw = bytearray((ROOT / "atlas.raw").read_bytes())[: BLOCK_TILES * TILE * TILE * 4]
    for path, box, base in TILES:
        raw += bake_tile(path, box, base)
    (ROOT / "atlas.raw").write_bytes(raw)

    # The engine loads atlas.raw at runtime (no embedded hex). Drop a copy
    # next to the built binary so it is found when run from target/.
    target = ROOT / "target"
    if target.is_dir():
        (target / "atlas.raw").write_bytes(raw)

    total = len(raw) // (TILE * TILE * 4)
    print(f"baked {len(TILES)} mob tiles; atlas now {total} tiles, {len(raw)} bytes")


if __name__ == "__main__":
    main()
