#!/usr/bin/env python3
"""
Kinderwürfeln – Ein spielerisches Mathe-Lernprogramm für Kinder.
Kinder lernen Addition und Subtraktion mit bunten Würfeln.
"""

import pygame
import random
import sys
import math
import os

# ── Farben ──────────────────────────────────────────────────────────────────
WEISS       = (255, 255, 255)
SCHWARZ     = (  0,   0,   0)
HELLBLAU    = (135, 206, 250)
DUNKELBLAU  = ( 30,  80, 160)
GELB        = (255, 230,  50)
DUNKELGELB  = (200, 160,   0)
GRUEN       = ( 80, 200,  80)
DUNKELGRUEN = ( 30, 140,  30)
ROT         = (220,  60,  60)
DUNKELROT   = (160,  20,  20)
ORANGE      = (255, 150,  40)
LILA        = (160,  80, 200)
ROSA        = (255, 180, 220)
HINTERGRUND = (240, 248, 255)
WUERFEL_BG  = (255, 253, 240)
WUERFEL_RND = (230, 225, 200)
PUNKT_FARBE = ( 40,  40,  40)
SCHATTEN    = (180, 180, 180)

# ── Würfelpunkt-Positionen (relativ zu Würfelgröße 1.0) ─────────────────────
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
    (255, 100, 100),   # Rot
    (100, 160, 255),   # Blau
    (100, 220, 100),   # Grün
    (255, 200,  50),   # Gelb
    (200, 100, 255),   # Lila
    (255, 150,  50),   # Orange
]


def zeichne_wuerfel(surf: pygame.Surface, x: int, y: int, groesse: int,
                    wert: int, farbe: tuple, alpha: int = 255) -> None:
    """Zeichnet einen einzelnen Würfel mit abgerundeten Ecken und Punkten."""
    rand = max(4, groesse // 10)
    # Schatten
    schatten_surf = pygame.Surface((groesse + 6, groesse + 6), pygame.SRCALPHA)
    pygame.draw.rect(schatten_surf, (*SCHATTEN, 120),
                     (4, 4, groesse, groesse), border_radius=rand + 2)
    surf.blit(schatten_surf, (x - 2, y - 2))

    # Würfelkörper
    wuerfel_surf = pygame.Surface((groesse, groesse), pygame.SRCALPHA)
    pygame.draw.rect(wuerfel_surf, (*farbe, alpha),
                     (0, 0, groesse, groesse), border_radius=rand)
    # Heller Innenrahmen
    pygame.draw.rect(wuerfel_surf, (*WEISS, 80),
                     (2, 2, groesse - 4, groesse - 4), width=2,
                     border_radius=rand)
    surf.blit(wuerfel_surf, (x, y))

    # Punkte zeichnen
    punkt_r = max(3, groesse // 10)
    for px, py in PUNKTE_LAYOUT[wert]:
        cx = int(x + px * groesse)
        cy = int(y + py * groesse)
        # Punkt-Schatten
        pygame.draw.circle(surf, SCHATTEN, (cx + 1, cy + 1), punkt_r)
        pygame.draw.circle(surf, PUNKT_FARBE, (cx, cy), punkt_r)


def zeichne_button(surf: pygame.Surface, rect: pygame.Rect, text: str,
                   font: pygame.font.Font, farbe: tuple, textfarbe: tuple,
                   hover: bool = False, radius: int = 18) -> None:
    """Zeichnet einen schönen Button."""
    dunkel = tuple(max(0, c - 40) for c in farbe)
    hell = tuple(min(255, c + 60) for c in farbe)

    # Schatten
    pygame.draw.rect(surf, SCHATTEN,
                     rect.move(4, 4), border_radius=radius)
    # Hauptfläche
    btn_farbe = hell if hover else farbe
    pygame.draw.rect(surf, btn_farbe, rect, border_radius=radius)
    # Unterer Rand (3D-Effekt)
    rand_rect = pygame.Rect(rect.x, rect.y + rect.height - radius // 2,
                            rect.width, radius // 2)
    pygame.draw.rect(surf, dunkel, rand_rect, border_radius=radius)
    # Rahmen
    pygame.draw.rect(surf, dunkel, rect, width=2, border_radius=radius)

    txt_surf = font.render(text, True, textfarbe)
    txt_rect = txt_surf.get_rect(center=rect.center)
    surf.blit(txt_surf, txt_rect)


class Stern:
    """Dekorativer Stern für Erfolgsanimation."""
    def __init__(self, x: int, y: int):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-8, -2)
        self.farbe = random.choice([GELB, ORANGE, ROSA, GRUEN, HELLBLAU])
        self.groesse = random.randint(8, 18)
        self.leben = 90
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.leben -= 1
        self.rotation += self.rot_speed

    def zeichne(self, surf: pygame.Surface):
        if self.leben <= 0:
            return
        alpha = min(255, self.leben * 3)
        stern_surf = pygame.Surface((self.groesse * 2 + 4,
                                     self.groesse * 2 + 4), pygame.SRCALPHA)
        # Kleiner Stern (5 Zacken)
        punkte = []
        for i in range(10):
            winkel = math.radians(self.rotation + i * 36 - 90)
            r = self.groesse if i % 2 == 0 else self.groesse * 0.45
            px = self.groesse + 2 + r * math.cos(winkel)
            py = self.groesse + 2 + r * math.sin(winkel)
            punkte.append((px, py))
        if len(punkte) >= 3:
            pygame.draw.polygon(stern_surf, (*self.farbe, alpha), punkte)
        surf.blit(stern_surf,
                  (int(self.x) - self.groesse - 2,
                   int(self.y) - self.groesse - 2))


# ── Spielzustand-Klassen ────────────────────────────────────────────────────

class Startbildschirm:
    def __init__(self, spiel):
        self.spiel = spiel
        self.anzahl = 2          # Ausgewählte Würfelanzahl
        self.hover_start = False
        self.hover_minus = False
        self.hover_plus = False
        self.wuerfel_werte = [random.randint(1, 6) for _ in range(6)]
        self.animation_timer = 0

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self._rect_start().collidepoint(mx, my):
                self.spiel.starte_spiel(self.anzahl)
            elif self._rect_minus().collidepoint(mx, my) and self.anzahl > 1:
                self.anzahl -= 1
            elif self._rect_plus().collidepoint(mx, my) and self.anzahl < 6:
                self.anzahl += 1

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.hover_start = self._rect_start().collidepoint(mx, my)
        self.hover_minus = self._rect_minus().collidepoint(mx, my)
        self.hover_plus  = self._rect_plus().collidepoint(mx, my)
        self.animation_timer += 1
        if self.animation_timer % 60 == 0:
            idx = random.randint(0, 5)
            self.wuerfel_werte[idx] = random.randint(1, 6)

    def zeichne(self, surf: pygame.Surface):
        W, H = surf.get_size()

        # Hintergrund-Gradient (simuliert)
        for i in range(H):
            t = i / H
            r = int(200 + 55 * (1 - t))
            g = int(225 + 30 * (1 - t))
            b = int(255)
            pygame.draw.line(surf, (r, g, b), (0, i), (W, i))

        # Dekorative Würfel im Hintergrund
        bg_size = 60
        positions = [
            (50, 80), (W - 110, 60), (30, H - 130), (W - 120, H - 140),
            (W // 2 - 200, H - 100), (W // 2 + 140, H - 80),
        ]
        for i, (bx, by) in enumerate(positions):
            alpha = 80 + int(20 * math.sin(self.animation_timer * 0.05 + i))
            wuerfel_surf = pygame.Surface((bg_size + 10, bg_size + 10),
                                          pygame.SRCALPHA)
            zeichne_wuerfel(wuerfel_surf, 5, 5, bg_size,
                            self.wuerfel_werte[i],
                            WUERFEL_FARBEN[i], alpha)
            surf.blit(wuerfel_surf, (bx, by))

        # Titel
        titel = self.spiel.font_gross.render("🎲 Kinderwürfeln 🎲", True, DUNKELBLAU)
        surf.blit(titel, titel.get_rect(centerx=W // 2, y=40))

        untertitel = self.spiel.font_mittel.render(
            "Lerne Rechnen mit Würfeln!", True, LILA)
        surf.blit(untertitel, untertitel.get_rect(centerx=W // 2, y=120))

        # Trennlinie
        pygame.draw.line(surf, DUNKELBLAU, (W // 2 - 200, 165),
                         (W // 2 + 200, 165), 3)

        # Würfelauswahl
        auswahl_text = self.spiel.font_mittel.render(
            "Wie viele Würfel?", True, SCHWARZ)
        surf.blit(auswahl_text,
                  auswahl_text.get_rect(centerx=W // 2, y=190))

        # Minus-Button
        zeichne_button(surf, self._rect_minus(), "−", self.spiel.font_gross,
                       ROT, WEISS, self.hover_minus and self.anzahl > 1)

        # Anzahl-Anzeige
        box = pygame.Rect(W // 2 - 50, 260, 100, 70)
        pygame.draw.rect(surf, WEISS, box, border_radius=12)
        pygame.draw.rect(surf, DUNKELBLAU, box, width=3, border_radius=12)
        zahl = self.spiel.font_zahl.render(str(self.anzahl), True, DUNKELBLAU)
        surf.blit(zahl, zahl.get_rect(center=box.center))

        # Plus-Button
        zeichne_button(surf, self._rect_plus(), "+", self.spiel.font_gross,
                       GRUEN, WEISS, self.hover_plus and self.anzahl < 6)

        # Vorschau der Würfel
        vorschau_y = 360
        vorschau_text = self.spiel.font_klein.render(
            "Vorschau:", True, SCHWARZ)
        surf.blit(vorschau_text,
                  vorschau_text.get_rect(centerx=W // 2, y=vorschau_y))

        w_size = min(70, (W - 80) // max(self.anzahl, 1) - 20)
        gesamt_breite = self.anzahl * (w_size + 12) - 12
        start_x = W // 2 - gesamt_breite // 2
        for i in range(self.anzahl):
            bob = int(5 * math.sin(self.animation_timer * 0.08 + i * 0.8))
            wert = ((i * 7 + self.animation_timer // 30) % 6) + 1
            zeichne_wuerfel(surf, start_x + i * (w_size + 12),
                            vorschau_y + 30 + bob, w_size, wert,
                            WUERFEL_FARBEN[i % len(WUERFEL_FARBEN)])

        # Start-Button
        zeichne_button(surf, self._rect_start(), "Spielen! 🎮",
                       self.spiel.font_mittel, GRUEN, WEISS, self.hover_start,
                       radius=22)

        # Info-Text
        info = self.spiel.font_klein.render(
            "Addition & Subtraktion  •  für Kinder ab 4 Jahren",
            True, DUNKELBLAU)
        surf.blit(info, info.get_rect(centerx=W // 2, y=H - 35))

    def _rect_start(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        return pygame.Rect(W // 2 - 130, H - 120, 260, 65)

    def _rect_minus(self):
        W = self.spiel.breite
        return pygame.Rect(W // 2 - 170, 255, 70, 70)

    def _rect_plus(self):
        W = self.spiel.breite
        return pygame.Rect(W // 2 + 100, 255, 70, 70)


class Spielbildschirm:
    ROLL_DAUER = 40   # Frames

    def __init__(self, spiel, anzahl_wuerfel: int):
        self.spiel = spiel
        self.anzahl = anzahl_wuerfel
        self.wuerfel = [random.randint(1, 6) for _ in range(anzahl_wuerfel)]
        self.wuerfel_ziel = self.wuerfel[:]
        self.aufgabe_typ = "+"    # "+" oder "-"
        self.aufgabe_a = 0
        self.aufgabe_b = 0
        self.loesung = 0
        self.eingabe = ""
        self.eingabe_aktiv = True
        self.feedback = None      # None / "richtig" / "falsch"
        self.feedback_timer = 0
        self.sterne: list[Stern] = []
        self.rollend = False
        self.roll_timer = 0
        self.hover_wuerfeln = False
        self.hover_pruefen = False
        self.hover_menu = False
        self.punkte_richtig = 0
        self.punkte_gesamt = 0
        self.wuerfeln()

    # ── Würfeln & Aufgabe generieren ────────────────────────────────────────
    def wuerfeln(self):
        self.wuerfel_ziel = [random.randint(1, 6) for _ in range(self.anzahl)]
        self.rollend = True
        self.roll_timer = self.ROLL_DAUER
        self.feedback = None
        self.eingabe = ""
        self.eingabe_aktiv = True

    def _generiere_aufgabe(self):
        """Generiert nach dem Würfeln eine sinnvolle Aufgabe."""
        summe = sum(self.wuerfel)
        if self.anzahl >= 2 and random.random() < 0.45:
            # Subtraktion: zufälliger Minuend/Subtrahend aus Würfelwerten
            a = random.choice(self.wuerfel)
            b = random.choice(self.wuerfel)
            if a < b:
                a, b = b, a
            self.aufgabe_typ = "-"
            self.aufgabe_a = a
            self.aufgabe_b = b
            self.loesung = a - b
        else:
            # Addition: zwei zufällige Würfel oder alle
            if self.anzahl == 1:
                a = self.wuerfel[0]
                b = random.randint(1, 6)
                self.aufgabe_a = a
                self.aufgabe_b = b
                self.loesung = a + b
                self.aufgabe_typ = "+"
            elif self.anzahl == 2:
                self.aufgabe_a = self.wuerfel[0]
                self.aufgabe_b = self.wuerfel[1]
                self.loesung = self.aufgabe_a + self.aufgabe_b
                self.aufgabe_typ = "+"
            else:
                # Bei mehr Würfeln: zufällig 2 auswählen oder alle addieren
                if random.random() < 0.5:
                    idx = random.sample(range(self.anzahl), 2)
                    self.aufgabe_a = self.wuerfel[idx[0]]
                    self.aufgabe_b = self.wuerfel[idx[1]]
                else:
                    self.aufgabe_a = summe
                    self.aufgabe_b = 0
                    self.loesung = summe
                    self.aufgabe_typ = "Summe"
                    return
                self.loesung = self.aufgabe_a + self.aufgabe_b
                self.aufgabe_typ = "+"
        self.punkte_gesamt += 1

    # ── Events ──────────────────────────────────────────────────────────────
    def event(self, event):
        if self.rollend:
            return
        mx, my = pygame.mouse.get_pos() if hasattr(event, 'pos') else (0, 0)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.feedback is None:
                if self._rect_wuerfeln().collidepoint(mx, my):
                    self.wuerfeln()
                elif self._rect_pruefen().collidepoint(mx, my):
                    self._pruefen()
            else:
                if self._rect_wuerfeln().collidepoint(mx, my):
                    self.wuerfeln()
            if self._rect_menu().collidepoint(mx, my):
                self.spiel.zustand = Startbildschirm(self.spiel)

        if event.type == pygame.KEYDOWN and self.feedback is None:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._pruefen()
            elif event.key == pygame.K_BACKSPACE:
                self.eingabe = self.eingabe[:-1]
            elif event.unicode.isdigit() and len(self.eingabe) < 3:
                self.eingabe += event.unicode
            elif event.key == pygame.K_ESCAPE:
                self.spiel.zustand = Startbildschirm(self.spiel)

    def _pruefen(self):
        if not self.eingabe:
            return
        versuch = int(self.eingabe)
        if versuch == self.loesung:
            self.feedback = "richtig"
            self.punkte_richtig += 1
            # Sterne-Feuerwerk
            W, H = self.spiel.breite, self.spiel.hoehe
            for _ in range(25):
                sx = random.randint(W // 4, 3 * W // 4)
                sy = random.randint(H // 3, 2 * H // 3)
                self.sterne.append(Stern(sx, sy))
        else:
            self.feedback = "falsch"
        self.feedback_timer = 0

    # ── Update ──────────────────────────────────────────────────────────────
    def update(self):
        # Roll-Animation
        if self.rollend:
            self.roll_timer -= 1
            frac = self.roll_timer / self.ROLL_DAUER
            if self.roll_timer % max(1, int(frac * 8 + 1)) == 0:
                self.wuerfel = [random.randint(1, 6)
                                for _ in range(self.anzahl)]
            if self.roll_timer <= 0:
                self.wuerfel = self.wuerfel_ziel[:]
                self.rollend = False
                self._generiere_aufgabe()

        # Feedback-Timer
        if self.feedback is not None:
            self.feedback_timer += 1

        # Sterne
        for s in self.sterne:
            s.update()
        self.sterne = [s for s in self.sterne if s.leben > 0]

        # Hover
        mx, my = pygame.mouse.get_pos()
        self.hover_wuerfeln = self._rect_wuerfeln().collidepoint(mx, my)
        self.hover_pruefen  = self._rect_pruefen().collidepoint(mx, my)
        self.hover_menu     = self._rect_menu().collidepoint(mx, my)

    # ── Zeichnen ─────────────────────────────────────────────────────────────
    def zeichne(self, surf: pygame.Surface):
        W, H = surf.get_size()

        # Hintergrund
        surf.fill(HINTERGRUND)
        # Oben farbig
        pygame.draw.rect(surf, DUNKELBLAU, (0, 0, W, 70))

        # Titel-Leiste
        titel = self.spiel.font_mittel.render("🎲 Kinderwürfeln", True, WEISS)
        surf.blit(titel, (20, 18))

        # Punkte-Anzeige
        punkte_txt = self.spiel.font_klein.render(
            f"✓ {self.punkte_richtig} / {self.punkte_gesamt}",
            True, GELB)
        surf.blit(punkte_txt, (W - punkte_txt.get_width() - 20, 22))

        # Menü-Button
        zeichne_button(surf, self._rect_menu(), "← Menü",
                       self.spiel.font_winzig, HELLBLAU, DUNKELBLAU,
                       self.hover_menu, radius=10)

        # ── Würfel ──
        wuerfel_y = 100
        w_max = min(90, (W - 80) // max(self.anzahl, 1) - 16)
        gesamt_breite = self.anzahl * (w_max + 14) - 14
        start_x = W // 2 - gesamt_breite // 2

        for i in range(self.anzahl):
            bob = (int(8 * math.sin(pygame.time.get_ticks() * 0.003 + i * 1.1))
                   if self.rollend else 0)
            farbe = WUERFEL_FARBEN[i % len(WUERFEL_FARBEN)]
            zeichne_wuerfel(surf, start_x + i * (w_max + 14),
                            wuerfel_y + bob, w_max, self.wuerfel[i], farbe)

        # ── Aufgabe ──
        if not self.rollend:
            aufgabe_y = wuerfel_y + w_max + 30

            if self.aufgabe_typ == "Summe":
                aufgabe_str = (f"Wie viel ergibt die Summe "
                               f"aller Würfel?")
            else:
                aufgabe_str = (f"Was ist  {self.aufgabe_a}  "
                               f"{self.aufgabe_typ}  {self.aufgabe_b}  =  ?")

            # Aufgaben-Karte
            karte = pygame.Rect(W // 2 - 250, aufgabe_y, 500, 70)
            pygame.draw.rect(surf, WEISS, karte, border_radius=16)
            pygame.draw.rect(surf, DUNKELBLAU, karte, width=3, border_radius=16)
            aufgabe_surf = self.spiel.font_aufgabe.render(
                aufgabe_str, True, SCHWARZ)
            surf.blit(aufgabe_surf,
                      aufgabe_surf.get_rect(center=karte.center))

            # ── Eingabefeld ──
            eingabe_y = aufgabe_y + 90
            eingabe_label = self.spiel.font_klein.render(
                "Deine Antwort:", True, DUNKELBLAU)
            surf.blit(eingabe_label,
                      eingabe_label.get_rect(centerx=W // 2, y=eingabe_y))

            eingabe_rect = pygame.Rect(W // 2 - 75, eingabe_y + 32, 150, 60)
            rand_farbe = DUNKELBLAU if self.feedback is None else (
                DUNKELGRUEN if self.feedback == "richtig" else DUNKELROT)
            bg_farbe = WEISS if self.feedback is None else (
                (220, 255, 220) if self.feedback == "richtig" else (255, 220, 220))
            pygame.draw.rect(surf, bg_farbe, eingabe_rect, border_radius=12)
            pygame.draw.rect(surf, rand_farbe, eingabe_rect,
                             width=3, border_radius=12)

            anzeige = self.eingabe if self.eingabe else "…"
            eingabe_surf = self.spiel.font_zahl.render(anzeige, True,
                                                        DUNKELBLAU)
            surf.blit(eingabe_surf,
                      eingabe_surf.get_rect(center=eingabe_rect.center))

            # Cursor-Blinken
            if (self.feedback is None
                    and pygame.time.get_ticks() % 1000 < 500
                    and self.eingabe):
                cw = eingabe_surf.get_width()
                cx = eingabe_rect.centerx + cw // 2 + 3
                cy = eingabe_rect.centery
                pygame.draw.line(surf, DUNKELBLAU,
                                 (cx, cy - 20), (cx, cy + 20), 2)

            # ── Feedback ──
            if self.feedback is not None:
                fb_y = eingabe_y + 110
                if self.feedback == "richtig":
                    fb_text = f"Super! Richtig! 🌟  {self.aufgabe_a} {self.aufgabe_typ if self.aufgabe_typ != 'Summe' else '='} {self.aufgabe_b if self.aufgabe_typ != 'Summe' else ''} = {self.loesung}"
                    fb_farbe = DUNKELGRUEN
                    fb_bg = (200, 255, 200)
                else:
                    fb_text = f"Nicht ganz… Die Antwort war {self.loesung}. Probier nochmal!"
                    fb_farbe = DUNKELROT
                    fb_bg = (255, 200, 200)

                fb_karte = pygame.Rect(W // 2 - 260, fb_y, 520, 55)
                pygame.draw.rect(surf, fb_bg, fb_karte, border_radius=14)
                pygame.draw.rect(surf, fb_farbe, fb_karte,
                                 width=2, border_radius=14)
                fb_surf = self.spiel.font_klein.render(fb_text, True, fb_farbe)
                surf.blit(fb_surf, fb_surf.get_rect(center=fb_karte.center))

        # ── Buttons ──
        wuerfeln_label = ("Nochmal würfeln 🎲" if self.feedback is not None
                          else "Würfeln 🎲")
        zeichne_button(surf, self._rect_wuerfeln(), wuerfeln_label,
                       self.spiel.font_klein, ORANGE, WEISS,
                       self.hover_wuerfeln and not self.rollend, radius=20)

        if self.feedback is None and not self.rollend:
            zeichne_button(surf, self._rect_pruefen(), "Prüfen ✓",
                           self.spiel.font_klein, GRUEN, WEISS,
                           self.hover_pruefen, radius=20)

        # Tastatur-Hinweis
        if not self.rollend and self.feedback is None:
            hint = self.spiel.font_winzig.render(
                "Ziffern tippen & Enter drücken", True, SCHATTEN)
            surf.blit(hint, hint.get_rect(centerx=W // 2, y=H - 25))

        # Sterne
        for s in self.sterne:
            s.zeichne(surf)

    def _rect_wuerfeln(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        return pygame.Rect(W // 2 - 170, H - 80, 155, 52)

    def _rect_pruefen(self):
        W, H = self.spiel.breite, self.spiel.hoehe
        return pygame.Rect(W // 2 + 15, H - 80, 155, 52)

    def _rect_menu(self):
        return pygame.Rect(self.spiel.breite - 120, 15, 100, 38)


# ── Haupt-Spielklasse ────────────────────────────────────────────────────────

class Spiel:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Kinderwürfeln – Mathe mit Würfeln")

        # Icon setzen
        icon_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(icon_surf, DUNKELBLAU, (0, 0, 32, 32), border_radius=6)
        for px, py in PUNKTE_LAYOUT[5]:
            pygame.draw.circle(icon_surf, WEISS,
                               (int(px * 32), int(py * 32)), 3)
        pygame.display.set_icon(icon_surf)

        self.breite = 700
        self.hoehe  = 600
        self.surf   = pygame.display.set_mode((self.breite, self.hoehe),
                                               pygame.RESIZABLE)
        self.uhr    = pygame.time.Clock()

        # Schriften (fallback-sicher)
        def lade_font(groesse):
            for name in ("DejaVu Sans", "Liberation Sans", "FreeSans",
                         "Arial", ""):
                try:
                    f = pygame.font.SysFont(name, groesse)
                    return f
                except Exception:
                    pass
            return pygame.font.Font(None, groesse)

        self.font_gross   = lade_font(52)
        self.font_zahl    = lade_font(44)
        self.font_aufgabe = lade_font(32)
        self.font_mittel  = lade_font(36)
        self.font_klein   = lade_font(26)
        self.font_winzig  = lade_font(20)

        self.zustand = Startbildschirm(self)

    def starte_spiel(self, anzahl: int):
        self.zustand = Spielbildschirm(self, anzahl)

    def laufe(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.breite = max(600, event.w)
                    self.hoehe  = max(500, event.h)
                    self.surf = pygame.display.set_mode(
                        (self.breite, self.hoehe), pygame.RESIZABLE)
                self.zustand.event(event)

            self.zustand.update()
            self.zustand.zeichne(self.surf)
            pygame.display.flip()
            self.uhr.tick(60)


def main():
    spiel = Spiel()
    spiel.laufe()


if __name__ == "__main__":
    main()
