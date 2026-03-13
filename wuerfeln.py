#!/usr/bin/env python3
"""
Kinderwürfeln – Ein spielerisches Mathe-Lernprogramm für Kinder.
Kinder lernen Addition und Subtraktion mit bunten Würfeln.
"""

import pygame
import random
import sys
import math

# ── Farben ──────────────────────────────────────────────────────────────────
WEISS       = (255, 255, 255)
SCHWARZ     = (  0,   0,   0)
HELLBLAU    = (135, 206, 250)
DUNKELBLAU  = ( 30,  80, 160)
GELB        = (255, 230,  50)
GRUEN       = ( 80, 200,  80)
DUNKELGRUEN = ( 30, 140,  30)
ROT         = (220,  60,  60)
DUNKELROT   = (160,  20,  20)
ORANGE      = (255, 150,  40)
LILA        = (160,  80, 200)
ROSA        = (255, 180, 220)
HINTERGRUND = (240, 248, 255)
PUNKT_FARBE = ( 40,  40,  40)
SCHATTEN    = (180, 180, 180)

# ── Würfelpunkt-Positionen (relativ 0..1) ────────────────────────────────────
PUNKTE_LAYOUT = {
    1: [(0.50, 0.50)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.50, 0.50), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.50, 0.50), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.22), (0.75, 0.22), (0.25, 0.50), (0.75, 0.50),
        (0.25, 0.78), (0.75, 0.78)],
}

WUERFEL_FARBEN = [
    (255, 100, 100),
    (100, 160, 255),
    (100, 220, 100),
    (255, 200,  50),
    (200, 100, 255),
    (255, 150,  50),
]


# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def _zeichne_wuerfel_auf(tmp, groesse, wert, farbe, punkte=True):
    """Zeichnet einen Würfel auf eine SRCALPHA-Surface der Größe groesse×groesse."""
    rand = max(6, groesse // 8)
    pygame.draw.rect(tmp, (*farbe, 255), (0, 0, groesse, groesse),
                     border_radius=rand)
    pygame.draw.rect(tmp, (*WEISS, 90), (3, 3, groesse - 6, groesse - 6),
                     width=3, border_radius=rand)
    if punkte:
        pr = max(5, groesse // 9)
        for px, py in PUNKTE_LAYOUT[wert]:
            cx = int(px * groesse)
            cy = int(py * groesse)
            pygame.draw.circle(tmp, SCHATTEN, (cx + 2, cy + 2), pr)
            pygame.draw.circle(tmp, PUNKT_FARBE, (cx, cy), pr)


def zeichne_wuerfel(surf, x, y, groesse, wert, farbe, alpha=255):
    rand = max(6, groesse // 8)
    # Schatten
    sh = pygame.Surface((groesse + 10, groesse + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (*SCHATTEN, 110), (6, 6, groesse, groesse),
                     border_radius=rand + 2)
    surf.blit(sh, (x - 4, y - 4))
    # Körper
    ws = pygame.Surface((groesse, groesse), pygame.SRCALPHA)
    _zeichne_wuerfel_auf(ws, groesse, wert, farbe)
    surf.blit(ws, (x, y))


def zeichne_wuerfel_3d_anim(surf, x, y, groesse, wert, farbe, spin_deg):
    """Würfel mit 3D-Dreh-Animation um die Y-Achse (Spinning beim Würfeln)."""
    spin_rad   = math.radians(spin_deg)
    cos_val    = math.cos(spin_rad)
    scale_x    = max(0.04, abs(cos_val))

    # Welche Seite ist gerade vorne?
    vorne = cos_val >= 0
    draw_farbe = farbe if vorne else tuple(min(255, c + 50) for c in farbe)
    punkte     = vorne and scale_x > 0.25

    tmp = pygame.Surface((groesse, groesse), pygame.SRCALPHA)
    _zeichne_wuerfel_auf(tmp, groesse, wert, draw_farbe, punkte)

    scaled_w = max(4, int(groesse * scale_x))
    scaled   = pygame.transform.scale(tmp, (scaled_w, groesse))

    rand = max(6, groesse // 8)
    # Schatten
    sh = pygame.Surface((scaled_w + 10, groesse + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (*SCHATTEN, 90), (6, 6, scaled_w, groesse),
                     border_radius=rand)
    cx_off = groesse // 2 - scaled_w // 2
    surf.blit(sh, (x + cx_off - 4, y - 4))
    surf.blit(scaled, (x + cx_off, y))


def zeichne_button(surf, rect, text, font, farbe, textfarbe,
                   hover=False, radius=24):
    dunkel = tuple(max(0, c - 50) for c in farbe)
    hell   = tuple(min(255, c + 50) for c in farbe)
    pygame.draw.rect(surf, SCHATTEN, rect.move(5, 5), border_radius=radius)
    pygame.draw.rect(surf, hell if hover else farbe, rect, border_radius=radius)
    tief = pygame.Rect(rect.x, rect.bottom - radius // 2,
                       rect.width, radius // 2)
    pygame.draw.rect(surf, dunkel, tief, border_radius=radius)
    pygame.draw.rect(surf, dunkel, rect, width=3, border_radius=radius)
    ts = font.render(text, True, textfarbe)
    surf.blit(ts, ts.get_rect(center=rect.center))


# ── Sterne-Partikel ──────────────────────────────────────────────────────────

class Stern:
    def __init__(self, x, y):
        self.x  = float(x)
        self.y  = float(y)
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -3)
        self.farbe    = random.choice([GELB, ORANGE, ROSA, GRUEN, HELLBLAU])
        self.groesse  = random.randint(14, 28)
        self.leben    = 90
        self.rotation = random.uniform(0, 360)
        self.rot_spd  = random.uniform(-6, 6)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.35
        self.leben -= 1
        self.rotation += self.rot_spd

    def zeichne(self, surf):
        if self.leben <= 0:
            return
        alpha = min(255, self.leben * 3)
        g = self.groesse
        s = pygame.Surface((g * 2 + 4, g * 2 + 4), pygame.SRCALPHA)
        pts = []
        for i in range(10):
            ang = math.radians(self.rotation + i * 36 - 90)
            r   = g if i % 2 == 0 else g * 0.42
            pts.append((g + 2 + r * math.cos(ang),
                        g + 2 + r * math.sin(ang)))
        pygame.draw.polygon(s, (*self.farbe, alpha), pts)
        surf.blit(s, (int(self.x) - g - 2, int(self.y) - g - 2))


# ── Startbildschirm ──────────────────────────────────────────────────────────

class Startbildschirm:
    MODI        = ["addition", "subtraktion", "gemischt"]
    MODI_TEXT   = ["Addition", "Subtraktion", "Gemischt"]
    MODI_FARBEN = [DUNKELBLAU, ROT, ORANGE]

    def __init__(self, spiel):
        self.spiel   = spiel
        self.anzahl  = 2
        self.modus   = "gemischt"
        self.hover_s = self.hover_m = self.hover_p = False
        self.hover_modi = [False, False, False]
        self.werte   = [random.randint(1, 6) for _ in range(6)]
        self.timer   = 0

    def event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            if self._r_start().collidepoint(mx, my):
                self.spiel.starte_spiel(self.anzahl, self.modus)
            elif self._r_minus().collidepoint(mx, my) and self.anzahl > 2:
                self.anzahl -= 1
            elif self._r_plus().collidepoint(mx, my) and self.anzahl < 6:
                self.anzahl += 1
            else:
                for i, r in enumerate(self._r_modus_buttons()):
                    if r.collidepoint(mx, my):
                        self.modus = self.MODI[i]

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.hover_s = self._r_start().collidepoint(mx, my)
        self.hover_m = self._r_minus().collidepoint(mx, my)
        self.hover_p = self._r_plus().collidepoint(mx, my)
        self.hover_modi = [r.collidepoint(mx, my) for r in self._r_modus_buttons()]
        self.timer  += 1
        if self.timer % 60 == 0:
            self.werte[random.randint(0, 5)] = random.randint(1, 6)

    def zeichne(self, surf):
        W, H = surf.get_size()

        # Verlaufs-Hintergrund
        for i in range(H):
            t = i / H
            pygame.draw.line(surf,
                (int(200 + 55 * (1 - t)), int(225 + 30 * (1 - t)), 255),
                (0, i), (W, i))

        # Deko-Würfel
        for i, (bx, by) in enumerate([
            (60, 100), (W - 160, 80), (40, H - 180),
            (W - 180, H - 200), (W // 2 - 280, H - 160),
            (W // 2 + 180, H - 140),
        ]):
            alpha = 70 + int(25 * math.sin(self.timer * 0.05 + i))
            tmp = pygame.Surface((130, 130), pygame.SRCALPHA)
            zeichne_wuerfel(tmp, 5, 5, 110, self.werte[i],
                            WUERFEL_FARBEN[i], alpha)
            surf.blit(tmp, (bx, by))

        # Titel
        t1 = self.spiel.fg.render("Kinderwuerfeln", True, DUNKELBLAU)
        surf.blit(t1, t1.get_rect(centerx=W // 2, y=60))
        t2 = self.spiel.fm.render("Lerne Rechnen mit Wuerfeln!", True, LILA)
        surf.blit(t2, t2.get_rect(centerx=W // 2, y=180))
        pygame.draw.line(surf, DUNKELBLAU,
                         (W // 2 - 320, 270), (W // 2 + 320, 270), 4)

        # ── Würfelanzahl ──────────────────────────────────────────────────────
        t3 = self.spiel.fm.render("Wie viele Wuerfel?", True, SCHWARZ)
        surf.blit(t3, t3.get_rect(centerx=W // 2, y=295))

        zeichne_button(surf, self._r_minus(), "-", self.spiel.fm,
                       ROT, WEISS, self.hover_m and self.anzahl > 2, radius=20)

        box = pygame.Rect(W // 2 - 80, 390, 160, 120)
        pygame.draw.rect(surf, WEISS, box, border_radius=18)
        pygame.draw.rect(surf, DUNKELBLAU, box, width=4, border_radius=18)
        tz = self.spiel.fz.render(str(self.anzahl), True, DUNKELBLAU)
        surf.blit(tz, tz.get_rect(center=box.center))

        zeichne_button(surf, self._r_plus(), "+", self.spiel.fm,
                       GRUEN, WEISS, self.hover_p and self.anzahl < 6,
                       radius=20)

        # ── Rechenart-Auswahl ────────────────────────────────────────────────
        tma = self.spiel.fm.render("Rechenart:", True, SCHWARZ)
        surf.blit(tma, tma.get_rect(centerx=W // 2, y=540))

        for i, (r, text, farbe) in enumerate(zip(
                self._r_modus_buttons(), self.MODI_TEXT, self.MODI_FARBEN)):
            gewahlt = (self.modus == self.MODI[i])
            bg      = farbe if gewahlt else SCHATTEN
            rand    = 3 if gewahlt else 0
            # Hervorheben bei Auswahl
            if gewahlt:
                pygame.draw.rect(surf, GELB, r.inflate(8, 8), border_radius=20)
            zeichne_button(surf, r, text, self.spiel.fk, bg, WEISS,
                           self.hover_modi[i], radius=18)

        # ── Vorschau ──────────────────────────────────────────────────────────
        vy = 720
        tv = self.spiel.fk.render("Vorschau:", True, SCHWARZ)
        surf.blit(tv, tv.get_rect(centerx=W // 2, y=vy))
        ws = min(110, (W - 120) // max(self.anzahl, 1) - 24)
        gw = self.anzahl * (ws + 18) - 18
        sx = W // 2 - gw // 2
        for i in range(self.anzahl):
            bob  = int(8 * math.sin(self.timer * 0.08 + i * 0.8))
            wert = ((i * 7 + self.timer // 30) % 6) + 1
            zeichne_wuerfel(surf, sx + i * (ws + 18), vy + 48 + bob,
                            ws, wert, WUERFEL_FARBEN[i % 6])

        # ── Start-Button ──────────────────────────────────────────────────────
        zeichne_button(surf, self._r_start(), "Spielen!",
                       self.spiel.fm, GRUEN, WEISS, self.hover_s, radius=32)

        ti = self.spiel.fk.render(
            "Addition & Subtraktion  *  fuer Kinder ab 4 Jahren",
            True, DUNKELBLAU)
        surf.blit(ti, ti.get_rect(centerx=W // 2, y=H - 55))

    def _r_start(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        return pygame.Rect(W // 2 - 200, H - 175, 400, 110)

    def _r_minus(self):
        return pygame.Rect(self.spiel.breite // 2 - 270, 390, 120, 120)

    def _r_plus(self):
        return pygame.Rect(self.spiel.breite // 2 + 150, 390, 120, 120)

    def _r_modus_buttons(self):
        W  = self.spiel.breite
        bw, bh = 280, 80
        ab = 20
        total = 3 * bw + 2 * ab
        x0    = W // 2 - total // 2
        y0    = 615
        return [pygame.Rect(x0 + i * (bw + ab), y0, bw, bh) for i in range(3)]


# ── Spielbildschirm ──────────────────────────────────────────────────────────

class Spielbildschirm:
    ROLL_DAUER = 45

    def __init__(self, spiel, anzahl, modus="gemischt"):
        self.spiel   = spiel
        self.anzahl  = anzahl
        self.modus   = modus          # "addition", "subtraktion", "gemischt"
        self.wuerfel = [random.randint(1, 6) for _ in range(anzahl)]
        self.wz      = self.wuerfel[:]
        # Aufgabe
        self.aufgabe_typ   = "+"
        self.aufgabe_teile = []
        self.loesung       = 0
        # Eingabe
        self.eingabe  = ""
        self.feedback = None
        self.fb_timer = 0
        self.sterne: list[Stern] = []
        # Roll + 3D-Animation
        self.rollend      = False
        self.roll_timer   = 0
        self.spin_phases  = [random.uniform(0, 360) for _ in range(anzahl)]
        self.spin_speeds  = [random.uniform(250, 420) for _ in range(anzahl)]
        # Hover
        self.hov_w = self.hov_p = self.hov_m = False
        # Punkte
        self.richtig = 0
        self.gesamt  = 0
        self.wuerfeln()

    # ── Würfeln ──────────────────────────────────────────────────────────────
    def wuerfeln(self):
        self.wz          = [random.randint(1, 6) for _ in range(self.anzahl)]
        self.rollend     = True
        self.roll_timer  = self.ROLL_DAUER
        self.feedback    = None
        self.eingabe     = ""
        self.spin_phases = [random.uniform(0, 360) for _ in range(self.anzahl)]
        self.spin_speeds = [random.uniform(250, 420) for _ in range(self.anzahl)]

    def _generiere_aufgabe(self):
        """
        Aufgabe auf Basis ALLER gewürfelten Würfel.
        Addition:    alle N Würfel addieren:  w1 + w2 + … + wN = ?
        Subtraktion: alle Würfel (absteigend): größter − rest, solange ≥ 0.
        """
        w = self.wuerfel

        if self.anzahl == 1:
            extra = random.randint(1, 6)
            self.aufgabe_typ   = "+"
            self.aufgabe_teile = [w[0], extra]
            self.loesung       = w[0] + extra
            self.gesamt += 1
            return

        # Modus bestimmt ob Addition, Subtraktion oder Zufall
        if self.modus == "addition":
            do_sub = False
        elif self.modus == "subtraktion":
            do_sub = True
        else:  # gemischt
            do_sub = random.random() < 0.40

        if do_sub:
            # Subtraktion: alle Würfel absteigend; nur wenn Ergebnis >= 0
            sortiert = sorted(w, reverse=True)
            ergebnis = sortiert[0] - sum(sortiert[1:])
            if ergebnis >= 0:
                self.aufgabe_typ   = "-"
                self.aufgabe_teile = sortiert
                self.loesung       = ergebnis
                # Würfel in gleicher Reihenfolge wie Gleichung anzeigen
                self.wuerfel = sortiert[:]
            else:
                # Geht nicht ohne negatives Ergebnis → Addition
                self.aufgabe_typ   = "+"
                self.aufgabe_teile = w[:]
                self.loesung       = sum(w)
        else:
            self.aufgabe_typ   = "+"
            self.aufgabe_teile = w[:]
            self.loesung       = sum(w)

        self.gesamt += 1

    # ── Events ───────────────────────────────────────────────────────────────
    def event(self, ev):
        if self.rollend:
            return

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            if self._r_menu().collidepoint(mx, my):
                self.spiel.zustand = Startbildschirm(self.spiel)
                return
            if self.feedback is None:
                if self._r_wuerfeln().collidepoint(mx, my):
                    self.wuerfeln()
                elif self._r_pruefen().collidepoint(mx, my):
                    self._pruefen()
                else:
                    for n, r in self._ziffern_rects():
                        if r.collidepoint(mx, my):
                            if len(self.eingabe) < 3:
                                self.eingabe += str(n)
                    if self._r_loeschen().collidepoint(mx, my):
                        self.eingabe = self.eingabe[:-1]
            else:
                if self._r_wuerfeln().collidepoint(mx, my):
                    self.wuerfeln()

        if ev.type == pygame.KEYDOWN and self.feedback is None:
            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._pruefen()
            elif ev.key == pygame.K_BACKSPACE:
                self.eingabe = self.eingabe[:-1]
            elif ev.unicode.isdigit() and len(self.eingabe) < 3:
                self.eingabe += ev.unicode
            elif ev.key == pygame.K_ESCAPE:
                self.spiel.zustand = Startbildschirm(self.spiel)

    def _pruefen(self):
        if not self.eingabe:
            return
        versuch = int(self.eingabe)
        if versuch == self.loesung:
            self.feedback = "richtig"
            self.richtig += 1
            W, H = self.spiel.breite, self.spiel.hoehe
            for _ in range(30):
                self.sterne.append(Stern(
                    random.randint(W // 4, 3 * W // 4),
                    random.randint(H // 4, 3 * H // 4)))
        else:
            self.feedback = "falsch"
        self.fb_timer = 0

    # ── Update ───────────────────────────────────────────────────────────────
    def update(self):
        if self.rollend:
            self.roll_timer -= 1
            frac = self.roll_timer / self.ROLL_DAUER
            # 3D-Spin-Animation
            for i in range(self.anzahl):
                self.spin_phases[i] = (self.spin_phases[i]
                                       + self.spin_speeds[i] / 60) % 360
            # Zufällige Würfelwerte während des Rollens
            if self.roll_timer % max(1, int(frac * 8 + 1)) == 0:
                self.wuerfel = [random.randint(1, 6)
                                for _ in range(self.anzahl)]
            if self.roll_timer <= 0:
                self.wuerfel = self.wz[:]
                self.rollend = False
                self._generiere_aufgabe()

        if self.feedback is not None:
            self.fb_timer += 1

        for s in self.sterne:
            s.update()
        self.sterne = [s for s in self.sterne if s.leben > 0]

        mx, my = pygame.mouse.get_pos()
        self.hov_w = self._r_wuerfeln().collidepoint(mx, my)
        self.hov_p = self._r_pruefen().collidepoint(mx, my)
        self.hov_m = self._r_menu().collidepoint(mx, my)

    # ── Zeichnen ──────────────────────────────────────────────────────────────
    def zeichne(self, surf):
        W, H = surf.get_size()

        surf.fill(HINTERGRUND)
        pygame.draw.rect(surf, DUNKELBLAU, (0, 0, W, 120))

        # ── Kopfzeile ────────────────────────────────────────────────────────
        # Titel – nur im Bereich links vom Menü-Button
        tt = self.spiel.fm.render("Kinderwuerfeln", True, WEISS)
        surf.blit(tt, (30, 32))

        # Punkte-Anzeige – links vom Menü-Button (mit Abstand)
        pt = self.spiel.fk.render(
            f"Richtig: {self.richtig} / {self.gesamt}", True, GELB)
        modus_kurz = {"addition": "Addition",
                      "subtraktion": "Subtraktion",
                      "gemischt": "Gemischt"}[self.modus]
        mk = self.spiel.fw.render(f"Modus: {modus_kurz}", True, HELLBLAU)
        # Platzierung: Score rechts, aber mit Abstand vor dem Menü-Button
        score_x = W - 260 - pt.get_width()
        surf.blit(pt, (score_x, 25))
        surf.blit(mk, (score_x, 72))

        # Menü-Button ganz rechts
        zeichne_button(surf, self._r_menu(), "< Menue",
                       self.spiel.fw, HELLBLAU, DUNKELBLAU,
                       self.hov_m, radius=14)

        # ── Würfel ──────────────────────────────────────────────────────────
        wuerfel_y = 145
        rand_lr   = 60
        abstand   = 20
        ws_max    = min(160, (W - rand_lr * 2 - abstand * (self.anzahl - 1))
                        // self.anzahl)
        gw        = self.anzahl * ws_max + (self.anzahl - 1) * abstand
        sx        = W // 2 - gw // 2

        for i in range(self.anzahl):
            xi = sx + i * (ws_max + abstand)
            if self.rollend:
                bob = int(12 * math.sin(pygame.time.get_ticks() * 0.004 + i * 1.1))
                zeichne_wuerfel_3d_anim(surf, xi, wuerfel_y + bob, ws_max,
                                        self.wuerfel[i], WUERFEL_FARBEN[i % 6],
                                        self.spin_phases[i])
            else:
                zeichne_wuerfel(surf, xi, wuerfel_y, ws_max,
                                self.wuerfel[i], WUERFEL_FARBEN[i % 6])

        # ── Aufgabe ──────────────────────────────────────────────────────────
        if not self.rollend:
            aufgabe_y = wuerfel_y + ws_max + 40

            if self.aufgabe_typ == "+":
                teile_str   = " + ".join(str(t) for t in self.aufgabe_teile)
                aufgabe_str = f"{teile_str}  =  ?"
            else:
                teile_str   = " - ".join(str(t) for t in self.aufgabe_teile)
                aufgabe_str = f"{teile_str}  =  ?"

            as_surf = self.spiel.fa.render(aufgabe_str, True, SCHWARZ)
            kw = max(500, as_surf.get_width() + 80)
            karte = pygame.Rect(W // 2 - kw // 2, aufgabe_y, kw, 100)
            pygame.draw.rect(surf, WEISS, karte, border_radius=22)
            pygame.draw.rect(surf, DUNKELBLAU, karte, width=4, border_radius=22)
            surf.blit(as_surf, as_surf.get_rect(center=karte.center))

            # ── Eingabebereich ───────────────────────────────────────────────
            eing_y = aufgabe_y + 130

            lbl = self.spiel.fk.render("Deine Antwort:", True, DUNKELBLAU)
            surf.blit(lbl, lbl.get_rect(centerx=W // 2, y=eing_y))

            rfarbe = (DUNKELBLAU if self.feedback is None
                      else (DUNKELGRUEN if self.feedback == "richtig"
                            else DUNKELROT))
            bgfarbe = (WEISS if self.feedback is None
                       else ((220, 255, 220) if self.feedback == "richtig"
                             else (255, 220, 220)))
            er = pygame.Rect(W // 2 - 110, eing_y + 55, 220, 100)
            pygame.draw.rect(surf, bgfarbe, er, border_radius=18)
            pygame.draw.rect(surf, rfarbe, er, width=4, border_radius=18)
            anz = self.eingabe if self.eingabe else "..."
            es  = self.spiel.fz.render(anz, True, DUNKELBLAU)
            surf.blit(es, es.get_rect(center=er.center))

            # Cursor
            if (self.feedback is None
                    and pygame.time.get_ticks() % 1000 < 500
                    and self.eingabe):
                cx = er.centerx + es.get_width() // 2 + 5
                pygame.draw.line(surf, DUNKELBLAU,
                                 (cx, er.centery - 30),
                                 (cx, er.centery + 30), 3)

            # ── Ziffern-Pad ──────────────────────────────────────────────────
            if self.feedback is None:
                for n, r in self._ziffern_rects():
                    mx2, my2 = pygame.mouse.get_pos()
                    hov = r.collidepoint(mx2, my2)
                    zeichne_button(surf, r, str(n), self.spiel.fm,
                                   DUNKELBLAU if hov else (70, 120, 200),
                                   WEISS, hov, radius=18)
                lr  = self._r_loeschen()
                hov = lr.collidepoint(*pygame.mouse.get_pos())
                zeichne_button(surf, lr, "Del", self.spiel.fk,
                               ORANGE, WEISS, hov, radius=18)

            # ── Feedback ────────────────────────────────────────────────────
            if self.feedback is not None:
                fby = eing_y + 175
                if self.feedback == "richtig":
                    ft = f"Super! Richtig! Die Antwort ist {self.loesung}."
                    fc, fb = DUNKELGRUEN, (200, 255, 200)
                else:
                    ft = f"Nicht ganz... Die Antwort war {self.loesung}."
                    fc, fb = DUNKELROT, (255, 210, 210)
                fs = self.spiel.fm.render(ft, True, fc)
                pad_x, pad_y = 40, 18
                fk_w = fs.get_width() + pad_x * 2
                fk_h = fs.get_height() + pad_y * 2
                fk_w = max(fk_w, 400)
                fk = pygame.Rect(W // 2 - fk_w // 2, fby, fk_w, fk_h)
                pygame.draw.rect(surf, fb,  fk, border_radius=20)
                pygame.draw.rect(surf, fc,  fk, width=3, border_radius=20)
                surf.blit(fs, fs.get_rect(center=fk.center))

        # ── Haupt-Buttons ────────────────────────────────────────────────────
        wl = "Nochmal wuerfeln" if self.feedback else "Wuerfeln"
        zeichne_button(surf, self._r_wuerfeln(), wl,
                       self.spiel.fk, ORANGE, WEISS,
                       self.hov_w and not self.rollend, radius=26)

        if self.feedback is None and not self.rollend:
            zeichne_button(surf, self._r_pruefen(), "Pruefen",
                           self.spiel.fk, GRUEN, WEISS,
                           self.hov_p, radius=26)

        for s in self.sterne:
            s.zeichne(surf)

    # ── Rect-Definitionen ─────────────────────────────────────────────────────
    def _r_wuerfeln(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        return pygame.Rect(W // 2 - 340, H - 120, 300, 90)

    def _r_pruefen(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        return pygame.Rect(W // 2 + 40, H - 120, 300, 90)

    def _r_menu(self):
        W = self.spiel.breite
        return pygame.Rect(W - 220, 28, 195, 64)

    def _r_loeschen(self):
        pad_x, pad_y, bw, bh, ab = self._pad_params()
        return pygame.Rect(pad_x + 5 * (bw + ab), pad_y, bw, bh)

    def _pad_params(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        bw, bh, ab = 130, 100, 16
        total_w = 6 * bw + 5 * ab
        pad_x   = W // 2 - total_w // 2
        pad_y   = H - 340
        return pad_x, pad_y, bw, bh, ab

    def _ziffern_rects(self):
        pad_x, pad_y, bw, bh, ab = self._pad_params()
        rects   = []
        ziffern = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        for i, n in enumerate(ziffern):
            col = i % 5
            row = i // 5
            x   = pad_x + col * (bw + ab)
            y   = pad_y + row * (bh + ab)
            rects.append((n, pygame.Rect(x, y, bw, bh)))
        return rects


# ── Haupt-Spielklasse ────────────────────────────────────────────────────────

class Spiel:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Kinderwuerfeln - Mathe mit Wuerfeln")

        self.breite = 1400
        self.hoehe  = 1200
        self.surf   = pygame.display.set_mode((self.breite, self.hoehe),
                                               pygame.RESIZABLE)
        self.uhr    = pygame.time.Clock()

        def lade_font(g):
            for name in ("DejaVu Sans", "Liberation Sans", "FreeSans", "Arial", ""):
                try:
                    return pygame.font.SysFont(name, g)
                except Exception:
                    pass
            return pygame.font.Font(None, g)

        self.fg = lade_font(90)
        self.fz = lade_font(80)
        self.fm = lade_font(62)
        self.fa = lade_font(56)
        self.fk = lade_font(46)
        self.fw = lade_font(34)

        self.zustand = Startbildschirm(self)

    def starte_spiel(self, anzahl, modus="gemischt"):
        self.zustand = Spielbildschirm(self, anzahl, modus)

    def laufe(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.VIDEORESIZE:
                    self.breite = max(800, ev.w)
                    self.hoehe  = max(600, ev.h)
                    self.surf   = pygame.display.set_mode(
                        (self.breite, self.hoehe), pygame.RESIZABLE)
                self.zustand.event(ev)

            self.zustand.update()
            self.zustand.zeichne(self.surf)
            pygame.display.flip()
            self.uhr.tick(60)


def main():
    Spiel().laufe()


if __name__ == "__main__":
    main()
