import sys
from pathlib import Path

try:
    import pygame
except ImportError:
    pygame = None


_state = {
    "initialized": False,
    "playing":     False,
    "path":        None,
    "error":       None,
}


def _resource_path(filename):

    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base / filename


def _log(log, msg):
    if log:
        try:
            log(msg)
        except Exception:
            pass


def start_music(log=None, music_file="music.mp3"):

    global _state

    if pygame is None:
        _log(log, "[MUSIC] pygame is not installed (pip install pygame)")
        return False

    if _state["initialized"] and _state["playing"]:
        return True

    candidates = [
        _resource_path(music_file),
        Path(__file__).resolve().parent / music_file,
        Path.cwd() / music_file,
    ]
    path = next((c for c in candidates if c.is_file()), None)

    if path is None:
        _log(log, f"[MUSIC] {music_file} not found next to app")
        return False

    _log(log, f"[MUSIC] using {path} ({path.stat().st_size} bytes)")

    try:
        if not _state["initialized"]:
            pygame.mixer.init()
            _state["initialized"] = True
            _log(log, "[MUSIC] mixer initialized")

        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(loops=-1)

        _state["playing"] = True
        _state["path"] = str(path)
        _state["error"] = None
        _log(log, "[MUSIC] playing (loop)")
        return True
    except Exception as e:
        _state["error"] = str(e)
        _log(log, f"[MUSIC] failed to start: {e}")
        return False


def stop_music(log=None):

    global _state
    if pygame is None:
        return
    try:
        if _state["initialized"]:
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()
            except Exception:
                pass
    except Exception as e:
        _log(log, f"[MUSIC] stop error: {e}")
    _state["playing"] = False


def ensure_music_playing(log=None):

    global _state
    if pygame is None or not _state["playing"]:
        return False
    try:
        if not pygame.mixer.music.get_busy():
            _log(log, "[MUSIC] watchdog: not busy, restarting")
            pygame.mixer.music.play(loops=-1)
            return True
    except Exception as e:
        _log(log, f"[MUSIC] watchdog error: {e}, attempting full restart")
        try:
            return start_music(log)
        except Exception:
            return False
    return True