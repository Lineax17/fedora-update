# Sudo Keepalive Module

## Übersicht

Das `sudo_keepalive` Modul sorgt dafür, dass sudo-Berechtigungen während der gesamten Skriptausführung erhalten bleiben, indem es den sudo-Timestamp regelmäßig im Hintergrund aktualisiert.

## Funktionsweise

1. **Initialer Check**: Prüft ob das Script bereits als root läuft (EUID=0)
2. **Sudo-Validierung**: Fordert einmalig das sudo-Passwort an (`sudo -v`)
3. **Background-Thread**: Startet einen Daemon-Thread, der alle 60 Sekunden `sudo -n true` ausführt
4. **Automatisches Cleanup**: Registriert Handler für atexit, SIGINT und SIGTERM

## API

### Funktionen

#### `start(refresh_interval: int = 60) -> None`
Startet den globalen sudo-keepalive Thread.

**Parameter:**
- `refresh_interval`: Sekunden zwischen den Refreshes (Standard: 60)

**Wirft:**
- `SystemExit`: Wenn sudo-Validierung fehlschlägt

**Beispiel:**
```python
import sudo_keepalive

sudo_keepalive.start()
# Führe sudo-Befehle aus
```

#### `stop() -> None`
Stoppt den globalen sudo-keepalive Thread.

**Beispiel:**
```python
sudo_keepalive.stop()
```

#### `is_running() -> bool`
Prüft ob der keepalive Thread aktiv ist.

**Rückgabe:**
- `True` wenn aktiv, `False` sonst

**Beispiel:**
```python
if sudo_keepalive.is_running():
    print("Keepalive läuft")
```

### Klasse: SudoKeepalive

Die Klasse kann auch direkt verwendet werden, wenn mehr Kontrolle benötigt wird:

```python
from helper.sudo_keepalive import SudoKeepalive

keepalive = SudoKeepalive(refresh_interval=30)
keepalive.start()
# ... Operationen ...
keepalive.stop()
```

## Verwendungsbeispiele

### Basis-Verwendung

```python
from helper import sudo_keepalive, runner

def main():
    sudo_keepalive.start()
    
    try:
        runner.run(["sudo", "dnf", "update", "-y"])
        runner.run(["sudo", "dnf", "clean", "all"])
    finally:
        sudo_keepalive.stop()
```

### Mit Error Handling

```python
from helper import sudo_keepalive, runner

def main():
    print("Starte System-Update...")
    
    sudo_keepalive.start()
    
    try:
        # DNF Updates
        runner.run(["sudo", "dnf", "update", "-y"])
        
        # Flatpak Updates
        runner.run(["sudo", "flatpak", "update", "-y"])
        
        # NVIDIA Akmods
        runner.run(["sudo", "akmods", "--force"])
        
        print("✅ Update erfolgreich abgeschlossen")
        return 0
        
    except runner.CommandError as e:
        print(f"❌ Fehler: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Abbruch durch Benutzer")
        return 130
    finally:
        sudo_keepalive.stop()
```

### Mit Custom Refresh-Interval

```python
from helper import sudo_keepalive

# Refresh alle 30 Sekunden statt 60
sudo_keepalive.start(refresh_interval=30)
```

## Technische Details

### Threading-Architektur

- **Daemon-Thread**: Beendet sich automatisch wenn Hauptprozess stirbt
- **Event-basiert**: Nutzt `threading.Event()` für sauberes Stoppen
- **Non-blocking**: Wartet mit timeout statt zu sleepen

### Cleanup-Mechanismen

1. **atexit**: Registriert bei `start()`, läuft bei normalem Exit
2. **signal handler**: Fängt SIGINT (Ctrl+C) und SIGTERM ab
3. **try-finally**: Zusätzlicher Schutz im Hauptscript

### Sicherheit

- **Minimale Privilegien**: Thread führt nur `sudo -n true` aus, keine anderen Befehle
- **User-Kontrolle**: Initiale Passwort-Eingabe gibt User volle Kontrolle
- **Automatic Timeout**: Wenn Refresh fehlschlägt, stoppt der Thread automatisch

### Root-Handling

Wenn das Script bereits als root läuft (EUID=0), macht der keepalive nichts:
```python
if os.geteuid() == 0:
    logging.debug("Already running as root, sudo keepalive not needed")
    return
```

## Logging

Das Modul nutzt Python's logging-Framework:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
# Jetzt werden keepalive Debug-Meldungen ausgegeben
```

Debug-Meldungen:
- `"Already running as root, sudo keepalive not needed"`
- `"Sudo keepalive started (refresh every 60s)"`
- `"Sudo timestamp refreshed"`
- `"Stopping sudo keepalive"`

Warnungen:
- `"Sudo keepalive is already running"`
- `"Failed to refresh sudo timestamp"`

Fehler:
- `"Error refreshing sudo: {exception}"`
- `"Sudo validation failed: {exception}"`

## Best Practices

### ✅ DO

```python
# Immer finally für Cleanup verwenden
sudo_keepalive.start()
try:
    # ... Code ...
finally:
    sudo_keepalive.stop()

# Nur einmal pro Prozess starten (Singleton-Pattern)
sudo_keepalive.start()
```

### ❌ DON'T

```python
# Kein Cleanup - Thread läuft weiter!
sudo_keepalive.start()
# ... Code ...

# Mehrfach starten (funktioniert, aber unnötig)
sudo_keepalive.start()
sudo_keepalive.start()  # Warnung: Already running
```

## Troubleshooting

### Problem: "Error: sudo privileges are required to continue"
**Lösung**: User hat keine sudo-Rechte oder hat falsches Passwort eingegeben.

### Problem: Keepalive stoppt unerwartet
**Prüfen**:
- Läuft `sudo -n true` noch? → `sudo -n true` im Terminal testen
- Ist sudo-Timeout zu kurz? → `/etc/sudoers` Einstellungen prüfen

### Problem: Script fragt nach Passwort trotz keepalive
**Ursachen**:
- Keepalive wurde nicht gestartet vor sudo-Befehlen
- Keepalive Thread ist abgestürzt (Check logs)
- Sudo-Timestamp wurde extern invalidiert

## Tests

Test-Suite ausführen:
```bash
python3 tests/test_sudo_keepalive.py
```

Die Tests prüfen:
- ✅ Start/Stop Funktionalität
- ✅ Multiple sudo-Befehle ohne erneutes Passwort
- ✅ is_running() Status
- ✅ Cleanup bei Exit

## Kompatibilität

- **Python**: 3.10+
- **OS**: Linux/Unix (sudo muss verfügbar sein)
- **Dependencies**: Nur Python stdlib (subprocess, threading, etc.)

## Performance

- **Memory**: ~100KB für Thread
- **CPU**: Minimal (~0.1% alle 60 Sekunden)
- **Network**: Keine

## Vergleich mit Bash-Version

| Feature | Bash | Python |
|---------|------|--------|
| Background-Process | Subshell `( ... ) &` | `threading.Thread` |
| Cleanup | `trap` | atexit + signal handler |
| PID-Check | `kill -0 $pid` | Event-based |
| Logging | echo/stderr | logging module |
| Testing | Schwierig | Einfach (mocking) |
| Typ-Sicherheit | Keine | Type hints |

## Lizenz

Siehe LICENSE Datei im Projekt-Root.

