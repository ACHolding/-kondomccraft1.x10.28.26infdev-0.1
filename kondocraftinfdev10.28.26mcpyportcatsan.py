#!/usr/bin/env python3
"""
MrKondo's Minecraft py port 0.1
Minecraft Indev (0.31, 2009-2010) reimplementation — finite worlds,
world types, themes, the Indev house. One file, no assets.

  * import math + pygame-ce only (import pygame)
  * files = off — procedural textures + audio, zero external data
  * OST: "Sweden" by C418 (Minecraft Volume Alpha), transcribed to MIDI,
    synthesised in RAM — no audio files
  * Finite maps: Small 64 · Normal 128 · Huge 256, height 64
  * Types: Island / Flat / Inland  |  Themes: Normal / Hell / Paradise / Woods
  * Cloth blocks, hellstone, sponge, TNT, mobs, falling sand, fluids, furnaces

MrKondo 2026. Minecraft is a trademark of Mojang. Not affiliated.
"Sweden" is (c) C418 / Daniel Rosenfeld. Run: python3 "mrkondos minecraft py port 0.1 .py"
"""

from __future__ import annotations

import array
import math
import random
import sys

import pygame

TITLE = "MrKondo's Minecraft py port 0.1"
SUBTITLE = "Minecraft Indev 0.31 — finite world reimplementation"
COPYRIGHT = "(c) MrKondo 2026 — Minecraft is a Mojang trademark"

SCREEN_W, SCREEN_H = 960, 600
HALF_W, HALF_H = SCREEN_W // 2, SCREEN_H // 2
FPS = 60
FOV = 470.0
NEAR_Z = 0.15
RENDER_DIST = 30.0

WORLD_H = 64
CHUNK = 16
SIZES = [("Small", 64), ("Normal", 128), ("Huge", 256)]
THEMES = ["Normal", "Hell", "Paradise", "Woods"]
TYPES = ["Island", "Flat", "Inland"]
SEA = 22

WALK_SPEED = 4.6
SPRINT_SPEED = 7.2
FLY_SPEED = 12.0
SWIM_SPEED = 3.0
JUMP_FORCE = 7.4
GRAVITY = 22.0
MOUSE_SENS = 0.0026

AIR = 0
STONE = 1
GRASS = 2
DIRT = 3
COBBLESTONE = 4
PLANKS = 5
SAND = 6
GRAVEL = 7
WOOD = 8
LEAVES = 9
GLASS = 10
BRICK = 11
MOSSY = 12
OBSIDIAN = 13
BEDROCK = 14
WATER = 15
LAVA = 16
COAL_ORE = 17
IRON_ORE = 18
GOLD_ORE = 19
DIAMOND_ORE = 20
GOLD = 21
IRON = 22
SPONGE = 23
TNT = 24
BOOKSHELF = 25
HELLSTONE = 26
SANDSTONE = 27
CHEST = 28
SPAWNER = 29
FURNACE = 30
TORCH = 31
FLOWER = 32
ROSE = 33
MUSHROOM = 34
SAPLING = 35
SNOW = 36
CLOTH_BASE = 40
CLOTH_N = 16

BLOCK_NAMES = {
    STONE: "Stone", GRASS: "Grass Block", DIRT: "Dirt", COBBLESTONE: "Cobblestone",
    PLANKS: "Oak Planks", SAND: "Sand", GRAVEL: "Gravel", WOOD: "Oak Log",
    LEAVES: "Oak Leaves", GLASS: "Glass", BRICK: "Bricks", MOSSY: "Mossy Cobblestone",
    OBSIDIAN: "Obsidian", BEDROCK: "Bedrock", WATER: "Water", LAVA: "Lava",
    COAL_ORE: "Coal Ore", IRON_ORE: "Iron Ore", GOLD_ORE: "Gold Ore",
    DIAMOND_ORE: "Diamond Ore", GOLD: "Gold Block", IRON: "Iron Block",
    SPONGE: "Sponge", TNT: "TNT", BOOKSHELF: "Bookshelf", HELLSTONE: "Hellstone",
    SANDSTONE: "Sandstone", CHEST: "Chest", SPAWNER: "Monster Spawner",
    FURNACE: "Furnace", TORCH: "Torch", FLOWER: "Dandelion", ROSE: "Rose",
    MUSHROOM: "Mushroom", SAPLING: "Sapling", SNOW: "Snow",
}
CLOTH_NAMES = ["White", "Orange", "Magenta", "Light Blue", "Yellow", "Lime",
               "Pink", "Gray", "Light Gray", "Cyan", "Purple", "Blue",
               "Brown", "Green", "Red", "Black"]
for _i, _n in enumerate(CLOTH_NAMES):
    BLOCK_NAMES[CLOTH_BASE + _i] = _n + " Cloth"

CLOTH_RGB = [
    (234, 236, 237), (240, 118, 19), (189, 68, 179), (58, 175, 217),
    (248, 198, 39), (112, 185, 25), (237, 141, 172), (62, 68, 71),
    (142, 142, 134), (21, 137, 145), (121, 42, 172), (53, 57, 157),
    (114, 71, 40), (84, 109, 27), (161, 39, 34), (20, 21, 25),
]

BASE_COLORS = {
    STONE: ((128, 128, 130), (118, 118, 120), (100, 100, 102)),
    GRASS: ((95, 159, 53), (134, 96, 67), (110, 78, 48)),
    DIRT: ((134, 96, 67), (120, 85, 58), (100, 70, 48)),
    COBBLESTONE: ((112, 112, 114), (96, 96, 98), (78, 78, 80)),
    PLANKS: ((162, 130, 78), (140, 112, 66), (118, 94, 54)),
    SAND: ((219, 207, 163), (203, 191, 148), (182, 171, 130)),
    GRAVEL: ((136, 130, 126), (118, 112, 108), (98, 94, 90)),
    WOOD: ((102, 78, 46), (74, 56, 32), (102, 78, 46)),
    LEAVES: ((58, 110, 40), (48, 94, 32), (38, 76, 26)),
    GLASS: ((200, 225, 240), (180, 205, 220), (160, 185, 200)),
    BRICK: ((150, 84, 68), (134, 74, 60), (110, 60, 48)),
    MOSSY: ((92, 108, 80), (78, 92, 68), (62, 74, 54)),
    OBSIDIAN: ((26, 18, 42), (20, 14, 32), (14, 10, 22)),
    BEDROCK: ((60, 60, 64), (48, 48, 52), (36, 36, 40)),
    WATER: ((58, 108, 208), (50, 96, 190), (42, 82, 168)),
    LAVA: ((226, 108, 22), (204, 84, 12), (170, 52, 0)),
    COAL_ORE: ((104, 104, 108), (86, 86, 90), (68, 68, 72)),
    IRON_ORE: ((168, 146, 124), (148, 126, 106), (120, 100, 84)),
    GOLD_ORE: ((190, 168, 76), (168, 146, 62), (138, 118, 46)),
    DIAMOND_ORE: ((100, 190, 208), (80, 160, 178), (60, 130, 146)),
    GOLD: ((250, 226, 74), (226, 198, 48), (192, 164, 30)),
    IRON: ((214, 214, 222), (188, 188, 196), (158, 158, 166)),
    SPONGE: ((198, 198, 76), (176, 176, 58), (148, 148, 42)),
    TNT: ((196, 62, 62), (216, 216, 216), (172, 44, 44)),
    BOOKSHELF: ((160, 122, 74), (120, 84, 48), (100, 70, 40)),
    HELLSTONE: ((112, 54, 52), (94, 44, 44), (74, 34, 34)),
    SANDSTONE: ((216, 204, 158), (198, 186, 142), (176, 164, 124)),
    CHEST: ((168, 120, 56), (140, 96, 44), (110, 74, 32)),
    SPAWNER: ((46, 66, 76), (34, 50, 58), (24, 36, 42)),
    FURNACE: ((104, 104, 108), (86, 86, 90), (68, 68, 72)),
    TORCH: ((255, 208, 90), (130, 86, 44), (100, 66, 34)),
    FLOWER: ((250, 214, 62), (78, 150, 48), (60, 120, 36)),
    ROSE: ((216, 52, 52), (78, 150, 48), (60, 120, 36)),
    MUSHROOM: ((196, 66, 56), (176, 156, 136), (98, 78, 58)),
    SAPLING: ((64, 132, 44), (48, 104, 34), (34, 78, 24)),
    SNOW: ((246, 250, 252), (226, 232, 238), (200, 208, 216)),
}
for _i in range(CLOTH_N):
    _c = CLOTH_RGB[_i]
    BASE_COLORS[CLOTH_BASE + _i] = (
        tuple(min(255, v + 14) for v in _c), _c, tuple(max(0, v - 22) for v in _c)
    )

SOLID = set(BASE_COLORS) - {WATER, LAVA, TORCH, FLOWER, ROSE, MUSHROOM, SAPLING, GLASS}
TRANSPARENT = {WATER, LAVA, GLASS, LEAVES, TORCH, FLOWER, ROSE, MUSHROOM, SAPLING}
FLUID = {WATER, LAVA}
FALLING = {SAND, GRAVEL}
FLAMMABLE = {WOOD, LEAVES, PLANKS, BOOKSHELF, TNT, FLOWER, ROSE, SAPLING}
REPLACEABLE = {AIR, WATER, TORCH, FLOWER, ROSE, MUSHROOM, SAPLING}

CUBE_FACES = [
    (0, 1, 0, [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], 1.00, True, False),
    (0, -1, 0, [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)], 0.50, False, True),
    (0, 0, 1, [(1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 1)], 0.84, False, False),
    (0, 0, -1, [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)], 0.80, False, False),
    (1, 0, 0, [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], 0.70, False, False),
    (-1, 0, 0, [(0, 0, 1), (0, 1, 1), (0, 1, 0), (0, 0, 0)], 0.66, False, False),
]

HOTBAR = [STONE, COBBLESTONE, PLANKS, WOOD, LEAVES, SAND, GLASS, BRICK, TORCH, TNT]
CHEST_KIT = {
    STONE: 64, COBBLESTONE: 64, PLANKS: 64, WOOD: 64, LEAVES: 64, SAND: 64,
    GRAVEL: 32, GLASS: 32, BRICK: 64, MOSSY: 32, OBSIDIAN: 16, SPONGE: 16,
    TNT: 16, BOOKSHELF: 16, HELLSTONE: 32, SANDSTONE: 32, FURNACE: 4,
    TORCH: 64, FLOWER: 16, ROSE: 16, MUSHROOM: 16, SAPLING: 16, SNOW: 32,
    COAL_ORE: 32, IRON_ORE: 32, GOLD_ORE: 16, DIAMOND_ORE: 16, GOLD: 8, IRON: 8,
    WATER: 16, LAVA: 8,
}
for _i in range(CLOTH_N):
    CHEST_KIT[CLOTH_BASE + _i] = 32


def _hash(x, y, z):
    n = (x * 374761393 + y * 668265263 + z * 982451653) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0x7FFFFFFF) / 2147483647.0


class Textures:
    def __init__(self):
        self.cache = {}

    def face(self, bid, kind):
        key = (bid, kind)
        if key in self.cache:
            return self.cache[key]
        cols = BASE_COLORS.get(bid, ((128, 128, 128),) * 3)
        base = cols[0] if kind == "top" else cols[2] if kind == "bot" else cols[1]
        out = []
        for y in range(4):
            for x in range(4):
                n = _hash(x, y, bid + (0 if kind == "top" else 5 if kind == "side" else 9))
                v = 0.86 + 0.28 * n
                if bid in (STONE, COBBLESTONE, MOSSY, HELLSTONE) and n > 0.86:
                    v *= 0.72
                if bid == BRICK and (y % 2 == 0 or x % 2 == 0):
                    v = 1.18
                if bid == PLANKS and (y == 0 or x == 0):
                    v *= 0.72
                if bid == LEAVES and n < 0.3:
                    v *= 0.55
                if bid == TNT and 1 <= y <= 2:
                    out.append((216, 216, 216))
                    continue
                out.append(tuple(max(0, min(255, int(c * v))) for c in base))
        self.cache[key] = out
        return out


class Sound:
    """SFX plus a RAM-rendered transcription of 'Sweden' (C418, Volume Alpha)."""
    SR = 16000
    BPM = 72.0

    # Lead line, 16 bars, loops. (midi, beats)
    MELODY = [
        (74, 1), (78, 1), (81, 2), (81, 1), (79, 1), (78, 2),
        (78, 1), (76, 1), (74, 2), (76, 4),
        (71, 1), (74, 1), (78, 2), (78, 1), (76, 1), (74, 2),
        (76, 1), (78, 1), (76, 1), (74, 1), (74, 4),
        (74, 1), (78, 1), (81, 2), (81, 1), (79, 1), (78, 2),
        (81, 2), (79, 2), (78, 4),
        (76, 1), (74, 1), (71, 2), (74, 1), (76, 1), (78, 2),
        (74, 2), (73, 2), (74, 4),
    ]
    # D  A/C#  Bm  A  G  D/F#  Em  A
    CHORDS = [
        (50, 54, 57), (49, 52, 57), (47, 50, 54), (45, 49, 52),
        (43, 47, 50), (42, 45, 50), (40, 43, 47), (45, 49, 52),
    ]

    def __init__(self):
        self.on = True
        self.sr = self.SR
        self.music_on = True
        self.ch_music = None
        self.music = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(self.sr, -16, 1, 1024)
            self.sr = pygame.mixer.get_init()[0] or self.SR
            pygame.mixer.set_num_channels(12)
            self.ch_music = pygame.mixer.Channel(0)
        except pygame.error:
            self.on = False

        self.sfx = {}
        if self.on:
            self.sfx["dig"] = self._noise(0.09, 0.30)
            self.sfx["place"] = self._sweep(200, 330, 0.06, 0.30)
            self.sfx["step"] = self._noise(0.03, 0.12)
            self.sfx["hurt"] = self._sweep(300, 110, 0.20, 0.40)
            self.sfx["pop"] = self._sweep(700, 900, 0.03, 0.20)
            self.sfx["boom"] = self._noise(0.45, 0.55)
            self.sfx["chest"] = self._sweep(420, 560, 0.10, 0.24)
            self.music = self._sweden()
            self.start_music()

    # ------------------------------------------------------------ conversion
    def _to_sound(self, floats, vol=1.0):
        peak = max(1e-6, max(abs(v) for v in floats))
        g = 30000.0 * vol / peak
        data = array.array("h", (int(max(-32000, min(32000, v * g))) for v in floats))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _noise(self, dur, vol):
        n = max(1, int(self.sr * dur))
        amp = int(24000 * vol)
        data = array.array("h", (int(random.randint(-amp, amp) * (1 - i / n)) for i in range(n)))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _sweep(self, f0, f1, dur, vol):
        n = max(1, int(self.sr * dur))
        amp = int(26000 * vol)
        out, ph = [], 0.0
        for i in range(n):
            t = i / n
            ph += 2 * math.pi * (f0 + (f1 - f0) * t) / self.sr
            out.append(amp * (1 - t) * (1 if math.sin(ph) >= 0 else -1))
        return self._to_sound(out, 1.0)

    # ------------------------------------------------------------ the song
    @staticmethod
    def _hz(midi):
        return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))

    def _sweden(self):
        beat = 60.0 / self.BPM
        total = sum(b for _, b in self.MELODY)
        n = int(self.sr * beat * total)
        buf = [0.0] * n

        # Soft pad bed, one chord per bar
        bar = int(self.sr * beat * 4)
        for idx, chord in enumerate(self.CHORDS * 2):
            start = idx * bar
            if start >= n:
                break
            length = min(bar, n - start)
            for voice, midi in enumerate(chord):
                hz = self._hz(midi)
                det = 1.0 + (voice - 1) * 0.0016
                ph = 0.0
                for i in range(length):
                    t = i / length
                    env = min(1.0, t * 6.0) * (1.0 - max(0.0, (t - 0.75) / 0.25))
                    buf[start + i] += (math.sin(ph) + 0.16 * math.sin(ph * 2.0)) * env * 0.085
                    ph += 2.0 * math.pi * hz * det / self.sr

        # Lead — soft piano-ish, slight bell partial
        cursor = 0.0
        for midi, beats in self.MELODY:
            start = int(cursor * self.sr * beat)
            length = int(beats * self.sr * beat)
            if length > 0:
                hz = self._hz(midi)
                ph = 0.0
                ph2 = 0.0
                for i in range(length):
                    if start + i >= n:
                        break
                    t = i / length
                    env = min(1.0, t * 26.0) * (1.0 - t) ** 1.5
                    buf[start + i] += (math.sin(ph) + 0.30 * math.sin(ph2)
                                       + 0.07 * math.sin(ph * 3.01)) * env * 0.20
                    ph += 2.0 * math.pi * hz / self.sr
                    ph2 += 2.0 * math.pi * (hz * 2.004) / self.sr
            cursor += beats

        # Air
        for i in range(n):
            t = i / self.sr
            buf[i] += 0.010 * math.sin(2.0 * math.pi * 0.06 * t) * math.sin(2.0 * math.pi * 220.0 * t)

        snd = self._to_sound(buf, 0.5)
        snd.set_volume(0.42)
        return snd

    def start_music(self):
        if not self.on or not self.music or not self.ch_music:
            return
        self.music_on = True
        self.ch_music.play(self.music, loops=-1)
        self.ch_music.set_volume(0.42)

    def stop_music(self):
        self.music_on = False
        if self.ch_music:
            self.ch_music.stop()

    def toggle_music(self):
        if self.music_on:
            self.stop_music()
        else:
            self.start_music()

    def play(self, k):
        if self.on and k in self.sfx:
            self.sfx[k].play()


class Mob:
    __slots__ = ("kind", "x", "y", "z", "yaw", "timer")

    def __init__(self, kind, x, y, z):
        self.kind = kind
        self.x, self.y, self.z = float(x), float(y), float(z)
        self.yaw = random.random() * 6.28
        self.timer = random.random() * 3

    def color(self):
        return {"pig": (238, 156, 168), "sheep": (238, 238, 238),
                "creeper": (60, 176, 66)}.get(self.kind, (200, 200, 200))


class World:
    def __init__(self, name, size, theme, wtype, seed):
        self.name = name
        self.size = size
        self.theme = theme
        self.type = wtype
        self.seed = seed
        self.blocks = bytearray(size * size * WORLD_H)
        self.faces = {}
        self.mobs = []
        self.fluid_q = []
        self.fall_q = []
        self.fuse = []
        self.acc = 0.0
        self.textures = Textures()
        self.generate()

    def inside(self, x, y, z):
        return 0 <= x < self.size and 0 <= z < self.size and 0 <= y < WORLD_H

    def get(self, p):
        x, y, z = p
        if not self.inside(x, y, z):
            return AIR
        return self.blocks[(y * self.size + z) * self.size + x]

    def put(self, p, b):
        x, y, z = p
        if self.inside(x, y, z):
            self.blocks[(y * self.size + z) * self.size + x] = b

    def solid(self, p):
        return self.get(p) in SOLID

    def ckey(self, x, z):
        return (x // CHUNK, z // CHUNK)

    def nchunks(self):
        return (self.size + CHUNK - 1) // CHUNK

    # -------------------------------------------------------- generation
    def h_at(self, x, z):
        n1 = _hash(x >> 3, 0, z >> 3)
        n2 = _hash(x >> 1, 1, z >> 1)
        n3 = _hash(x, 2, z)
        return SEA + (n1 - 0.5) * 18 + (n2 - 0.5) * 7 + (n3 - 0.5) * 2.4

    def generate(self):
        rnd = random.Random(self.seed)
        n = self.size
        surf, filler, sea_block = GRASS, DIRT, WATER
        if self.theme == "Hell":
            surf, filler, sea_block = HELLSTONE, HELLSTONE, LAVA
        elif self.theme == "Woods":
            surf = GRASS

        if self.type == "FLAT":
            ground = SEA + 4
            for x in range(n):
                for z in range(n):
                    self.put((x, 0, z), BEDROCK)
                    for y in range(1, ground - 3):
                        self.put((x, y, z), STONE)
                    for y in range(ground - 3, ground):
                        self.put((x, y, z), filler)
                    self.put((x, ground, z), surf)
        elif self.type == "ISLAND":
            centres = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(max(1, n // 26))]
            for x in range(n):
                for z in range(n):
                    d = min(math.hypot(x - cx, z - cz) for cx, cz in centres)
                    if d > 12 + rnd.random() * 3:
                        continue
                    top = int(SEA + 10 - d * 1.1 + rnd.random() * 3)
                    depth = int(6 + (12 - min(12, d)) * 1.4)
                    self.put((x, 0, z), BEDROCK)
                    for y in range(max(1, top - depth), top):
                        self.put((x, y, z), STONE)
                    for y in range(max(1, top - 2), top):
                        self.put((x, y, z), filler)
                    self.put((x, top, z), surf)
        else:
            for x in range(n):
                for z in range(n):
                    h = max(1, min(WORLD_H - 6, int(self.h_at(x, z))))
                    self.put((x, 0, z), BEDROCK)
                    for y in range(1, h - 3):
                        self.put((x, y, z), STONE)
                    for y in range(max(1, h - 3), h):
                        self.put((x, y, z), filler)
                    self.put((x, h, z), surf if h >= SEA else SAND)
                    for y in range(h + 1, SEA + 1):
                        if self.get((x, y, z)) == AIR:
                            self.put((x, y, z), sea_block)

        self._ores(rnd)
        if self.theme == "Paradise":
            self._flora(rnd, 0.35)
        elif self.theme == "Woods":
            self._trees(rnd, 0.14)
        elif self.theme == "Normal":
            self._trees(rnd, 0.03)
            self._flora(rnd, 0.05)
        else:
            self._flora(rnd, 0.06)

        self._house()
        self._mobs(rnd)
        self.rebuild_all()

    def _ores(self, rnd):
        n = self.size
        for _ in range(n * n // 22):
            x, z = rnd.randrange(n), rnd.randrange(n)
            y = rnd.randrange(1, SEA + 6)
            for _ in range(rnd.randint(2, 7)):
                p = (x, y, z)
                if self.get(p) == STONE:
                    r = rnd.random()
                    self.put(p, DIAMOND_ORE if r < 0.06 else GOLD_ORE if r < 0.16
                             else IRON_ORE if r < 0.42 else COAL_ORE)
                x = max(1, min(n - 2, x + rnd.choice((-1, 0, 1))))
                z = max(1, min(n - 2, z + rnd.choice((-1, 0, 1))))
                y = max(1, min(WORLD_H - 2, y + rnd.choice((-1, 0, 1))))

    def _flora(self, rnd, density):
        n = self.size
        for _ in range(int(n * n * density)):
            x, z = rnd.randrange(1, n - 1), rnd.randrange(1, n - 1)
            for y in range(WORLD_H - 2, 0, -1):
                if self.solid((x, y, z)):
                    if self.get((x, y, z)) == GRASS and self.get((x, y + 1, z)) == AIR:
                        b = FLOWER if rnd.random() < 0.6 else ROSE if rnd.random() < 0.5 else MUSHROOM
                        self.put((x, y + 1, z), b)
                    break

    def _trees(self, rnd, density):
        n = self.size
        for _ in range(int(n * n * density)):
            x, z = rnd.randrange(2, n - 2), rnd.randrange(2, n - 2)
            for y in range(WORLD_H - 8, 0, -1):
                if self.get((x, y, z)) == GRASS:
                    self._tree(x, y + 1, z, rnd)
                    break

    def _tree(self, x, y, z, rnd):
        h = rnd.randint(4, 6)
        for i in range(h):
            self.put((x, y + i, z), WOOD)
        for dy in range(h - 3, h + 1):
            r = 2 if dy < h - 1 else 1
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if abs(dx) == r and abs(dz) == r and rnd.random() < 0.5:
                        continue
                    p = (x + dx, y + dy, z + dz)
                    if self.get(p) == AIR:
                        self.put(p, LEAVES)

    def _house(self):
        cx, cz = self.size // 2, self.size // 2
        ground = 1
        for y in range(WORLD_H - 2, 0, -1):
            if self.solid((cx, y, cz)):
                ground = y + 1
                break
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                for y in range(ground, ground + 5):
                    self.put((x, y, z), AIR)
                self.put((x, ground - 1, z), COBBLESTONE)
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                edge = abs(x - cx) == 4 or abs(z - cz) == 4
                if not edge:
                    continue
                if z == cz + 4 and abs(x - cx) <= 1:
                    continue
                for y in range(ground, ground + 4):
                    self.put((x, y, z), COBBLESTONE if (x + z + y) % 3 else PLANKS)
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                self.put((x, ground + 4, z), PLANKS)
        self.put((cx - 2, ground, cz - 2), CHEST)
        self.put((cx + 2, ground, cz - 2), FURNACE)
        self.put((cx, ground + 3, cz), TORCH)
        self.spawn = (cx + 0.5, ground + 1.0, cz + 1.5)

    def _mobs(self, rnd):
        if self.theme == "Hell":
            kinds = ["creeper"]
        elif self.theme == "Paradise":
            kinds = ["pig", "sheep"]
        else:
            kinds = ["pig", "sheep", "creeper"]
        for _ in range(self.size // 6):
            x, z = rnd.randrange(self.size), rnd.randrange(self.size)
            for y in range(WORLD_H - 2, 0, -1):
                if self.solid((x, y, z)) and self.get((x, y + 1, z)) == AIR:
                    self.mobs.append(Mob(rnd.choice(kinds), x + 0.5, y + 1, z + 0.5))
                    break

    # -------------------------------------------------------- faces
    def rebuild_chunk(self, cx, cz):
        faces = []
        x0, z0 = cx * CHUNK, cz * CHUNK
        for x in range(x0, min(x0 + CHUNK, self.size)):
            for z in range(z0, min(z0 + CHUNK, self.size)):
                for y in range(WORLD_H):
                    b = self.get((x, y, z))
                    if b == AIR:
                        continue
                    for nx, ny, nz, verts, shade, top, bot in CUBE_FACES:
                        nb = self.get((x + nx, y + ny, z + nz))
                        if nb in SOLID and nb not in TRANSPARENT:
                            continue
                        if b in FLUID and nb == b:
                            continue
                        kind = "top" if top else "bot" if bot else "side"
                        tex = self.textures.face(b, kind)
                        c = tex[((y & 1) * 2 + (x & 1)) % 16]
                        mul = shade * (0.86 if b in FLUID else 1.0)
                        if b == TORCH:
                            mul = 1.3
                        col = tuple(min(255, int(v * mul)) for v in c)
                        w = [(x + vx, y + vy, z + vz) for vx, vy, vz in verts]
                        faces.append((x + .5 + nx * .5, y + .5 + ny * .5, z + .5 + nz * .5,
                                      nx, ny, nz, w, col, b))
        self.faces[(cx, cz)] = faces

    def rebuild_all(self):
        for cx in range(self.nchunks()):
            for cz in range(self.nchunks()):
                self.rebuild_chunk(cx, cz)

    def touch(self, p):
        cx, cz = self.ckey(p[0], p[2])
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                k = (cx + dx, cz + dz)
                if k in self.faces:
                    self.rebuild_chunk(*k)

    # -------------------------------------------------------- edits
    def set(self, p, b):
        if not self.inside(*p) or p[1] <= 0:
            return False
        cur = self.get(p)
        if b == AIR:
            if cur in (AIR, BEDROCK):
                return False
            self.put(p, AIR)
            for n in ((p[0], p[1] + 1, p[2]), (p[0] + 1, p[1], p[2]), (p[0] - 1, p[1], p[2]),
                      (p[0], p[1], p[2] + 1), (p[0], p[1], p[2] - 1)):
                if self.get(n) in FLUID:
                    self.fluid_q.append(n)
            self.fall_q.append((p[0], p[1] + 1, p[2]))
        else:
            if cur not in REPLACEABLE:
                return False
            self.put(p, b)
            if b in FLUID:
                self.fluid_q.append(p)
            elif b in FALLING:
                self.fall_q.append(p)
            elif b == TNT:
                self.fuse.append([p[0], p[1], p[2], 2.6])
        self.touch(p)
        return True

    def explode(self, p, r=3.4):
        x, y, z = p
        ri = int(r) + 1
        for dx in range(-ri, ri + 1):
            for dy in range(-ri, ri + 1):
                for dz in range(-ri, ri + 1):
                    if dx * dx + dy * dy + dz * dz > r * r:
                        continue
                    q = (x + dx, y + dy, z + dz)
                    if self.get(q) in (AIR, BEDROCK):
                        continue
                    self.put(q, AIR)
        self.touch(p)

    def tick(self, dt):
        self.acc += dt
        while self.acc >= 0.12:
            self.acc -= 0.12
            self._fluids()
            self._falling()
        for item in self.fuse:
            item[3] -= dt
            if item[3] <= 0:
                q = (item[0], item[1], item[2])
                if self.get(q) == TNT:
                    self.put(q, AIR)
                    self.explode(q)
        self.fuse = [i for i in self.fuse if i[3] > 0]
        for m in self.mobs:
            m.timer -= dt
            if m.timer <= 0:
                m.timer = 1.4 + random.random() * 2
                m.yaw += (random.random() - 0.5) * 1.6
            nx = m.x + math.sin(m.yaw) * 1.4 * dt
            nz = m.z + math.cos(m.yaw) * 1.4 * dt
            if self.solid((int(nx), int(m.y), int(nz))):
                m.yaw += 1.7
            else:
                m.x, m.z = nx, nz
            if not self.solid((int(m.x), int(m.y - 0.2), int(m.z))):
                m.y = max(1.0, m.y - 6 * dt)

    def _fluids(self):
        q = self.fluid_q[:48]
        self.fluid_q = self.fluid_q[48:]
        for p in q:
            b = self.get(p)
            if b not in FLUID:
                continue
            x, y, z = p
            below = (x, y - 1, z)
            if self.get(below) in REPLACEABLE:
                self.put(below, b)
                self.fluid_q.append(below)
                self.touch(below)
                continue
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                s = (x + d[0], y, z + d[1])
                if self.get(s) == AIR:
                    self.put(s, b)
                    self.fluid_q.append(s)
                    self.touch(s)

    def _falling(self):
        q = self.fall_q[:24]
        self.fall_q = self.fall_q[24:]
        for p in q:
            b = self.get(p)
            if b not in FALLING:
                continue
            below = (p[0], p[1] - 1, p[2])
            if self.get(below) in REPLACEABLE or self.get(below) in FLUID:
                self.put(p, AIR)
                self.put(below, b)
                self.fall_q.append(below)
                self.touch(p)
                self.touch(below)


class Player:
    def __init__(self, world):
        self.radius = 0.3
        self.height = 1.75
        self.eye = 1.6
        self.hp = 20
        self.world = world
        self.reset()

    def reset(self):
        self.x, self.y, self.z = self.world.spawn
        self.vy = 0.0
        self.yaw = math.pi
        self.pitch = -0.1
        self.on_ground = False
        self.flying = False
        self.in_water = False
        self.step = 0.0

    def blocked(self, x, y, z):
        for bx in range(int(x - self.radius), int(x + self.radius) + 1):
            for bz in range(int(z - self.radius), int(z + self.radius) + 1):
                for by in range(int(y), int(y + self.height) + 1):
                    if self.world.solid((bx, by, bz)):
                        return True
        return False


MENU, CREATE, PLAY, INV, HELP, ABOUT = "menu", "create", "play", "inv", "help", "about"


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 14, bold=True)
        self.font_lg = pygame.font.SysFont("Courier", 26, bold=True)
        self.font_xl = pygame.font.SysFont("Courier", 38, bold=True)
        self.sound = Sound()
        self.state = MENU
        self.sel = 0
        self.world = None
        self.player = None
        self.inv = {}
        self.slot = 0
        self.typing = 0
        self.w_name = "New World"
        self.w_size = 0
        self.w_theme = 0
        self.w_type = 2
        self.show_debug = True
        self.paused = False
        self.swing = 0.0
        self.target = None
        self.time = 0.0
        self.grab(False)

    def grab(self, on):
        pygame.mouse.set_visible(not on)
        pygame.event.set_grab(on)
        if on:
            pygame.mouse.get_rel()

    def start(self):
        size = SIZES[self.w_size][1]
        self.world = World(self.w_name, size, THEMES[self.w_theme], TYPES[self.w_type],
                           random.randrange(1, 2 ** 40))
        self.player = Player(self.world)
        self.inv = dict(CHEST_KIT)
        self.state = PLAY
        self.paused = False
        self.grab(True)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.time += dt
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self.event(ev)
            if self.state == PLAY and not self.paused:
                self.update(dt)
            self.draw()
            pygame.display.flip()

    # -------------------------------------------------------- events
    def event(self, ev):
        if self.state == MENU:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.sel = (self.sel - 1) % 3
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel = (self.sel + 1) % 3
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.sel == 0:
                        self.state = CREATE
                        self.typing = 0
                    elif self.sel == 1:
                        self.state = HELP
                    else:
                        pygame.quit()
                        sys.exit(0)
                elif ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
        elif self.state == CREATE:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.state = MENU
                elif ev.key == pygame.K_RETURN:
                    self.start()
                elif ev.key == pygame.K_TAB:
                    self.typing = (self.typing + 1) % 4
                elif self.typing == 0:
                    if ev.key == pygame.K_BACKSPACE:
                        self.w_name = self.w_name[:-1]
                    elif ev.unicode.isprintable() and len(self.w_name) < 22:
                        self.w_name += ev.unicode
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    self.step_field(-1)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    self.step_field(1)
        elif self.state in (HELP, ABOUT):
            if ev.type == pygame.KEYDOWN:
                self.state = MENU
        elif self.state == INV:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_e, pygame.K_ESCAPE):
                    self.state = PLAY
                    self.grab(True)
        elif self.state == PLAY:
            self.play_event(ev)

    def step_field(self, d):
        if self.typing == 1:
            self.w_size = (self.w_size + d) % len(SIZES)
        elif self.typing == 2:
            self.w_theme = (self.w_theme + d) % len(THEMES)
        elif self.typing == 3:
            self.w_type = (self.w_type + d) % len(TYPES)

    def play_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if self.paused:
                    self.state = MENU
                    self.grab(False)
                else:
                    self.paused = True
                    self.grab(False)
            elif self.paused:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.paused = False
                    self.grab(True)
            elif ev.key == pygame.K_e:
                self.state = INV
                self.grab(False)
            elif ev.key == pygame.K_f:
                self.player.flying = not self.player.flying
                self.player.vy = 0.0
            elif ev.key == pygame.K_F3:
                self.show_debug = not self.show_debug
            elif ev.key == pygame.K_n:
                self.sound.toggle_music()
            elif pygame.K_1 <= ev.key <= pygame.K_9:
                self.slot = ev.key - pygame.K_1
            elif ev.key == pygame.K_0:
                self.slot = 9
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if self.paused:
                self.paused = False
                self.grab(True)
                return
            if ev.button == 4:
                self.slot = (self.slot - 1) % len(HOTBAR)
            elif ev.button == 5:
                self.slot = (self.slot + 1) % len(HOTBAR)
            elif ev.button == 1:
                self.swing = 1.0
                if self.target:
                    hit, _, _ = self.target
                    if self.world.get(hit) == CHEST:
                        self.inv.update(CHEST_KIT)
                        self.sound.play("chest")
                    else:
                        drop = self.world.get(hit)
                        if self.world.set(hit, AIR):
                            if drop not in (AIR, BEDROCK, WATER, LAVA):
                                self.inv[drop] = self.inv.get(drop, 0) + 1
                            self.sound.play("dig")
            elif ev.button == 3:
                self.swing = 1.0
                if self.target:
                    hit, place, _ = self.target
                    b = HOTBAR[self.slot]
                    if self.inv.get(b, 0) > 0 and self.world.set(place, b):
                        self.inv[b] -= 1
                        self.sound.play("place")

    # -------------------------------------------------------- update
    def update(self, dt):
        p = self.player
        w = self.world
        w.tick(dt)

        mx, my = pygame.mouse.get_rel()
        p.yaw = (p.yaw + mx * MOUSE_SENS) % 6.2832
        p.pitch = max(-1.5, min(1.5, p.pitch - my * MOUSE_SENS))

        k = pygame.key.get_pressed()
        fwd = (1.0 if k[pygame.K_w] else 0.0) - (1.0 if k[pygame.K_s] else 0.0)
        str_ = (1.0 if k[pygame.K_d] else 0.0) - (1.0 if k[pygame.K_a] else 0.0)

        p.in_water = w.get((int(p.x), int(p.y), int(p.z))) == WATER
        if p.flying:
            spd = FLY_SPEED
        elif p.in_water:
            spd = SWIM_SPEED
        elif k[pygame.K_LSHIFT] or k[pygame.K_LCTRL]:
            spd = SPRINT_SPEED
        else:
            spd = WALK_SPEED

        ln = math.hypot(fwd, str_)
        if ln:
            fwd /= ln
            str_ /= ln
        sy, cy = math.sin(p.yaw), math.cos(p.yaw)
        vx = (fwd * sy + str_ * cy) * spd
        vz = (fwd * cy - str_ * sy) * spd

        nx = p.x + vx * dt
        if not p.blocked(nx, p.y, p.z):
            p.x = nx
        nz = p.z + vz * dt
        if not p.blocked(p.x, p.y, nz):
            p.z = nz
        p.x = max(1.0, min(w.size - 2.0, p.x))
        p.z = max(1.0, min(w.size - 2.0, p.z))

        if p.flying:
            vy = 0.0
            if k[pygame.K_SPACE]:
                vy = FLY_SPEED * 0.8
            if k[pygame.K_LSHIFT]:
                vy -= FLY_SPEED * 0.8
            ny = p.y + vy * dt
            if not p.blocked(p.x, ny, p.z):
                p.y = ny
        else:
            if k[pygame.K_SPACE] and p.on_ground:
                p.vy = JUMP_FORCE
                p.on_ground = False
            if p.in_water:
                p.vy = max(-4.0, p.vy - GRAVITY * 0.3 * dt)
                p.vy *= 0.9
            else:
                p.vy = max(-30.0, p.vy - GRAVITY * dt)
            ny = p.y + p.vy * dt
            if not p.blocked(p.x, ny, p.z):
                p.y = ny
                p.on_ground = False
            else:
                p.on_ground = p.vy < 0
                p.vy = 0.0

        if p.on_ground and ln:
            p.step += dt
            if p.step > 0.4:
                p.step = 0.0
                self.sound.play("step")

        feet = (int(p.x), int(p.y), int(p.z))
        if w.get(feet) == LAVA:
            p.hp -= dt * 5
        for m in w.mobs:
            if m.kind == "creeper" and (m.x - p.x) ** 2 + (m.z - p.z) ** 2 < 2.0:
                p.hp -= dt * 3

        if p.hp <= 0 or p.y < 0:
            p.hp = 20
            p.reset()
            self.sound.play("hurt")

        if self.swing > 0:
            self.swing = max(0.0, self.swing - dt * 5)
        self.target = self.raycast()

    def raycast(self, reach=5.0):
        p = self.player
        ox, oy, oz = p.x, p.y + p.eye, p.z
        cp = math.cos(p.pitch)
        dx, dy, dz = math.sin(p.yaw) * cp, math.sin(p.pitch), math.cos(p.yaw) * cp
        prev = (int(ox), int(oy), int(oz))
        t = 0.0
        while t < reach:
            t += 0.04
            bp = (int(ox + dx * t), int(oy + dy * t), int(oz + dz * t))
            b = self.world.get(bp)
            if b not in (AIR, WATER):
                return bp, prev, b
            prev = bp
        return None

    # -------------------------------------------------------- draw
    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == CREATE:
            self.draw_create()
        elif self.state == HELP:
            self.panel("Help", [
                "WASD move  SPACE jump  F fly",
                "SHIFT sprint  E inventory  F3 debug",
                "LMB mine  RMB place  1-0 hotbar  N music",
                "Right-click a chest to refill blocks",
                "ESC pause / menu",
                "",
                "Indev has finite worlds, no day cycle,",
                "and no hunger. Size, theme and type are",
                "chosen at world creation.",
            ])
        elif self.state == INV:
            self.draw_inventory()
        elif self.state == PLAY:
            self.draw_play()
        else:
            self.panel("About", [TITLE, SUBTITLE, "", COPYRIGHT])

    def text(self, s, x, y, col, font=None):
        self.screen.blit((font or self.font).render(s, True, col), (x, y))

    def ctext(self, s, y, col, font=None):
        f = font or self.font
        surf = f.render(s, True, col)
        self.screen.blit(surf, (HALF_W - surf.get_width() // 2, y))

    def draw_menu(self):
        self.screen.fill((34, 26, 20))
        for y in range(0, SCREEN_H, 6):
            v = 30 + int(12 * math.sin(y * 0.05 + self.time))
            pygame.draw.rect(self.screen, (v + 22, v + 12, v), (0, y, SCREEN_W, 6))
        self.ctext("MrKondo's", 70, (255, 232, 120), self.font_xl)
        self.ctext("MINECRAFT py port 0.1", 118, (250, 250, 250), self.font_lg)
        self.ctext("Indev 0.31 · finite worlds", 152, (150, 230, 140))
        for i, label in enumerate(["Create World", "Help", "Quit"]):
            col = (255, 255, 130) if i == self.sel else (215, 215, 215)
            self.ctext(("> " if i == self.sel else "  ") + label, 210 + i * 40, col, self.font_lg)
        self.ctext("Up/Down · Enter", 380, (170, 170, 170))
        self.ctext('OST: "Sweden" — C418 (RAM synth)', 410, (150, 200, 150))
        self.ctext(COPYRIGHT, SCREEN_H - 28, (140, 140, 140))

    def draw_create(self):
        self.screen.fill((28, 22, 18))
        self.ctext("NEW WORLD", 46, (255, 230, 120), self.font_lg)
        rows = [
            ("World name", self.w_name + ("_" if self.typing == 0 and int(self.time * 2) % 2 else "")),
            ("Size", "< %s >" % SIZES[self.w_size][0]),
            ("Theme", "< %s >" % THEMES[self.w_theme]),
            ("Type", "< %s >" % TYPES[self.w_type]),
        ]
        for i, (label, val) in enumerate(rows):
            y = 120 + i * 52
            sel = i == self.typing
            if sel:
                pygame.draw.rect(self.screen, (70, 62, 40), (140, y - 8, SCREEN_W - 280, 40))
            self.text(label, 160, y, (200, 200, 200))
            self.text(val, 360, y, (255, 255, 140) if sel else (235, 235, 235), self.font_lg)
        self.ctext("Tab field · Left/Right change · Enter generate", 360, (180, 180, 180))
        self.ctext("Small is fastest. Huge is 256 x 256.", 384, (150, 150, 150))
        self.ctext("Esc back", 420, (200, 160, 160))

    def panel(self, title, lines):
        self.screen.fill((26, 22, 18))
        self.ctext(title, 40, (255, 230, 120), self.font_lg)
        for i, line in enumerate(lines):
            self.text(line, 90, 100 + i * 22, (225, 225, 225))
        self.ctext("Press any key", SCREEN_H - 40, (180, 180, 180))

    def draw_inventory(self):
        self.screen.fill((26, 22, 18))
        self.ctext("Inventory", 30, (255, 230, 120), self.font_lg)
        items = sorted(self.inv)
        cols = 9
        for i, b in enumerate(items):
            x = 70 + (i % cols) * 92
            y = 90 + (i // cols) * 74
            top, side, _ = BASE_COLORS[b]
            pygame.draw.rect(self.screen, side, (x, y + 16, 60, 30))
            pygame.draw.rect(self.screen, top, (x, y, 60, 16))
            pygame.draw.rect(self.screen, (140, 140, 140), (x, y, 60, 46), 1)
            self.text(str(self.inv[b]), x + 4, y + 30, (255, 255, 255))
            self.text(BLOCK_NAMES.get(b, "?"), x, y + 50, (200, 200, 200))
        self.ctext("E to close", SCREEN_H - 30, (180, 180, 180))

    def draw_play(self):
        sky = (128, 178, 240)
        if self.world.theme == "Hell":
            sky = (52, 26, 26)
        elif self.world.theme == "Paradise":
            sky = (156, 214, 255)
        elif self.world.theme == "Woods":
            sky = (86, 122, 96)
        self.screen.fill(sky)

        p = self.player
        cx, cy, cz = p.x, p.y + p.eye, p.z
        sy, cyaw = math.sin(p.yaw), math.cos(p.yaw)
        sp, cp = math.sin(p.pitch), math.cos(p.pitch)
        tgt = self.target[0] if self.target else None
        lim = RENDER_DIST ** 2
        queue = []

        for key, faces in self.world.faces.items():
            for fx, fy, fz, nx, ny, nz, verts, col, b in faces:
                dx, dy, dz = fx - cx, fy - cy, fz - cz
                d = dx * dx + dy * dy + dz * dz
                if d > lim or dx * nx + dy * ny + dz * nz >= 0:
                    continue
                pts = self.project(verts, cx, cy, cz, sy, cyaw, sp, cp)
                if not pts:
                    continue
                fog = min(1.0, d / lim) ** 1.5
                c = tuple(int(col[i] * (1 - fog) + sky[i] * fog) for i in range(3))
                queue.append((d, pts, c, (fx - 0.5, fy - 0.5, fz - 0.5) == tgt, b))

        for m in self.world.mobs:
            dx, dy, dz = m.x - cx, m.y - cy, m.z - cz
            d = dx * dx + dy * dy + dz * dz
            if d > lim:
                continue
            for nx, ny, nz, verts, shade, _, _ in CUBE_FACES:
                if dx * nx + dy * ny + dz * nz >= 0:
                    continue
                w = [(m.x - .35 + vx * .7, m.y + vy * .85, m.z - .35 + vz * .7)
                     for vx, vy, vz in verts]
                pts = self.project(w, cx, cy, cz, sy, cyaw, sp, cp)
                if pts:
                    col = tuple(min(255, int(v * shade)) for v in m.color())
                    queue.append((d, pts, col, False, 0))

        queue.sort(key=lambda i: i[0], reverse=True)
        for _, pts, col, hot, b in queue:
            pygame.draw.polygon(self.screen, col, pts)
            if hot:
                pygame.draw.polygon(self.screen, (255, 255, 255), pts, 2)

        if p.in_water:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((30, 70, 150, 80))
            self.screen.blit(ov, (0, 0))

        self.draw_hand()
        self.draw_hud()

    def project(self, verts, cx, cy, cz, sy, cyaw, sp, cp):
        cam = []
        for vx, vy, vz in verts:
            rx, ry, rz = vx - cx, vy - cy, vz - cz
            tx = rx * cyaw - rz * sy
            tz = rx * sy + rz * cyaw
            ty = ry * cp - tz * sp
            cam.append((tx, ty, ry * sp + tz * cp))
        clip = []
        for i in range(len(cam)):
            a, b = cam[i], cam[(i + 1) % len(cam)]
            ia, ib = a[2] >= NEAR_Z, b[2] >= NEAR_Z
            if ia and ib:
                clip.append(b)
            elif ia != ib:
                t = (NEAR_Z - a[2]) / (b[2] - a[2] + 1e-9)
                clip.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), NEAR_Z))
                if ib:
                    clip.append(b)
        if len(clip) < 3:
            return None
        out, on = [], False
        for tx, ty, tz in clip:
            s = FOV / tz
            sx, sy2 = int(HALF_W + tx * s), int(HALF_H - ty * s)
            on = on or (0 <= sx < SCREEN_W and 0 <= sy2 < SCREEN_H)
            out.append((sx, sy2))
        return out if on else None

    def draw_hand(self):
        b = HOTBAR[self.slot]
        top, side, _ = BASE_COLORS[b]
        bob = math.sin(self.player.step * 12) * 5 if self.player.on_ground else 0
        sw = math.sin(self.swing * math.pi) * 40
        hx, hy = int(SCREEN_W - 140 - sw), int(SCREEN_H - 90 + bob + sw * 0.4)
        pygame.draw.polygon(self.screen, top, [(hx, hy - 30), (hx + 44, hy - 14), (hx, hy), (hx - 44, hy - 14)])
        pygame.draw.polygon(self.screen, side, [(hx - 44, hy - 14), (hx, hy), (hx, hy + 50), (hx - 44, hy + 34)])
        pygame.draw.polygon(self.screen, tuple(int(v * .8) for v in side),
                            [(hx, hy), (hx + 44, hy - 14), (hx + 44, hy + 34), (hx, hy + 50)])

    def draw_hud(self):
        pygame.draw.line(self.screen, (255, 255, 255), (HALF_W - 7, HALF_H), (HALF_W + 7, HALF_H), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (HALF_W, HALF_H - 7), (HALF_W, HALF_H + 7), 2)
        w = 40
        x0 = HALF_W - len(HOTBAR) * w // 2
        for i, b in enumerate(HOTBAR):
            x = x0 + i * w
            top, side, _ = BASE_COLORS[b]
            pygame.draw.rect(self.screen, (28, 28, 32), (x, SCREEN_H - 50, w - 4, w - 4))
            pygame.draw.rect(self.screen, top, (x + 7, SCREEN_H - 43, 22, 9))
            pygame.draw.rect(self.screen, side, (x + 7, SCREEN_H - 34, 22, 12))
            pygame.draw.rect(self.screen, (255, 255, 90) if i == self.slot else (130, 130, 140),
                             (x, SCREEN_H - 50, w - 4, w - 4), 3 if i == self.slot else 1)
            self.text(str((i + 1) % 10), x + 3, SCREEN_H - 49, (255, 255, 255))
        self.ctext(BLOCK_NAMES.get(HOTBAR[self.slot], "?"), SCREEN_H - 70, (255, 255, 160))
        for i in range(10):
            hx, hy = 12 + i * 17, SCREEN_H - 74
            pygame.draw.polygon(self.screen, (210, 40, 40) if i < self.player.hp / 2 else (70, 30, 30),
                                [(hx + 7, hy + 3), (hx + 13, hy + 8), (hx + 7, hy + 13), (hx + 1, hy + 8)])
        if self.show_debug:
            p = self.player
            lines = [
                TITLE,
                "FPS %5.1f | %s | %s | %s" % (self.clock.get_fps(), self.world.theme,
                                              self.world.type, self.world.size),
                "XYZ %.1f / %.1f / %.1f | mobs %d | OST %s" % (
                    p.x, p.y, p.z, len(self.world.mobs), "ON" if self.sound.music_on else "OFF"),
                "WASD SPACE F fly SHIFT sprint E inv N music F3 debug",
            ]
            for i, s in enumerate(lines):
                self.text(s, 11, 9 + i * 17, (0, 0, 0))
                self.text(s, 10, 8 + i * 17, (90, 255, 130) if i == 0 else (240, 240, 240))
        if self.paused:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            self.screen.blit(ov, (0, 0))
            self.ctext("PAUSED", HALF_H - 40, (255, 240, 120), self.font_lg)
            self.ctext("Enter resume · ESC menu", HALF_H + 10, (210, 210, 210))


def main():
    print(TITLE)
    print(SUBTITLE)
    print(COPYRIGHT)
    print('OST: "Sweden" (C418) transcribed to MIDI, synthesised in RAM')
    Game().run()


if __name__ == "__main__":
    main()
