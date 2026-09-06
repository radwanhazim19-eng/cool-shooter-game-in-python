import os
import time
import random
import sys

try:
    import msvcrt
except ImportError:
    print("This script requires 'msvcrt' (Windows standard library).")
    sys.exit()

# --- ENABLE ANSI COLORS ON WINDOWS ---
os.system('')

# --- COLOR PALETTE & ANSI CODES ---
RESET = '\033[0m'
RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
BLUE = '\033[94m'; CYAN = '\033[96m'; WHITE = '\033[97m'
GRAY = '\033[90m'; MAGENTA = '\033[95m'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'
CURSOR_HOME = '\033[H'

# --- ENGINE SETTINGS ---
VIEW_WIDTH = 80
VIEW_HEIGHT = 20
MAP_WIDTH = 150
MAP_HEIGHT = 40

DIR_VECTORS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIR_CHARS = ['^', '>', 'v', '<']

WEAPONS = {
    '1': {'name': 'Pistol', 'max': 12, 'spread': False, 'color': GRAY},
    '2': {'name': 'Shotgun', 'max': 6, 'spread': True, 'color': RED},
    '3': {'name': 'Rifle', 'max': 30, 'spread': False, 'color': YELLOW}
}

# --- DYNAMIC SETTINGS MENU ---
SETTINGS = {
    "teammates": 1,
    "civilians": 15,
    "friendly_fire": True,
    "start_wep": '1'
}

def clear_screen_once():
    os.system('cls' if os.name == 'nt' else 'clear')

def bresenham_line(r1, c1, r2, c2):
    points = []
    dr = abs(r2 - r1); dc = abs(c2 - c1)
    sr = 1 if r1 < r2 else -1; sc = 1 if c1 < c2 else -1
    err = dr - dc
    while True:
        points.append((r1, c1))
        if r1 == r2 and c1 == c2: break
        e2 = 2 * err
        if e2 > -dc: err -= dc; r1 += sr
        if e2 < dr: err += dr; c1 += sc
    return points

def has_line_of_sight(r1, c1, r2, c2, walls):
    line = bresenham_line(r1, c1, r2, c2)
    for p in line:
        if p in walls and p != (r1, c1) and p != (r2, c2): return False
    return True

def settings_menu():
    while True:
        clear_screen_once()
        print(f"{CYAN}=== ADVANCED SETTINGS ===\n{RESET}")
        print(f"{WHITE}1. AI Teammates Deploying:{RESET} {GREEN}{SETTINGS['teammates']}{RESET} (0-3)")
        print(f"{WHITE}2. Civilian Density:{RESET}       {BLUE}{SETTINGS['civilians']}{RESET} (0, 15, 30, 50)")
        print(f"{WHITE}3. Friendly Fire:{RESET}          {RED if SETTINGS['friendly_fire'] else GREEN}{'ON' if SETTINGS['friendly_fire'] else 'OFF'}{RESET}")
        print(f"{WHITE}4. Starting Weapon:{RESET}        {WEAPONS[SETTINGS['start_wep']]['color']}{WEAPONS[SETTINGS['start_wep']]['name']}{RESET}")
        print(f"\n{GRAY}Press 1-4 to change, 'O' to return{RESET}")
        
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                if key == '1': 
                    SETTINGS['teammates'] = (SETTINGS['teammates'] + 1) % 4; break
                elif key == '2':
                    if SETTINGS['civilians'] == 0: SETTINGS['civilians'] = 15
                    elif SETTINGS['civilians'] == 15: SETTINGS['civilians'] = 30
                    elif SETTINGS['civilians'] == 30: SETTINGS['civilians'] = 50
                    else: SETTINGS['civilians'] = 0
                    break
                elif key == '3':
                    SETTINGS['friendly_fire'] = not SETTINGS['friendly_fire']; break
                elif key == '4':
                    w = int(SETTINGS['start_wep']) + 1
                    if w > 3: w = 1
                    SETTINGS['start_wep'] = str(w); break
                elif key == 'o': 
                    return

def main_menu():
    while True:
        clear_screen_once()
        print(f"{CYAN}=== TACTICAL DEPLOYMENT: MAP SELECTION ==={RESET}\n")
        print(f"{GREEN}1.{RESET} High School         {GREEN}9.{RESET} Casino Resort")
        print(f"{GREEN}2.{RESET} Downtown Bank       {GREEN}A.{RESET} Art Museum")
        print(f"{GREEN}3.{RESET} Shopping Mall       {GREEN}B.{RESET} Cruise Ship")
        print(f"{GREEN}4.{RESET} City Hospital       {GREEN}C.{RESET} Military Base")
        print(f"{GREEN}5.{RESET} Corp. Office        {GREEN}D.{RESET} Subway Station")
        print(f"{GREEN}6.{RESET} Warehouse           {GREEN}E.{RESET} Airport Terminal")
        print(f"{GREEN}7.{RESET} City Park           {GREEN}F.{RESET} Mansion Estate")
        print(f"{GREEN}8.{RESET} Prison Block")
        print(f"\n{YELLOW}S.{RESET} Settings Menu")
        print(f"{RED}O.{RESET} Quit Game\n")
        
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                maps = {
                    '1': "School", '2': "Bank", '3': "Mall", '4': "Hospital",
                    '5': "Office", '6': "Warehouse", '7': "Park", '8': "Prison",
                    '9': "Casino", 'a': "Museum", 'b': "Ship", 'c': "Base",
                    'd': "Subway", 'e': "Airport", 'f': "Mansion"
                }
                if key in maps: return maps[key]
                elif key == 's': settings_menu(); break 
                elif key == 'o': sys.exit()

def make_room(walls, r, c, w, h, door_side='bottom'):
    for i in range(w):
        walls.add((r, c+i)); walls.add((r+h-1, c+i))
    for i in range(h):
        walls.add((r+i, c)); walls.add((r+i, c+w-1))
    
    center_c, center_r = c + w//2, r + h//2
    if door_side == 'bottom': 
        walls.discard((r+h-1, center_c)); walls.discard((r+h-1, center_c-1))
    elif door_side == 'top': 
        walls.discard((r, center_c)); walls.discard((r, center_c-1))
    elif door_side == 'left': 
        walls.discard((center_r, c)); walls.discard((center_r-1, c))
    elif door_side == 'right': 
        walls.discard((center_r, c+w-1)); walls.discard((center_r-1, c+w-1))

def generate_huge_map(loc_type):
    walls = set()
    for r in range(MAP_HEIGHT):
        walls.add((r, 0)); walls.add((r, MAP_WIDTH-1))
    for c in range(MAP_WIDTH):
        walls.add((0, c)); walls.add((MAP_HEIGHT-1, c))
        
    if loc_type == "School":
        for c in range(5, MAP_WIDTH-15, 18):
            make_room(walls, 2, c, random.randint(14, 18), 16, 'bottom') 
            make_room(walls, 22, c, random.randint(14, 18), 16, 'top') 
    elif loc_type == "Bank":
        vault_w, vault_h = random.randint(25, 35), random.randint(12, 16)
        vr, vc = 5, MAP_WIDTH - vault_w - 5
        for i in range(vault_h):
            for j in range(vault_w):
                if i < 2 or i > vault_h-3 or j < 2 or j > vault_w-3: walls.add((vr+i, vc+j))
        walls.discard((vr+vault_h//2, vc)); walls.discard((vr+vault_h//2 - 1, vc))
        for r in range(10, 30, 5):
            for c in range(25, 60):
                if c == 40 and r % 10 != 0: walls.add((r, c)) 
                if 30 < c < 35 and random.random() > 0.5: walls.add((r, c)) 
    elif loc_type == "Mall":
        for c in range(4, MAP_WIDTH-15, 22):
            make_room(walls, 2, c, random.randint(15, 20), 14, 'bottom')
            make_room(walls, 24, c, random.randint(15, 20), 14, 'top')
        for c in range(20, MAP_WIDTH-20, 30):
            if random.random() > 0.3:
                walls.add((19, c)); walls.add((19, c+1))
                walls.add((20, c)); walls.add((20, c+1))
    elif loc_type == "Hospital":
        for r in range(2, MAP_HEIGHT-2, 9):
            for c in range(2, MAP_WIDTH-12, 14):
                if 17 <= r <= 23 or 65 <= c <= 75: continue 
                make_room(walls, r, c, 12, 7, random.choice(['top', 'bottom', 'left', 'right']))
    elif loc_type == "Office":
        for r in range(4, MAP_HEIGHT-4, 6):
            for c in range(8, MAP_WIDTH-8, 10):
                if random.random() > 0.2:
                    walls.add((r, c)); walls.add((r, c+1)); walls.add((r, c+2))
                    walls.add((r+1, c)); walls.add((r+2, c))
    elif loc_type == "Warehouse":
        for c in range(12, MAP_WIDTH-10, 14):
            for r in range(4, 16): walls.add((r, c)); walls.add((r, c+1))
            for r in range(22, 36): walls.add((r, c)); walls.add((r, c+1))
    elif loc_type == "Park":
        for _ in range(180):
            r, c = random.randint(2, MAP_HEIGHT-5), random.randint(2, MAP_WIDTH-5)
            size = random.randint(1, 3)
            for i in range(size):
                for j in range(size):
                    if random.random() > 0.3: walls.add((r+i, c+j))
    # --- 8 NEW MAPS ---
    elif loc_type == "Prison":
        for r in range(2, MAP_HEIGHT-8, 6):
            for c in range(4, MAP_WIDTH-4, 8):
                if 60 < c < 90: continue # Central guard area
                make_room(walls, r, c, 8, 6, 'right' if c < 60 else 'left')
    elif loc_type == "Casino":
        for r in range(5, MAP_HEIGHT-5, 3):
            for c in range(5, MAP_WIDTH-5, 4):
                if random.random() > 0.4: walls.add((r, c)); walls.add((r, c+1)) # Slot machines
    elif loc_type == "Museum":
        for dist in range(6, 18, 5):
            for c in range(dist*2, MAP_WIDTH-dist*2):
                if c % 10 != 0: walls.add((dist, c)); walls.add((MAP_HEIGHT-dist, c))
            for r in range(dist, MAP_HEIGHT-dist):
                if r % 8 != 0: walls.add((r, dist*2)); walls.add((r, MAP_WIDTH-dist*2))
    elif loc_type == "Ship":
        for r in range(0, 12): 
            for c in range(MAP_WIDTH): walls.add((r, c)) # Ocean top
        for r in range(28, MAP_HEIGHT): 
            for c in range(MAP_WIDTH): walls.add((r, c)) # Ocean bottom
        for c in range(10, MAP_WIDTH-10, 10):
            make_room(walls, 12, c, 10, 6, 'bottom') # Upper cabins
            make_room(walls, 22, c, 10, 6, 'top') # Lower cabins
    elif loc_type == "Base":
        for c in range(20, MAP_WIDTH-20, 30):
            for r in [5, 25]:
                for i in range(8):
                    for j in range(12):
                        if i == 0 or i == 7 or j == 0 or j == 11: walls.add((r+i, c+j))
                walls.discard((r+7, c+5)); walls.discard((r+7, c+6)) # Bunker doors
    elif loc_type == "Subway":
        for c in range(MAP_WIDTH):
            if c % 5 != 0: walls.add((12, c)); walls.add((28, c)) # Train tracks barrier
        for r in range(15, 25, 4):
            for c in range(10, MAP_WIDTH-10, 15):
                walls.add((r, c)); walls.add((r+1, c)); walls.add((r, c+1)); walls.add((r+1, c+1)) # Pillars
    elif loc_type == "Airport":
        for c in range(MAP_WIDTH//2 - 5, MAP_WIDTH//2 + 5):
            for r in range(5, 35, 2): walls.add((r, c)) # Security lanes
        make_room(walls, 2, 2, 30, 36, 'right') # Terminal A
        make_room(walls, 2, MAP_WIDTH-32, 30, 36, 'left') # Terminal B
    elif loc_type == "Mansion":
        make_room(walls, 2, MAP_WIDTH//2 - 20, 40, 10, 'bottom') # Grand Hall
        for c in [10, MAP_WIDTH-40]:
            make_room(walls, 15, c, 30, 20, 'top') # East/West Wings

    return walls

def get_safe_spawn(walls):
    while True:
        r = random.randint(2, MAP_HEIGHT - 3)
        c = random.randint(2, MAP_WIDTH - 3)
        if (r, c) not in walls: return r, c

def game_loop():
    sys.stdout.write(HIDE_CURSOR)
    try:
        while True:
            loc_name = main_menu()
            
            clear_screen_once()
            walls = generate_huge_map(loc_name)
            
            pr, pc = get_safe_spawn(walls)
            player = {'r': pr, 'c': pc, 'dir': 1, 'hp': 100, 'wep': SETTINGS['start_wep'], 'ammo': WEAPONS[SETTINGS['start_wep']]['max'], 'grenades': 3}
            
            enemies = []
            for _ in range(random.randint(1, 2)): # MAX 2 SHOOTERS
                er, ec = get_safe_spawn(walls)
                enemies.append({'r': er, 'c': ec})
                
            civilians = []
            for _ in range(SETTINGS['civilians']):
                cr, cc = get_safe_spawn(walls)
                civilians.append({'r': cr, 'c': cc})

            teammates = []
            for _ in range(SETTINGS['teammates']):
                tr, tc = get_safe_spawn(walls)
                teammates.append({'r': tr, 'c': tc})
            
            bullets, grenades, particles, loot = [], [], [], []
            score, msg = 0, f"{YELLOW}Secure the {loc_name}. Press G to throw Grenades.{RESET}"
            
            while msvcrt.kbhit(): msvcrt.getch()

            while True:
                cam_r = max(0, min(player['r'] - VIEW_HEIGHT // 2, MAP_HEIGHT - VIEW_HEIGHT))
                cam_c = max(0, min(player['c'] - VIEW_WIDTH // 2, MAP_WIDTH - VIEW_WIDTH))

                sys.stdout.write(CURSOR_HOME)
                screen_buffer = []

                hp_color = GREEN if player['hp'] > 50 else (YELLOW if player['hp'] > 20 else RED)
                screen_buffer.append(f"{CYAN}=== TACTICAL ENGINE v3.0 | LOC: {loc_name.upper()} ==={RESET}".ljust(VIEW_WIDTH + 10))
                screen_buffer.append(f"HP: {hp_color}{player['hp']:03d}{RESET} | SCO: {score:04d} | TGT: {RED}{len(enemies):02d}{RESET} | CIV: {BLUE}{len(civilians):02d}{RESET}".ljust(VIEW_WIDTH + 10))
                screen_buffer.append(f"WEP: {WEAPONS[player['wep']]['color']}{WEAPONS[player['wep']]['name']:<7}{RESET} | AMMO: {YELLOW}{player['ammo']:02d}{RESET} | GRENADES: {MAGENTA}{player['grenades']}{RESET}".ljust(VIEW_WIDTH + 10))
                screen_buffer.append(f"{msg}".ljust(VIEW_WIDTH + 10))
                
                grid = [[(' ', RESET) for _ in range(VIEW_WIDTH)] for _ in range(VIEW_HEIGHT)]
                
                def draw(world_r, world_c, char, color):
                    vr, vc = world_r - cam_r, world_c - cam_c
                    if 0 <= vr < VIEW_HEIGHT and 0 <= vc < VIEW_WIDTH:
                        grid[vr][vc] = (char, color)

                for r, c in walls: draw(r, c, '█', GRAY)
                for l in loot: draw(l['r'], l['c'], '+', GREEN)
                for p in particles: draw(p['r'], p['c'], p['char'], p['color'])
                for b in bullets: draw(b['r'], b['c'], '-' if b['team'] else '*', YELLOW if b['team'] else RED)
                for g in grenades: draw(g['r'], g['c'], 'o', MAGENTA)
                for c in civilians: draw(c['r'], c['c'], 'C', CYAN)
                for t in teammates: draw(t['r'], t['c'], 'T', GREEN)
                for e in enemies: draw(e['r'], e['c'], 'X', RED)
                
                draw(player['r'], player['c'], DIR_CHARS[player['dir']], GREEN)

                for row in grid:
                    screen_buffer.append("".join([c + char for char, c in row]) + RESET)
                    
                sys.stdout.write("\n".join(screen_buffer) + "\n")
                sys.stdout.flush()
                msg = "" 

                if player['hp'] <= 0:
                    print(f"\n{RED}OFFICER DOWN - MISSION FAILED{RESET}"); time.sleep(3); break
                if len(enemies) == 0:
                    print(f"\n{GREEN}AREA SECURED! Score: {score}{RESET}"); time.sleep(3); break

                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    nr, nc = player['r'], player['c']
                    
                    if key == 'w': nr -= 1
                    elif key == 's': nr += 1
                    elif key == 'a': nc -= 1
                    elif key == 'd': nc += 1
                    elif key == 'q': player['dir'] = (player['dir'] - 1) % 4
                    elif key == 'e': player['dir'] = (player['dir'] + 1) % 4
                    elif key in ('1', '2', '3'): 
                        player['wep'] = key; player['ammo'] = WEAPONS[key]['max']; msg = f"Equipped {WEAPONS[key]['name']}"
                    elif key == 'r': 
                        player['ammo'] = WEAPONS[player['wep']]['max']; msg = "Reloading..."
                    elif key == 'g' and player['grenades'] > 0:
                        dr, dc = DIR_VECTORS[player['dir']]
                        grenades.append({'r': player['r'], 'c': player['c'], 'dr': dr, 'dc': dc, 'timer': 4})
                        player['grenades'] -= 1; msg = f"{MAGENTA}Grenade out!{RESET}"
                    elif key == ' ': 
                        if player['ammo'] > 0:
                            dr, dc = DIR_VECTORS[player['dir']]
                            bullets.append({'r': player['r'], 'c': player['c'], 'dr': dr, 'dc': dc, 'team': True})
                            if WEAPONS[player['wep']]['spread']: 
                                for d1, d2 in ([(-1, 1), (1, 1)] if dc != 0 else [(1, -1), (1, 1)]):
                                    bullets.append({'r': player['r'], 'c': player['c'], 'dr': dr or d1, 'dc': dc or d2, 'team': True})
                            player['ammo'] -= 1
                        else: msg = f"{RED}*CLICK* Reload!{RESET}"
                    elif key == 'o': 
                        break

                    if (nr, nc) not in walls and 0 <= nr < MAP_HEIGHT and 0 <= nc < MAP_WIDTH:
                        player['r'], player['c'] = nr, nc
                        for l in list(loot):
                            if l['r'] == nr and l['c'] == nc:
                                player['hp'] = min(100, player['hp'] + 25)
                                loot.remove(l)
                                msg = f"{GREEN}+25 Health!{RESET}"

                next_grenades = []
                for g in grenades:
                    g['timer'] -= 1
                    nr, nc = g['r'] + g['dr'], g['c'] + g['dc']
                    if (nr, nc) not in walls and 0 <= nr < MAP_HEIGHT and 0 <= nc < MAP_WIDTH:
                        g['r'], g['c'] = nr, nc
                    
                    if g['timer'] <= 0:
                        msg = f"{MAGENTA}KABOOM!{RESET}"
                        for r_offset in range(-2, 3):
                            for c_offset in range(-2, 3):
                                er, ec = g['r'] + r_offset, g['c'] + c_offset
                                particles.append({'r': er, 'c': ec, 'char': '▓', 'color': YELLOW if random.random()>0.5 else RED, 'life': 4})
                                if (er, ec) in walls and 0 < er < MAP_HEIGHT-1 and 0 < ec < MAP_WIDTH-1:
                                    walls.remove((er, ec))
                                if abs(player['r'] - er) <= 1 and abs(player['c'] - ec) <= 1: player['hp'] -= 30
                                
                                if SETTINGS['friendly_fire']:
                                    for t in list(teammates):
                                        if t['r'] == er and t['c'] == ec: teammates.remove(t)
                                    for c in list(civilians):
                                        if c['r'] == er and c['c'] == ec: civilians.remove(c)
                                        
                                for e in list(enemies):
                                    if e['r'] == er and e['c'] == ec: enemies.remove(e); score += 150
                    else: next_grenades.append(g)
                grenades = next_grenades

                next_bullets = []
                for b in bullets:
                    b['r'] += b['dr']; b['c'] += b['dc']
                    hit = False
                    
                    if (b['r'], b['c']) in walls or not (0 <= b['r'] < MAP_HEIGHT and 0 <= b['c'] < MAP_WIDTH):
                        particles.append({'r': b['r'], 'c': b['c'], 'char': ',', 'color': YELLOW, 'life': 2}); continue
                        
                    if b['team']: # PLAYER OR TEAMMATE FIRED
                        for e in list(enemies):
                            if b['r'] == e['r'] and b['c'] == e['c']:
                                enemies.remove(e); score += 100; hit = True
                                particles.append({'r': e['r'], 'c': e['c'], 'char': 'x', 'color': RED, 'life': 6})
                                if random.random() < 0.3: loot.append({'r': e['r'], 'c': e['c']}) 
                                break
                        
                        if SETTINGS['friendly_fire'] and not hit:
                            for c in list(civilians):
                                if b['r'] == c['r'] and b['c'] == c['c']:
                                    civilians.remove(c); score -= 50; hit = True
                                    msg = f"{RED}CHECK YOUR FIRE! Civilian hit!{RESET}"
                                    particles.append({'r': c['r'], 'c': c['c'], 'char': 'x', 'color': RED, 'life': 5})
                                    break
                            for t in list(teammates):
                                if b['r'] == t['r'] and b['c'] == t['c']:
                                    teammates.remove(t); score -= 50; hit = True
                                    msg = f"{RED}BLUE ON BLUE! Teammate down!{RESET}"
                                    particles.append({'r': t['r'], 'c': t['c'], 'char': 'x', 'color': RED, 'life': 5})
                                    break
                    else: # ENEMY FIRED
                        if b['r'] == player['r'] and b['c'] == player['c']:
                            player['hp'] -= 15; hit = True; particles.append({'r': player['r'], 'c': player['c'], 'char': 'x', 'color': RED, 'life': 5})
                        for t in list(teammates):
                            if b['r'] == t['r'] and b['c'] == t['c']:
                                teammates.remove(t); hit = True
                                break
                        for c in list(civilians):
                            if b['r'] == c['r'] and b['c'] == c['c']:
                                civilians.remove(c); hit = True
                                msg = f"{YELLOW}Shooter eliminated a civilian!{RESET}"
                                particles.append({'r': c['r'], 'c': c['c'], 'char': 'x', 'color': RED, 'life': 5})
                                break
                    if not hit: next_bullets.append(b)
                bullets = next_bullets

                for t in teammates:
                    if random.random() < 0.4:
                        tr, tc = t['r'], t['c']
                        if player['r'] < tr: tr -= 1
                        elif player['r'] > tr: tr += 1
                        elif player['c'] < tc: tc -= 1
                        elif player['c'] > tc: tc += 1
                        if (tr, tc) not in walls: t['r'], t['c'] = tr, tc
                    
                    if enemies and random.random() < 0.1:
                        e = enemies[0] 
                        if has_line_of_sight(t['r'], t['c'], e['r'], e['c'], walls):
                            dr = 1 if e['r'] > t['r'] else (-1 if e['r'] < t['r'] else 0)
                            dc = 1 if e['c'] > t['c'] else (-1 if e['c'] < t['c'] else 0)
                            if (dr != 0 or dc != 0) and (dr == 0 or dc == 0): 
                                bullets.append({'r': t['r'], 'c': t['c'], 'dr': dr, 'dc': dc, 'team': True})

                for c in civilians:
                    if random.random() < 0.4 and enemies:
                        near = min(enemies, key=lambda e: abs(e['r']-c['r']) + abs(e['c']-c['c']))
                        nr, nc = c['r'] + (1 if near['r'] < c['r'] else -1), c['c'] + (1 if near['c'] < c['c'] else -1)
                        if (nr, nc) not in walls and 0 < nr < MAP_HEIGHT-1 and 0 < nc < MAP_WIDTH-1:
                            c['r'], c['c'] = nr, nc
                
                # UPDATED ENEMY AI: Will actively target nearest person (Player, Teammate, or Civilian)
                for e in list(enemies):
                    if random.random() < 0.00005: 
                        enemies.remove(e); msg = f"{YELLOW}Target eliminated themselves!{RESET}"; score += 50; continue
                    
                    # Find all possible valid targets
                    targets = [{'r': player['r'], 'c': player['c']}]
                    for t in teammates: targets.append({'r': t['r'], 'c': t['c']})
                    for c in civilians: targets.append({'r': c['r'], 'c': c['c']})
                    
                    if targets:
                        # Find closest person
                        closest = min(targets, key=lambda t: abs(t['r'] - e['r']) + abs(t['c'] - e['c']))
                        dist = abs(closest['r'] - e['r']) + abs(closest['c'] - e['c'])
                        
                        if dist < 20 and has_line_of_sight(e['r'], e['c'], closest['r'], closest['c'], walls):
                            if random.random() < 0.15: # Fire rate
                                dr = 1 if closest['r'] > e['r'] else (-1 if closest['r'] < e['r'] else 0)
                                dc = 1 if closest['c'] > e['c'] else (-1 if closest['c'] < e['c'] else 0)
                                if (dr != 0 or dc != 0) and (dr == 0 or dc == 0): 
                                    bullets.append({'r': e['r'], 'c': e['c'], 'dr': dr, 'dc': dc, 'team': False})
                        else:
                            # Wander if no one is in sight
                            if random.random() < 0.3:
                                nr, nc = e['r'] + random.choice([-1,0,1]), e['c'] + random.choice([-1,0,1])
                                if (nr, nc) not in walls and 0 < nr < MAP_HEIGHT-1 and 0 < nc < MAP_WIDTH-1:
                                    e['r'], e['c'] = nr, nc

                next_particles = []
                for p in particles:
                    p['life'] -= 1
                    if p['life'] > 0: next_particles.append(p)
                particles = next_particles

                time.sleep(0.06)
                
    finally:
        sys.stdout.write(SHOW_CURSOR)

if __name__ == "__main__":
    game_loop()