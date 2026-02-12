"""Pomodoro Miner - Idle/Pomodoro hybrid game with Pygame."""

import asyncio
import math
import os
import random
import pygame

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
BG_COLOR = (0, 0, 0)

# Font paths (relative to this file)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSET_DIR = os.path.join(_BASE_DIR, "assets")
FONT_TITLE = os.path.join(_ASSET_DIR, "fonts", "ChakraPetch-Bold.ttf")
FONT_HEADING = os.path.join(_ASSET_DIR, "fonts", "ChakraPetch-Regular.ttf")
FONT_MONO = os.path.join(_ASSET_DIR, "fonts", "ShareTechMono-Regular.ttf")

# Colors
WHITE = (255, 255, 255)
GRAY = (160, 160, 160)
DARK_GRAY = (60, 60, 60)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 50)
RED = (220, 60, 60)
GREEN = (60, 220, 60)
ORANGE = (255, 160, 40)
ASTEROID_COLOR = (130, 130, 130)

# Ship / mission tunables
ORBIT_RADIUS = 150
ORBIT_SPEED = 0.4  # radians per second
SHOOT_INTERVAL_RANGE = (1, 5)  # seconds between shots
PROJECTILE_SPEED = 200  # px/s
FRAGMENT_SPEED = 80
FRAGMENT_DECEL = 0.97
MAGNET_RADIUS = 60
MAGNET_STRENGTH = 300
ORBIT_SETTLE_STRENGTH = 40  # how strongly fragments are pulled to orbit radius


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
_AUDIO_DIR = os.path.join(_BASE_DIR, "assets", "audio")


class AudioManager:
    """Handles SFX and ambient audio with independent volume controls."""

    def __init__(self):
        pygame.mixer.init()
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._ambient_channel: pygame.mixer.Channel | None = None
        self._current_ambient: str | None = None
        self._load_all()

    def _load_all(self):
        if not os.path.isdir(_AUDIO_DIR):
            return
        for fname in os.listdir(_AUDIO_DIR):
            if fname.endswith((".wav", ".ogg")):
                name = os.path.splitext(fname)[0]
                try:
                    self._sounds[name] = pygame.mixer.Sound(
                        os.path.join(_AUDIO_DIR, fname))
                except Exception:
                    pass  # graceful: skip files that fail to load

    def play(self, name, volume=None):
        """Play a one-shot SFX. Volume from game.sfx_volume if not given."""
        sound = self._sounds.get(name)
        if sound:
            if volume is not None:
                sound.set_volume(volume)
            sound.play()

    def play_ambient(self, name, volume=0.5):
        """Start looping an ambient sound. Stops previous ambient if any."""
        if name == self._current_ambient:
            # Already playing, just update volume
            if self._ambient_channel:
                self._ambient_channel.set_volume(volume)
            return
        self.stop_ambient()
        sound = self._sounds.get(name)
        if sound:
            self._ambient_channel = sound.play(loops=-1)
            if self._ambient_channel:
                self._ambient_channel.set_volume(volume)
            self._current_ambient = name

    def stop_ambient(self):
        if self._ambient_channel:
            self._ambient_channel.stop()
            self._ambient_channel = None
            self._current_ambient = None

    def set_sfx_volume(self, vol):
        """Update volume for all non-ambient sounds."""
        for name, sound in self._sounds.items():
            if name != self._current_ambient:
                sound.set_volume(vol)

    def set_ambient_volume(self, vol):
        if self._ambient_channel:
            self._ambient_channel.set_volume(vol)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def generate_asteroid_points(cx, cy, base_r, n=14):
    """Create an irregular polygon (circle with noise)."""
    pts = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        r = base_r + random.uniform(-base_r * 0.25, base_r * 0.25)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


# ---------------------------------------------------------------------------
# Talent System
# ---------------------------------------------------------------------------
TALENT_DEFS = {
    "fire_rate":       {"name": "Rapid Fire",      "max": 5, "per_lvl": 0.10, "desc": "-10% shot interval"},
    "bullet_count":    {"name": "Multi Shot",      "max": 5, "per_lvl": 1,    "desc": "+1 bullet per shot"},
    "magnet_range":    {"name": "Magnetic Pull",    "max": 5, "per_lvl": 0.20, "desc": "+20% magnet radius"},
    "double_frag":     {"name": "Double Fragment",  "max": 5, "per_lvl": 0.08, "desc": "+8% double chance"},
    "orbit_speed":     {"name": "Thruster Boost",   "max": 5, "per_lvl": 0.10, "desc": "+10% orbit speed"},
    "frag_magnet_str": {"name": "Tractor Beam",     "max": 3, "per_lvl": 0.30, "desc": "+30% magnet strength"},
}
TALENT_ORDER = ["fire_rate", "bullet_count", "magnet_range", "double_frag", "orbit_speed", "frag_magnet_str"]

# Ship shooting tunables
BASE_BULLET_COUNT = 2
BULLET_SPREAD = 0.15  # radians spread per bullet from center
BURST_INTERVAL = 0.12  # seconds between each bullet in a burst
SHOOTING_SPEED_MULT = 0.3  # orbit speed multiplier while shooting


class TalentTree:
    def __init__(self):
        self.levels = {tid: 0 for tid in TALENT_DEFS}
        self.fragments = 0

    def cost(self, talent_id):
        next_lvl = self.levels[talent_id] + 1
        return next_lvl * 5

    def can_upgrade(self, talent_id):
        d = TALENT_DEFS[talent_id]
        if self.levels[talent_id] >= d["max"]:
            return False
        return self.fragments >= self.cost(talent_id)

    def upgrade(self, talent_id):
        if not self.can_upgrade(talent_id):
            return False
        self.fragments -= self.cost(talent_id)
        self.levels[talent_id] += 1
        return True

    def get_multiplier(self, talent_id):
        """Return multiplier (e.g. 1.2 for +20% at lvl 1)."""
        d = TALENT_DEFS[talent_id]
        return 1.0 + d["per_lvl"] * self.levels[talent_id]

    def get_chance(self, talent_id):
        """Return raw chance (e.g. 0.08 at lvl 1 for double_frag)."""
        d = TALENT_DEFS[talent_id]
        return d["per_lvl"] * self.levels[talent_id]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
class Task:
    def __init__(self, name: str):
        self.name = name
        self.pomodoros = 0


# ---------------------------------------------------------------------------
# Game objects (MissionScene helpers)
# ---------------------------------------------------------------------------
class Ship:
    STATE_ORBITING = 0
    STATE_SHOOTING = 1

    def __init__(self, cx, cy, orbit_speed=ORBIT_SPEED):
        self.cx = cx
        self.cy = cy
        self.angle = 0.0
        self.base_orbit_speed = orbit_speed
        self.x = cx + ORBIT_RADIUS
        self.y = cy
        self.size = 12
        self.state = self.STATE_ORBITING
        # Burst state
        self.bullets_remaining = 0
        self.burst_timer = 0.0

    def start_shooting(self, bullet_count):
        self.state = self.STATE_SHOOTING
        self.bullets_remaining = bullet_count
        self.burst_timer = 0.0  # fire first bullet immediately

    def _angle_toward_center(self):
        return math.atan2(self.cy - self.y, self.cx - self.x)

    def update(self, dt):
        # Orbit (slower while shooting)
        if self.state == self.STATE_SHOOTING:
            speed = self.base_orbit_speed * SHOOTING_SPEED_MULT
        else:
            speed = self.base_orbit_speed

        self.angle += speed * dt
        self.x = self.cx + ORBIT_RADIUS * math.cos(self.angle)
        self.y = self.cy + ORBIT_RADIUS * math.sin(self.angle)

        # Burst timer
        if self.state == self.STATE_SHOOTING:
            self.burst_timer -= dt

    @property
    def facing(self):
        if self.state == self.STATE_SHOOTING:
            return self._angle_toward_center()
        return self.angle + math.pi / 2  # tangent

    def should_fire(self):
        """Returns True once per bullet in the burst, at BURST_INTERVAL pace."""
        if self.state != self.STATE_SHOOTING:
            return False
        if self.bullets_remaining <= 0:
            return False
        if self.burst_timer <= 0:
            self.bullets_remaining -= 1
            self.burst_timer = BURST_INTERVAL
            if self.bullets_remaining <= 0:
                self.state = self.STATE_ORBITING
            return True
        return False

    def draw(self, surf):
        f = self.facing
        cos_t, sin_t = math.cos(f), math.sin(f)
        s = self.size
        tip = (self.x + cos_t * s, self.y + sin_t * s)
        left = (self.x + math.cos(f + 2.4) * s * 0.7,
                self.y + math.sin(f + 2.4) * s * 0.7)
        right = (self.x + math.cos(f - 2.4) * s * 0.7,
                 self.y + math.sin(f - 2.4) * s * 0.7)
        pygame.draw.polygon(surf, CYAN, [tip, left, right])


class Projectile:
    def __init__(self, x, y, tx, ty):
        dx, dy = tx - x, ty - y
        dist = math.hypot(dx, dy) or 1
        self.x, self.y = x, y
        self.vx = dx / dist * PROJECTILE_SPEED
        self.vy = dy / dist * PROJECTILE_SPEED
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), 3)


class Fragment:
    def __init__(self, x, y, cx, cy):
        # Launch radially outward from asteroid center
        angle = math.atan2(y - cy, x - cx) + random.uniform(-0.3, 0.3)
        speed = random.uniform(FRAGMENT_SPEED * 0.5, FRAGMENT_SPEED)
        self.x, self.y = x, y
        self.cx, self.cy = cx, cy
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.alive = True
        self.color = random.choice([ORANGE, YELLOW, GREEN, CYAN])
        self.size = random.randint(3, 6)

    def update(self, dt, ship, magnet_radius=MAGNET_RADIUS, magnet_strength=MAGNET_STRENGTH):
        # Decelerate
        self.vx *= FRAGMENT_DECEL
        self.vy *= FRAGMENT_DECEL

        # Settle toward orbit radius
        dx_c = self.x - self.cx
        dy_c = self.y - self.cy
        dist_c = math.hypot(dx_c, dy_c)
        if dist_c > 0:
            current_dir_x = dx_c / dist_c
            current_dir_y = dy_c / dist_c
            error = ORBIT_RADIUS - dist_c
            settle = ORBIT_SETTLE_STRENGTH * dt
            self.vx += current_dir_x * error * settle / ORBIT_RADIUS
            self.vy += current_dir_y * error * settle / ORBIT_RADIUS

        # Magnet toward ship if close
        dx, dy = ship.x - self.x, ship.y - self.y
        dist = math.hypot(dx, dy)
        if dist < magnet_radius and dist > 0:
            pull = magnet_strength * dt
            self.vx += dx / dist * pull
            self.vy += dy / dist * pull

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Collected?
        if dist < 15:
            self.alive = False
            return True  # collected
        return False

    def draw(self, surf):
        rect = pygame.Rect(int(self.x) - self.size // 2,
                           int(self.y) - self.size // 2,
                           self.size, self.size)
        pygame.draw.rect(surf, self.color, rect)


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

# Intro text lines (typewriter effect)
INTRO_LINES = [
    "Bienvenido a POMI Corp.",
    "",
    "Cargue sus tareas para comenzar la mision.",
    "Aproveche los recursos para optimizar la nave.",
]


class IntroScene:
    """Welcome screen shown once at game start with typewriter text."""

    TITLE_FADE_DURATION = 1.0   # seconds to fade in title
    TITLE_HOLD = 0.6            # pause after title before text starts
    CHAR_DELAY = 0.035          # seconds per character (~28 chars/s)
    LINE_PAUSE = 0.4            # extra pause between lines
    END_HOLD = 1.5              # pause after all text before auto-advance

    def __init__(self, game):
        self.game = game
        self.timer = 0.0
        self.phase = "title_fade"  # title_fade -> title_hold -> typing -> done
        self.char_index = 0        # global char index across all lines
        self.type_timer = 0.0
        self.finished_text = False

        # Pre-calculate total chars and line boundaries
        self._total_chars = sum(len(line) for line in INTRO_LINES)
        self._line_starts = []
        acc = 0
        for line in INTRO_LINES:
            self._line_starts.append(acc)
            acc += len(line)

    def _skip(self):
        self.game.scene = FadeTransition(self.game, self, self.game.menu)

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN or (
            ev.type == pygame.KEYDOWN and ev.key != pygame.K_ESCAPE
        ):
            self._skip()

    def update(self, dt):
        self.timer += dt

        if self.phase == "title_fade":
            if self.timer >= self.TITLE_FADE_DURATION:
                self.phase = "title_hold"
                self.timer = 0.0

        elif self.phase == "title_hold":
            if self.timer >= self.TITLE_HOLD:
                self.phase = "typing"
                self.timer = 0.0
                self.type_timer = 0.0

        elif self.phase == "typing":
            self.type_timer += dt
            # Advance characters based on elapsed time
            while self.type_timer >= self.CHAR_DELAY and self.char_index < self._total_chars:
                self.type_timer -= self.CHAR_DELAY
                self.char_index += 1
                # Add extra pause at line boundaries
                for start in self._line_starts[1:]:
                    if self.char_index == start:
                        self.type_timer -= self.LINE_PAUSE
                        break
            if self.char_index >= self._total_chars and not self.finished_text:
                self.finished_text = True
                self.timer = 0.0
                self.phase = "done"

        elif self.phase == "done":
            if self.timer >= self.END_HOLD:
                self._skip()

    def draw(self, surf):
        # Title
        if self.phase == "title_fade":
            alpha = clamp(int(255 * self.timer / self.TITLE_FADE_DURATION), 0, 255)
        else:
            alpha = 255

        title_surf = self.game.font_title.render("POMI Corp.", True, CYAN)
        if alpha < 255:
            title_surf.set_alpha(alpha)
        surf.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2,
                                HEIGHT // 3 - title_surf.get_height() // 2))

        # Typewriter text (only during typing and done phases)
        if self.phase in ("typing", "done"):
            remaining = self.char_index
            y = HEIGHT // 3 + 50
            for line in INTRO_LINES:
                if remaining <= 0:
                    break
                visible = line[:remaining]
                remaining -= len(line)
                if visible:
                    line_surf = self.game.font.render(visible, True, GRAY)
                    surf.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y))
                y += 28

        # Skip hint
        if self.phase != "title_fade":
            hint = self.game.font_small.render("Click o presione una tecla para continuar",
                                                True, DARK_GRAY)
            surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 40))


class MenuScene:
    def __init__(self, game):
        self.game = game
        self.input_text = ""
        self.input_active = False
        self.scroll_offset = 0
        # Layout
        self.input_rect = pygame.Rect(50, 90, 500, 36)
        self.add_btn = pygame.Rect(560, 90, 80, 36)
        self.talent_btn = pygame.Rect(WIDTH - 160, 20, 140, 36)
        self.settings_btn = pygame.Rect(WIDTH - 310, 20, 140, 36)
        self.list_top = 150
        self.row_h = 44

    # -- events --
    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            # Click input box
            self.input_active = self.input_rect.collidepoint(mx, my)
            # Add button
            if self.add_btn.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self._add_task()
            # Talents button
            if self.talent_btn.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.scene = TalentScene(self.game)
                return
            # Settings button
            if self.settings_btn.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.scene = SettingsScene(self.game)
                return
            # Task list buttons
            self._check_list_click(mx, my)
            # Scroll
            if ev.button == 4:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif ev.button == 5:
                max_scroll = max(0, len(self.game.tasks) - self._visible_rows())
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        elif ev.type == pygame.KEYDOWN and self.input_active:
            if ev.key == pygame.K_RETURN:
                self._add_task()
            elif ev.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if ev.unicode and ev.unicode.isprintable() and len(self.input_text) < 40:
                    self.input_text += ev.unicode

    def _add_task(self):
        name = self.input_text.strip()
        if name:
            self.game.tasks.append(Task(name))
            self.input_text = ""

    def _visible_rows(self):
        return max(1, (HEIGHT - self.list_top - 20) // self.row_h)

    def _check_list_click(self, mx, my):
        vis = self._visible_rows()
        for i in range(vis):
            idx = i + self.scroll_offset
            if idx >= len(self.game.tasks):
                break
            row_y = self.list_top + i * self.row_h
            # Start button
            start_r = pygame.Rect(WIDTH - 220, row_y + 4, 80, 32)
            if start_r.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.start_mission(idx)
                return
            # Delete button
            del_r = pygame.Rect(WIDTH - 130, row_y + 4, 80, 32)
            if del_r.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.tasks.pop(idx)
                self.scroll_offset = clamp(self.scroll_offset, 0,
                                           max(0, len(self.game.tasks) - vis))
                return

    # -- update / draw --
    def update(self, dt):
        pass

    def draw(self, surf):
        font = self.game.font

        # Title
        title = self.game.font_title.render("POMODORO MINER", True, CYAN)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 16))

        # Fragment counter
        frag_s = font.render(f"Fragments: {self.game.talents.fragments}", True, YELLOW)
        surf.blit(frag_s, (20, 20))

        # Settings button
        pygame.draw.rect(surf, GRAY, self.settings_btn, border_radius=4)
        sl = font.render("Settings", True, BG_COLOR)
        surf.blit(sl, (self.settings_btn.centerx - sl.get_width() // 2,
                        self.settings_btn.centery - sl.get_height() // 2))

        # Talents button
        pygame.draw.rect(surf, ORANGE, self.talent_btn, border_radius=4)
        tl = font.render("Talents", True, BG_COLOR)
        surf.blit(tl, (self.talent_btn.centerx - tl.get_width() // 2,
                        self.talent_btn.centery - tl.get_height() // 2))

        # Input box
        col = WHITE if self.input_active else GRAY
        pygame.draw.rect(surf, col, self.input_rect, 2)
        txt_surf = font.render(self.input_text, True, WHITE)
        surf.blit(txt_surf, (self.input_rect.x + 8, self.input_rect.y + 6))

        # Add button
        pygame.draw.rect(surf, GREEN, self.add_btn, border_radius=4)
        add_lbl = font.render("Add", True, BG_COLOR)
        surf.blit(add_lbl, (self.add_btn.centerx - add_lbl.get_width() // 2,
                            self.add_btn.centery - add_lbl.get_height() // 2))

        # Column headers
        hdr_y = self.list_top - 24
        surf.blit(font.render("Task", True, GRAY), (60, hdr_y))
        surf.blit(font.render("Pomodoros", True, GRAY), (WIDTH - 380, hdr_y))

        # Task list
        vis = self._visible_rows()
        for i in range(vis):
            idx = i + self.scroll_offset
            if idx >= len(self.game.tasks):
                break
            task = self.game.tasks[idx]
            row_y = self.list_top + i * self.row_h

            # Separator line
            pygame.draw.line(surf, DARK_GRAY, (50, row_y), (WIDTH - 50, row_y))

            # Name
            name_s = font.render(task.name, True, WHITE)
            surf.blit(name_s, (60, row_y + 10))

            # Pomodoro count
            count_s = font.render(str(task.pomodoros), True, YELLOW)
            surf.blit(count_s, (WIDTH - 360, row_y + 10))

            # Start button
            start_r = pygame.Rect(WIDTH - 220, row_y + 4, 80, 32)
            pygame.draw.rect(surf, GREEN, start_r, border_radius=4)
            sl = font.render("Start", True, BG_COLOR)
            surf.blit(sl, (start_r.centerx - sl.get_width() // 2,
                           start_r.centery - sl.get_height() // 2))

            # Delete button
            del_r = pygame.Rect(WIDTH - 130, row_y + 4, 80, 32)
            pygame.draw.rect(surf, RED, del_r, border_radius=4)
            dl = font.render("Delete", True, BG_COLOR)
            surf.blit(dl, (del_r.centerx - dl.get_width() // 2,
                           del_r.centery - dl.get_height() // 2))

        # Scroll hint
        if len(self.game.tasks) > vis:
            hint = self.game.font_small.render(
                f"(scroll: {self.scroll_offset + 1}-"
                f"{min(self.scroll_offset + vis, len(self.game.tasks))}"
                f" / {len(self.game.tasks)})", True, DARK_GRAY)
            surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))


class TalentScene:
    def __init__(self, game):
        self.game = game
        self.back_btn = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 55, 120, 36)
        self.upgrade_btns = []
        start_y = 110
        row_h = 80
        for i in range(len(TALENT_ORDER)):
            btn = pygame.Rect(WIDTH - 180, start_y + i * row_h + 20, 100, 32)
            self.upgrade_btns.append(btn)

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.scene = self.game.menu
                return
            for i, btn in enumerate(self.upgrade_btns):
                if btn.collidepoint(mx, my):
                    self.game.audio.play("ui_click", self.game.sfx_volume)
                    tid = TALENT_ORDER[i]
                    self.game.talents.upgrade(tid)

    def update(self, dt):
        pass

    def draw(self, surf):
        font = self.game.font
        talents = self.game.talents

        # Title
        title = self.game.font_title.render("TALENTS", True, ORANGE)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 12))

        # Fragment count
        frag_s = font.render(f"Fragments: {talents.fragments}", True, YELLOW)
        surf.blit(frag_s, (WIDTH // 2 - frag_s.get_width() // 2, 60))

        # Talent rows
        start_y = 110
        row_h = 80
        for i, tid in enumerate(TALENT_ORDER):
            d = TALENT_DEFS[tid]
            lvl = talents.levels[tid]
            y = start_y + i * row_h

            # Separator
            pygame.draw.line(surf, DARK_GRAY, (40, y), (WIDTH - 40, y))

            # Name and level
            name_s = font.render(f"{d['name']}  Lv {lvl}/{d['max']}", True, WHITE)
            surf.blit(name_s, (60, y + 8))

            # Description
            desc_s = font.render(d["desc"], True, GRAY)
            surf.blit(desc_s, (60, y + 32))

            # Level pips
            pip_x = 350
            for p in range(d["max"]):
                color = CYAN if p < lvl else DARK_GRAY
                pygame.draw.rect(surf, color, (pip_x + p * 18, y + 10, 12, 12))

            # Upgrade button
            btn = self.upgrade_btns[i]
            if lvl >= d["max"]:
                pygame.draw.rect(surf, DARK_GRAY, btn, border_radius=4)
                bl = font.render("MAXED", True, GRAY)
            elif talents.can_upgrade(tid):
                pygame.draw.rect(surf, GREEN, btn, border_radius=4)
                bl = font.render(f"{talents.cost(tid)} frags", True, BG_COLOR)
            else:
                pygame.draw.rect(surf, DARK_GRAY, btn, border_radius=4)
                bl = font.render(f"{talents.cost(tid)} frags", True, GRAY)
            surf.blit(bl, (btn.centerx - bl.get_width() // 2,
                           btn.centery - bl.get_height() // 2))

        # Back button
        pygame.draw.rect(surf, RED, self.back_btn, border_radius=4)
        bl = font.render("Back", True, WHITE)
        surf.blit(bl, (self.back_btn.centerx - bl.get_width() // 2,
                        self.back_btn.centery - bl.get_height() // 2))


class SettingsScene:
    """Settings screen with volume sliders and duration selectors."""

    SLIDER_W = 260
    SLIDER_H = 8
    KNOB_R = 10

    def __init__(self, game):
        self.game = game
        self.back_btn = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 55, 120, 36)

        # Layout positions (centered)
        cx = WIDTH // 2
        self.label_x = cx - 220
        self.slider_x = cx - 40
        self.row_y = [150, 220, 300, 370]  # sfx, ambient, pomodoro, break

        # Slider rects (for hit detection)
        self.sfx_slider = pygame.Rect(self.slider_x, self.row_y[0] - self.KNOB_R,
                                       self.SLIDER_W, self.KNOB_R * 2)
        self.amb_slider = pygame.Rect(self.slider_x, self.row_y[1] - self.KNOB_R,
                                       self.SLIDER_W, self.KNOB_R * 2)

        # Duration selector rects
        btn_w, btn_h = 36, 32
        sel_cx = self.slider_x + self.SLIDER_W // 2
        self.pom_left = pygame.Rect(sel_cx - 100, self.row_y[2] - btn_h // 2, btn_w, btn_h)
        self.pom_right = pygame.Rect(sel_cx + 100 - btn_w, self.row_y[2] - btn_h // 2, btn_w, btn_h)
        self.brk_left = pygame.Rect(sel_cx - 100, self.row_y[3] - btn_h // 2, btn_w, btn_h)
        self.brk_right = pygame.Rect(sel_cx + 100 - btn_w, self.row_y[3] - btn_h // 2, btn_w, btn_h)

        self.dragging = None  # "sfx" or "ambient"

    def _slider_value_from_x(self, mx):
        return clamp((mx - self.slider_x) / self.SLIDER_W, 0.0, 1.0)

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            if self.back_btn.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.scene = self.game.menu
                return
            # Slider drag start
            if self.sfx_slider.collidepoint(mx, my):
                self.dragging = "sfx"
                self.game.sfx_volume = self._slider_value_from_x(mx)
            elif self.amb_slider.collidepoint(mx, my):
                self.dragging = "ambient"
                self.game.ambient_volume = self._slider_value_from_x(mx)
            # Duration selectors
            elif self.pom_left.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self._cycle_option("pomodoro", -1)
            elif self.pom_right.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self._cycle_option("pomodoro", 1)
            elif self.brk_left.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self._cycle_option("break", -1)
            elif self.brk_right.collidepoint(mx, my):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self._cycle_option("break", 1)

        elif ev.type == pygame.MOUSEBUTTONUP:
            self.dragging = None

        elif ev.type == pygame.MOUSEMOTION and self.dragging:
            mx = ev.pos[0]
            val = self._slider_value_from_x(mx)
            if self.dragging == "sfx":
                self.game.sfx_volume = val
            elif self.dragging == "ambient":
                self.game.ambient_volume = val
                self.game.audio.set_ambient_volume(val)

    def _cycle_option(self, which, direction):
        if which == "pomodoro":
            opts = self.game._pomodoro_options
            idx = opts.index(self.game.pomodoro_minutes) if self.game.pomodoro_minutes in opts else 0
            idx = (idx + direction) % len(opts)
            self.game.pomodoro_minutes = opts[idx]
        else:
            opts = self.game._break_options
            idx = opts.index(self.game.break_minutes) if self.game.break_minutes in opts else 0
            idx = (idx + direction) % len(opts)
            self.game.break_minutes = opts[idx]

    def update(self, dt):
        pass

    def _draw_slider(self, surf, x, y, value, label, font):
        # Label
        lbl = font.render(label, True, WHITE)
        surf.blit(lbl, (self.label_x, y - lbl.get_height() // 2))

        # Track background
        track_rect = pygame.Rect(x, y - self.SLIDER_H // 2, self.SLIDER_W, self.SLIDER_H)
        pygame.draw.rect(surf, DARK_GRAY, track_rect, border_radius=4)

        # Track fill
        fill_w = int(self.SLIDER_W * value)
        if fill_w > 0:
            fill_rect = pygame.Rect(x, y - self.SLIDER_H // 2, fill_w, self.SLIDER_H)
            pygame.draw.rect(surf, CYAN, fill_rect, border_radius=4)

        # Knob
        knob_x = x + fill_w
        pygame.draw.circle(surf, WHITE, (knob_x, y), self.KNOB_R)

        # Percentage
        pct = font.render(f"{int(value * 100)}%", True, GRAY)
        surf.blit(pct, (x + self.SLIDER_W + 16, y - pct.get_height() // 2))

    def _draw_selector(self, surf, y, value_str, left_btn, right_btn, label, font):
        # Label
        lbl = font.render(label, True, WHITE)
        surf.blit(lbl, (self.label_x, y - lbl.get_height() // 2))

        # Left arrow
        pygame.draw.rect(surf, DARK_GRAY, left_btn, border_radius=4)
        al = font.render("<", True, WHITE)
        surf.blit(al, (left_btn.centerx - al.get_width() // 2,
                        left_btn.centery - al.get_height() // 2))

        # Value
        val_s = font.render(value_str, True, CYAN)
        cx = (left_btn.right + right_btn.left) // 2
        surf.blit(val_s, (cx - val_s.get_width() // 2, y - val_s.get_height() // 2))

        # Right arrow
        pygame.draw.rect(surf, DARK_GRAY, right_btn, border_radius=4)
        ar = font.render(">", True, WHITE)
        surf.blit(ar, (right_btn.centerx - ar.get_width() // 2,
                        right_btn.centery - ar.get_height() // 2))

    def draw(self, surf):
        font = self.game.font

        # Title
        title = self.game.font_title.render("SETTINGS", True, WHITE)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Sliders
        self._draw_slider(surf, self.slider_x, self.row_y[0],
                          self.game.sfx_volume, "SFX Volume", font)
        self._draw_slider(surf, self.slider_x, self.row_y[1],
                          self.game.ambient_volume, "Ambience", font)

        # Duration selectors
        self._draw_selector(surf, self.row_y[2],
                            f"{self.game.pomodoro_minutes} min",
                            self.pom_left, self.pom_right, "Pomodoro", font)
        self._draw_selector(surf, self.row_y[3],
                            f"{self.game.break_minutes} min",
                            self.brk_left, self.brk_right, "Break", font)

        # Back button
        pygame.draw.rect(surf, RED, self.back_btn, border_radius=4)
        bl = font.render("Back", True, WHITE)
        surf.blit(bl, (self.back_btn.centerx - bl.get_width() // 2,
                        self.back_btn.centery - bl.get_height() // 2))


class MissionScene:
    def __init__(self, game, task):
        self.game = game
        self.task = task
        self.remaining = game.pomodoro_minutes * 60  # seconds
        self.collected = 0

        cx, cy = WIDTH // 2, HEIGHT // 2 + 30
        self.cx, self.cy = cx, cy

        # Apply talent multipliers
        t = game.talents
        eff_orbit_speed = ORBIT_SPEED * t.get_multiplier("orbit_speed")
        self.eff_magnet_radius = MAGNET_RADIUS * t.get_multiplier("magnet_range")
        self.eff_magnet_strength = MAGNET_STRENGTH * t.get_multiplier("frag_magnet_str")
        self.eff_shoot_interval_mult = 1.0 / t.get_multiplier("fire_rate")  # lower = faster
        self.double_frag_chance = t.get_chance("double_frag")
        self.bullet_count = BASE_BULLET_COUNT + int(t.get_chance("bullet_count"))

        self.ship = Ship(cx, cy, eff_orbit_speed)
        self.asteroid_pts = generate_asteroid_points(cx, cy, 40)
        self.projectiles: list[Projectile] = []
        self.fragments: list[Fragment] = []

        self._next_shot_time()
        self.complete = False

        # Abort button
        self.abort_btn = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 50, 140, 36)

    def _next_shot_time(self):
        lo, hi = SHOOT_INTERVAL_RANGE
        self.shoot_timer = random.uniform(lo, hi) * self.eff_shoot_interval_mult

    def _fire_one_bullet(self):
        """Fire a single bullet toward the asteroid with slight spread."""
        base_angle = math.atan2(self.cy - self.ship.y, self.cx - self.ship.x)
        spread = random.uniform(-BULLET_SPREAD, BULLET_SPREAD)
        a = base_angle + spread
        dist = math.hypot(self.cx - self.ship.x, self.cy - self.ship.y)
        tx = self.ship.x + math.cos(a) * dist
        ty = self.ship.y + math.sin(a) * dist
        self.projectiles.append(Projectile(self.ship.x, self.ship.y, tx, ty))

    # -- events --
    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if self.abort_btn.collidepoint(ev.pos):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.scene = AbortScene(self.game, self.task, self.collected, self.remaining)

    # -- update --
    def update(self, dt):
        if self.complete:
            return

        # Timer
        self.remaining -= dt
        if self.remaining <= 0:
            self.remaining = 0
            self.task.pomodoros += 1
            self.game.total_pomodoros += 1
            self.complete = True
            # Award fragments on completion
            self.game.talents.fragments += self.collected
            # Store mission result for BreakScene
            self.game._last_mission = {"task": self.task.name, "fragments": self.collected}
            # Brief delay then transition to break
            pygame.time.set_timer(pygame.USEREVENT + 1, 1500, loops=1)
            return

        # Ship
        self.ship.update(dt)

        # Shooting state machine
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and self.ship.state == Ship.STATE_ORBITING:
            self.ship.start_shooting(self.bullet_count)
            self._next_shot_time()

        # Fire bullets one by one during burst
        if self.ship.should_fire():
            self._fire_one_bullet()

        # Projectiles
        for p in self.projectiles:
            p.update(dt)
            # Hit asteroid center?
            if math.hypot(p.x - self.cx, p.y - self.cy) < 35:
                p.alive = False
                # Spawn fragment(s) from asteroid surface
                spawn_angle = random.uniform(0, 2 * math.pi)
                spawn_r = 35  # asteroid radius
                sx = self.cx + math.cos(spawn_angle) * spawn_r
                sy = self.cy + math.sin(spawn_angle) * spawn_r
                self.fragments.append(Fragment(sx, sy, self.cx, self.cy))
                if random.random() < self.double_frag_chance:
                    spawn_angle2 = random.uniform(0, 2 * math.pi)
                    sx2 = self.cx + math.cos(spawn_angle2) * spawn_r
                    sy2 = self.cy + math.sin(spawn_angle2) * spawn_r
                    self.fragments.append(Fragment(sx2, sy2, self.cx, self.cy))

        self.projectiles = [p for p in self.projectiles if p.alive]

        # Fragments
        for f in self.fragments:
            if f.update(dt, self.ship, self.eff_magnet_radius, self.eff_magnet_strength):
                self.collected += 1
        self.fragments = [f for f in self.fragments if f.alive]

    # -- draw --
    def draw(self, surf):
        font = self.game.font

        # Timer
        mins = int(self.remaining) // 60
        secs = int(self.remaining) % 60
        timer_str = f"{mins:02d}:{secs:02d}"
        timer_surf = self.game.font_timer.render(timer_str, True, WHITE)
        surf.blit(timer_surf, (WIDTH // 2 - timer_surf.get_width() // 2, 10))

        # Task name
        task_surf = font.render(self.task.name, True, GRAY)
        surf.blit(task_surf, (WIDTH // 2 - task_surf.get_width() // 2, 55))

        # Collected counter
        res_surf = font.render(f"Fragments: {self.collected}", True, YELLOW)
        surf.blit(res_surf, (20, 20))

        # Asteroid
        pygame.draw.polygon(surf, ASTEROID_COLOR, self.asteroid_pts)
        pygame.draw.polygon(surf, GRAY, self.asteroid_pts, 2)

        # Ship
        self.ship.draw(surf)

        # Projectiles
        for p in self.projectiles:
            p.draw(surf)

        # Fragments
        for f in self.fragments:
            f.draw(surf)

        # Orbit ring (subtle)
        pygame.draw.circle(surf, (30, 30, 40), (self.cx, self.cy),
                           ORBIT_RADIUS, 1)

        # Abort button
        pygame.draw.rect(surf, RED, self.abort_btn, border_radius=4)
        al = font.render("Abort Mission", True, WHITE)
        surf.blit(al, (self.abort_btn.centerx - al.get_width() // 2,
                        self.abort_btn.centery - al.get_height() // 2))

        # Completion overlay
        if self.complete:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surf.blit(overlay, (0, 0))
            done = self.game.font_heading.render("MISSION COMPLETE!", True, GREEN)
            surf.blit(done, (WIDTH // 2 - done.get_width() // 2,
                             HEIGHT // 2 - 30))
            earned = font.render(f"+{self.collected} fragments earned!", True, YELLOW)
            surf.blit(earned, (WIDTH // 2 - earned.get_width() // 2,
                               HEIGHT // 2 + 15))


class AbortScene:
    PENALTY = 0.30  # keep 30% of collected fragments

    def __init__(self, game, task, collected, time_remaining):
        self.game = game
        self.task = task
        self.collected = collected
        self.earned = int(collected * self.PENALTY)
        self.time_remaining = time_remaining
        self.time_elapsed = game.pomodoro_minutes * 60 - time_remaining

        # Award the 30% immediately
        self.game.talents.fragments += self.earned

        # Button
        self.continue_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 120, 160, 40)

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_btn.collidepoint(ev.pos):
                self.game.audio.play("ui_click", self.game.sfx_volume)
                self.game.set_scene("menu")
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
            self.game.set_scene("menu")

    def update(self, dt):
        pass

    def draw(self, surf):
        font = self.game.font

        # Overlay background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        # Title
        title = self.game.font_heading.render("MISSION ABORTED", True, RED)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 140))

        # Task name
        name_s = font.render(f"Task: {self.task.name}", True, GRAY)
        surf.blit(name_s, (WIDTH // 2 - name_s.get_width() // 2, HEIGHT // 2 - 80))

        # Time elapsed
        mins_e = int(self.time_elapsed) // 60
        secs_e = int(self.time_elapsed) % 60
        mins_r = int(self.time_remaining) // 60
        secs_r = int(self.time_remaining) % 60
        time_s = font.render(
            f"Time: {mins_e:02d}:{secs_e:02d} elapsed  /  {mins_r:02d}:{secs_r:02d} remaining",
            True, WHITE)
        surf.blit(time_s, (WIDTH // 2 - time_s.get_width() // 2, HEIGHT // 2 - 45))

        # Fragments collected
        coll_s = font.render(f"Fragments mined: {self.collected}", True, YELLOW)
        surf.blit(coll_s, (WIDTH // 2 - coll_s.get_width() // 2, HEIGHT // 2 - 10))

        # Penalty
        pen_s = font.render(f"Abort penalty: only 30% kept", True, ORANGE)
        surf.blit(pen_s, (WIDTH // 2 - pen_s.get_width() // 2, HEIGHT // 2 + 25))

        # Earned
        earn_s = self.game.font_heading.render(f"+{self.earned} fragments", True, YELLOW)
        surf.blit(earn_s, (WIDTH // 2 - earn_s.get_width() // 2, HEIGHT // 2 + 65))

        # Continue button
        pygame.draw.rect(surf, GRAY, self.continue_btn, border_radius=4)
        bl = font.render("Continue", True, BG_COLOR)
        surf.blit(bl, (self.continue_btn.centerx - bl.get_width() // 2,
                        self.continue_btn.centery - bl.get_height() // 2))


class FadeTransition:
    """Fade-to-black transition between two scenes."""

    def __init__(self, game, old_scene, new_scene, duration=0.5):
        self.game = game
        self.old_scene = old_scene
        self.new_scene = new_scene
        self.duration = duration
        self.timer = 0.0
        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill((0, 0, 0))

    def handle_event(self, ev):
        pass  # Block input during transition

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.game.scene = self.new_scene

    def draw(self, surf):
        half = self.duration / 2
        if self.timer < half:
            # Fade out: draw old scene, overlay goes 0→255
            self.old_scene.draw(surf)
            alpha = int(255 * (self.timer / half))
        else:
            # Fade in: draw new scene, overlay goes 255→0
            self.new_scene.draw(surf)
            alpha = int(255 * (1.0 - (self.timer - half) / half))
        alpha = max(0, min(255, alpha))
        self.overlay.set_alpha(alpha)
        surf.blit(self.overlay, (0, 0))


class StoryScene:
    def __init__(self, game, task, image):
        self.game = game
        self.task = task
        self.image = image
        # Scale image to fit screen while keeping aspect ratio
        iw, ih = image.get_size()
        scale = min(WIDTH / iw, HEIGHT / ih)
        new_w, new_h = int(iw * scale), int(ih * scale)
        self.scaled = pygame.transform.smoothscale(image, (new_w, new_h))
        self.img_x = (WIDTH - new_w) // 2
        self.img_y = (HEIGHT - new_h) // 2

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN or (
            ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE)
        ):
            new_scene = MissionScene(self.game, self.task)
            self.game.scene = FadeTransition(self.game, self, new_scene)

    def update(self, dt):
        pass

    def draw(self, surf):
        surf.fill(BG_COLOR)
        surf.blit(self.scaled, (self.img_x, self.img_y))
        # Hint text
        hint = self.game.font_small.render("Click or press SPACE to start mission", True, GRAY)
        surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pomodoro Miner")
        self.clock = pygame.time.Clock()
        # Typography scale
        self.font_title = pygame.font.Font(FONT_TITLE, 38)       # Main titles
        self.font_heading = pygame.font.Font(FONT_HEADING, 28)   # Section headings
        self.font_timer = pygame.font.Font(FONT_MONO, 42)        # Mission timer
        self.font = pygame.font.Font(FONT_MONO, 18)              # Body / UI text
        self.font_small = pygame.font.Font(FONT_MONO, 14)        # Hints, captions

        self.audio = AudioManager()
        self.tasks: list[Task] = []
        self.talents = TalentTree()
        self.total_pomodoros = 0

        # Settings (configurable via SettingsScene)
        self.sfx_volume = 0.7           # 0.0 - 1.0
        self.ambient_volume = 0.5       # 0.0 - 1.0
        self.pomodoro_minutes = 25      # minutes
        self.break_minutes = 5          # minutes
        self._pomodoro_options = [1, 5, 15, 25, 30, 45, 60]
        self._break_options = [1, 3, 5, 10]

        # Break timer (persistent across menu scenes)
        self.break_active = False
        self.break_remaining = 0.0
        self.break_ready = False
        self.break_ready_timer = 0.0
        self._break_task_name = ""
        self._break_fragments = 0
        self.story_images = self._load_story_images()
        self.menu = MenuScene(self)
        self.scene = IntroScene(self)
        self.running = True

    def _load_story_images(self):
        """Load all story_XX.png images sorted by number."""
        img_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
        images = []
        if not os.path.isdir(img_dir):
            return images
        files = sorted(
            f for f in os.listdir(img_dir)
            if f.startswith("story_") and f.endswith(".png")
        )
        for f in files:
            path = os.path.join(img_dir, f)
            images.append(pygame.image.load(path).convert_alpha())
        return images

    def set_scene(self, name):
        if name == "menu":
            self.scene = FadeTransition(self, self.scene, self.menu)

    def _start_break(self):
        info = getattr(self, "_last_mission", {"task": "", "fragments": 0})
        self.break_active = True
        self.break_remaining = self.break_minutes * 60
        self.break_ready = False
        self.break_ready_timer = 0.0
        self._break_task_name = info["task"]
        self._break_fragments = info["fragments"]
        self.set_scene("menu")

    def update_break(self, dt):
        """Tick the break timer (called from main loop)."""
        if not self.break_active:
            return
        if self.break_ready:
            self.break_ready_timer += dt
            return
        self.break_remaining -= dt
        if self.break_remaining <= 0:
            self.break_remaining = 0
            self.break_ready = True
            self.break_ready_timer = 0.0

    def draw_break_banner(self, surf):
        """Draw break status bar at the bottom of any menu scene."""
        if not self.break_active:
            return

        BANNER_H = 36
        banner_y = HEIGHT - BANNER_H
        # Background bar
        pygame.draw.rect(surf, (15, 15, 25), (0, banner_y, WIDTH, BANNER_H))
        pygame.draw.line(surf, DARK_GRAY, (0, banner_y), (WIDTH, banner_y))

        if not self.break_ready:
            # Countdown mode
            mins = int(self.break_remaining) // 60
            secs = int(self.break_remaining) % 60
            timer_str = f"Break  {mins:02d}:{secs:02d}"
            timer_surf = self.font_small.render(timer_str, True, GRAY)
            surf.blit(timer_surf, (WIDTH // 2 - timer_surf.get_width() // 2,
                                    banner_y + BANNER_H // 2 - timer_surf.get_height() // 2))
            # Task info (left side, subtle)
            info = self.font_small.render(
                f"{self._break_task_name}  ·  +{self._break_fragments} frags",
                True, DARK_GRAY)
            surf.blit(info, (12, banner_y + BANNER_H // 2 - info.get_height() // 2))
        else:
            # Ready mode - pulsing green text
            t = self.break_ready_timer * 0.8 * 2 * math.pi
            alpha = 100 + int(155 * (0.5 + 0.5 * math.sin(t)))
            ready_surf = self.font.render("Ready for mission", True, GREEN)
            ready_surf.set_alpha(alpha)
            surf.blit(ready_surf, (WIDTH // 2 - ready_surf.get_width() // 2,
                                    banner_y + BANNER_H // 2 - ready_surf.get_height() // 2))

    def dismiss_break(self):
        """Called when player starts a new mission - clear the break state."""
        self.break_active = False
        self.break_ready = False

    def start_mission(self, task_idx):
        self.dismiss_break()
        task = self.tasks[task_idx]
        if self.story_images:
            # Pick image based on total pomodoros completed (0-indexed)
            idx = min(self.total_pomodoros, len(self.story_images) - 1)
            new_scene = StoryScene(self, task, self.story_images[idx])
        else:
            new_scene = MissionScene(self, task)
        self.scene = FadeTransition(self, self.scene, new_scene)

    async def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                elif ev.type == pygame.USEREVENT + 1:
                    # Mission complete -> break
                    self._start_break()
                else:
                    self.scene.handle_event(ev)

            self.update_break(dt)
            self.scene.update(dt)

            # Ambient audio: play in menu scenes, stop in gameplay
            if isinstance(self.scene, (MenuScene, TalentScene, SettingsScene, IntroScene)):
                self.audio.play_ambient("ambient_menu", self.ambient_volume)
            else:
                self.audio.stop_ambient()

            self.screen.fill(BG_COLOR)
            self.scene.draw(self.screen)
            # Break banner on top of menu scenes
            if isinstance(self.scene, (MenuScene, TalentScene, SettingsScene)):
                self.draw_break_banner(self.screen)
            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(Game().run())
