from constants import *

CHARACTERS = [
    {"name": "Brawler", "color": RED,    "speed": 4, "jump": -14,
     "punch_dmg": 12, "kick_dmg": 18, "max_hp": 130, "block": 6,
     "desc": "Tanky heavy hitter",   "double_jump": False},
    {"name": "Ninja",   "color": CYAN,   "speed": 7, "jump": -16,
     "punch_dmg":  7, "kick_dmg": 10, "max_hp":  90, "block": 8,
     "desc": "Fast & double jump",   "double_jump": True},
    {"name": "Boxer",   "color": GREEN,  "speed": 5, "jump": -13,
     "punch_dmg": 16, "kick_dmg":  8, "max_hp": 110, "block": 9,
     "desc": "Devastating punches",  "double_jump": False},
    {"name": "Phantom", "color": PURPLE, "speed": 6, "jump": -15,
     "punch_dmg": 10, "kick_dmg": 14, "max_hp": 100, "block": 7,
     "desc": "Balanced & evasive",   "double_jump": True},
    {"name": "Ares",    "color": ORANGE, "speed": 5,  "jump": -14,
     "punch_dmg": 21, "kick_dmg": 20, "max_hp": 90, "block": 3,
     "desc": "God of War",           "double_jump": False},
    {"name": "Zephyr",  "color": BLUE,  "speed": 9,  "jump": -18,
     "punch_dmg": 10, "kick_dmg": 14, "max_hp": 100, "block": 7,
     "desc": "Swift and agile",      "double_jump": True},
    {"name": "Titan",  "color": YELLOW,  "speed": 3,  "jump": -7,
     "punch_dmg": 18, "kick_dmg": 16, "max_hp": 155, "block": 3,
     "desc": "Enormous Health",      "double_jump": False},
    {"name": "Dancing Man",    "color": (100, 100, 255), "speed": 10,  "jump": -20,
     "punch_dmg": 10, "kick_dmg": 10, "max_hp": 100, "block": 6,
     "desc": "evasive",    "double_jump": True},
    {"name": "Tank",   "color": (30, 30, 30), "speed": 1,  "jump": -0,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 190, "block": 9,
     "desc": "Defensive",   "double_jump": False},
    {"name": "Mighty Medieval Man",  "color": GRAY, "speed": 4,  "jump": -18,
     "punch_dmg": 15, "kick_dmg": 15, "max_hp": 120, "block": 8,
     "desc": "Lord of chivalry",   "double_jump": False},
    {"name": "Samurai",   "color": BLACK, "speed": 6,  "jump": -15,
     "punch_dmg": 12, "kick_dmg": 19, "max_hp": 170, "block": 7,
     "desc": "Katana Master",   "double_jump": True},
    {"name": "Skeleton",   "color": WHITE,   "speed": 3, "jump": -5,
     "punch_dmg":  25, "kick_dmg": 20, "max_hp":  65, "block": 2,
     "desc": "Dead",   "double_jump": False},
    {"name": "Unknown",   "color": (100, 160, 220),   "speed": 5,  "jump": -5,
     "punch_dmg":  3, "kick_dmg": 5, "max_hp":  300, "block": 5,
     "desc": "Mysterious and powerful",   "double_jump": True},
    {"name": "Hardy", "color": (110, 120, 225), "speed": 3, "jump": -5,
     "punch_dmg": 3, "kick_dmg": 4, "max_hp": 65, "block": 2,
     "desc": "Pros should try him",   "double_jump": False},
    {"name": "Rogue", "color": (220, 180, 60), "speed": 8, "jump": -17,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 80, "block": 6,
     "desc": "Stealthy and agile",   "double_jump": True},
    {"name": "Gladiator", "color": (200, 80, 80), "speed": 4, "jump": -12,
     "punch_dmg": 14, "kick_dmg": 18, "max_hp": 140, "block": 7,
     "desc": "Arena Champion",   "double_jump": False},
    {"name": "Oni", "color": (80, 220, 200), "speed": 2, "jump": -1,
     "punch_dmg": 12, "kick_dmg": 14, "max_hp": 200, "block": 3,
     "desc": "Fat Demon",   "double_jump": False},
    {"name": "Cecalia",     "color": (50, 255, 255), "speed": 8,  "jump": -8,
     "punch_dmg": 8,  "kick_dmg": 8,  "max_hp": 300, "block": 4,
     "desc": "Octo hard",        "double_jump": False},
    {"name": "Acrobat",     "color": (255, 180, 80), "speed": 8,  "jump": -20,
     "punch_dmg": 8,  "kick_dmg": 12, "max_hp": 85, "block": 6,
     "desc": "Aerial specialist", "double_jump": True},
    {"name": "Shapeshifter", "color": (180, 80, 255), "speed": 6, "jump": -15,
     "punch_dmg": 14, "kick_dmg": 14, "max_hp": 105, "block": 5,
     "desc": "Unpredictable",    "double_jump": True},
    {"name": "Spring",   "color": (255, 100, 100), "speed": 10, "jump": -45,
     "punch_dmg": 1, "kick_dmg": 1, "max_hp": 400, "block": 1,
     "desc": "Bouncy",   "double_jump": True},
    {"name": "Harpy",   "color": (150, 0, 150), "speed": 9, "jump": -19,
     "punch_dmg": 20, "kick_dmg": 20, "max_hp": 40, "block": 3,
     "desc": "Blood-eater",   "double_jump": True},
    {"name": "Scarecrow",   "color": (50, 0, 50), "speed": 1, "jump": -0,
     "punch_dmg": 100, "kick_dmg": 100, "max_hp": 60, "block": 1,
     "desc": "Strong and Weak",   "double_jump": False},
    {"name": "Cactus", "color": (40, 180, 60), "speed": 4, "jump": -11,
     "punch_dmg": 4, "kick_dmg": 4, "max_hp": 135, "block": 4,
     "desc": "Poisons on contact", "double_jump": False, "contact_dmg": 8},
    {"name": "Medic", "color": (200, 255, 200), "speed": 5, "jump": -13,
     "punch_dmg": 7, "kick_dmg": 9, "max_hp": 120, "block": 6,
     "desc": "+2 HP every 5 seconds", "double_jump": False, "regen": True},
    {"name": "Arsonist", "color": (255, 80, 20), "speed": 6, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 8, "max_hp": 100, "block": 4,
     "desc": "Punches set targets on fire", "double_jump": False, "fire_punch": True},
    {"name": "Cryogenisist", "color": (150, 220, 255), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 0, "max_hp": 110, "block": 6,
     "desc": "Kicks freeze opponents for 3s", "double_jump": False, "freeze_kick": True},
    {"name": "Magician", "color": (180, 80, 255), "speed": 5, "jump": -13,
     "punch_dmg": 8, "kick_dmg": 10, "max_hp": 105, "block": 7,
     "desc": "Powerups drift toward him", "double_jump": True, "magnet": True},
    {"name": "Charger", "color": (255, 220, 0), "speed": 5, "jump": -13,
     "punch_dmg": 7, "kick_dmg": 9, "max_hp": 115, "block": 5,
     "desc": "Punches shock: halves speed for 8 sec", "double_jump": False, "shock_punch": True},
    {"name": "Psychopath", "color": (180, 0, 180), "speed": 6, "jump": -14,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 100, "block": 2,
     "desc": "Kick teleports to random spot", "double_jump": False, "teleport_kick": True},
    {"name": "Ran-Doom", "color": (128, 128, 128), "speed": 5, "jump": -13,
     "punch_dmg": 10, "kick_dmg": 10, "max_hp": 110, "block": 5,
     "desc": "All stats randomized each match", "double_jump": False, "random_stats": True},
    {"name": "Outbacker", "color": (200, 130, 50), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 7, "max_hp": 115, "block": 5,
     "desc": "Kick throws orbiting boomerang", "double_jump": False, "boomerang_kick": True},
    {"name": "Gunner", "color": (60, 180, 80), "speed": 5, "jump": -13,
     "punch_dmg": 8, "kick_dmg": 0, "max_hp": 110, "block": 4,
     "desc": "Kicks shoot a ball (10 dmg)", "double_jump": False, "shoot_kick": True},
    {"name": "Bazooka Man", "color": (180, 60, 60), "speed": 1, "jump": -0,
     "punch_dmg": 8, "kick_dmg": 0, "max_hp": 75, "block": 1,
     "desc": "Kick fires exploding orb (35 dmg)", "double_jump": False, "bazooka_kick": True},
    {"name": "Pinball", "color": (255, 80, 200), "speed": 5, "jump": -13,
     "punch_dmg": 8, "kick_dmg": 0, "max_hp": 110, "block": 5,
     "desc": "Kick shoots a bouncing ball (10 dmg)", "double_jump": False, "bounce_kick": True},
    {"name": "Giant", "color": (100, 160, 100), "speed": 2, "jump": -8,
     "punch_dmg": 20, "kick_dmg": 18, "max_hp": 260, "block": 4,
     "desc": "Very big and very strong", "double_jump": False, "giant": True},
    {"name": "Morph", "color": (80, 200, 220), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 110, "block": 5,
     "desc": "Kick cycles size: normal → big → small", "double_jump": False, "size_kick": True},
    {"name": "Ghost", "color": (210, 210, 255), "speed": 5, "jump": -15,
     "punch_dmg": 8, "kick_dmg": 9, "max_hp": 105, "block": 8,
     "desc": "Phases through platforms", "double_jump": True, "phase": True},
    {"name": "Vampire", "color": (120, 0, 40), "speed": 6, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 90, "block": 5,
     "desc": "Heals 8 HP on every hit", "double_jump": False, "vampire": True},
    {"name": "Astronaut", "color": (220, 230, 255), "speed": 5, "jump": -10,
     "punch_dmg": 8, "kick_dmg": 9, "max_hp": 105, "block": 5,
     "desc": "Anti-gravity on every map", "double_jump": True, "anti_gravity": True},
    {"name": "Spooderman", "color": (180, 20, 20), "speed": 7, "jump": -16,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 100, "block": 7,
     "desc": "Clings to walls, wall-jumps", "double_jump": True, "wall_cling": True},
    {"name": "Hooker", "color": (40, 160, 60), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 0, "max_hp": 110, "block": 5,
     "desc": "Kick fires a snake grappling hook", "double_jump": False, "grapple_kick": True},
    {"name": "Mouse", "color": (200, 180, 160), "speed": 9, "jump": -17,
     "punch_dmg": 6, "kick_dmg": 8, "max_hp": 65, "block": 8,
     "desc": "Tiny and very hard to hit", "double_jump": True, "tiny": True},
    {"name": "Sumo", "color": (255, 200, 100), "speed": 1, "jump": -2,
     "punch_dmg": 1, "kick_dmg": 1, "max_hp": 600, "block": 10,
     "desc": "Enormous health, barely moves", "double_jump": False},
    {"name": "Headless Horseman", "color": (80, 40, 15), "speed": 7, "jump": -11,
     "punch_dmg": 13, "kick_dmg": 0, "max_hp": 145, "block": 5,
     "desc": "Kicks throw a physics pumpkin that explodes", "double_jump": False, "pumpkin_kick": True},
    {"name": "Ink Brush", "color": (20, 20, 40), "speed": 6, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 110, "block": 6,
     "desc": "Kick spawns a moving clone that distracts enemies", "double_jump": True, "ink_kick": True},
    {"name": "Hammerhead", "color": (80, 55, 30), "speed": 3, "jump": -11,
     "punch_dmg": 22, "kick_dmg": 6, "max_hp": 135, "block": 5,
     "desc": "Hammer punch squishes opponents flat for 4 seconds", "double_jump": False, "hammer_punch": True},
    {"name": "Viking", "color": (180, 130, 60), "speed": 4, "jump": -13,
     "punch_dmg": 15, "kick_dmg": 13, "max_hp": 145, "block": 5,
     "desc": "Goes berserk below 50% HP: speed & damage x1.5", "double_jump": False, "berserker": True},
    {"name": "Wizard", "color": (100, 60, 200), "speed": 5, "jump": -14,
     "punch_dmg": 11, "kick_dmg": 8, "max_hp": 95, "block": 6,
     "desc": "Punch fires a bouncing magic orb", "double_jump": True, "bounce_punch": True},
    {"name": "Wrestler", "color": (220, 100, 40), "speed": 3, "jump": -10,
     "punch_dmg": 12, "kick_dmg": 8, "max_hp": 155, "block": 6,
     "desc": "Kick sends opponents flying across the arena", "double_jump": False, "slam_kick": True},
    {"name": "Clown", "color": (255, 60, 120), "speed": 7, "jump": -15,
     "punch_dmg": 8, "kick_dmg": 10, "max_hp": 100, "block": 4,
     "desc": "Kick reverses opponent controls for 3 seconds", "double_jump": True, "confuse_kick": True},
    {"name": "Speedster", "color": (255, 200, 0), "speed": 13, "jump": -17,
     "punch_dmg": 7, "kick_dmg": 9, "max_hp": 85, "block": 5,
     "desc": "Blazing fast with a speed trail", "double_jump": True, "speedster": True},
    {"name": "Knight", "color": (160, 160, 180), "speed": 3, "jump": -11,
     "punch_dmg": 17, "kick_dmg": 15, "max_hp": 150, "block": 12,
     "desc": "Heavily armored — massive block rating", "double_jump": False},
    {"name": "Lava Man",   "color": (230, 80, 20),   "speed": 4, "jump": -13,
     "punch_dmg": 11, "kick_dmg": 9,  "max_hp": 115, "block": 4,
     "desc": "Burns on contact; punches ignite foes", "double_jump": False,
     "fire_punch": True, "contact_dmg": 10},
    {"name": "Angel",      "color": (255, 250, 210),  "speed": 6, "jump": -18,
     "punch_dmg": 8,  "kick_dmg": 10, "max_hp": 90,  "block": 6,
     "desc": "Slow fall — glides gracefully in the air", "double_jump": True, "slow_fall": True},
    {"name": "Mime",       "color": (240, 240, 240),  "speed": 6, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 8,  "max_hp": 100, "block": 7,
     "desc": "Landing a punch turns Mime invisible for 2s", "double_jump": False, "stealth_punch": True},
    {"name": "Lumberjack", "color": (160, 80, 30),    "speed": 4, "jump": -12,
     "punch_dmg": 14, "kick_dmg": 11, "max_hp": 140, "block": 5,
     "desc": "Axe swing hits at double reach", "double_jump": False, "wide_punch": True},
    {"name": "Bouncer",    "color": (80, 200, 80),    "speed": 4, "jump": -12,
     "punch_dmg": 10, "kick_dmg": 12, "max_hp": 130, "block": 8,
     "desc": "Reflects 50% damage back when blocking", "double_jump": False, "reflect_block": True},
    {"name": "Demon",      "color": (160, 20, 20),    "speed": 7, "jump": -15,
     "punch_dmg": 16, "kick_dmg": 14, "max_hp": 110, "block": 4,
     "desc": "Dark and powerful demon warrior", "double_jump": True},
    {"name": "Dark Mage",  "color": (60, 20, 100),    "speed": 5, "jump": -14,
     "punch_dmg": 10, "kick_dmg": 8,  "max_hp": 100, "block": 6,
     "desc": "Magic orb punch + freeze kick combo", "double_jump": True,
     "bounce_punch": True, "freeze_kick": True},
    {"name": "Pirate",     "color": (80, 55, 30),     "speed": 4, "jump": -12,
     "punch_dmg": 10, "kick_dmg": 0,  "max_hp": 120, "block": 5,
     "desc": "Fires an explosive cannonball on kick (35 dmg)", "double_jump": False, "bazooka_kick": True},
    {"name": "Impossible", "color": CYAN,    "speed": 10, "jump": -16,
     "punch_dmg": 1, "kick_dmg": 1, "max_hp": 1, "block": 1,
     "desc": "gods at this game should try him",   "double_jump": True},
    {"name": "Laser Eyes", "color": (255, 60, 0), "speed": 5, "jump": -13,
     "punch_dmg": 9, "kick_dmg": 10, "max_hp": 105, "block": 5,
     "desc": "Every 10s fires a laser beam for 2s", "double_jump": False, "laser_eyes": True},
]

POWERUPS = [
    # --- existing ---
    {'name': 'Swiftness',     'type': 'speed',     'mult': 1.6,  'duration': 360, 'color': (80, 200, 250)},
    {'name': 'Rage',      'type': 'kick_dmg',  'amount': 10, 'duration': 500, 'color': (240,120,  40)},
    {'name': 'Drugs',     'type': 'punch_dmg', 'amount': 10, 'duration': 540, 'color': (180,240, 180)},
    {'name': 'Heal',      'type': 'heal',       'amount': 30, 'duration': 0,   'color': (200,255, 120)},
    {'name': 'Poison',    'type': 'heal',       'amount':-30, 'duration': 0,   'color': (200,160, 255)},
    # --- new ---
    {'name': 'Turbo',     'type': 'speed',     'mult': 2.4,  'duration': 180, 'color': (255,230,   0)},
    {'name': 'Forcefield',    'type': 'shield',    'reduction': 0.5, 'duration': 360, 'color': (100,150, 255)},
    {'name': 'Leech',     'type': 'leech',     'amount':  8, 'duration': 360, 'color': (200,  0, 200)},
    {'name': 'MegaHeal',  'type': 'heal',      'amount': 60, 'duration': 0,   'color': (0,   220,  80)},
    {'name': 'Killer',      'type': 'heal',      'amount':-60, 'duration': 0,   'color': (255,  60,   0)},
    {'name': 'Wither',      'type': 'speed',     'amount':  -2, 'duration': 420, 'color': (255,  0,  0)},
    {'name': '2x Trouble',  'type': 'clone',     'duration': 0,                  'color': (255, 80, 200)},
    {'name': 'Cleanse',       'type': 'cleanse',       'duration': 0,        'color': (205, 205, 155)},
    {'name': 'Bubble Shield', 'type': 'bubble_shield', 'duration': FPS * 10, 'color': (100, 200, 255)},
]

STAGES = [
    # Grasslands
    {"name": "Grasslands", "platforms": [
        (60,  GROUND_Y-90,  200, 0,   0),
        (640, GROUND_Y-140, 140, 0,   0),
        (310, GROUND_Y-215, 210, 1.5, 140),
    ], "springs": [
        (310, -22), (620, -22),
    ], "conveyors": [
        (50,  GROUND_Y, 180, 2.5),
        (650, GROUND_Y, 180, -2.5),
    ], "portals": [(160, GROUND_Y-160), (700, GROUND_Y-160)]},
    # Volcano
    {"name": "Volcano", "platforms": [
        (70,  GROUND_Y-120, 130, 2,   80),
        (630, GROUND_Y-150, 120, -2,  70),
        (395, GROUND_Y-240, 100, 0,   0),
    ], "springs": [
        (450, -30),
    ], "conveyors": [
        (80,  GROUND_Y, 200, 3.5),
        (600, GROUND_Y, 200, -3.5),
    ], "portals": [(140, GROUND_Y-180), (710, GROUND_Y-180)]},
    # Dojo
    {"name": "Dojo", "platforms": [
        (50,  GROUND_Y-115, 155, 0,   0),
        (695, GROUND_Y-115, 155, 0,   0),
        (355, GROUND_Y-205, 145, 2.5, 100),
    ], "springs": [
        (230, -22), (670, -22),
    ], "conveyors": [
        (200, GROUND_Y, 200, -2.0),
        (500, GROUND_Y, 200,  2.0),
    ], "portals": [(130, GROUND_Y-170), (730, GROUND_Y-170)]},
    # Desert
    {"name": "Desert", "platforms": [
        (80,  GROUND_Y-75,  220, 0,   0),
        (590, GROUND_Y-110, 190, 0,   0),
        (330, GROUND_Y-185, 180, 1,   160),
    ], "springs": [
        (180, -20), (450, -20), (720, -20),
    ], "conveyors": [
        (50,  GROUND_Y, 260, 1.8),
        (570, GROUND_Y, 260, -1.8),
    ], "portals": [(150, GROUND_Y-140), (700, GROUND_Y-140)]},
    # Arena
    {"name": "Arena", "platforms": [
        (80,  GROUND_Y-110, 140, 2,   120),
        (620, GROUND_Y-110, 140, -2,  120),
        (350, GROUND_Y-210, 160, 3,   160),
    ], "springs": [
        (250, -24), (640, -24),
    ], "conveyors": [
        (50,  GROUND_Y, 350, 3.0),
        (500, GROUND_Y, 350, -3.0),
    ], "portals": [(160, GROUND_Y-175), (690, GROUND_Y-175)]},
    # Dream Land
    {"name": "Dream Land", "platforms": [
        (55,  GROUND_Y-95,  175, 0,   0),
        (670, GROUND_Y-95,  175, 0,   0),
        (195, GROUND_Y-190, 155, 0,   0),
        (550, GROUND_Y-190, 155, 0,   0),
    ], "springs": [
        (80,  -22), (235, -22), (390, -22),
        (530, -22), (680, -22), (820, -22),
    ], "conveyors": [
        (60,  GROUND_Y, 160, 1.5),
        (680, GROUND_Y, 160, -1.5),
    ], "portals": [(120, GROUND_Y-150), (740, GROUND_Y-150)]},
    # Underworld
    {"name": "Underworld", "platforms": [
        (55,  GROUND_Y-105, 165, 0,   0),
        (680, GROUND_Y-105, 165, 0,   0),
        (270, GROUND_Y-175, 135, 1.5, 110),
        (495, GROUND_Y-175, 135, -1.5,110),
    ], "springs": [
        (200, -22), (450, -22), (700, -22),
    ], "conveyors": [
        (50,  GROUND_Y, 220, -2.5),
        (620, GROUND_Y, 220,  2.5),
    ], "portals": [(170, GROUND_Y-165), (690, GROUND_Y-165)]},
    # Space
    {"name": "Space", "platforms": [
        (80,  GROUND_Y-120, 150, 1.5, 110),
        (630, GROUND_Y-120, 150, -1.5,110),
        (355, GROUND_Y-230, 130, 2.5, 100),
    ], "springs": [
        (280, -26), (620, -26),
    ], "conveyors": [
        (60,  GROUND_Y, 200, 2.0),
        (640, GROUND_Y, 200, -2.0),
    ], "portals": [(155, GROUND_Y-190), (710, GROUND_Y-190)]},
    # Jungle
    {"name": "Jungle", "platforms": [
        (55,  GROUND_Y-110, 175, 0,   0),
        (670, GROUND_Y-110, 175, 0,   0),
        (340, GROUND_Y-210, 150, 1.2, 120),
    ], "springs": [
        (450, -22),
    ], "conveyors": [
        (50,  GROUND_Y, 240, 2.2),
        (600, GROUND_Y, 240, -2.2),
    ], "portals": [(140, GROUND_Y-160), (720, GROUND_Y-160)]},
    # Computer
    {"name": "Computer", "platforms": [
        (60,  GROUND_Y-105, 160, 0,   0),
        (680, GROUND_Y-105, 160, 0,   0),
        (330, GROUND_Y-200, 140, 1.5, 120),
    ], "springs": [], "conveyors": [
        (50,  GROUND_Y, 200, 2.8),
        (640, GROUND_Y, 200, -2.8),
    ], "portals": [(160, GROUND_Y-170), (700, GROUND_Y-170)]},
    # Ice Cave
    {"name": "Ice Cave", "platforms": [
        (50,  GROUND_Y-100, 180, 0,   0),
        (670, GROUND_Y-130, 160, 0,   0),
        (340, GROUND_Y-220, 160, 2.0, 130),
    ], "springs": [
        (200, -22), (700, -22),
    ], "conveyors": [
        (50,  GROUND_Y, 300, 4.5),
        (550, GROUND_Y, 300, -4.5),
    ], "portals": [(140, GROUND_Y-165), (720, GROUND_Y-165)]},
    # Pirate Ship
    {"name": "Pirate Ship", "platforms": [
        (55,  GROUND_Y-90,  170, 1.0, 110),
        (670, GROUND_Y-120, 155, -1.0,110),
        (350, GROUND_Y-205, 140, 0,   0),
    ], "springs": [
        (430, -22),
    ], "conveyors": [
        (60,  GROUND_Y, 220, 2.0),
        (610, GROUND_Y, 220, -2.0),
    ], "portals": [(150, GROUND_Y-155), (710, GROUND_Y-155)]},
    # City Rooftop
    {"name": "City Rooftop", "platforms": [
        (60,  GROUND_Y-130, 150, 0,   0),
        (690, GROUND_Y-100, 140, 0,   0),
        (365, GROUND_Y-215, 130, 1.8, 100),
        (170, GROUND_Y-215, 120, 0,   0),
    ], "springs": [
        (250, -22), (650, -22),
    ], "conveyors": [
        (80,  GROUND_Y, 180, 2.5),
        (630, GROUND_Y, 180, -2.5),
    ], "portals": [(160, GROUND_Y-180), (700, GROUND_Y-145)]},
    # Medieval Castle
    {"name": "Medieval Castle", "platforms": [
        (55,  GROUND_Y-110, 165, 0,   0),
        (680, GROUND_Y-110, 165, 0,   0),
        (310, GROUND_Y-200, 145, 1.5, 120),
        (460, GROUND_Y-285, 110, 0,   0),
    ], "springs": [
        (350, -22), (600, -22),
    ], "conveyors": [
        (70,  GROUND_Y, 200, 1.8),
        (620, GROUND_Y, 200, -1.8),
    ], "portals": [(145, GROUND_Y-170), (715, GROUND_Y-170)]},
    # Circus
    {"name": "Circus", "platforms": [
        (60,  GROUND_Y-100, 160, 2.0, 130),
        (670, GROUND_Y-140, 150, -2.0,130),
        (345, GROUND_Y-220, 170, 0,   0),
    ], "springs": [
        (200, -22), (450, -22), (720, -22),
    ], "conveyors": [
        (55,  GROUND_Y, 240, 3.0),
        (590, GROUND_Y, 240, -3.0),
    ], "portals": [(165, GROUND_Y-175), (695, GROUND_Y-175)]},
    # The Void
    {"name": "The Void", "platforms": [
        (310, GROUND_Y-70,  280, 0,   0),    # large central platform (spawn zone)
        (50,  GROUND_Y-160, 175, 0,   0),    # left ledge
        (675, GROUND_Y-160, 175, 0,   0),    # right ledge
        (175, GROUND_Y-270, 140, 1.8, 110),  # left floating
        (580, GROUND_Y-270, 140, -1.8,110),  # right floating
        (380, GROUND_Y-360, 120, 0,   0),    # top centre
    ], "springs": [
        (430, -22), (580, -22),
    ], "conveyors": [], "portals": [(160, GROUND_Y-230), (700, GROUND_Y-230)]},
    # Underwater
    {"name": "Underwater", "platforms": [
        (60,  GROUND_Y-95,  175, 0.8, 100),
        (660, GROUND_Y-130, 165, -0.8,100),
        (330, GROUND_Y-210, 150, 1.2, 120),
    ], "springs": [
        (300, -22), (600, -22),
    ], "conveyors": [
        (60,  GROUND_Y, 210, 1.5),
        (620, GROUND_Y, 210, -1.5),
    ], "portals": [(155, GROUND_Y-160), (705, GROUND_Y-185)]},
    # Arctic Tundra
    {"name": "Arctic Tundra", "platforms": [
        (55,  GROUND_Y-100, 180, 0,   0),
        (665, GROUND_Y-130, 160, 0,   0),
        (335, GROUND_Y-220, 160, 0,   0),
    ], "springs": [
        (220, -22), (680, -22),
    ], "conveyors": [
        (50,  GROUND_Y, 320, 5.0),
        (530, GROUND_Y, 320, -5.0),
    ], "portals": [(145, GROUND_Y-165), (720, GROUND_Y-165)]},
    # Haunted House
    {"name": "Haunted House", "platforms": [
        (60,  GROUND_Y-110, 160, 0,   0),
        (680, GROUND_Y-110, 160, 0,   0),
        (320, GROUND_Y-215, 150, 1.2, 110),
        (150, GROUND_Y-300, 120, 0,   0),
    ], "springs": [
        (390, -22),
    ], "conveyors": [
        (60,  GROUND_Y, 200, -1.8),
        (640, GROUND_Y, 200,  1.8),
    ], "portals": [(155, GROUND_Y-175), (710, GROUND_Y-175)]},
    # Volcano Core
    {"name": "Volcano Core", "platforms": [
        (55,  GROUND_Y-90,  170, 1.5, 100),
        (675, GROUND_Y-120, 155, -1.5,100),
        (360, GROUND_Y-200, 135, 0,   0),
        (200, GROUND_Y-295, 110, 2.0, 90),
        (590, GROUND_Y-295, 110, -2.0,90),
    ], "springs": [
        (440, -22),
    ], "conveyors": [
        (60,  GROUND_Y, 220, 3.2),
        (620, GROUND_Y, 220, -3.2),
    ], "portals": [(160, GROUND_Y-210), (700, GROUND_Y-210)]},
    # Sky Island
    {"name": "Sky Island", "platforms": [
        (80,  GROUND_Y-150, 160, 0,   0),
        (660, GROUND_Y-150, 160, 0,   0),
        (350, GROUND_Y-255, 145, 0,   0),
        (200, GROUND_Y-340, 110, 0,   0),
        (590, GROUND_Y-340, 110, 0,   0),
    ], "springs": [
        (160, -22), (460, -22), (740, -22),
    ], "conveyors": [
        (80,  GROUND_Y, 180, 1.5),
        (640, GROUND_Y, 180, -1.5),
    ], "portals": [(165, GROUND_Y-210), (695, GROUND_Y-210)]},
    # Graveyard
    {"name": "Graveyard", "platforms": [
        (50,  GROUND_Y-105, 170, 0,   0),
        (680, GROUND_Y-130, 155, 0,   0),
        (330, GROUND_Y-210, 145, 1.0, 100),
        (460, GROUND_Y-295, 115, 0,   0),
    ], "springs": [
        (300, -22), (620, -22),
    ], "conveyors": [
        (55,  GROUND_Y, 210, -2.0),
        (635, GROUND_Y, 210,  2.0),
    ], "portals": [(150, GROUND_Y-165), (715, GROUND_Y-165)]},
]

# Stage-specific character advantages and disadvantages.
# adv gets +25% speed & +25% damage; dis gets -20% speed & -20% damage.
STAGE_MATCHUPS = {
    "Grasslands": {"adv": "Scarecrow",   "dis": "Titan"},
    "Volcano":    {"adv": "Arsonist",    "dis": "Cryogenisist"},
    "Dojo":       {"adv": "Ninja",       "dis": "Oni"},
    "Desert":     {"adv": "Cactus",      "dis": "Tank"},
    "Arena":      {"adv": "Gladiator",   "dis": "Rogue"},
    "Dream Land": {"adv": "Spring",      "dis": "Brawler"},
    "Underworld": {"adv": "Skeleton",    "dis": "Boxer"},
    "Space":      {"adv": "Astronaut",    "dis": "Giant"},
    "Jungle":     {"adv": "Hooker",       "dis": "Gunner"},
    "Computer":        {"adv": "Charger",      "dis": "Viking"},
    "Ice Cave":        {"adv": "Cryogenisist", "dis": "Arsonist"},
    "Pirate Ship":     {"adv": "Pirate",        "dis": "Wizard"},
    "City Rooftop":    {"adv": "Speedster",     "dis": "Headless Horseman"},
    "Medieval Castle": {"adv": "Knight",        "dis": "Vampire"},
    "Circus":          {"adv": "Clown",         "dis": "Samurai"},
    "Underwater":      {"adv": "Cecalia",       "dis": "Arsonist"},
    "The Void":        {"adv": "Acrobat",       "dis": "Titan"},
    "Arctic Tundra":   {"adv": "Cryogenisist",  "dis": "Lava Man"},
    "Haunted House":   {"adv": "Ghost",          "dis": "Rogue"},
    "Volcano Core":    {"adv": "Lava Man",       "dis": "Cryogenisist"},
    "Sky Island":      {"adv": "Angel",          "dis": "Sumo"},
    "Graveyard":       {"adv": "Ghost",       "dis": "Medic"},
}

