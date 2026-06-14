#!/usr/bin/env python3
"""Convert a curated subset of the Enhanced Audio OGG pack into the uniform
WAV format the game's audio engine expects (44.1 kHz, mono, signed 16-bit PCM).

Output goes under the project's ``sounds/`` tree. Keep the selection focused so
the game ships only the clips it actually plays — see the MAP table below.
"""
import os
import numpy as np
import soundfile as sf

SRC = r"C:\Users\users\Downloads\Enhanced Audio r7\assets\minecraft\sounds"
DST = r"C:\Users\users\RustroverProjects\voxel-axle\sounds"
RATE = 44100

# dst-relative folder  ->  list of source ogg paths (relative to SRC), in order.
MAP = {
    # ── Footsteps, one folder per material (1..N variants) ──
    "step/grass":   ["step/grass1.ogg", "step/grass2.ogg", "step/grass3.ogg", "step/grass4.ogg", "step/grass5.ogg", "step/grass6.ogg"],
    "step/stone":   ["step/stone1.ogg", "step/stone2.ogg", "step/stone3.ogg", "step/stone4.ogg", "step/stone5.ogg", "step/stone6.ogg"],
    "step/sand":    ["step/sand1.ogg", "step/sand2.ogg", "step/sand3.ogg", "step/sand4.ogg", "step/sand5.ogg"],
    "step/gravel":  ["step/gravel1.ogg", "step/gravel2.ogg", "step/gravel3.ogg", "step/gravel4.ogg"],
    "step/snow":    ["step/snow1.ogg", "step/snow2.ogg", "step/snow3.ogg", "step/snow4.ogg"],
    "step/wood":    ["step/wood1.ogg", "step/wood2.ogg", "step/wood3.ogg", "step/wood4.ogg", "step/wood5.ogg", "step/wood6.ogg"],
    "step/foliage": ["step/cloth1.ogg", "step/cloth2.ogg", "step/cloth3.ogg", "step/cloth4.ogg"],
    # ── Block break / place, one folder per material ──
    "dig/grass":    ["dig/grass1.ogg", "dig/grass2.ogg", "dig/grass3.ogg", "dig/grass4.ogg"],
    "dig/stone":    ["dig/stone1.ogg", "dig/stone2.ogg", "dig/stone3.ogg", "dig/stone4.ogg"],
    "dig/sand":     ["dig/sand1.ogg", "dig/sand2.ogg", "dig/sand3.ogg", "dig/sand4.ogg"],
    "dig/gravel":   ["dig/gravel1.ogg", "dig/gravel2.ogg", "dig/gravel3.ogg", "dig/gravel4.ogg"],
    "dig/snow":     ["dig/snow1.ogg", "dig/snow2.ogg", "dig/snow3.ogg", "dig/snow4.ogg"],
    "dig/wood":     ["dig/wood1.ogg", "dig/wood2.ogg", "dig/wood3.ogg", "dig/wood4.ogg"],
    "dig/foliage":  ["dig/cloth1.ogg", "dig/cloth2.ogg", "dig/cloth3.ogg", "dig/cloth4.ogg"],
    "dig/glass":    ["dig/glass1.ogg", "dig/glass2.ogg", "dig/glass3.ogg", "dig/glass4.ogg"],
    # ── Mob voices + hurt ──
    "mob/chicken/say":  ["mob/chicken/say1.ogg", "mob/chicken/say2.ogg", "mob/chicken/say3.ogg"],
    "mob/chicken/hurt": ["mob/chicken/hurt1.ogg", "mob/chicken/hurt2.ogg"],
    "mob/cow/say":      ["mob/cow/say1.ogg", "mob/cow/say2.ogg", "mob/cow/say3.ogg", "mob/cow/say4.ogg"],
    "mob/cow/hurt":     ["mob/cow/hurt1.ogg", "mob/cow/hurt2.ogg", "mob/cow/hurt3.ogg"],
    "mob/sheep/say":    ["mob/sheep/say1.ogg", "mob/sheep/say2.ogg", "mob/sheep/say3.ogg"],
    # ── Player ──
    "player/hurt":  ["damage/hit1.ogg", "damage/hit2.ogg", "damage/hit3.ogg"],
    "player/splash": ["liquid/splash.ogg", "liquid/splash2.ogg"],
    # ── Ambient (underwater) ──
    "ambient/underwater": ["ambient/underwater/underwater_ambience.ogg"],
    # NOTE: the creeper's charge / blast clips (sounds/mob/creeper/*.wav) are
    # bespoke — a fuse shortened to ~2.47 s to match creeperFuseFrames — and are
    # re-encoded to this uniform format in place, NOT regenerated from the pack.
}


def to_mono16(data):
    if data.ndim > 1:
        data = data.mean(axis=1)
    # soundfile read returns float in [-1, 1]; clip then scale to int16.
    data = np.clip(data, -1.0, 1.0)
    return (data * 32767.0).astype("<i2")


def main():
    total = 0
    for folder, srcs in MAP.items():
        outdir = os.path.join(DST, folder)
        os.makedirs(outdir, exist_ok=True)
        idx = 1
        for rel in srcs:
            spath = os.path.join(SRC, rel)
            if not os.path.exists(spath):
                print("MISSING", rel)
                continue
            data, sr = sf.read(spath)
            mono = to_mono16(data)
            if sr != RATE:
                # Linear resample to the uniform device rate.
                n_out = int(round(len(mono) * RATE / sr))
                if n_out > 0:
                    xp = np.linspace(0.0, 1.0, num=len(mono), endpoint=False)
                    x = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
                    mono = np.interp(x, xp, mono.astype(np.float32)).astype("<i2")
            opath = os.path.join(outdir, f"{idx}.wav")
            sf.write(opath, mono, RATE, subtype="PCM_16", format="WAV")
            idx += 1
            total += 1
    print("converted", total, "clips")


if __name__ == "__main__":
    main()
