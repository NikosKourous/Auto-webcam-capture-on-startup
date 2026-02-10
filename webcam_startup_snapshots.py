#!/usr/bin/env python3

"""
Webcam Startup Snapshots (fswebcam-only, ultra-light)

Folder structure: ~/Pictures/Webcam-Pics-Startup/YEAR/MonthName/Day

  1) 3 shots (rapid)
  2) wait 3s
  3) 3 shots (rapid)
  4) wait 5s
  5) 4 shots (rapid)
  6) run silently ~10 minutes (low-power sleep)
  7) 3 shots (1s apart)
  8) exit

Filenames: HOUR-MINUTE-SECOND-DD-MM-XX.jpg

"""

import os
import time
import signal
import shutil
import subprocess
from datetime import datetime

try:
    os.nice(10)
except Exception:
    pass

HOME = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME, "Pictures", "Webcam-Pics-Startup")

_running = True
def _handle_signal(signum, frame):
    global _running
    _running = False
for _sig in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(_sig, _handle_signal)
    except Exception:
        pass

def dir_for_timestamp(ts: datetime) -> str:
    """~/Pictures/Webcam-Pics-Startup/YEAR/MonthName/Day"""
    year = ts.strftime("%Y")       
    month = ts.strftime("%B")      
    day = ts.strftime("%d")        
    path = os.path.join(BASE_DIR, year, month, day)
    os.makedirs(path, exist_ok=True)
    return path

def filename_for_timestamp(ts: datetime, index: int) -> str:
    """HOUR-MINUTE-SECOND-DD-MM-XX.jpg"""
    base = ts.strftime("%H-%M-%S-%d-%m")
    return f"{base}-{index:02d}.jpg"

def fswebcam_exists() -> bool:
    return shutil.which("fswebcam") is not None

def take_one_shot(index: int) -> int:
    """Capture one frame via fswebcam; returns next index."""
    if not fswebcam_exists():
        return index
    ts = datetime.now()
    save_dir = dir_for_timestamp(ts)
    out_name = filename_for_timestamp(ts, index)
    out_path = os.path.join(save_dir, out_name)

    with open(os.devnull, "wb") as devnull:
        subprocess.run(
            ["fswebcam", "-q", "--no-banner", "-S", "2", "--jpeg", "85", out_path],
            stdout=devnull,
            stderr=devnull,
            check=False,
        )
    return index + 1

def take_burst(count: int, min_gap: float, start_index: int) -> int:
    """Take `count` photos, sleeping `min_gap` seconds between each."""
    idx = start_index
    for _ in range(count):
        if not _running:
            break
        idx = take_one_shot(idx)
        if min_gap > 0:
            end_t = time.monotonic() + min_gap
            while _running and time.monotonic() < end_t:
                time.sleep(0.05)
    return idx

def sleep_interruptible(total_seconds: float):
    """Low-resource sleep, responsive to SIGTERM."""
    end_t = time.monotonic() + total_seconds
    while _running and time.monotonic() < end_t:
        time.sleep(0.25)

def main():
    os.makedirs(BASE_DIR, exist_ok=True)

    idx = 0
    idx = take_burst(3, 0.10, idx)
    sleep_interruptible(3.0)
    idx = take_burst(3, 0.10, idx)
    sleep_interruptible(5.0)
    idx = take_burst(4, 0.10, idx)

    sleep_interruptible(10 * 60)

    idx = take_burst(3, 1.0, idx)

if __name__ == "__main__":
    main()
