"""
Direct evdev touch input for the Waveshare 3.5" resistive screen (ADS7846).

SDL2 in offscreen mode is render-only and never reads from SDL_MOUSEDEV /
SDL_MOUSEDRV=TSLIB.  This thread opens the kernel input device directly,
applies the TSLIB calibration matrix from /etc/pointercal, and posts
pygame MOUSEBUTTONDOWN / MOUSEBUTTONUP events so the rest of the app sees
touch as normal mouse clicks with no SDL input support required.
"""
import os
import struct
import sys
import threading
import pygame


# ── evdev constants ────────────────────────────────────────────────────────
EV_KEY    = 0x01
EV_ABS    = 0x03
ABS_X     = 0x00
ABS_Y     = 0x01
BTN_TOUCH = 0x14a  # 330

# input_event: timeval (2 × long) + u16 type + u16 code + s32 value
# 32-bit ARM: long = 4 B → 'iiHHi' = 16 bytes
# 64-bit ARM: long = 8 B → 'qqHHi' = 24 bytes
_LONG     = 'i' if sys.maxsize <= 2**32 else 'q'
_EVT_FMT  = f'{_LONG}{_LONG}HHi'
_EVT_SIZE = struct.calcsize(_EVT_FMT)


def _find_touch_device(preferred: str) -> str:
    """Return a usable touch device path.

    Tries *preferred* first, then scans /proc/bus/input/devices for the
    ADS7846 handler, then falls back to /dev/input/event0..event9.
    """
    if os.path.exists(preferred):
        return preferred

    # Parse /proc/bus/input/devices for the ADS7846 touch controller
    try:
        with open('/proc/bus/input/devices') as fh:
            block, name = [], ''
            for line in fh:
                line = line.strip()
                if line.startswith('N:'):
                    name = line
                elif line.startswith('H:') and 'ADS7846' in name:
                    # Handlers line e.g. "H: Handlers=mouse0 event2"
                    for token in line.split():
                        if token.startswith('event'):
                            path = f'/dev/input/{token}'
                            if os.path.exists(path):
                                print(f"Touch: found ADS7846 at {path} "
                                      f"(symlink {preferred} missing)")
                                return path
                elif line == '':
                    name = ''
    except Exception:
        pass

    # Last-resort: try event0..event9 in order
    for n in range(10):
        path = f'/dev/input/event{n}'
        if os.path.exists(path):
            print(f"Touch: falling back to {path}")
            return path

    return preferred  # will fail in run() with a clear error


class TouchInputThread(threading.Thread):
    """Reads ADS7846 evdev events and injects them into pygame's event queue."""

    def __init__(self, device_path: str, screen_w: int, screen_h: int,
                 pointercal: str = '/etc/pointercal'):
        super().__init__(daemon=True, name='touch-input')
        self.device_path = _find_touch_device(device_path)
        self.screen_w    = screen_w
        self.screen_h    = screen_h
        self._raw_x      = 0
        self._raw_y      = 0
        self._touching   = False
        self._running    = False
        self._cal        = self._load_calibration(pointercal)
        if self._cal:
            print(f"Touch: calibration loaded from {pointercal}")
        else:
            print(f"Touch: {pointercal} not found — using linear raw mapping")

    # ── calibration ────────────────────────────────────────────────────────

    @staticmethod
    def _load_calibration(path: str):
        """Return (a, b, c, d, e, f, s) from /etc/pointercal, or None."""
        try:
            with open(path) as fh:
                vals = list(map(int, fh.read().split()))
            if len(vals) >= 7:
                return vals[:7]
        except Exception:
            pass
        return None

    def _map(self, raw_x: int, raw_y: int):
        """Convert raw ADS7846 counts to screen (x, y), clamped."""
        if self._cal:
            a, b, c, d, e, f, s = self._cal
            sx = (a * raw_x + b * raw_y + c) // s
            sy = (d * raw_x + e * raw_y + f) // s
        else:
            # ADS7846 full-scale ≈ 0–4095
            sx = int(raw_x / 4095 * self.screen_w)
            sy = int(raw_y / 4095 * self.screen_h)
        sx = max(0, min(self.screen_w  - 1, sx))
        sy = max(0, min(self.screen_h - 1, sy))
        return sx, sy

    # ── thread body ────────────────────────────────────────────────────────

    def run(self):
        self._running = True
        try:
            with open(self.device_path, 'rb') as fd:
                while self._running:
                    data = fd.read(_EVT_SIZE)
                    if len(data) < _EVT_SIZE:
                        break
                    _, _, etype, code, value = struct.unpack(_EVT_FMT, data)
                    self._handle(etype, code, value)
        except Exception as exc:
            print(f"Touch input thread error: {exc}")

    def _handle(self, etype: int, code: int, value: int):
        if etype == EV_ABS:
            if code == ABS_X:
                self._raw_x = value
            elif code == ABS_Y:
                self._raw_y = value
        elif etype == EV_KEY and code == BTN_TOUCH:
            pos = self._map(self._raw_x, self._raw_y)
            if value == 1 and not self._touching:
                self._touching = True
                pygame.event.post(pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN, pos=pos, button=1
                ))
            elif value == 0 and self._touching:
                self._touching = False
                pygame.event.post(pygame.event.Event(
                    pygame.MOUSEBUTTONUP, pos=pos, button=1
                ))

    def stop(self):
        self._running = False
