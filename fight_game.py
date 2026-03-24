import pygame
import sys
import math
import random
import constants
from constants import *
from fight_data import CHARACTERS, POWERUPS, STAGES, STAGE_MATCHUPS
from fight_drawing import (draw_bg, draw_health_bars, draw_health_bars_labeled,
                           draw_win_screen, draw_active_powerups)
from fight_entities import (Fighter, AIFighter, Powerup, Platform, StagePencil,
                            StageEraser, DrawnPlatform, Portal, ConveyorBelt,
                            Spring, SnakeHook, Pumpkin, FallingSkull,
                            JungleSnake, ComputerBug, MousePlatform,
                            Projectile, Orb, BouncingBall, Whip, HotPotato)
import fight_network as _net
from fight_ui import stage_select, mode_select, character_select, online_menu

# ---------------------------------------------------------------------------
# Fight loop
# ---------------------------------------------------------------------------

def run_fight(p1_idx, p2_idx, vs_ai=False, ai_difficulty='medium', stage_idx=0):
    _stage_name = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13   # floaty anti-gravity
    constants.STAGE_VOID = (_stage_name == "The Void")

    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g, duck=pygame.K_s, block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l, duck=pygame.K_DOWN, block=pygame.K_o)

    p1 = Fighter(200, CHARACTERS[p1_idx],  1, P1_CTRL)
    if vs_ai:
        p2 = AIFighter(700, CHARACTERS[p2_idx], -1, ai_difficulty)
    else:
        p2 = Fighter(700, CHARACTERS[p2_idx], -1, P2_CTRL)

    if constants.STAGE_VOID:
        # Spawn on the central platform (GROUND_Y-70), not on the (absent) floor
        p1.x = 380.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        p2.x = 520.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True

    stage_data = STAGES[stage_idx % len(STAGES)]
    platforms  = [Platform(*p) for p in stage_data["platforms"]] + [ConveyorBelt(*c) for c in stage_data.get("conveyors", [])]
    springs    = [Spring(*s)   for s in stage_data["springs"]]

    # Apply stage advantage / disadvantage stat modifiers
    matchup = STAGE_MATCHUPS.get(stage_data["name"], {})
    for f in (p1, p2):
        if f.char["name"] == matchup.get("adv"):
            f.speed_boost *= 1.25
            f.punch_boost += f.char["punch_dmg"] // 4
            f.kick_boost  += f.char["kick_dmg"]  // 4
        elif f.char["name"] == matchup.get("dis"):
            f.speed_boost *= 0.8
            f.punch_boost -= f.char["punch_dmg"] // 5
            f.kick_boost  -= f.char["kick_dmg"]  // 5

    def _stage_tag(fighter):
        name = fighter.char["name"]
        if name == matchup.get("adv"): return ("★ ADVANTAGE", (100, 255, 100))
        if name == matchup.get("dis"): return ("✗ DISADVANTAGE", (255, 100, 100))
        return (None, None)

    p1_stag, p1_stag_col = _stage_tag(p1)
    p2_stag, p2_stag_col = _stage_tag(p2)
    announce_timer = 180   # 3 seconds

    game_over    = False
    winner       = None
    timer        = 90 * FPS
    powerups     = []
    clones       = []   # list of {'fighter': AIFighter, 'timer': int, 'target': Fighter}
    balls        = []   # active Projectile objects
    orbs         = []   # active Orb objects (bazooka)
    bounce_balls = []   # active BouncingBall objects (Pinball)
    hooks        = []   # active SnakeHook objects (Hooker)
    pumpkins     = []   # active Pumpkin objects (Headless Horseman)
    whips        = []   # active Whip objects (Whipper)
    spawn_timer  = 300   # first spawn after 5 seconds
    is_jungle      = stage_data["name"] == "Jungle"
    is_computer    = stage_data["name"] == "Computer"
    is_underworld  = stage_data["name"] == "Underworld"
    jungle_snakes      = []
    snake_spawn_timer  = 180
    computer_bugs      = []
    bug_spawn_timer    = 150
    falling_skulls     = []
    skull_spawn_timer  = 200
    stage_pencil = None
    stage_eraser = None
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))
        stage_pencil = StagePencil()
        stage_eraser = StageEraser()

    _portal_cols = [(80, 100, 220), (220, 120, 20)]
    _px1 = random.randint(80, WIDTH // 2 - 60)
    _px2 = random.randint(WIDTH // 2 + 60, WIDTH - 80)
    _py1 = random.randint(GROUND_Y - 280, GROUND_Y - 80)
    _py2 = random.randint(GROUND_Y - 280, GROUND_Y - 80)
    portals_obj  = [Portal(_px1, _py1, _portal_cols[0]), Portal(_px2, _py2, _portal_cols[1])]
    portals_obj[0].partner = portals_obj[1]
    portals_obj[1].partner = portals_obj[0]

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; return 'rematch'
                    if event.key == pygame.K_c:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; return 'select'
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False
                        pygame.quit(); sys.exit()
                else:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; return 'select'

        if not game_over:
            for portal in portals_obj:
                portal.update()
            for fighter in (p1, p2):
                for portal in portals_obj:
                    if portal.partner and fighter.portal_cooldown == 0 and portal.near(fighter):
                        fighter.x = portal.partner.x
                        fighter.y = portal.partner.y
                        fighter.vy = 0
                        fighter.portal_cooldown = FPS * 2
                        break

            for plat in platforms:
                plat.update()
            for sp in springs:
                sp.update()
                sp.trigger(p1)
                sp.trigger(p2)
                for cd in clones:
                    sp.trigger(cd['fighter'])

            # Update clones
            new_clones = []
            for cd in clones:
                cd['timer'] -= 1
                if cd['timer'] > 0 and cd['fighter'].hp > 0:
                    cd['fighter'].update(None, cd['target'], platforms)
                    new_clones.append(cd)
            clones = new_clones

            # Cactus contact damage + poison
            for cactus, victim in [(p1, p2), (p2, p1)]:
                if (cactus.char.get("contact_dmg") and
                        victim.contact_cooldown == 0 and
                        abs(cactus.x - victim.x) < 55):
                    victim.hp = max(0, victim.hp - cactus.char["contact_dmg"])
                    victim.contact_cooldown = 60
                    victim.flash_timer = 8
                    if victim.poison_frames == 0:
                        victim.poison_tick = 180
                    victim.poison_frames = max(victim.poison_frames, 600)  # 10 sec

            # Boomerang collision
            for thrower, victim in [(p1, p2), (p2, p1)]:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    if math.hypot(bx - victim.x, by - (victim.y - 60)) < 48:
                        victim.hp = max(0, victim.hp - 8)
                        victim.flash_timer = 6
                        thrower.boomerang_hit_cd = 30   # 0.5s between hits

            # Laser Eyes beam damage
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    correct_side = ((shooter.facing == 1  and victim.x > shooter.x) or
                                    (shooter.facing == -1 and victim.x < shooter.x))
                    if correct_side and abs((victim.y - 60) - laser_y) < 35:
                        victim.hp = max(0, victim.hp - 2)
                        victim.flash_timer = 4
                        shooter.laser_hit_cd = 15  # damage tick every 15 frames

            keys = pygame.key.get_pressed()
            p1.update(keys, p2, platforms)
            p2.update(keys, p1, platforms)

            # Spawn balls from shoot_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))

            # Update balls and check collisions
            for b in balls:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8
                        b.alive = False
            balls = [b for b in balls if b.alive]

            # Spawn orbs from bazooka_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing * 30,
                                    shooter.y - 60, shooter.facing, shooter))

            # Update orbs and apply explosion damage
            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    victim = p2 if o.owner is p1 else p1
                    if math.hypot(o.x - victim.x, o.y - (victim.y - 60)) < o.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - o.EXPLODE_DMG)
                        victim.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            # Spawn bouncing balls from bounce_kick
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing * 30,
                                                     shooter.y - 60, shooter.facing, shooter))

            # Update bouncing balls and check collisions
            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    victim = p2 if bb.owner is p1 else p1
                    if bb.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8
                        bb.hit_cd = BouncingBall.HIT_CD
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            # Spawn snake hooks from grapple_kick (Hooker)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_hook:
                    shooter.pending_hook = False
                    hooks.append(SnakeHook(
                        shooter.x + shooter.facing * 20, shooter.y - 60,
                        victim.x, victim.y - 60, shooter))

            # Update snake hooks and pull on hit
            for h in hooks:
                h.update()
                if h.alive:
                    victim = p2 if h.owner is p1 else p1
                    if h.collides(victim):
                        pull_dir = 1 if h.owner.x > victim.x else -1
                        victim.knockback = pull_dir * 22
                        victim.hp = max(0, victim.hp - 6)
                        victim.flash_timer = 8
                        h.alive = False
            hooks = [h for h in hooks if h.alive]

            # Pumpkins (Headless Horseman)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - pk.EXPLODE_DMG)
                        victim.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    victim = p2 if pk.owner is p1 else p1
                    if pk.collides(victim):
                        pk._explode()
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Whips (Whipper)
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_whip:
                    shooter.pending_whip = False
                    whips.append(Whip(
                        shooter.x + shooter.facing * 28, shooter.y - 60,
                        shooter.facing, shooter))
            for w in whips:
                w.update()
                if w.can_hit():
                    victim = p2 if w.owner is p1 else p1
                    if w.collides(victim):
                        victim.hp = max(0, victim.hp - w.DMG)
                        victim.flash_timer = 10
                        victim.knockback = w.facing * 14
                        w.hit_done = True
            whips = [w for w in whips if w.alive]

            # Ink Brush clones
            for shooter, foe in [(p1, p2), (p2, p1)]:
                if shooter.pending_ink_clone:
                    shooter.pending_ink_clone = False
                    cf = AIFighter(shooter.x + shooter.facing * 55, shooter.char, -shooter.facing, 'medium')
                    cf.hp = max(1, shooter.hp)
                    cf.color = shooter.color
                    cf.no_attack = True
                    clones.append({'fighter': cf, 'timer': FPS * 8, 'target': foe, 'ink': True})

            # Jungle snakes
            if is_jungle:
                snake_spawn_timer -= 1
                if snake_spawn_timer <= 0 and len(jungle_snakes) < 4:
                    jungle_snakes.append(JungleSnake())
                    snake_spawn_timer = random.randint(300, 480)
                for sn in jungle_snakes:
                    sn.update(p1, p2)
                jungle_snakes = [sn for sn in jungle_snakes if sn.alive]

            # Computer bugs
            if is_computer:
                bug_spawn_timer -= 1
                if bug_spawn_timer <= 0 and len(computer_bugs) < 5:
                    computer_bugs.append(ComputerBug())
                    bug_spawn_timer = random.randint(200, 360)
                for b in computer_bugs:
                    target = min([p1, p2], key=lambda p: abs(p.x - b.x))
                    b.update(target)
                computer_bugs = [b for b in computer_bugs if b.alive]
                # Pencil: draw new platforms
                stage_pencil.update()
                drawn_count = sum(1 for p in platforms if isinstance(p, DrawnPlatform))
                if stage_pencil.pending_plat and drawn_count < StagePencil.MAX_PLATS:
                    stage_pencil.pending_plat = False
                    platforms.append(DrawnPlatform(int(stage_pencil.x) - 50, int(stage_pencil.y) + 20, w=100))
                # Eraser: wipe platforms it passes
                platforms = stage_eraser.update(platforms)
                # Update / expire DrawnPlatforms
                for p in platforms:
                    if isinstance(p, DrawnPlatform): p.update()
                platforms = [p for p in platforms if not (isinstance(p, DrawnPlatform) and not p.alive)]
                # Eraser contact damage
                for pf in (p1, p2):
                    if pf.hp > 0 and pf.contact_cooldown == 0:
                        if math.hypot(pf.x - stage_eraser.x, pf.y - stage_eraser.y) < 50:
                            pf.hp = max(0, pf.hp - 5)
                            pf.flash_timer = 8
                            pf.contact_cooldown = 60

            # Falling skulls (Underworld)
            if is_underworld:
                skull_spawn_timer -= 1
                if skull_spawn_timer <= 0 and len(falling_skulls) < 8:
                    falling_skulls.append(FallingSkull())
                    skull_spawn_timer = random.randint(120, 280)
                for sk in falling_skulls:
                    sk.update()
                    if sk.hit_cd == 0:
                        for victim in (p1, p2):
                            if sk.collides(victim):
                                victim.hp = max(0, victim.hp - sk.DMG)
                                victim.flash_timer = 10
                                sk.hit_cd = sk.HIT_CD

            timer -= 1
            if timer <= 0 or p1.hp <= 0 or p2.hp <= 0:
                game_over = True
                winner = p1 if p1.hp >= p2.hp else p2

            # Spawn powerups
            spawn_timer -= 1
            if spawn_timer <= 0 and len(powerups) < 3:
                powerups.append(Powerup())
                spawn_timer = random.randint(480, 720)   # 8-12 seconds

            # Magician attraction: pull all powerups slowly toward Magician fighters
            for f in (p1, p2):
                if f.char.get("magnet"):
                    for pu in powerups:
                        if not pu.picked_up:
                            dx = f.x - pu.x
                            dy = (f.y - 60) - pu.y
                            dist = math.hypot(dx, dy) or 1
                            speed = min(2.5, 300 / dist)   # faster when closer
                            pu.x += (dx / dist) * speed
                            pu.y += (dy / dist) * speed

            # Update & pickup
            for pu in powerups:
                pu.update()
                for fighter, foe in [(p1, p2), (p2, p1)]:
                    if not pu.picked_up and pu.collides(fighter):
                        if pu.spec['type'] == 'clone':
                            cf = AIFighter(fighter.x + 60 * fighter.facing,
                                           fighter.char, fighter.facing, 'hard')
                            cf.hp    = 80
                            cf.color = fighter.color
                            clones.append({'fighter': cf, 'timer': 30 * FPS, 'target': foe})
                        else:
                            fighter.apply_powerup(pu.spec)
                        pu.picked_up = True
                        break
            powerups = [pu for pu in powerups if not pu.picked_up]

        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for portal in portals_obj:
            portal.draw(screen)
        for plat in platforms:
            plat.draw(screen, stage_idx)
        for sp in springs:
            sp.draw(screen)
        for pu in powerups:
            pu.draw(screen)
        for b in balls:
            b.draw(screen)
        for o in orbs:
            o.draw(screen)
        for bb in bounce_balls:
            bb.draw(screen)
        for h in hooks:
            h.draw(screen)
        for pk in pumpkins:
            pk.draw(screen)
        for w in whips:
            w.draw(screen)
        for sn in jungle_snakes:
            sn.draw(screen)
        for sk in falling_skulls:
            sk.draw(screen)
        for b in computer_bugs:
            b.draw(screen)
        if is_computer and stage_pencil:
            stage_pencil.draw(screen)
            stage_eraser.draw(screen)
        # Draw Laser Eyes beam
        for f in (p1, p2):
            if f.char.get("laser_eyes") and f.laser_active > 0:
                eye_x = int(f.x)
                eye_y = int(f.y - 100)
                end_x = WIDTH if f.facing == 1 else 0
                x = eye_x
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    dash_end = x + f.facing * 18
                    dash_end = min(dash_end, end_x) if f.facing == 1 else max(dash_end, end_x)
                    pygame.draw.line(screen, (255, 40, 0),  (x, eye_y),     (dash_end, eye_y), 3)
                    pygame.draw.line(screen, (255, 160, 80), (x, eye_y),    (dash_end, eye_y), 1)
                    x = dash_end + f.facing * 6  # 6-pixel gap between dashes
        # Draw magnet beams from powerups to any Magician fighter
        for f in (p1, p2):
            if f.char.get("magnet"):
                for pu in powerups:
                    if not pu.picked_up:
                        pygame.draw.line(screen, (140, 60, 220),
                                         (int(pu.x), int(pu.y)),
                                         (int(f.x), int(f.y - 60)), 1)
        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)
        # Bubble shield visuals
        for f in (p1, p2):
            if f.bubble_shield:
                bsurf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(bsurf, (100, 200, 255, 70), (50, 50), 48)
                pygame.draw.circle(bsurf, (100, 200, 255, 160), (50, 50), 48, 3)
                screen.blit(bsurf, (int(f.x) - 50, int(f.y) - 90))
        clone_draws = [(cd, cd['fighter'].draw(screen)) for cd in clones]

        if not game_over:
            if p1.attacking and not p1.attack_hit:
                p1.check_hit(p1_hit, p2)
            if p2.attacking and not p2.attack_hit:
                p2.check_hit(p2_hit, p1)
            # Fighter attacks hit jungle snakes
            for attacker, hit_pos in [(p1, p1_hit), (p2, p2_hit)]:
                if attacker.attacking and hit_pos:
                    for sn in jungle_snakes:
                        if math.hypot(hit_pos[0] - sn.x, hit_pos[1] - (sn.y - 8)) < 44:
                            dmg = (attacker.char["punch_dmg"] if attacker.action == 'punch'
                                   else attacker.char["kick_dmg"])
                            sn.take_damage(dmg)
            # Fighter attacks hit computer bugs
            if is_computer:
                for attacker, hit_pos in [(p1, p1_hit), (p2, p2_hit)]:
                    if attacker.attacking and hit_pos:
                        for b in computer_bugs:
                            if math.hypot(hit_pos[0]-b.x, hit_pos[1]-(b.y-8)) < 40:
                                dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                       else attacker.char["kick_dmg"])
                                b.take_damage(dmg)
            for cd, cf_hit in clone_draws:
                cf = cd['fighter']
                # clone attacks its target (ink clones can't attack)
                if not cd.get('ink') and cf.attacking and not cf.attack_hit:
                    cf.check_hit(cf_hit, cd['target'])
                # opponent can hit the clone
                if cd['target'] is p2:
                    if p2.attacking and not p2.attack_hit:
                        p2.check_hit(p2_hit, cf)
                else:
                    if p1.attacking and not p1.attack_hit:
                        p1.check_hit(p1_hit, cf)
            # draw clone timer above each clone (ink clones get no label)
            for cd in clones:
                if cd.get('ink'):
                    continue
                cf = cd['fighter']
                secs = cd['timer'] // FPS
                tag = font_tiny.render(f"2x [{secs}s]", True, (255, 80, 200))
                screen.blit(tag, (int(cf.x) - tag.get_width()//2,
                                  int(cf.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        # Draw AI tag above CPU fighter
        if vs_ai:
            diff_col = {
                'easy': GREEN, 'medium': YELLOW, 'hard': RED,
                'super_hard': PURPLE, 'super_super_hard': CYAN, 'mega_hard': ORANGE
            }[ai_difficulty]
            cpu_tag = font_tiny.render(f"CPU [{ai_difficulty.upper()}]", True, diff_col)
            screen.blit(cpu_tag, (int(p2.x) - cpu_tag.get_width()//2,
                                  int(p2.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        p2_label = f"CPU — {p2.char['name']}" if vs_ai else f"P2 — {p2.char['name']}"
        draw_health_bars_labeled(screen, p1, p2, p2_label)
        draw_active_powerups(screen, p1, 'left')
        draw_active_powerups(screen, p2, 'right')

        secs = max(0, timer // FPS)
        t_surf = font_medium.render(str(secs), True, RED if secs <= 10 else WHITE)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 40))

        if vs_ai:
            hint  = font_tiny.render("WASD + F punch  G kick  S duck  R block", True, (140, 140, 140))
        else:
            hint  = font_tiny.render(
                "P1: WASD F punch G kick S duck R block        P2: Arrows K punch L kick ↓ duck O block",
                True, (140, 140, 140))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 22))

        # Stage advantage / disadvantage announcement (first 3 seconds)
        if announce_timer > 0 and not game_over:
            announce_timer -= 1
            if p1_stag:
                s = font_small.render(p1_stag, True, p1_stag_col)
                screen.blit(s, (10, 80))
            if p2_stag:
                s = font_small.render(p2_stag, True, p2_stag_col)
                screen.blit(s, (WIDTH - s.get_width() - 10, 80))

        if game_over:
            draw_win_screen(screen, winner, p1, p2, vs_ai=vs_ai)

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Survival mode
# ---------------------------------------------------------------------------

def run_survival(p1_idx, p2_idx=None, two_player=False, stage_idx=0):
    _stage_name   = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13
    constants.STAGE_VOID = (_stage_name == "The Void")

    P1_CTRL = dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w,
                   punch=pygame.K_f, kick=pygame.K_g, duck=pygame.K_s, block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k, kick=pygame.K_l, duck=pygame.K_DOWN, block=pygame.K_o)

    p1      = Fighter(250, CHARACTERS[p1_idx],  1, P1_CTRL)
    p2      = Fighter(650, CHARACTERS[p2_idx], -1, P2_CTRL) if two_player else None
    if constants.STAGE_VOID:
        p1.x = 400.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        if p2:
            p2.x = 500.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True
    players = [p1, p2] if two_player else [p1]

    stage_data  = STAGES[stage_idx % len(STAGES)]
    platforms   = [Platform(*p) for p in stage_data["platforms"]]
    springs     = [Spring(*s)   for s in stage_data["springs"]]
    is_jungle     = stage_data["name"] == "Jungle"
    is_computer   = stage_data["name"] == "Computer"
    is_underworld = stage_data["name"] == "Underworld"
    stage_pencil = None
    stage_eraser = None
    if is_computer:
        platforms.append(MousePlatform(80, GROUND_Y - 62, travel=720))
        stage_pencil = StagePencil()
        stage_eraser = StageEraser()

    _portal_cols_s = [(80, 100, 220), (220, 120, 20)]
    _px1s = random.randint(80, WIDTH // 2 - 60)
    _px2s = random.randint(WIDTH // 2 + 60, WIDTH - 80)
    _py1s = random.randint(GROUND_Y - 280, GROUND_Y - 80)
    _py2s = random.randint(GROUND_Y - 280, GROUND_Y - 80)
    portals_obj_s  = [Portal(_px1s, _py1s, _portal_cols_s[0]), Portal(_px2s, _py2s, _portal_cols_s[1])]
    portals_obj_s[0].partner = portals_obj_s[1]
    portals_obj_s[1].partner = portals_obj_s[0]

    enemies           = []
    death_pops        = []   # [{x,y,color,t}] death burst particles
    balls             = []   # Projectile (shoot_kick)
    orbs              = []   # Orb (bazooka_kick)
    bounce_balls      = []   # BouncingBall (bounce_kick)
    hooks             = []   # SnakeHook (grapple_kick)
    pumpkins          = []   # Pumpkin (pumpkin_kick)
    whips             = []   # Whip (whip_punch)
    ink_clones        = []   # Ink Brush clones
    en_balls          = []
    en_orbs           = []
    en_bounce_balls   = []
    en_pumpkins       = []
    en_hooks          = []
    en_whips          = []
    powerups          = []
    jungle_snakes     = []
    computer_bugs     = []
    bug_spawn_timer   = 150
    falling_skulls    = []
    skull_spawn_timer = 200
    survival_timer    = 0
    enemies_killed    = 0
    enemy_spawn_timer = 180
    snake_spawn_timer = 180
    powerup_timer     = 480
    game_over         = False

    def wave_info():
        s = survival_timer // FPS
        if   s <  30: return 1, 'easy'
        elif s <  60: return 2, 'easy'
        elif s <  90: return 2, 'medium'
        elif s < 120: return 3, 'medium'
        elif s < 180: return 3, 'hard'
        elif s < 240: return 4, 'hard'
        else:         return 4, 'super_hard'

    def _draw_survival_hud():
        # HP bars for players
        bw = 240
        pygame.draw.rect(screen, (60,60,60), (10, 10, bw, 20), border_radius=4)
        fw = int(bw * max(0, p1.hp / p1.max_hp))
        pygame.draw.rect(screen, p1.char["color"], (10, 10, fw, 20), border_radius=4)
        pygame.draw.rect(screen, WHITE, (10, 10, bw, 20), 2, border_radius=4)
        ht = font_tiny.render(f"P1 {p1.char['name']}  {max(0,p1.hp)}/{p1.max_hp}", True, WHITE)
        screen.blit(ht, (14, 13))
        if two_player:
            pygame.draw.rect(screen, (60,60,60), (WIDTH-bw-10, 10, bw, 20), border_radius=4)
            fw2 = int(bw * max(0, p2.hp / p2.max_hp))
            pygame.draw.rect(screen, p2.char["color"], (WIDTH-bw-10+bw-fw2, 10, fw2, 20), border_radius=4)
            pygame.draw.rect(screen, WHITE, (WIDTH-bw-10, 10, bw, 20), 2, border_radius=4)
            ht2 = font_tiny.render(f"{max(0,p2.hp)}/{p2.max_hp}  P2 {p2.char['name']}", True, WHITE)
            screen.blit(ht2, (WIDTH-bw-10 + bw - ht2.get_width() - 4, 13))
        # Timer (counting up)
        elapsed = survival_timer // FPS
        mins, secs = divmod(elapsed, 60)
        t_surf = font_medium.render(f"{mins}:{secs:02d}", True, YELLOW)
        screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 6))
        # Kills
        k_surf = font_tiny.render(f"Kills: {enemies_killed}", True, (200, 200, 200))
        screen.blit(k_surf, (WIDTH//2 - k_surf.get_width()//2, 38))
        # Wave
        max_en, diff = wave_info()
        w_surf = font_tiny.render(f"Wave difficulty: {diff.replace('_',' ')}  |  Max enemies: {max_en}", True, GRAY)
        screen.blit(w_surf, (WIDTH//2 - w_surf.get_width()//2, HEIGHT - 22))

    def _draw_game_over():
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        go = font_large.render("GAME OVER", True, RED)
        screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//3 - 40))
        elapsed = survival_timer // FPS
        mins, secs = divmod(elapsed, 60)
        ts = font_medium.render(f"Survived: {mins}:{secs:02d}", True, WHITE)
        screen.blit(ts, (WIDTH//2 - ts.get_width()//2, HEIGHT//3 + 40))
        ks = font_medium.render(f"Kills: {enemies_killed}", True, YELLOW)
        screen.blit(ks, (WIDTH//2 - ks.get_width()//2, HEIGHT//3 + 90))
        hint = font_small.render("R — restart     C — menu     Q — quit", True, (200,200,200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT*2//3 + 30))

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; return 'rematch'
                    if event.key == pygame.K_c:
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; return 'select'
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; pygame.quit(); sys.exit()
                else:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        constants.GRAVITY = _orig_gravity; constants.STAGE_VOID = False; return 'select'

        if not game_over:
            survival_timer += 1
            max_en, diff = wave_info()

            # Platforms & springs
            for plat in platforms:
                plat.update()
            for sp in springs:
                sp.update()
                sp.trigger(p1)
                if two_player: sp.trigger(p2)
                for en in enemies: sp.trigger(en)

            # Portals
            for portal in portals_obj_s:
                portal.update()
            for fighter in players:
                for portal in portals_obj_s:
                    if portal.partner and fighter.portal_cooldown == 0 and portal.near(fighter):
                        fighter.x = portal.partner.x
                        fighter.y = portal.partner.y
                        fighter.vy = 0
                        fighter.portal_cooldown = FPS * 2
                        break

            # Spawn enemies
            enemy_spawn_timer -= 1
            if enemy_spawn_timer <= 0 and len(enemies) < max_en:
                ci = random.randint(0, len(CHARACTERS) - 1)
                if constants.STAGE_VOID:
                    # Spawn on the central platform so they don't fall into the void
                    sx = float(random.randint(330, 570))
                    sy = float(GROUND_Y - 70)
                else:
                    sx = float(random.choice([60, WIDTH - 60]))
                    sy = float(GROUND_Y)
                en    = AIFighter(sx, CHARACTERS[ci], -1 if sx > WIDTH // 2 else 1, diff)
                en.x  = sx; en.y = sy; en.on_ground = True
                en.hp = en.char["max_hp"]
                enemies.append(en)
                interval          = max(60, 300 - survival_timer // (2 * FPS))
                enemy_spawn_timer = random.randint(max(30, interval // 2), interval)

            # Update enemies — each targets nearest living player
            living = [p for p in players if p.hp > 0]
            for en in enemies:
                if living:
                    target = min(living, key=lambda p: abs(p.x - en.x))
                    en.update(None, target, platforms)
                    if en.pending_ball:
                        en.pending_ball = False
                        en_balls.append(Projectile(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_orb and en.bazooka_cooldown == 0:
                        en.pending_orb = False
                        en_orbs.append(Orb(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_bounce:
                        en.pending_bounce = False
                        en_bounce_balls.append(BouncingBall(en.x + en.facing*30, en.y-60, en.facing, en))
                    if en.pending_hook and living:
                        en.pending_hook = False
                        tgt = min(living, key=lambda p: abs(p.x - en.x))
                        en_hooks.append(SnakeHook(en.x + en.facing*20, en.y-60,
                                                   tgt.x, tgt.y-60, en))

            # Mark newly dead players and freeze them
            for p in players:
                if p.hp <= 0 and p.action != 'dead':
                    p.action     = 'dead'
                    p.action_t   = 0
                    p.flash_timer = 0
                    p.vx = 0
                    p.vy = 0

            # Update players (skip dead ones)
            keys     = pygame.key.get_pressed()
            other_p1 = p2 if two_player else (enemies[0] if enemies else p1)
            if p1.hp > 0:
                p1.update(keys, other_p1, platforms)
            if two_player and p2.hp > 0:
                p2.update(keys, p1, platforms)

            # Spawn player projectiles
            for shooter in players:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing*30, shooter.y-60,
                                            shooter.facing, shooter))
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing*30, shooter.y-60,
                                    shooter.facing, shooter))
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing*30, shooter.y-60,
                                                     shooter.facing, shooter))
                if shooter.pending_hook and enemies:
                    shooter.pending_hook = False
                    tgt = min(enemies, key=lambda e: abs(e.x - shooter.x))
                    hooks.append(SnakeHook(shooter.x + shooter.facing*20, shooter.y-60,
                                           tgt.x, tgt.y-60, shooter))
                else:
                    shooter.pending_hook = False

            # Laser Eyes beam damage (survival)
            for shooter in players:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    for en in enemies:
                        correct_side = ((shooter.facing == 1  and en.x > shooter.x) or
                                        (shooter.facing == -1 and en.x < shooter.x))
                        if correct_side and abs((en.y - 60) - laser_y) < 35:
                            en.hp = max(0, en.hp - 2)
                            en.flash_timer = 4
                            shooter.laser_hit_cd = 15
                            break
            for en in enemies:
                if (en.char.get("laser_eyes") and en.laser_active > 0
                        and en.laser_hit_cd == 0):
                    laser_y = en.y - 100
                    for p in living:
                        correct_side = ((en.facing == 1  and p.x > en.x) or
                                        (en.facing == -1 and p.x < en.x))
                        if correct_side and abs((p.y - 60) - laser_y) < 35:
                            p.hp = max(0, p.hp - 2)
                            p.flash_timer = 4
                            en.laser_hit_cd = 15
                            break

            # Boomerang damage: player boomerangs hit enemies, enemy boomerangs hit players
            for thrower in players:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    for en in enemies:
                        if math.hypot(bx - en.x, by - (en.y - 60)) < 48:
                            en.hp = max(0, en.hp - 8)
                            en.flash_timer = 6
                            thrower.boomerang_hit_cd = 30
                            break
            for en in enemies:
                if en.boomerang_timer > 0 and en.boomerang_hit_cd == 0:
                    bx = en.x + math.cos(en.boomerang_angle) * 85
                    by = (en.y - 60) + math.sin(en.boomerang_angle) * 55
                    for p in living:
                        if math.hypot(bx - p.x, by - (p.y - 60)) < 48:
                            p.hp = max(0, p.hp - 8)
                            p.flash_timer = 6
                            en.boomerang_hit_cd = 30
                            break

            # Player balls → enemies
            for b in balls:
                b.update()
                if b.alive:
                    for en in enemies:
                        if b.collides(en):
                            en.hp = max(0, en.hp - 10); en.flash_timer = 8
                            b.alive = False; break
            balls = [b for b in balls if b.alive]

            # Player orbs → enemies
            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for en in enemies:
                        if math.hypot(o.x - en.x, o.y - (en.y - 60)) < o.EXPLODE_RADIUS:
                            en.hp = max(0, en.hp - o.EXPLODE_DMG); en.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            # Player bouncing balls → enemies
            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for en in enemies:
                        if bb.collides(en):
                            en.hp = max(0, en.hp - 10); en.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            # Player hooks → enemies
            for h in hooks:
                h.update()
                if h.alive:
                    for en in enemies:
                        if h.collides(en):
                            pull = 1 if h.owner.x > en.x else -1
                            en.knockback = pull * 22
                            en.hp = max(0, en.hp - 6); en.flash_timer = 8
                            h.alive = False; break
            hooks = [h for h in hooks if h.alive]

            # Enemy hooks → players
            for h in en_hooks:
                h.update()
                if h.alive:
                    for p in living:
                        if h.collides(p):
                            pull = 1 if h.owner.x > p.x else -1
                            p.knockback = pull * 22
                            p.hp = max(0, p.hp - 6); p.flash_timer = 8
                            h.alive = False; break
            en_hooks = [h for h in en_hooks if h.alive]

            # Enemy balls → players
            for b in en_balls:
                b.update()
                if b.alive:
                    for p in living:
                        if b.collides(p):
                            p.hp = max(0, p.hp - 10); p.flash_timer = 8
                            b.alive = False; break
            en_balls = [b for b in en_balls if b.alive]

            # Enemy orbs → players
            for o in en_orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    for p in living:
                        if math.hypot(o.x - p.x, o.y - (p.y - 60)) < o.EXPLODE_RADIUS:
                            p.hp = max(0, p.hp - o.EXPLODE_DMG); p.flash_timer = 14
            en_orbs = [o for o in en_orbs if o.alive]

            # Enemy bouncing balls → players
            for bb in en_bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    for p in living:
                        if bb.collides(p):
                            p.hp = max(0, p.hp - 10); p.flash_timer = 8
                            bb.hit_cd = BouncingBall.HIT_CD; break
            en_bounce_balls = [bb for bb in en_bounce_balls if bb.alive]

            # Player pumpkins → enemies
            for shooter in players:
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(
                        shooter.x + shooter.facing * 24, shooter.y - 80,
                        shooter.facing, shooter))
            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    for en in enemies:
                        if math.hypot(pk.x - en.x, pk.y - (en.y - 60)) < pk.EXPLODE_RADIUS:
                            en.hp = max(0, en.hp - pk.EXPLODE_DMG); en.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    for en in enemies:
                        if pk.collides(en):
                            pk._explode(); break
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Enemy pumpkins → players
            for en in enemies:
                if en.pending_pumpkin:
                    en.pending_pumpkin = False
                    en_pumpkins.append(Pumpkin(
                        en.x + en.facing * 24, en.y - 80, en.facing, en))
            for pk in en_pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    for p in living:
                        if math.hypot(pk.x - p.x, pk.y - (p.y - 60)) < pk.EXPLODE_RADIUS:
                            p.hp = max(0, p.hp - pk.EXPLODE_DMG); p.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    for p in living:
                        if pk.collides(p):
                            pk._explode(); break
            en_pumpkins = [pk for pk in en_pumpkins if pk.alive]

            # Player whips → enemies
            for shooter in players:
                if shooter.pending_whip:
                    shooter.pending_whip = False
                    whips.append(Whip(
                        shooter.x + shooter.facing * 28, shooter.y - 60,
                        shooter.facing, shooter))
            for w in whips:
                w.update()
                if w.can_hit():
                    for en in enemies:
                        if w.collides(en):
                            en.hp = max(0, en.hp - w.DMG)
                            en.flash_timer = 10
                            en.knockback = w.facing * 14
                            w.hit_done = True
                            break
            whips = [w for w in whips if w.alive]

            # Enemy whips → players
            for en in enemies:
                if en.pending_whip:
                    en.pending_whip = False
                    en_whips.append(Whip(
                        en.x + en.facing * 28, en.y - 60,
                        en.facing, en))
            for w in en_whips:
                w.update()
                if w.can_hit():
                    for p in living:
                        if w.collides(p):
                            p.hp = max(0, p.hp - w.DMG)
                            p.flash_timer = 10
                            p.knockback = w.facing * 14
                            w.hit_done = True
                            break
            en_whips = [w for w in en_whips if w.alive]

            # Ink Brush clones (survival)
            for shooter in players:
                if shooter.pending_ink_clone:
                    shooter.pending_ink_clone = False
                    tgt = min(enemies, key=lambda e: abs(e.x - shooter.x)) if enemies else None
                    if tgt:
                        cf = AIFighter(shooter.x + shooter.facing * 55, shooter.char, -shooter.facing, 'medium')
                        cf.hp = max(1, shooter.hp)
                        cf.color = shooter.color
                        cf.no_attack = True
                        ink_clones.append({'fighter': cf, 'timer': FPS * 100, 'target': tgt})
            for en in enemies:
                if en.pending_ink_clone and living:
                    en.pending_ink_clone = False
                    tgt2 = min(living, key=lambda p: abs(p.x - en.x))
                    cf2 = AIFighter(en.x + en.facing * 55, en.char, -en.facing, 'medium')
                    cf2.hp = max(1, en.hp)
                    cf2.color = en.color
                    cf2.no_attack = True
                    ink_clones.append({'fighter': cf2, 'timer': FPS * 8, 'target': tgt2})
            new_ink = []
            for ic in ink_clones:
                ic['timer'] -= 1
                if ic['timer'] > 0 and ic['fighter'].hp > 0:
                    ic['fighter'].update(None, ic['target'], platforms)
                    new_ink.append(ic)
            ink_clones = new_ink

            # Death pops: spawn burst when enemy hp hits 0, then remove enemy
            for en in enemies:
                if en.hp <= 0:
                    death_pops.append({'x': en.x, 'y': en.y - 60,
                                       'color': en.char["color"], 't': 22})
            for dp in death_pops:
                dp['t'] -= 1
            death_pops = [dp for dp in death_pops if dp['t'] > 0]

            # Count kills, remove dead enemies
            before         = len(enemies)
            enemies        = [en for en in enemies if en.hp > 0]
            enemies_killed += before - len(enemies)

            # Jungle snakes
            if is_jungle:
                snake_spawn_timer -= 1
                if snake_spawn_timer <= 0 and len(jungle_snakes) < 4:
                    jungle_snakes.append(JungleSnake())
                    snake_spawn_timer = random.randint(300, 480)
                for sn in jungle_snakes:
                    all_targets = players + enemies
                    living_targets = [t for t in all_targets if t.hp > 0]
                    if living_targets:
                        closest = min(living_targets, key=lambda t: abs(t.x - sn.x))
                        sn.update(closest, closest)
                jungle_snakes = [sn for sn in jungle_snakes if sn.alive]

            if is_underworld:
                skull_spawn_timer -= 1
                if skull_spawn_timer <= 0 and len(falling_skulls) < 8:
                    falling_skulls.append(FallingSkull())
                    skull_spawn_timer = random.randint(120, 280)
                for sk in falling_skulls:
                    sk.update()
                    if sk.hit_cd == 0:
                        for victim in [p for p in players if p.hp > 0] + enemies:
                            if sk.collides(victim):
                                victim.hp = max(0, victim.hp - sk.DMG)
                                victim.flash_timer = 10
                                sk.hit_cd = sk.HIT_CD

            if is_computer:
                bug_spawn_timer -= 1
                if bug_spawn_timer <= 0 and len(computer_bugs) < 5:
                    computer_bugs.append(ComputerBug())
                    bug_spawn_timer = random.randint(200, 360)
                for b in computer_bugs:
                    all_targets = [p for p in players if p.hp > 0] + enemies
                    target = min(all_targets, key=lambda t: abs(t.x - b.x)) if all_targets else None
                    b.update(target)
                computer_bugs = [b for b in computer_bugs if b.alive]
                stage_pencil.update()
                drawn_count = sum(1 for p in platforms if isinstance(p, DrawnPlatform))
                if stage_pencil.pending_plat and drawn_count < StagePencil.MAX_PLATS:
                    stage_pencil.pending_plat = False
                    platforms.append(DrawnPlatform(int(stage_pencil.x) - 50, int(stage_pencil.y) + 20, w=100))
                platforms = stage_eraser.update(platforms)
                for p in platforms:
                    if isinstance(p, DrawnPlatform): p.update()
                platforms = [p for p in platforms if not (isinstance(p, DrawnPlatform) and not p.alive)]
                for pf in [p for p in players if p.hp > 0]:
                    if pf.contact_cooldown == 0:
                        if math.hypot(pf.x - stage_eraser.x, pf.y - stage_eraser.y) < 50:
                            pf.hp = max(0, pf.hp - 5)
                            pf.flash_timer = 8
                            pf.contact_cooldown = 60

            # Powerups (no clone type in survival)
            _survival_pool = [p for p in POWERUPS if p['type'] != 'clone']
            powerup_timer -= 1
            if powerup_timer <= 0 and len(powerups) < 3:
                pu_new = Powerup.__new__(Powerup)
                pu_new.spec = random.choice(_survival_pool)
                pu_new.name = pu_new.spec['name']
                pu_new.color = pu_new.spec['color']
                pu_new.x = float(random.randint(80, WIDTH - 80))
                pu_new.y = float(GROUND_Y - 14)
                pu_new.age = 0
                pu_new.picked_up = False
                powerups.append(pu_new)
                powerup_timer = random.randint(480, 720)
            for pu in powerups:
                pu.update()
                for p in players:
                    if p.hp > 0 and not pu.picked_up and pu.collides(p):
                        p.apply_powerup(pu.spec)
                        pu.picked_up = True; break
                if not pu.picked_up:
                    for en in enemies:
                        if pu.collides(en):
                            en.apply_powerup(pu.spec)
                            pu.picked_up = True; break
            powerups = [pu for pu in powerups if not pu.picked_up]

            # Game over when all players dead
            if all(p.hp <= 0 for p in players):
                game_over = True

        # --- Draw ---
        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for portal in portals_obj_s: portal.draw(screen)
        for plat in platforms:     plat.draw(screen, stage_idx)
        for sp   in springs:       sp.draw(screen)
        for pu   in powerups:      pu.draw(screen)
        for b    in balls:         b.draw(screen)
        for b    in en_balls:      b.draw(screen)
        for o    in orbs:          o.draw(screen)
        for o    in en_orbs:       o.draw(screen)
        for bb   in bounce_balls:  bb.draw(screen)
        for bb   in en_bounce_balls: bb.draw(screen)
        for h    in hooks:         h.draw(screen)
        for h    in en_hooks:      h.draw(screen)
        for pk   in pumpkins:      pk.draw(screen)
        for pk   in en_pumpkins:   pk.draw(screen)
        for w    in whips:         w.draw(screen)
        for w    in en_whips:      w.draw(screen)
        for sn   in jungle_snakes: sn.draw(screen)
        for sk   in falling_skulls: sk.draw(screen)
        for b    in computer_bugs: b.draw(screen)
        if is_computer and stage_pencil:
            stage_pencil.draw(screen)
            stage_eraser.draw(screen)
        for ic   in ink_clones:    ic['fighter'].draw(screen)

        # Draw Laser Eyes beams (survival)
        for f in list(players) + enemies:
            if f.char.get("laser_eyes") and f.laser_active > 0:
                eye_x = int(f.x)
                eye_y = int(f.y - 100)
                end_x = WIDTH if f.facing == 1 else 0
                x = eye_x
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    dash_end = x + f.facing * 18
                    dash_end = min(dash_end, end_x) if f.facing == 1 else max(dash_end, end_x)
                    pygame.draw.line(screen, (255, 40, 0),   (x, eye_y), (dash_end, eye_y), 3)
                    pygame.draw.line(screen, (255, 160, 80), (x, eye_y), (dash_end, eye_y), 1)
                    x = dash_end + f.facing * 6

        # Death burst particles
        for dp in death_pops:
            prog  = 1.0 - dp['t'] / 22
            r     = int(4 + prog * 28)
            col   = dp['color']
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                px  = int(dp['x'] + math.cos(rad) * r * 1.4)
                py  = int(dp['y'] + math.sin(rad) * r)
                cr  = max(1, int(6 * (1.0 - prog)))
                pygame.draw.circle(screen, col, (px, py), cr)
            pygame.draw.circle(screen, WHITE, (int(dp['x']), int(dp['y'])), max(1, int(10 * (1.0 - prog))))

        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen) if two_player else None
        en_hits = [(en, en.draw(screen)) for en in enemies]
        # Bubble shield visuals (survival)
        for f in players:
            if f.bubble_shield:
                bsurf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(bsurf, (100, 200, 255, 70), (50, 50), 48)
                pygame.draw.circle(bsurf, (100, 200, 255, 160), (50, 50), 48, 3)
                screen.blit(bsurf, (int(f.x) - 50, int(f.y) - 90))

        if not game_over:
            # Player attacks hit enemies
            for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                if attacker.attacking and not attacker.attack_hit and hit_pos:
                    for en in enemies:
                        attacker.check_hit(hit_pos, en)
            # Enemy attacks hit players — 2P players can't hurt each other
            for en, en_hit in en_hits:
                if en.attacking and not en.attack_hit and en_hit:
                    for p in players:
                        en.check_hit(en_hit, p)
            # Fighter attacks on jungle snakes
            for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                if attacker.attacking and hit_pos:
                    for sn in jungle_snakes:
                        if math.hypot(hit_pos[0]-sn.x, hit_pos[1]-(sn.y-8)) < 44:
                            dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                   else attacker.char["kick_dmg"])
                            sn.take_damage(dmg)
            # Fighter attacks on computer bugs
            if is_computer:
                for attacker, hit_pos in ([(p1, p1_hit)] + ([(p2, p2_hit)] if two_player else [])):
                    if attacker.attacking and hit_pos:
                        for b in computer_bugs:
                            if math.hypot(hit_pos[0]-b.x, hit_pos[1]-(b.y-8)) < 40:
                                dmg = (attacker.char["punch_dmg"] if attacker.action=='punch'
                                       else attacker.char["kick_dmg"])
                                b.take_damage(dmg)

        # Enemy name tags
        for en in enemies:
            tag = font_tiny.render(en.char["name"], True, en.char["color"])
            screen.blit(tag, (int(en.x) - tag.get_width()//2,
                               int(en.y) - HEAD_R*2 - NECK_LEN - BODY_LEN - LEG_LEN - 22))

        _draw_survival_hud()
        draw_active_powerups(screen, p1, 'left')
        if two_player:
            draw_active_powerups(screen, p2, 'right')
        if game_over:
            _draw_game_over()

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Online fight helpers
# ---------------------------------------------------------------------------

class _KeyProxy:
    """Lets Fighter.update() accept a dict instead of pygame.key.get_pressed()."""
    def __init__(self, mapping):
        self._m = mapping   # {pygame_key_const: bool}
    def __getitem__(self, k): return self._m.get(k, False)
    def get(self, k, d=False): return self._m.get(k, d)


def _f2s(f):
    """Serialize the fields a remote client needs to render a fighter."""
    return {
        'x': f.x, 'y': f.y, 'hp': f.hp,
        'action': f.action, 'action_t': f.action_t,
        'facing': f.facing, 'vy': f.vy, 'on_ground': f.on_ground,
        'knockback': f.knockback,
        'hurt_timer': f.hurt_timer, 'flash_timer': f.flash_timer,
        'draw_scale': f.draw_scale,
        'attacking': f.attacking, 'attack_hit': f.attack_hit,
        'laser_active': f.laser_active,
        'boomerang_timer': f.boomerang_timer,
        'boomerang_angle': f.boomerang_angle,
        'stealth_frames': f.stealth_frames,
        'bubble_shield': f.bubble_shield,
    }


def _s2f(f, s):
    """Apply a serialized state dict to a fighter (client-side rendering)."""
    f.x = s['x']; f.y = s['y']; f.hp = s['hp']
    f.action = s['action']; f.action_t = s['action_t']
    f.facing = s['facing']; f.vy = s['vy']
    f.on_ground = s.get('on_ground', True)
    f.knockback = s['knockback']
    f.hurt_timer = s['hurt_timer']; f.flash_timer = s['flash_timer']
    f.draw_scale = s.get('draw_scale', 1.0)
    f.attacking = s.get('attacking', False)
    f.attack_hit = s.get('attack_hit', False)
    f.laser_active = s.get('laser_active', 0)
    f.boomerang_timer = s.get('boomerang_timer', 0)
    f.boomerang_angle = s.get('boomerang_angle', 0.0)
    f.stealth_frames = s.get('stealth_frames', 0)
    f.bubble_shield = s.get('bubble_shield', False)


# ---------------------------------------------------------------------------
# Online fight loop
# ---------------------------------------------------------------------------

def run_online_fight(net, is_host, p1_char_idx, p2_char_idx,
                     stage_idx, my_name, opp_name):
    """
    Networked 1v1 fight.
    * Host (is_host=True)  runs the authoritative sim and sends STATE each frame.
    * Client (is_host=False) sends INPUT each frame and renders received STATE.
    * p1 = host's fighter (left), p2 = client's fighter (right) on both screens.
    * Both players use P1_CTRL (WASD/FG) on their own machines; the client's
      inputs are remapped to P2_CTRL by the host before simulation.
    """
    _stage_name   = STAGES[stage_idx % len(STAGES)]["name"]
    _orig_gravity = constants.GRAVITY
    if _stage_name == "Space":
        constants.GRAVITY = 0.13
    constants.STAGE_VOID = (_stage_name == "The Void")

    P1_CTRL = dict(left=pygame.K_a,     right=pygame.K_d,     jump=pygame.K_w,
                   punch=pygame.K_f,    kick=pygame.K_g,      duck=pygame.K_s,
                   block=pygame.K_r)
    P2_CTRL = dict(left=pygame.K_LEFT,  right=pygame.K_RIGHT, jump=pygame.K_UP,
                   punch=pygame.K_k,    kick=pygame.K_l,      duck=pygame.K_DOWN,
                   block=pygame.K_o)

    p1 = Fighter(200, CHARACTERS[p1_char_idx],  1, P1_CTRL)
    p2 = Fighter(700, CHARACTERS[p2_char_idx], -1, {})

    if constants.STAGE_VOID:
        p1.x = 380.0; p1.y = float(GROUND_Y - 70); p1.on_ground = True
        p2.x = 520.0; p2.y = float(GROUND_Y - 70); p2.on_ground = True

    stage_data   = STAGES[stage_idx % len(STAGES)]
    platforms    = [Platform(*p) for p in stage_data["platforms"]]
    springs      = [Spring(*s)   for s in stage_data["springs"]]
    balls        = []; orbs = []; bounce_balls = []; hooks = []; pumpkins = []; whips = []

    # Easter eggs
    hot_potatoes   = []
    crazy_snakes   = []
    crazy_bugs     = []
    crazy_timer    = 0
    _chat_done     = 0   # index into net.chat_log already processed for easter eggs

    game_over    = False
    winner       = None
    timer        = 90 * FPS
    _remote_keys = {}   # action → bool  (latest from opponent; host uses for p2)

    # Chat
    chat_active  = False
    chat_input   = ""

    def _local_actions(keys, ctrl):
        return {a: bool(keys[ctrl[a]]) for a in ctrl}

    def _proxy(actions, ctrl):
        """Map {action: bool} through ctrl keys into a _KeyProxy."""
        return _KeyProxy({ctrl[a]: actions.get(a, False) for a in ctrl})

    while True:
        clock.tick(FPS)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                constants.GRAVITY = _orig_gravity
                constants.STAGE_VOID = False
                net.close(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if chat_active:
                    if event.key == pygame.K_RETURN:
                        if chat_input.strip():
                            net.send_chat(chat_input)
                        chat_active = False; chat_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        chat_active = False; chat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    elif event.unicode.isprintable():
                        chat_input += event.unicode
                else:
                    if event.key == pygame.K_t:
                        chat_active = True
                    if game_over and event.key in (pygame.K_q, pygame.K_ESCAPE,
                                                   pygame.K_RETURN, pygame.K_r):
                        constants.GRAVITY = _orig_gravity
                        constants.STAGE_VOID = False
                        net.close(); return 'select'

        if not net.connected and not game_over:
            game_over = True
            winner    = "disconnect"

        # ── Network ─────────────────────────────────────────────────────────
        msgs = net.recv_all()
        keys = pygame.key.get_pressed()

        # ── Easter eggs (host-authoritative; triggered by chat keywords) ────
        if is_host and not game_over:
            while _chat_done < len(net.chat_log):
                sender, text = net.chat_log[_chat_done]
                kw = text.strip().lower()
                if kw == "hotpotato":
                    hot_potatoes.append(HotPotato())
                elif kw == "wtf":
                    target = p1 if sender == "You" else p2
                    target.hp = max(0, target.hp - 10)
                    target.flash_timer = 25
                elif kw == "crazy":
                    crazy_timer = FPS * 8   # 8 seconds of chaos
                _chat_done += 1

        if is_host and not game_over:
            # Collect latest client input
            for m in msgs:
                if m.get("type") == "INPUT":
                    _remote_keys = m

            # Simulate p1 (local)
            p1.update(keys, p2, platforms)

            # Simulate p2 using client's inputs remapped through P2_CTRL
            p2.update(_proxy(_remote_keys, P2_CTRL), p1, platforms)

            # Spawn projectiles for both fighters
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_ball:
                    shooter.pending_ball = False
                    balls.append(Projectile(shooter.x + shooter.facing * 30,
                                            shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_orb:
                    shooter.pending_orb = False
                    orbs.append(Orb(shooter.x + shooter.facing * 30,
                                    shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_bounce:
                    shooter.pending_bounce = False
                    bounce_balls.append(BouncingBall(shooter.x + shooter.facing * 30,
                                                     shooter.y - 60, shooter.facing, shooter))
                if shooter.pending_hook:
                    shooter.pending_hook = False
                    hooks.append(SnakeHook(shooter.x + shooter.facing * 20, shooter.y - 60,
                                           victim.x, victim.y - 60, shooter))
                if shooter.pending_pumpkin:
                    shooter.pending_pumpkin = False
                    pumpkins.append(Pumpkin(shooter.x + shooter.facing * 24,
                                            shooter.y - 80, shooter.facing, shooter))

            # Update projectiles
            for b in balls:
                b.update()
                if b.alive:
                    victim = p2 if b.owner is p1 else p1
                    if b.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8; b.alive = False
            balls = [b for b in balls if b.alive]

            for o in orbs:
                o.update()
                if o.exploding and not o.damaged:
                    o.damaged = True
                    victim = p2 if o.owner is p1 else p1
                    if math.hypot(o.x - victim.x, o.y - (victim.y - 60)) < o.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - o.EXPLODE_DMG)
                        victim.flash_timer = 14
            orbs = [o for o in orbs if o.alive]

            for bb in bounce_balls:
                bb.update()
                if bb.alive and bb.hit_cd == 0:
                    victim = p2 if bb.owner is p1 else p1
                    if bb.collides(victim):
                        victim.hp = max(0, victim.hp - 10)
                        victim.flash_timer = 8; bb.hit_cd = BouncingBall.HIT_CD
            bounce_balls = [bb for bb in bounce_balls if bb.alive]

            for h in hooks:
                h.update()
                if h.alive:
                    victim = p2 if h.owner is p1 else p1
                    if h.collides(victim):
                        pull = 1 if h.owner.x > victim.x else -1
                        victim.knockback = pull * 22
                        victim.hp = max(0, victim.hp - 6)
                        victim.flash_timer = 8; h.alive = False
            hooks = [h for h in hooks if h.alive]

            for pk in pumpkins:
                pk.update()
                if pk.exploding and not pk.damaged:
                    pk.damaged = True
                    victim = p2 if pk.owner is p1 else p1
                    if math.hypot(pk.x - victim.x, pk.y - (victim.y - 60)) < pk.EXPLODE_RADIUS:
                        victim.hp = max(0, victim.hp - pk.EXPLODE_DMG)
                        victim.flash_timer = 14
                elif not pk.exploding and not pk.damaged:
                    victim = p2 if pk.owner is p1 else p1
                    if pk.collides(victim): pk._explode()
            pumpkins = [pk for pk in pumpkins if pk.alive]

            # Whips
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if shooter.pending_whip:
                    shooter.pending_whip = False
                    whips.append(Whip(
                        shooter.x + shooter.facing * 28, shooter.y - 60,
                        shooter.facing, shooter))
            for w in whips:
                w.update()
                if w.can_hit():
                    victim = p2 if w.owner is p1 else p1
                    if w.collides(victim):
                        victim.hp = max(0, victim.hp - w.DMG)
                        victim.flash_timer = 10
                        victim.knockback = w.facing * 14
                        w.hit_done = True
            whips = [w for w in whips if w.alive]

            # Hot potatoes
            for hp in hot_potatoes:
                hp.update()
                if hp.exploding and not hp.damaged:
                    hp.damaged = True
                    for f in (p1, p2):
                        if hp.collides(f):
                            f.hp = max(0, f.hp - hp.EXPLODE_DMG)
                            f.flash_timer = 20
            hot_potatoes = [hp for hp in hot_potatoes if hp.alive]

            # Crazy mode — rapid snake & bug spawning
            if crazy_timer > 0:
                crazy_timer -= 1
                if crazy_timer % 10 == 0:
                    crazy_snakes.append(JungleSnake())
                if crazy_timer % 7 == 0:
                    crazy_bugs.append(ComputerBug())
            for sn in crazy_snakes:
                sn.update(p1, p2)   # biting handled internally
            crazy_snakes = [sn for sn in crazy_snakes if sn.alive]
            for cb in crazy_bugs:
                target = min((p1, p2), key=lambda f: abs(f.x - cb.x))
                cb.update(target)   # biting handled internally
            crazy_bugs = [cb for cb in crazy_bugs if cb.alive]

            # Laser eyes
            for shooter, victim in [(p1, p2), (p2, p1)]:
                if (shooter.char.get("laser_eyes") and shooter.laser_active > 0
                        and shooter.laser_hit_cd == 0):
                    laser_y = shooter.y - 100
                    side_ok  = ((shooter.facing ==  1 and victim.x > shooter.x) or
                                (shooter.facing == -1 and victim.x < shooter.x))
                    if side_ok and abs((victim.y - 60) - laser_y) < 35:
                        victim.hp = max(0, victim.hp - 2)
                        victim.flash_timer = 4; shooter.laser_hit_cd = 15

            # Boomerang
            for thrower, victim in [(p1, p2), (p2, p1)]:
                if thrower.boomerang_timer > 0 and thrower.boomerang_hit_cd == 0:
                    bx = thrower.x + math.cos(thrower.boomerang_angle) * 85
                    by = (thrower.y - 60) + math.sin(thrower.boomerang_angle) * 55
                    if math.hypot(bx - victim.x, by - (victim.y - 60)) < 48:
                        victim.hp = max(0, victim.hp - 8)
                        victim.flash_timer = 6; thrower.boomerang_hit_cd = 30

            # Springs
            for sp in springs:
                sp.update(); sp.trigger(p1); sp.trigger(p2)

            # Timer / game over
            timer -= 1
            if p1.hp <= 0 or p2.hp <= 0 or timer <= 0:
                game_over = True
                if   p1.hp > p2.hp: winner = "p1"
                elif p2.hp > p1.hp: winner = "p2"
                else:               winner = "draw"

            # Send authoritative state to client
            net.send({
                "type":   "STATE",
                "p1":     _f2s(p1),
                "p2":     _f2s(p2),
                "balls":  [{"x": b.x, "y": b.y, "vx": b.vx} for b in balls],
                "orbs":   [{"x": o.x, "y": o.y, "exp": o.exploding} for o in orbs],
                "winner": winner,
            })

        elif not is_host:
            # Send our (client's) inputs as action booleans
            if not game_over:
                net.send({"type": "INPUT",
                          **_local_actions(keys, P1_CTRL)})

            # Apply received state
            for m in msgs:
                if m.get("type") == "STATE":
                    _s2f(p1, m["p1"]); _s2f(p2, m["p2"])
                    winner = m.get("winner")
                    if winner:
                        game_over = True
                    # Reconstruct ball visuals from state
                    balls = []
                    for bd in m.get("balls", []):
                        b = Projectile.__new__(Projectile)
                        b.x = bd["x"]; b.y = bd["y"]
                        b.vx = bd["vx"]; b.alive = True; b.owner = None
                        balls.append(b)

            # Springs (visual only on client — host is authoritative)
            for sp in springs:
                sp.update()

        # ── Draw ────────────────────────────────────────────────────────────
        draw_bg(screen, stage_idx)
        pygame.draw.rect(screen, (60, 60, 70), (0, 0, WIDTH, 20))
        pygame.draw.line(screen, (180, 180, 200), (0, 20), (WIDTH, 20), 3)
        for plat in platforms: plat.draw(screen, stage_idx)
        for sp   in springs:   sp.draw(screen)
        for b    in balls:     b.draw(screen)
        for o    in orbs:      o.draw(screen)
        for bb   in bounce_balls: bb.draw(screen)
        for h    in hooks:     h.draw(screen)
        for pk   in pumpkins:  pk.draw(screen)
        for w    in whips:     w.draw(screen)

        # Laser beams
        for f in (p1, p2):
            if f.char.get("laser_eyes") and f.laser_active > 0:
                ex, ey  = int(f.x), int(f.y - 100)
                end_x   = WIDTH if f.facing == 1 else 0
                x = ex
                while (f.facing == 1 and x < end_x) or (f.facing == -1 and x > end_x):
                    de = x + f.facing * 18
                    de = min(de, end_x) if f.facing == 1 else max(de, end_x)
                    pygame.draw.line(screen, (255, 40, 0),   (x, ey), (de, ey), 3)
                    pygame.draw.line(screen, (255, 160, 80), (x, ey), (de, ey), 1)
                    x = de + f.facing * 6

        for hp in hot_potatoes:  hp.draw(screen)
        for sn in crazy_snakes:  sn.draw(screen)
        for cb in crazy_bugs:    cb.draw(screen)

        p1_hit = p1.draw(screen)
        p2_hit = p2.draw(screen)

        # Bubble shields
        for f in (p1, p2):
            if f.bubble_shield:
                bsurf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(bsurf, (100, 200, 255, 70),  (50, 50), 48)
                pygame.draw.circle(bsurf, (100, 200, 255, 160), (50, 50), 48, 3)
                screen.blit(bsurf, (int(f.x) - 50, int(f.y) - 90))

        # Melee hit detection (authoritative — host only)
        if is_host and not game_over:
            for attacker, hit_pos, other in [(p1, p1_hit, p2), (p2, p2_hit, p1)]:
                if attacker.attacking and not attacker.attack_hit and hit_pos:
                    attacker.check_hit(hit_pos, other)

        # HUD — health bars + names + timer
        p1_label = my_name  if is_host else opp_name
        p2_label = opp_name if is_host else my_name
        draw_health_bars_labeled(screen, p1, p2, f"{p2_label} — {p2.char['name']}")
        for f, lbl in [(p1, p1_label), (p2, p2_label)]:
            ns = font_tiny.render(lbl, True, f.char["color"])
            screen.blit(ns, (int(f.x) - ns.get_width()//2, int(f.y) - 148))

        if not game_over:
            secs = max(0, timer // FPS)
            tc = WHITE if secs > 10 else RED
            ts = font_medium.render(str(secs), True, tc)
            screen.blit(ts, (WIDTH//2 - ts.get_width()//2, 25))

        # Chat overlay
        recent = net.chat_log[-5:]
        for i, (sender, text) in enumerate(recent):
            col  = CYAN if sender == "You" else YELLOW
            line = font_tiny.render(f"{sender}: {text}", True, col)
            screen.blit(line, (10, HEIGHT - 110 + i * 18))
        if chat_active:
            pygame.draw.rect(screen, (30, 30, 50), (0, HEIGHT - 36, WIDTH, 36))
            cur = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            ci  = font_small.render("Say: " + chat_input + cur, True, WHITE)
            screen.blit(ci, (10, HEIGHT - 30))
        else:
            ht = font_tiny.render("T = chat", True, (70, 70, 70))
            screen.blit(ht, (10, HEIGHT - 16))

        # Win / disconnect screen
        if game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            if winner == "disconnect":
                wt = font_large.render("DISCONNECTED", True, RED)
            elif winner == "draw":
                wt = font_large.render("DRAW!", True, YELLOW)
            elif (winner == "p1") == is_host:
                wt = font_large.render("YOU WIN!", True, GREEN)
            else:
                wt = font_large.render("YOU LOSE!", True, RED)
            screen.blit(wt, (WIDTH//2 - wt.get_width()//2, HEIGHT//3))
            ht = font_small.render("Any key — back to menu", True, WHITE)
            screen.blit(ht, (WIDTH//2 - ht.get_width()//2, HEIGHT//2 + 40))

        pygame.display.flip()

    constants.GRAVITY    = _orig_gravity
    constants.STAGE_VOID = False
    net.close()
    return 'select'


# ---------------------------------------------------------------------------
# Relay fight (matchmaking via fight_server.py)
# ---------------------------------------------------------------------------

class _RelayNet:
    """
    Thin adapter so run_online_fight() can drive a LobbyClient with the
    same send / recv_all / send_chat / chat_log / close interface it uses
    for GameServer / GameClient.
    """
    def __init__(self, lobby):
        self._lobby   = lobby
        self.chat_log = lobby.match_chat_log   # shared reference
        self.opp_name = (lobby.match_info or {}).get("opp_name", "Opponent")

    @property
    def connected(self):
        return self._lobby.connected

    def send(self, obj):
        self._lobby.relay(obj)

    def recv_all(self):
        return self._lobby.poll()   # already returns unwrapped relay payloads

    def send_chat(self, text):
        self._lobby.match_chat(text)

    def close(self):
        self._lobby.close()


def run_relay_fight(lobby, is_host, p1_char_idx, p2_char_idx,
                    stage_idx, my_name, opp_name):
    """Wrapper: create a _RelayNet adapter and delegate to run_online_fight."""
    net = _RelayNet(lobby)
    net.opp_name = opp_name
    return run_online_fight(net, is_host, p1_char_idx, p2_char_idx,
                            stage_idx, my_name, opp_name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    while True:
        mode = mode_select()

        # --- Online path ---
        if mode == 'online':
            userdata = _net.load_userdata()
            result   = online_menu(userdata)
            if result is None:
                continue
            role, info = result
            if role == 'quickmatch':
                # info = (lobby, p1_char_idx, p2_char_idx, stage_idx, is_host, opp_name)
                lobby, p1_char, p2_char, s_idx, is_host, opp_name = info
                run_relay_fight(lobby, is_host, p1_char, p2_char,
                                s_idx, userdata['username'], opp_name)
            else:
                net, my_char, opp_char, s_idx = info
                if role == 'host':
                    p1_char, p2_char = my_char, opp_char
                else:
                    p1_char, p2_char = opp_char, my_char
                run_online_fight(net, role == 'host', p1_char, p2_char,
                                 s_idx, userdata['username'], net.opp_name)
            continue

        # --- Survival path ---
        if mode in ('survival_1p', 'survival_2p'):
            two_player = (mode == 'survival_2p')
            p1_idx, p2_idx = character_select(vs_ai=not two_player)
            if p1_idx is None:
                continue
            s_idx = stage_select()
            while True:
                result = run_survival(p1_idx, p2_idx if two_player else None,
                                      two_player=two_player, stage_idx=s_idx)
                if result == 'rematch':
                    continue
                break
            continue

        # --- Normal fight path ---
        if mode == '2p':
            vs_ai, difficulty = False, 'medium'
        else:
            vs_ai, difficulty = True, mode[1]

        p1_idx, p2_idx = character_select(vs_ai=vs_ai)
        if p1_idx is None:
            continue

        s_idx = stage_select()
        while True:
            result = run_fight(p1_idx, p2_idx, vs_ai=vs_ai, ai_difficulty=difficulty, stage_idx=s_idx)
            if result == 'rematch':
                continue
            break

if __name__ == "__main__":
    main()
