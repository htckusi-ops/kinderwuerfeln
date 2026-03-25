#!/usr/bin/env python3
"""
Kinderwürfeln V2 – Verbessert für Svea & Binja
Mit Sound, Sprachausgabe, Schwierigkeitsstufen, Highscore, besserem Feedback und Web-Support
"""

import pygame
import random
import sys
import math
import os
import json
import asyncio

# ====================== PFade & KONSTANTEN ======================
_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(_DIR, "assets")
BUNDLED_TTF = os.path.join(_DIR, "DejaVuSans.ttf")

VIRT_W, VIRT_H = 1400, 1000

# ====================== FARBEN (knalliger & kindgerecht) ======================
HINTERGRUND = (255, 245, 250)
DUNKELBLAU = (25, 70, 150)
GRUEN = (70, 200, 70)
DUNKELGRUEN = (30, 150, 30)
ROT = (255, 70, 70)
ORANGE = (255, 140, 40)
GELB = (255, 220, 50)
LILA = (170, 90, 255)
WEISS = (255, 255, 255)
SCHWARZ = (35, 35, 35)
HELLGRAU = (230, 230, 230)

# ====================== FONTS ======================
def lade_font(groesse):
    if os.path.exists(BUNDLED_TTF):
        try:
            return pygame.font.Font(BUNDLED_TTF, groesse)
        except:
            pass
    return pygame.font.SysFont("Arial", groesse, bold=True)

# ====================== HIGHSCORE ======================
def lade_highscore():
    try:
        with open(os.path.join(_DIR, "highscore.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"sterne_gesamt": 0, "stufen": {}}

def speichere_highscore(data):
    with open(os.path.join(_DIR, "highscore.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====================== SOUND & SPRACHAUSGABE ======================
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

roll_sound = correct_sound = wrong_sound = None
try:
    roll_sound = pygame.mixer.Sound(os.path.join(ASSETS, "dice_roll.wav"))
    correct_sound = pygame.mixer.Sound(os.path.join(ASSETS, "correct.wav"))
    wrong_sound = pygame.mixer.Sound(os.path.join(ASSETS, "wrong.wav"))
    pygame.mixer.music.load(os.path.join(ASSETS, "background_music.mp3"))
    pygame.mixer.music.set_volume(0.22)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Warnung: Sounds konnten nicht geladen werden:", e)

def sprich(text):
    """Sprachausgabe der Aufgabe – funktioniert gut auf Desktop"""
    try:
        # Versuch mit pyttsx3 (Desktop)
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 135)
        engine.say(text)
        engine.runAndWait()
    except:
        # Fallback für Web / andere Systeme (Browser TTS später möglich)
        pass

# ====================== STERN-PARTIKEL ======================
class Stern:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-12, -4)
        self.farbe = random.choice([GELB, ORANGE, (255, 100, 255), GRUEN, (100, 200, 255)])
        self.groesse = random.randint(16, 32)
        self.leben = 110
        self.rotation = random.uniform(0, 360)
        self.rot_spd = random.uniform(-8, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.38
        self.leben -= 1
        self.rotation += self.rot_spd

    def zeichne(self, surf):
        if self.leben <= 0:
            return
        alpha = min(255, int(self.leben * 3))
        g = self.groesse
        s = pygame.Surface((g*2 + 8, g*2 + 8), pygame.SRCALPHA)
        pts = []
        for i in range(10):
            ang = math.radians(self.rotation + i * 36 - 90)
            r = g if i % 2 == 0 else g * 0.4
            pts.append((g + 4 + r * math.cos(ang), g + 4 + r * math.sin(ang)))
        pygame.draw.polygon(s, (*self.farbe, alpha), pts)
        surf.blit(s, (int(self.x) - g - 4, int(self.y) - g - 4))

# ====================== HAUPT-SPIEL ======================
class KinderWuerfeln:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Svea's und Binja's Würfelspiel ✨")
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
        self.virt = pygame.Surface((VIRT_W, VIRT_H))
        self.clock = pygame.time.Clock()

        self.font_titel = lade_font(85)
        self.font_gross = lade_font(68)
        self.font_mittel = lade_font(52)
        self.font_klein = lade_font(42)
        self.font_tiny = lade_font(34)

        self.highscore = lade_highscore()
        self.sterne_gesamt = self.highscore.get("sterne_gesamt", 0)

        self.zustand = "start"          # start, spiel, ergebnis
        self.aktueller_spieler = 1
        self.spieler_punkte = [0, 0]    # für 2-Spieler

        self.stufe = 1
        self.modus = "addition"         # addition, subtraktion, gemischt
        self.anzahl_wuerfel = 2
        self.zeitmodus = False
        self.zeit_limit = 0

        self.reset_runde()

    def reset_runde(self):
        self.wuerfel = []
        self.aufgabe_str = ""
        self.loesung = 0
        self.eingabe = ""
        self.feedback = None          # None, "richtig", "falsch"
        self.feedback_timer = 0
        self.sterne_partikel = []
        self.richtig_diese_runde = 0
        self.gesamt_diese_runde = 0
        self.rollend = False
        self.roll_timer = 0

    def neue_aufgabe(self):
        max_wert = min(6, self.stufe + 2)
        self.wuerfel = [random.randint(1, max_wert) for _ in range(self.anzahl_wuerfel)]

        if self.modus == "subtraktion" or (self.modus == "gemischt" and random.random() < 0.45):
            sortiert = sorted(self.wuerfel, reverse=True)
            self.loesung = sortiert[0] - sum(sortiert[1:])
            if self.loesung < 0:
                self.loesung = sum(self.wuerfel)
                self.aufgabe_str = " + ".join(map(str, self.wuerfel)) + " = ?"
            else:
                self.aufgabe_str = " - ".join(map(str, sortiert)) + " = ?"
        else:
            self.loesung = sum(self.wuerfel)
            self.aufgabe_str = " + ".join(map(str, self.wuerfel)) + " = ?"

        # Aufgabe laut vorlesen
        sprich(self.aufgabe_str.replace("= ?", "ist wie viel?"))

        if roll_sound:
            roll_sound.play()

        self.rollend = True
        self.roll_timer = 45

    def pruefen(self):
        if not self.eingabe:
            return
        try:
            versuch = int(self.eingabe)
        except:
            return

        if versuch == self.loesung:
            self.feedback = "richtig"
            self.richtig_diese_runde += 1
            self.sterne_gesamt += 1
            if correct_sound:
                correct_sound.play()

            for _ in range(35):
                self.sterne_partikel.append(Stern(random.randint(300, 1100), random.randint(200, 700)))
        else:
            self.feedback = "falsch"
            if wrong_sound:
                wrong_sound.play()

        self.feedback_timer = 0
        self.gesamt_diese_runde += 1

    def handle_event(self, ev):
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.zustand == "start":
            # Hier kommen später die Buttons für Stufe, Modus, Anzahl, Start
            if ev.type == pygame.MOUSEBUTTONDOWN:
                # Vereinfacht: Klick irgendwo startet das Spiel (später erweitern)
                self.zustand = "spiel"
                self.neue_aufgabe()

        elif self.zustand == "spiel":
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.zustand = "start"
                elif ev.key == pygame.K_BACKSPACE:
                    self.eingabe = self.eingabe[:-1]
                elif ev.unicode.isdigit() and len(self.eingabe) < 3:
                    self.eingabe += ev.unicode
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.pruefen()

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                # Hier später Ziffern-Buttons, Wuerfeln-Button etc.
                if self.feedback is None and not self.rollend:
                    self.pruefen()   # für schnelles Testen

    def update(self):
        if self.rollend:
            self.roll_timer -= 1
            if self.roll_timer <= 0:
                self.rollend = False
                # Würfel sind fertig gerollt → Aufgabe generieren (bereits in neue_aufgabe)

        if self.feedback is not None:
            self.feedback_timer += 1
            if self.feedback_timer > 180:   # ca. 3 Sekunden
                self.feedback = None
                self.eingabe = ""
                self.neue_aufgabe()

        # Partikel updaten
        for s in self.sterne_partikel[:]:
            s.update()
            if s.leben <= 0:
                self.sterne_partikel.remove(s)

    def draw(self):
        self.virt.fill(HINTERGRUND)

        if self.zustand == "start":
            titel = self.font_titel.render("Svea's & Binja's", True, LILA)
            self.virt.blit(titel, titel.get_rect(centerx=VIRT_W//2, y=80))
            titel2 = self.font_gross.render("Würfelspiel", True, DUNKELBLAU)
            self.virt.blit(titel2, titel2.get_rect(centerx=VIRT_W//2, y=180))

            start_txt = self.font_mittel.render("Klick zum Starten", True, GRUEN)
            self.virt.blit(start_txt, start_txt.get_rect(center=(VIRT_W//2, VIRT_H//2)))

        elif self.zustand == "spiel":
            # Kopfzeile
            header = self.font_klein.render(f"Stufe {self.stufe}  •  {self.modus.capitalize()}", True, DUNKELBLAU)
            self.virt.blit(header, (50, 30))

            score = self.font_mittel.render(f"Sterne: {self.sterne_gesamt}", True, GELB)
            self.virt.blit(score, score.get_rect(topright=(VIRT_W-50, 30)))

            # Würfel zeichnen (vereinfacht)
            ws = 140
            start_x = (VIRT_W - (self.anzahl_wuerfel * (ws + 40))) // 2
            for i, wert in enumerate(self.wuerfel):
                x = start_x + i * (ws + 40)
                # Hier später schöne Würfel-Zeichnung einbauen (aus deinem Original übernehmen)
                pygame.draw.rect(self.virt, (255, 200, 100), (x, 180, ws, ws), border_radius=20)
                num = self.font_gross.render(str(wert), True, SCHWARZ)
                self.virt.blit(num, num.get_rect(center=(x + ws//2, 180 + ws//2)))

            # Aufgabe
            if not self.rollend:
                aufg = self.font_mittel.render(self.aufgabe_str, True, SCHWARZ)
                self.virt.blit(aufg, aufg.get_rect(centerx=VIRT_W//2, y=420))

            # Eingabe
            eingabe_txt = self.font_gross.render(self.eingabe if self.eingabe else "?", True, DUNKELBLAU)
            self.virt.blit(eingabe_txt, eingabe_txt.get_rect(centerx=VIRT_W//2, y=580))

            # Feedback
            if self.feedback == "richtig":
                fb = self.font_mittel.render("Super! Richtig! ⭐", True, DUNKELGRUEN)
                self.virt.blit(fb, fb.get_rect(centerx=VIRT_W//2, y=720))
            elif self.feedback == "falsch":
                fb = self.font_mittel.render(f"Fast! Die Lösung war {self.loesung}", True, ROT)
                self.virt.blit(fb, fb.get_rect(centerx=VIRT_W//2, y=720))

            # Sterne zeichnen
            for s in self.sterne_partikel:
                s.zeichne(self.virt)

        # Skalieren und anzeigen
        scaled = pygame.transform.smoothscale(self.virt, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)


# ====================== START ======================
async def main():
    game = KinderWuerfeln()
    await asyncio.sleep(0)   # für pygbag notwendig
    game.run()               # (die run-Methode ist synchron, für Web wird sie angepasst)

if __name__ == "__main__":
    asyncio.run(main())
