import os
import sys
import re
import json
import base64
import queue
import shutil
import hashlib
import struct
import tempfile
import threading
import subprocess
import math
import webbrowser
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk

from pyasar import pack, open_archive
from music_player import start_music, stop_music, ensure_music_playing


# ==========================================
# PATHS (PyInstaller-aware)
# ==========================================

if getattr(sys, "frozen", False):
    BASE    = Path(sys.executable).resolve().parent
    APP_DIR = Path(sys._MEIPASS)
else:
    BASE    = Path(__file__).resolve().parent
    APP_DIR = BASE


# ==========================================
# CONFIGURATION
# ==========================================

WAND_ROOT   = Path(os.environ.get("LOCALAPPDATA", "")) / "Wand"
OUTPUT_ROOT = BASE / "Wand-Patcher"

ENDPOINT     = "/v3/account"
PATCH_FIELDS = {"subscription": "Pro"}

UPDATE_EXE          = WAND_ROOT / "Update.exe"
UPDATE_EXE_DISABLED = WAND_ROOT / "Update.exe.disabled"

MUSIC_FILE = "music.mp3"

# Paste a base64-encoded image here to use as logo (header + window icon).
# PNG and GIF work out of the box. JPG/WebP need Pillow installed.
LOGO_B64 = "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"

AUTHOR_NAME      = "AliHo55eini"
AUTHOR_URL       = "https://github.com/AliHo55eini"
TEAM_NAME        = "The Great Hazard"
TEAM_URL         = "https://thegreathazard.com"
TEAM_URL_DISPLAY = "TheGreatHazard.com"

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

COL_BG           = "#0b1020"
COL_CARD         = "#151b2e"
COL_CARD_HOVER   = "#1c2440"
COL_TEXT         = "#e6e9f2"
COL_TEXT_MUTED   = "#8b93a7"
COL_ACCENT       = "#7c5cff"
COL_ACCENT_HOVER = "#9179ff"
COL_SUCCESS      = "#22c55e"
COL_WARNING      = "#f59e0b"
COL_DANGER       = "#ef4444"
COL_LOG_BG       = "#060912"
COL_LOG_FG       = "#7dd3fc"

FONT_UI      = ("Segoe UI", 10)
FONT_UI_BOLD = ("Segoe UI", 10, "bold")
FONT_H1      = ("Segoe UI", 18, "bold")
FONT_SMALL   = ("Segoe UI", 9)
FONT_SMALL_B = ("Segoe UI", 9, "bold")
FONT_MONO    = ("Consolas", 9)

_MUSIC_QUIET_PREFIXES = (
    "[MUSIC] using ",
    "[MUSIC] mixer initialized",
    "[MUSIC] playing (loop)",
    "[MUSIC] reusing ",
    "[MUSIC] wrote ",
)


# ==========================================
# LOGO LOADER
# ==========================================

def load_logo_b64(base64_str, max_size=48):
    if not base64_str.strip():
        return None

    raw = re.sub(r"\s+", "", base64_str)

    try:
        data = base64.b64decode(raw)
    except Exception:
        return None

    try:
        from PIL import Image, ImageTk
        import io
        img = Image.open(io.BytesIO(data))
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        pass

    try:
        img = tk.PhotoImage(data=raw)
        while img.width() > max_size or img.height() > max_size:
            img = img.subsample(2, 2)
        return img
    except Exception:
        return None


# ==========================================
# PROCESS HELPERS
# ==========================================

def is_process_running(image_name):
    if os.name != "nt":
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/NH", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5,
            creationflags=_NO_WINDOW,
        ).stdout or ""
        if "INFO:" in out:
            return False
        return image_name.lower() in out.lower()
    except Exception:
        return False


def kill_wand():
    if os.name != "nt":
        return
    for name in ("Wand.exe", "Update.exe"):
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/IM", name],
                capture_output=True, timeout=10,
                creationflags=_NO_WINDOW,
            )
        except Exception:
            pass


# ==========================================
# UPDATE.EXE TOGGLE
# ==========================================

def get_update_state():
    try:
        if UPDATE_EXE.exists() and not UPDATE_EXE_DISABLED.exists():
            return "enabled"
        if UPDATE_EXE_DISABLED.exists() and not UPDATE_EXE.exists():
            return "disabled"
    except OSError:
        pass
    return "missing"


def toggle_update_exe():
    state = get_update_state()
    if state == "enabled":
        UPDATE_EXE.rename(UPDATE_EXE_DISABLED)
        return "disabled"
    if state == "disabled":
        UPDATE_EXE_DISABLED.rename(UPDATE_EXE)
        return "enabled"
    raise FileNotFoundError(f"Update.exe was not found in:\n{WAND_ROOT}")


# ==========================================
# DETECTION
# ==========================================

def detect_versions():
    if not WAND_ROOT.is_dir():
        raise FileNotFoundError(
            "Wand doesn't appear to be installed.\n\n"
            f"Missing directory:\n{WAND_ROOT}"
        )

    installations = []
    for folder in WAND_ROOT.iterdir():
        if not folder.is_dir():
            continue
        version = folder.name.removeprefix("app-")
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", version):
            continue
        resources = folder / "resources"
        if (resources / "app.asar").is_file() and (folder / "Wand.exe").is_file():
            installations.append((version, folder))

    if not installations:
        raise FileNotFoundError(
            "Wand was found, but no complete app-x.x.x installation was detected."
        )

    installations.sort(
        key=lambda item: tuple(int(x) for x in item[0].split(".")),
        reverse=True,
    )
    return installations


def next_backup_dir():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    base = OUTPUT_ROOT / "Backup"
    if not base.exists():
        return base
    n = 1
    while True:
        candidate = OUTPUT_ROOT / f"Backup ({n})"
        if not candidate.exists():
            return candidate
        n += 1


# ==========================================
# JS PATCHING
# ==========================================

ACCOUNT_PATTERN = re.compile(
    r'getUserAccount\(\)\{return '
    r'this\.(#\w+)\.fetch\(\{'
    r'endpoint:"/v3/account",'
    r'method:"GET",'
    r'name:"/v3/account",'
    r'collectMetrics:!1'
    r'\}\)\}'
)

BOOST_PATTERN = re.compile(
    r'getBalance:(\w+)=>(\w+)\('
    r'(\w+\.\w+),'
    r'"/v3/account",'
    r'new URLSearchParams,'
    r'\{signal:\1\}\)'
)

INTEGRITY_PATTERN = re.compile(
    rb'\{"file":"resources\\\\app\.asar",'
    rb'"alg":"SHA256",'
    rb'"value":"([0-9a-fA-F]{64})"\}'
)


def account_transform(variable, fields):
    encoded = json.dumps(fields, ensure_ascii=True, separators=(",", ":"))
    return (
        f'({variable}!==null'
        f'&&typeof {variable}==="object"'
        f'&&!Array.isArray({variable})'
        f'?{{...{variable},...{encoded}}}'
        f':{variable})'
    )


def patch_javascript(content, fields):
    count = 0

    def replace_account(match):
        nonlocal count
        count += 1
        client = match.group(1)
        variable = "__wandPatchAccount"
        return (
            "async getUserAccount(){"
            f"const {variable}=await "
            f'this.{client}.fetch({{'
            'endpoint:"/v3/account",'
            'method:"GET",'
            'name:"/v3/account",'
            'collectMetrics:!1'
            '});'
            f"return {account_transform(variable, fields)};"
            "}"
        )

    content = ACCOUNT_PATTERN.sub(replace_account, content)

    def replace_boost(match):
        nonlocal count
        count += 1
        signal, fetch_fn, schema = match.groups()
        variable = "__wandPatchAccount"
        request = (
            f'{fetch_fn}({schema},'
            '"/v3/account",'
            'new URLSearchParams,'
            f'{{signal:{signal}}})'
        )
        return (
            f"getBalance:{signal}=>"
            f"{request}.then("
            f"{variable}=>"
            f"{account_transform(variable, fields)}"
            ")"
        )

    content = BOOST_PATTERN.sub(replace_boost, content)
    return content, count


def patch_bundles(source_dir, fields, log):
    changes = []
    unknown = []

    log("Searching JavaScript bundles...")
    for path in source_dir.rglob("*.js"):
        content = path.read_text(encoding="utf-8", errors="replace")
        if f'"{ENDPOINT}"' not in content:
            continue
        patched, count = patch_javascript(content, fields)
        if count:
            changes.append((path, patched, count))
            log(f"  Found: {path.name} ({count} matches)")
        else:
            unknown.append(path.name)

    if unknown:
        raise RuntimeError(
            "Unrecognized endpoint implementations:\n" + "\n".join(unknown)
        )
    if not changes:
        raise RuntimeError("No compatible account request methods found.")

    for path, patched, _ in changes:
        path.write_text(patched, encoding="utf-8")
        log(f"  Patched: {path.name}")

    return len(changes)


# ==========================================
# ASAR HELPERS
# ==========================================

def get_asar_header_hash(path):
    with Path(path).open("rb") as file:
        prefix = file.read(8)
        if len(prefix) != 8:
            raise ValueError("Invalid ASAR prefix.")
        header_size = struct.unpack_from("<I", prefix, 4)[0]
        if not 8 <= header_size <= 100_000_000:
            raise ValueError("Invalid ASAR header size.")
        header_pickle = file.read(header_size)
        if len(header_pickle) != header_size:
            raise ValueError("Incomplete ASAR header.")
        json_size = struct.unpack_from("<I", header_pickle, 4)[0]
        if json_size > header_size - 8:
            raise ValueError("Invalid JSON header size.")
        header_bytes = header_pickle[8:8 + json_size]
        header = json.loads(header_bytes.decode("utf-8"))
        if not isinstance(header, dict):
            raise ValueError("Invalid ASAR header JSON.")
        return hashlib.sha256(header_bytes).hexdigest()


def _close_archive(archive):
    close = getattr(archive, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def safe_extract(asar_path, dest_dir, log):
    asar_path = Path(asar_path)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    archive = open_archive(asar_path)
    try:
        with asar_path.open("rb") as probe:
            prefix = probe.read(8)
            header_size = struct.unpack_from("<I", prefix, 4)[0]
            payload_start = 8 + header_size

        packed = skipped = 0
        with asar_path.open("rb") as f:
            for name in archive.names():
                info = archive.info(name)
                if info.get("unpacked", False):
                    skipped += 1
                    continue
                if "files" in info:
                    continue

                rel = name.replace("\\", "/")
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)

                size = info.get("size", 0)
                if isinstance(size, str):
                    size = int(size, 10) if size else 0
                if size == 0:
                    target.write_bytes(b"")
                    packed += 1
                    continue

                offset = info.get("offset")
                if offset is None:
                    raise RuntimeError(f"Missing offset for {name}")
                if isinstance(offset, str):
                    offset = int(offset, 10)

                f.seek(payload_start + offset)
                data = f.read(size)
                if len(data) != size:
                    raise RuntimeError(f"Truncated ASAR payload for {name}")
                target.write_bytes(data)
                packed += 1

        log(f"  Extracted {packed} packed entries ({skipped} unpacked skipped)")
    finally:
        _close_archive(archive)


# ==========================================
# EXE INTEGRITY
# ==========================================

def inspect_exe_integrity(exe_path):
    data = Path(exe_path).read_bytes()
    match = INTEGRITY_PATTERN.search(data)
    if not match:
        return None
    return match.group(1).decode("ascii").lower()


def patch_exe_integrity(exe_path, new_hash):
    new_hash = new_hash.lower()
    if not re.fullmatch(r"[0-9a-f]{64}", new_hash):
        raise ValueError("Invalid SHA-256 hash.")
    path = Path(exe_path)
    data = bytearray(path.read_bytes())
    match = INTEGRITY_PATTERN.search(bytes(data))
    if not match:
        raise RuntimeError("No ELECTRONASAR integrity record found.")
    start = match.start(1)
    end = match.end(1)
    if (end - start) != 64:
        raise RuntimeError(f"Unexpected hash length: {end - start}")
    data[start:end] = new_hash.encode("ascii")
    path.write_bytes(bytes(data))
    return start


# ==========================================
# MAIN PATCH (replaces installation in place)
# ==========================================

def run_patch(installation, log):
    version, install_dir = installation
    resources = install_dir / "resources"

    original_asar    = resources / "app.asar"
    original_sidecar = resources / "app.asar.unpacked"
    original_exe     = install_dir / "Wand.exe"

    if not original_asar.is_file():
        raise FileNotFoundError(f"Missing {original_asar}")
    if not original_sidecar.is_dir():
        raise FileNotFoundError(f"Missing {original_sidecar}")
    if not original_exe.is_file():
        raise FileNotFoundError(f"Missing {original_exe}")

    backup_dir = next_backup_dir()

    try:
        temp_obj = tempfile.TemporaryDirectory(
            prefix="wand-debug-", ignore_cleanup_errors=True,
        )
    except TypeError:
        temp_obj = tempfile.TemporaryDirectory(prefix="wand-debug-")

    work = Path(temp_obj.name)

    try:
        log(f"Temporary folder: {work}")

        work_asar    = work / "app.asar"
        work_sidecar = work / "app.asar.unpacked"
        work_exe     = work / "Wand.exe"
        source       = work / "wand-src"
        stage_out    = work / "stage"

        log("Copying app.asar...")
        shutil.copy2(original_asar, work_asar)
        log("Copying app.asar.unpacked...")
        shutil.copytree(original_sidecar, work_sidecar)
        log("Copying Wand.exe...")
        shutil.copy2(original_exe, work_exe)

        log("Reading original ASAR hash...")
        original_hash = get_asar_header_hash(work_asar)
        exe_hash = inspect_exe_integrity(work_exe)
        log(f"  ASAR: {original_hash}")
        log(f"  EXE : {exe_hash}" if exe_hash else "  EXE : no integrity record")

        log("Reading unpacked paths...")
        archive = open_archive(work_asar)
        try:
            unpacked_paths = {
                name.replace("\\", "/")
                for name in archive.names()
                if archive.info(name).get("unpacked", False)
            }
        finally:
            _close_archive(archive)

        log("Extracting packed entries...")
        safe_extract(work_asar, source, log)

        log("Merging unpacked sidecar...")
        merged = 0
        for item in work_sidecar.rglob("*"):
            if item.is_file():
                rel = item.relative_to(work_sidecar)
                target = source / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
                merged += 1
        log(f"  Merged {merged} unpacked files")

        log("Applying subscription override...")
        count = patch_bundles(source, PATCH_FIELDS, log)

        stage_out.mkdir(parents=True, exist_ok=False)
        staged_asar = stage_out / "app.asar"
        staged_exe  = stage_out / "Wand.exe"

        def should_unpack(path):
            name = path.as_posix()
            return name in unpacked_paths or name.startswith("static/unpacked/")

        log("Repacking app.asar...")
        pack(str(source), str(staged_asar), unpack=should_unpack)

        log("Validating new ASAR...")
        archive = open_archive(staged_asar)
        try:
            new_names = set(archive.names())
            if not new_names:
                raise RuntimeError("Repacked ASAR is empty.")
            missing = unpacked_paths - new_names
            if missing:
                raise RuntimeError(
                    "Missing unpacked entries: " + ", ".join(sorted(missing)[:10])
                )
        finally:
            _close_archive(archive)

        log("Calculating new ASAR hash...")
        new_hash = get_asar_header_hash(staged_asar)
        log(f"  New ASAR hash: {new_hash}")

        shutil.copy2(work_exe, staged_exe)

        if exe_hash is not None:
            log("Injecting hash into Wand.exe...")
            patch_exe_integrity(staged_exe, new_hash)
            if inspect_exe_integrity(staged_exe) != new_hash:
                raise RuntimeError("EXE verification failed after injection.")
            log("  Wand.exe verified.")

        log(f"Backing up originals to {backup_dir}")
        backup_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy2(original_exe, backup_dir / "Wand.exe")
        shutil.copy2(original_asar, backup_dir / "app.asar")

        metadata = {
            "wandVersion":      version,
            "patchedBundles":   count,
            "fields":           PATCH_FIELDS,
            "originalAsarHash": original_hash,
            "newAsarHash":      new_hash,
            "exeIntegrityHash": inspect_exe_integrity(staged_exe),
            "integrityMatches": True,
            "patchedInPlace":   str(install_dir),
            "backupDirectory":  str(backup_dir),
        }
        (backup_dir / "patch-info.json").write_text(
            json.dumps(metadata, indent=4), encoding="utf-8"
        )

        log("Staging patched files in installation...")
        staged_asar_live = resources / "app.asar.new"
        staged_exe_live  = install_dir / "Wand.exe.new"
        shutil.copy2(staged_asar, staged_asar_live)
        shutil.copy2(staged_exe, staged_exe_live)

        log("Replacing app.asar...")
        try:
            os.replace(staged_asar_live, original_asar)
        except Exception:
            for p in (staged_asar_live, staged_exe_live):
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass
            raise

        log("Replacing Wand.exe...")
        try:
            os.replace(staged_exe_live, original_exe)
        except Exception:
            try:
                shutil.copy2(backup_dir / "app.asar", original_asar)
            except Exception:
                pass
            try:
                staged_exe_live.unlink(missing_ok=True)
            except Exception:
                pass
            raise

        log(f"Patched {count} bundle file(s).")
        log("Wand installation updated in place.")
        log(f"Backup: {backup_dir}")

        return str(backup_dir)

    finally:
        try:
            temp_obj.cleanup()
            log(f"Temporary folder deleted: {work}")
        except Exception as err:
            log(f"Warning: temp cleanup failed: {err}")


# ==========================================
# ROUNDED BUTTON
# ==========================================

class RoundButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg=None, fg=COL_TEXT,
                 hover=None, width=200, height=42, radius=10, font=None,
                 disabled=False, canvas_bg=None):
        try:
            parent_bg = parent.cget("bg")
        except Exception:
            parent_bg = COL_BG
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0,
                         bg=canvas_bg or parent_bg)
        self._rb_text     = text
        self._rb_cmd      = command
        self._rb_bg       = bg or COL_ACCENT
        self._rb_hover    = hover or self._rb_bg
        self._rb_fg       = fg
        self._rb_cw       = width
        self._rb_ch       = height
        self._rb_r        = radius
        self._rb_font     = font or FONT_UI_BOLD
        self._rb_disabled = disabled
        self._rb_hovered  = False
        self._rb_draw()
        if not disabled:
            self.bind("<Enter>", self._rb_on_enter)
            self.bind("<Leave>", self._rb_on_leave)
            self.bind("<Button-1>", self._rb_on_click)

    def _rb_draw(self):
        self.delete("all")
        color = "#2a3146" if self._rb_disabled else (
            self._rb_hover if self._rb_hovered else self._rb_bg
        )
        self._rb_round_rect(1, 1, self._rb_cw - 1, self._rb_ch - 1, self._rb_r, color)
        text_color = "#5a6478" if self._rb_disabled else self._rb_fg
        self.create_text(self._rb_cw / 2, self._rb_ch / 2, text=self._rb_text,
                         fill=text_color, font=self._rb_font)

    def _rb_round_rect(self, x1, y1, x2, y2, r, fill):
        pts = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        self.create_polygon(pts, smooth=True, fill=fill, outline=fill)

    def _rb_on_enter(self, _):
        self._rb_hovered = True
        self._rb_draw()

    def _rb_on_leave(self, _):
        self._rb_hovered = False
        self._rb_draw()

    def _rb_on_click(self, _):
        if self._rb_cmd and not self._rb_disabled:
            self._rb_cmd()

    def set_text(self, text):
        self._rb_text = text
        self._rb_draw()

    def set_disabled(self, disabled):
        self._rb_disabled = disabled
        self._rb_draw()


# ==========================================
# MODERN DIALOG
# ==========================================

class ModernDialog(tk.Toplevel):
    def __init__(self, parent, title, message, kind="info", buttons=None):
        super().__init__(parent)
        self.configure(bg=COL_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.title(title)
        self.result = None

        accent = {
            "info":    COL_ACCENT,
            "success": COL_SUCCESS,
            "warning": COL_WARNING,
            "error":   COL_DANGER,
        }.get(kind, COL_ACCENT)

        try:
            parent_icons = getattr(parent, "_window_icons", None)
            if parent_icons:
                self.iconphoto(True, *parent_icons)
            else:
                single = getattr(parent, "_window_icon_single", None)
                if single:
                    self.iconphoto(True, single)
        except Exception:
            pass

        frame = tk.Frame(self, bg=COL_BG, padx=26, pady=22)
        frame.pack(fill="both", expand=True)

        btn_area = tk.Frame(frame, bg=COL_BG)
        btn_area.pack(side="bottom", fill="x", pady=(20, 0))

        if buttons is None:
            buttons = [("OK", True)]

        for label, value in reversed(buttons):
            primary = (value is True or value == "primary")
            RoundButton(
                btn_area, label,
                command=lambda v=value: self._finish(v),
                bg=accent if primary else COL_CARD,
                hover=accent if primary else COL_CARD_HOVER,
                fg="#ffffff", width=110, height=38, radius=8,
                font=FONT_UI_BOLD, canvas_bg=COL_BG,
            ).pack(side="right", padx=(8, 0))

        tk.Label(frame, text=title, bg=COL_BG, fg=COL_TEXT,
                 font=("Segoe UI", 14, "bold"), anchor="w",
                 justify="left").pack(fill="x")
        tk.Frame(frame, bg=accent, height=2).pack(fill="x", pady=(8, 14))
        tk.Label(frame, text=message, bg=COL_BG, fg=COL_TEXT_MUTED,
                 font=("Segoe UI", 10), anchor="w", justify="left",
                 wraplength=440).pack(fill="x")

        self.update_idletasks()
        req_w = self.winfo_reqwidth()
        req_h = self.winfo_reqheight()
        w = max(req_w, 500)
        h = max(req_h, 200)
        px = parent.winfo_x() + (parent.winfo_width() - w) // 2
        py = parent.winfo_y() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{max(px, 0)}+{max(py, 0)}")

        self.grab_set()
        self.lift()
        self.focus_force()
        self.bind("<Escape>", lambda e: self._finish(None))
        self.bind("<Return>", lambda e: self._finish(buttons[0][1]))

    def _finish(self, value):
        self.result = value
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


def show_dialog(parent, title, message, kind="info", buttons=None):
    d = ModernDialog(parent, title, message, kind, buttons)
    parent.wait_window(d)
    return d.result


# ==========================================
# MAIN APP
# ==========================================

class WandPatcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wand(WeMod) Patcher")
        self.geometry("580x760")
        self.resizable(False, False)
        self.configure(bg=COL_BG)

        self.events        = queue.Queue()
        self.installations = []
        self.version_var   = tk.StringVar()
        self.status_var    = tk.StringVar(value="Ready")
        self._wand_running = False
        self._patching     = False
        self._kill_visible = False
        self._music_on     = False
        self._logo_image   = None

        self._window_icons       = []
        self._window_icon_single = None

        self._apply_window_icon()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()

        self.after(150, self._detect)
        self.after(100, self._process_events)
        self.after(500, self._poll_wand)

        self._music_on = start_music(self.log, MUSIC_FILE)
        self.after(3000, self._music_watchdog)

    # ---------- Window icon ----------

    def _apply_window_icon(self):
        if not LOGO_B64.strip():
            return
        try:
            raw = re.sub(r"\s+", "", LOGO_B64)
            data = base64.b64decode(raw)
        except Exception:
            return

        try:
            from PIL import Image, ImageTk
            import io
            base = Image.open(io.BytesIO(data))
            if base.mode != "RGBA":
                base = base.convert("RGBA")
            icons = []
            for size in (16, 24, 32, 48, 64, 128, 256):
                ico = base.copy()
                ico.thumbnail((size, size), Image.LANCZOS)
                icons.append(ImageTk.PhotoImage(ico))
            if icons:
                self._window_icons = icons
                self.iconphoto(True, *icons)
                return
        except ImportError:
            pass
        except Exception:
            pass

        try:
            img = tk.PhotoImage(data=raw)
            self._window_icon_single = img
            self.iconphoto(True, img)
        except Exception:
            pass

    # ---------- UI ----------

    def _build_ui(self):
        footer = tk.Frame(self, bg=COL_BG, padx=22)
        footer.pack(side="bottom", fill="x", pady=(4, 14))

        author = tk.Label(
            footer, text=AUTHOR_NAME, bg=COL_BG, fg=COL_ACCENT,
            font=FONT_SMALL, cursor="hand2",
        )
        author.pack(side="left")
        author.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_URL))

        team = tk.Label(
            footer, text=TEAM_URL_DISPLAY, bg=COL_BG, fg=COL_ACCENT,
            font=FONT_SMALL, cursor="hand2",
        )
        team.pack(side="right")
        team.bind("<Button-1>", lambda e: webbrowser.open(TEAM_URL))

        main = tk.Frame(self, bg=COL_BG, padx=22)
        main.pack(side="top", fill="both", expand=True, pady=(18, 0))

        header_row = tk.Frame(main, bg=COL_BG)
        header_row.pack(fill="x")

        self._logo_image = load_logo_b64(LOGO_B64, max_size=48)
        if self._logo_image is not None:
            logo_label = tk.Label(
                header_row, image=self._logo_image, bg=COL_BG,
            )
            logo_label.pack(side="left", padx=(0, 14))

        title_col = tk.Frame(header_row, bg=COL_BG)
        title_col.pack(side="left", fill="x", expand=True)

        tk.Label(title_col, text="Wand(WeMod) Patcher", bg=COL_BG, fg=COL_TEXT,
                 font=FONT_H1, anchor="w").pack(fill="x")
        tk.Label(title_col, text=f"by {AUTHOR_NAME}  ·  {TEAM_NAME}",
                 bg=COL_BG, fg=COL_TEXT_MUTED, font=FONT_SMALL,
                 anchor="w").pack(fill="x", pady=(2, 0))

        desc = tk.Frame(main, bg=COL_CARD, padx=16, pady=14)
        desc.pack(fill="x", pady=(14, 10))

        tk.Label(
            desc,
            text="[ + ]  WAND(WeMod) PRO — PATCHER",
            bg=COL_CARD, fg=COL_TEXT, font=FONT_UI_BOLD,
            anchor="w", justify="left",
        ).pack(fill="x")

        tk.Label(
            desc,
            text="[+]  Unlocks Pro features by patching the application.",
            bg=COL_CARD, fg=COL_TEXT_MUTED,
            font=("Segoe UI", 9), anchor="w", justify="left",
            wraplength=500,
        ).pack(fill="x", pady=(8, 0))

        tk.Label(
            desc,
            text=(
                "[!]  Online features require server-side verification "
                "and are not included."
            ),
            bg=COL_CARD, fg=COL_TEXT_MUTED,
            font=("Segoe UI", 9), anchor="w", justify="left",
            wraplength=500,
        ).pack(fill="x", pady=(4, 0))

        tk.Label(
            desc,
            text=(
                "[*]  Want online features patched too? Contact me via "
                "GitHub or my website. I'll consider implementing them if "
                "there's sufficient demand and financial incentive, "
                "potentially through a low-cost subscription."
            ),
            bg=COL_CARD, fg=COL_WARNING,
            font=("Segoe UI", 9, "bold"), anchor="w", justify="left",
            wraplength=500,
        ).pack(fill="x", pady=(10, 0))

        links_row = tk.Frame(desc, bg=COL_CARD)
        links_row.pack(fill="x", pady=(12, 0))

        gh_link = tk.Label(
            links_row, text=f"{AUTHOR_NAME}",
            bg=COL_CARD, fg=COL_ACCENT,
            font=("Segoe UI", 9, "underline"), cursor="hand2",
        )
        gh_link.pack(side="left")
        gh_link.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_URL))

        tk.Label(
            links_row, text="   ·   ",
            bg=COL_CARD, fg=COL_TEXT_MUTED, font=("Segoe UI", 9),
        ).pack(side="left")

        web_link = tk.Label(
            links_row, text=TEAM_URL_DISPLAY,
            bg=COL_CARD, fg=COL_ACCENT,
            font=("Segoe UI", 9, "underline"), cursor="hand2",
        )
        web_link.pack(side="left")
        web_link.bind("<Button-1>", lambda e: webbrowser.open(TEAM_URL))

        st = tk.Frame(main, bg=COL_CARD, padx=16, pady=12)
        st.pack(fill="x", pady=(0, 10))

        top_row = tk.Frame(st, bg=COL_CARD)
        top_row.pack(fill="x")
        self.dot = tk.Label(top_row, text="●", bg=COL_CARD,
                            fg=COL_TEXT_MUTED, font=("Segoe UI", 12))
        self.dot.pack(side="left")
        self.status_text = tk.Label(top_row, text="Checking Wand…",
                                    bg=COL_CARD, fg=COL_TEXT,
                                    font=FONT_UI, anchor="w")
        self.status_text.pack(side="left", padx=(6, 0), fill="x", expand=True)
        self.kill_btn = RoundButton(
            top_row, "Close Wand", command=self._kill_clicked,
            bg=COL_DANGER, hover="#f87171", fg="#ffffff",
            width=110, height=30, radius=8, font=FONT_SMALL_B,
            canvas_bg=COL_CARD,
        )

        vrow = tk.Frame(st, bg=COL_CARD)
        vrow.pack(fill="x", pady=(10, 0))
        tk.Label(vrow, text="Wand version", bg=COL_CARD,
                 fg=COL_TEXT_MUTED, font=FONT_SMALL).pack(side="left")
        self.version_box = ttk.Combobox(
            vrow, textvariable=self.version_var,
            state="readonly", width=14,
        )
        self.version_box.pack(side="left", padx=(10, 0))

        self.update_btn = RoundButton(
            main, "Disable Update.exe",
            command=self._toggle_update,
            bg=COL_CARD, hover=COL_CARD_HOVER, fg=COL_TEXT,
            width=536, height=40, radius=10, font=FONT_UI_BOLD,
            canvas_bg=COL_BG,
        )
        self.update_btn.pack(fill="x", pady=(0, 8))

        self.patch_btn = RoundButton(
            main, "Start Patch",
            command=self._start_patch,
            bg=COL_ACCENT, hover=COL_ACCENT_HOVER, fg="#ffffff",
            width=536, height=48, radius=12,
            font=("Segoe UI", 12, "bold"),
            canvas_bg=COL_BG,
        )
        self.patch_btn.pack(fill="x", pady=(0, 10))

        self.progress_canvas = tk.Canvas(
            main, height=6, bg=COL_BG,
            highlightthickness=0, bd=0,
        )
        self.progress_canvas.pack(fill="x", pady=(0, 8))
        self._progress_phase = 0
        self._progress_anim_running = False
        self._draw_progress_idle()

        tk.Label(main, textvariable=self.status_var, bg=COL_BG,
                 fg=COL_TEXT_MUTED, font=FONT_SMALL,
                 anchor="w").pack(fill="x", pady=(0, 8))

        log_frame = tk.Frame(main, bg=COL_CARD)
        log_frame.pack(fill="both", expand=True)
        self.log_widget = tk.Text(
            log_frame, font=FONT_MONO, bg=COL_LOG_BG, fg=COL_LOG_FG,
            relief="flat", height=8, state="disabled",
            padx=10, pady=8, wrap="word",
            bd=0, highlightthickness=0,
        )
        self.log_widget.pack(fill="both", expand=True)

        self._refresh_update_button()

    # ---------- Music watchdog ----------

    def _music_watchdog(self):
        try:
            if not self.winfo_exists():
                return
            if self._music_on:
                ensure_music_playing(self.log)
        except Exception as e:
            self.log(f"[MUSIC] Watchdog error: {e}")
        finally:
            if self.winfo_exists():
                self.after(3000, self._music_watchdog)

    # ---------- Progress ----------

    def _draw_progress_idle(self):
        self.progress_canvas.delete("all")
        self.progress_canvas.update_idletasks()
        w = max(self.progress_canvas.winfo_width(), 536)
        h = max(self.progress_canvas.winfo_height(), 6)
        self.progress_canvas.create_rectangle(0, 0, w, h, fill=COL_CARD, outline="")

    def _start_progress_anim(self):
        self._progress_anim_running = True
        self._progress_phase = 0
        self._animate_progress()

    def _stop_progress_anim(self):
        self._progress_anim_running = False
        self._draw_progress_idle()

    def _animate_progress(self):
        if not self._progress_anim_running:
            return
        self._progress_phase += 0.09
        self.progress_canvas.delete("all")
        self.progress_canvas.update_idletasks()
        w = max(self.progress_canvas.winfo_width(), 536)
        h = max(self.progress_canvas.winfo_height(), 6)
        self.progress_canvas.create_rectangle(0, 0, w, h, fill=COL_CARD, outline="")
        phase = self._progress_phase % (2 * math.pi)
        pos = (math.sin(phase) + 1) / 2
        seg_w = w * 0.35
        x1 = pos * (w - seg_w)
        x2 = x1 + seg_w
        self.progress_canvas.create_rectangle(x1, 0, x2, h, fill=COL_ACCENT, outline="")
        self.after(30, self._animate_progress)

    # ---------- Log ----------

    def log(self, text):
        if isinstance(text, str):
            stripped = text.strip()
            for prefix in _MUSIC_QUIET_PREFIXES:
                if stripped.startswith(prefix):
                    return
        self.log_widget.config(state="normal")
        self.log_widget.insert("end", text + "\n")
        self.log_widget.see("end")
        self.log_widget.config(state="disabled")

    # ---------- Update.exe ----------

    def _refresh_update_button(self):
        state = get_update_state()
        if state == "enabled":
            self.update_btn.set_text("Disable Update.exe")
            self.update_btn.set_disabled(False)
        elif state == "disabled":
            self.update_btn.set_text("Enable Update.exe")
            self.update_btn.set_disabled(False)
        else:
            self.update_btn.set_text("Update.exe not found")
            self.update_btn.set_disabled(True)

    def _toggle_update(self):
        if self._wand_running:
            show_dialog(self, "Wand is running",
                        "Close Wand before changing Update.exe.",
                        kind="warning")
            return
        try:
            new_state = toggle_update_exe()
        except Exception as err:
            show_dialog(self, "Update Toggle Error", str(err), kind="error")
            self._refresh_update_button()
            return
        self._refresh_update_button()
        self.log(f"Update.exe is now {new_state}")

    # ---------- Detection ----------

    def _detect(self):
        try:
            self.installations = detect_versions()
            versions = [v for v, _ in self.installations]
            self.version_box["values"] = versions
            self.version_var.set(versions[0])
            self.status_var.set(f"Wand {versions[0]} detected")
            self.log(f"Found installation: {WAND_ROOT}")
            self.log(f"Detected version: {versions[0]}")
        except Exception as err:
            self.status_var.set("Wand not installed")
            self.log(f"ERROR: {err}")
        finally:
            self._refresh_update_button()
            self._refresh_patch_button()

    # ---------- Wand process state ----------

    def _poll_wand(self):
        try:
            running = is_process_running("Wand.exe")
        except Exception:
            running = False
        self._set_wand_running(running)
        self.after(2000, self._poll_wand)

    def _set_wand_running(self, running):
        self._wand_running = running
        if running:
            self.dot.config(fg=COL_DANGER)
            self.status_text.config(
                text="Wand is running — please close it", fg=COL_DANGER
            )
            if not self._kill_visible:
                self.kill_btn.pack(side="right", padx=(8, 0))
                self._kill_visible = True
        else:
            self.dot.config(fg=COL_SUCCESS)
            self.status_text.config(
                text="Wand is not running", fg=COL_SUCCESS
            )
            if self._kill_visible:
                self.kill_btn.pack_forget()
                self._kill_visible = False
        self._refresh_patch_button()

    def _refresh_patch_button(self):
        can = bool(self.installations) and not self._wand_running and not self._patching
        self.patch_btn.set_disabled(not can)

    def _kill_clicked(self):
        self.log("Closing Wand…")
        kill_wand()
        self.after(500, self._poll_wand)

    # ---------- Patch workflow ----------

    def _start_patch(self):
        if self._wand_running:
            choice = show_dialog(
                self, "Wand is running",
                "Wand is currently open. Close it before patching.\n\n"
                "Would you like me to close it for you?",
                kind="warning",
                buttons=[("Cancel", None), ("Close Wand", "kill")],
            )
            if choice != "kill":
                return
            self.log("Closing Wand…")
            kill_wand()
            for _ in range(10):
                self.update()
                self.after(100)
                if not is_process_running("Wand.exe"):
                    break
            if is_process_running("Wand.exe"):
                show_dialog(self, "Could not close Wand",
                            "Wand is still running. Please close it manually.",
                            kind="error")
                return
            self._set_wand_running(False)

        try:
            installation = next(
                item for item in self.installations
                if item[0] == self.version_var.get()
            )
        except StopIteration:
            show_dialog(self, "Configuration Error",
                        "Please select a Wand version.", kind="error")
            return

        self._patching = True
        self._refresh_patch_button()
        self._start_progress_anim()
        self.status_var.set("Processing…")

        def worker():
            try:
                backup = run_patch(
                    installation,
                    lambda t: self.events.put(("log", t)),
                )
                self.events.put(("success", backup))
            except Exception as err:
                self.events.put(("error", str(err)))

        threading.Thread(target=worker, daemon=True).start()

    def _process_events(self):
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "log":
                    self.log(value)
                elif event == "success":
                    self._patching = False
                    self._stop_progress_anim()
                    self._refresh_patch_button()
                    self.status_var.set("Completed")
                    show_dialog(
                        self, "Patch Completed",
                        "Wand has been patched successfully.\n\n"
                        "Originals backed up to:\n"
                        f"{value}",
                        kind="success",
                    )
                elif event == "error":
                    self._patching = False
                    self._stop_progress_anim()
                    self._refresh_patch_button()
                    self.status_var.set("Failed")
                    self.log(f"ERROR: {value}")
                    show_dialog(self, "Patch Error", value, kind="error")
        except queue.Empty:
            pass
        self.after(100, self._process_events)

    # ---------- Close ----------

    def _on_close(self):
        try:
            stop_music(self.log)
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    WandPatcher().mainloop()