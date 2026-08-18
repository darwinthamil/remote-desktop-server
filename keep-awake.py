"""
keep-awake.py
-------------
Keeps the machine from going idle (screensaver / sleep / auto-lock) by nudging
the mouse pointer a single pixel and back at a fixed interval.

Usage:
    python keep-awake.py            # default: jiggle every 60 seconds
    python keep-awake.py 30         # jiggle every 30 seconds
    python keep-awake.py 120        # jiggle every 2 minutes

Stop it with Ctrl+C.

Note: this only prevents the *idle* timer from firing. It cannot unlock an
already-locked screen, and if a Group Policy enforces a lock timeout it may
lock anyway.
"""

import sys
import time
from pynput.mouse import Controller

# Interval in seconds between jiggles (first CLI arg, default 60).
try:
    INTERVAL = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
except ValueError:
    print(f"Invalid interval '{sys.argv[1]}'. Using 60 seconds.")
    INTERVAL = 60.0

mouse = Controller()


def jiggle():
    x, y = mouse.position
    mouse.position = (x + 5, y + 5)   # nudge right 1px
    time.sleep(1)
    mouse.position = (x, y)       # move back
    return x, y


def main():
    print(f"Keep-awake running. Jiggling every {INTERVAL:g}s. Press Ctrl+C to stop.")
    count = 0
    try:
        while True:
            time.sleep(INTERVAL)
            x, y = jiggle()
            count += 1
            print(f"  [{count}] jiggle at ({x}, {y})", flush=True)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
