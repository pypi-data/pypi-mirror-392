from ..imports import *
import os, sys
from PyQt6.QtWidgets import QWidget

# ---------------- xrandr / wmctrl parsing ----------------
def get_monitors(self) -> List[Tuple[str, int, int, int, int]]:
    self.monitors = []
    out = self.run_command("xrandr --query | grep ' connected'")
    for line in out.splitlines():
        m = re.match(r"(\S+)\s+connected\s+(\d+)x(\d+)\+(\d+)\+(\d+)", line)
        if m:
            name, w, h, x, y = m.groups()
            self.monitors.append((name, int(x), int(y), int(w), int(h)))
    return self.monitors


def get_windows(self) -> List[Tuple[str, str, str, str, str]]:
    """Return [(id, pid, title, monitor, type), …]"""
    self.windows.clear()
    mons = self.get_monitors()
    out = self.run_command("wmctrl -l -p -G")
    self_pid = getattr(self, "_self_pid", None)
    self_win_hex = getattr(self, "_self_win_hex", None)

    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 8:
            continue
        win_id, desktop, pid, x, y, w, h = parts[:7]
        title = " ".join(parts[8:])
        # --- skip our own window ---
        if self_pid and pid == self_pid:
            continue
        if self_win_hex and win_id.lower() == self_win_hex.lower():
            continue
        # ---------------------------
        x, y = int(x), int(y)
        monitor = "Unknown"
        for name, mx, my, mw, mh in mons:
            if mx <= x < mx + mw and my <= y < my + mh:
                monitor = name
                break
        win_type = classify_type(title)
        self.windows.append((win_id, pid, title, monitor, win_type))
    return self.windows


def _compute_self_ids(self) -> None:
    """
    Compute and cache this process PID and our top-level window id in wmctrl's hex format.
    Safe to call multiple times; cheap.
    """
    self._self_pid = str(os.getpid())
    self._self_win_hex = None

    # Only attempt winId() on X11
    platform = os.environ.get("QT_QPA_PLATFORM", "").lower()
    if not platform and os.environ.get("XDG_SESSION_TYPE") == "wayland":
        platform = "wayland"

    if platform.startswith("wayland"):
        print("[INFO] Running on Wayland: skipping X11 window id")
        return

    try:
        wid = int(self.winId() or 0)
        if wid:
            self._self_win_hex = f"0x{wid:08x}"
            print(f"[DEBUG] Computed window id: {self._self_win_hex}")
        else:
            print("[WARN] winId() returned 0 — window not realized yet?")
    except Exception as e:
        print(f"[ERROR] Could not get winId(): {e}")
