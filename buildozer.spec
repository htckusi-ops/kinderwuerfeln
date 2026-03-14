[app]

# Anzeigename auf dem Gerät
title = Sveas und Binjas Wuerfelspiel

# Eindeutiger Package-Name (lowercase, keine Sonderzeichen)
package.name = wuerfelspiel
package.domain = org.kinderspiel

# Quelldateien
source.dir = .
source.include_exts = py,ttf
source.include_patterns = DejaVuSans.ttf

# Version
version = 1.0

# Python-Abhängigkeiten
# pygame wird von python-for-android als Rezept mitgeliefert
requirements = python3,pygame

# Startdatei
entrypoint = wuerfeln.py

# Bildschirm
orientation = landscape
fullscreen = 1

# Android-Ziel-API (33 = Android 13, minAPI 21 = Android 5.0+)
android.api = 33
android.minapi = 21

# Architektur – arm64-v8a für moderne Geräte, armeabi-v7a für ältere
android.archs = arm64-v8a, armeabi-v7a

# Kein Icon nötig (Buildozer verwendet Standard wenn leer)
# icon.filename = %(source.dir)s/icon.png

# Berechtigungen – keine speziellen nötig für dieses Spiel
# android.permissions =

# Gradle-Optimierungen
android.gradle_dependencies =

# Release-Einstellungen (für Produktions-APK, debug reicht zum Testen)
# android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
