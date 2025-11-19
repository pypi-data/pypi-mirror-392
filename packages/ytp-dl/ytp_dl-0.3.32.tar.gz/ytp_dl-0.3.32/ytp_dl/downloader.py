#!/usr/bin/env python3
"""
downloader.py — VPS download-only helpers for yt-dlp (no transcoding here).

Objective (Option B):
- Keep Mullvad tunnel UP during all active jobs; do NOT rotate/disconnect per job.
- Rotate Mullvad relay ONLY when idle (handled by a systemd timer outside this file).

Improvements:
- Reliable final-path detection using yt-dlp:
    --no-progress --print after_move:filepath --print filepath
- Concurrency-safe job tracking to avoid mid-flight route flips.

Env:
- YTPDL_VENV               (default: /opt/yt-dlp-mullvad/venv)
- YTPDL_MULLVAD_LOCATION   (default: "us")
- YTPDL_USER_AGENT         (UA override)
- YTPDL_MAX_PARALLEL       (optional local limiter; API has its own semaphore)
"""

from __future__ import annotations
import os
import shlex
import shutil
import subprocess
import time
from typing import Optional, List
from threading import Lock, BoundedSemaphore

# =========================
# Config / constants
# =========================
VENV_PATH = os.environ.get("YTPDL_VENV", "/opt/yt-dlp-mullvad/venv")
YTDLP_BIN = os.path.join(VENV_PATH, "bin", "yt-dlp")
MULLVAD_LOCATION = os.environ.get("YTPDL_MULLVAD_LOCATION", "us")
MODERN_UA = os.environ.get(
    "YTPDL_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
MAX_PARALLEL = int(os.environ.get("YTPDL_MAX_PARALLEL", "4"))

# =========================
# Concurrency state (process-wide)
# =========================
_state_lock = Lock()
_active_jobs = 0
_slots = BoundedSemaphore(MAX_PARALLEL)

# =========================
# Shell helpers
# =========================
def _run_argv(argv: List[str], check: bool = True) -> str:
    """Run a command and return stdout; raise if check=True and rc!=0."""
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(shlex.quote(a) for a in argv)}\n{p.stdout}")
    return p.stdout or ""

# =========================
# Environment / yt-dlp / Mullvad
# =========================
def validate_environment() -> None:
    if not os.path.isdir(VENV_PATH):
        raise RuntimeError(
            "Virtualenv missing. Create and install yt-dlp:\n"
            f"  python3 -m venv {VENV_PATH}\n"
            f"  source {VENV_PATH}/bin/activate\n"
            "  pip install -U yt-dlp"
        )
    if not os.path.exists(YTDLP_BIN):
        raise RuntimeError(f"yt-dlp not found at {YTDLP_BIN}. Install inside the venv.")

def _mullvad_present() -> bool:
    return shutil.which("mullvad") is not None

def mullvad_logged_in() -> bool:
    if not _mullvad_present():
        return False
    res = subprocess.run(["mullvad", "account", "get"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return "not logged in" not in (res.stdout or "").lower()

def manual_login(mullvad_account: str) -> None:
    if not _mullvad_present():
        raise RuntimeError("Mullvad CLI not installed on this host.")
    if not mullvad_account:
        raise RuntimeError("Missing Mullvad account number.")
    res = subprocess.run(["mullvad", "account", "get"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if "not logged in" not in (res.stdout or "").lower():
        print("Already logged into Mullvad.")
        return
    _run_argv(["mullvad", "account", "login", mullvad_account])
    print("Mullvad login complete (no VPN connection started).")

def require_mullvad_login() -> None:
    if _mullvad_present() and not mullvad_logged_in():
        raise RuntimeError(
            "Mullvad is not logged in on this server.\n"
            "Run once via SSH:  mullvad account login <ACCOUNT>"
        )

def mullvad_is_connected() -> bool:
    if not _mullvad_present():
        return True
    res = subprocess.run(["mullvad", "status"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return "Connected" in (res.stdout or "")

def mullvad_connect_if_needed(location: Optional[str] = None) -> None:
    """
    Ensure the VPN is connected. DO NOT disconnect first; no rotation here.
    Rotation is handled externally when idle.
    """
    if not _mullvad_present():
        return
    if mullvad_is_connected():
        return
    loc = (location or MULLVAD_LOCATION).strip()
    if loc:
        _run_argv(["mullvad", "relay", "set", "location", loc], check=False)
    _run_argv(["mullvad", "connect"], check=False)

def mullvad_wait_connected(timeout: int = 10) -> bool:
    if not _mullvad_present():
        return True
    for _ in range(timeout):
        res = subprocess.run(["mullvad", "status"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if "Connected" in (res.stdout or ""):
            return True
        time.sleep(1)
    return False

# ---------- Job lifecycle (no per-job disconnect/rotate) ----------
def _begin_job() -> None:
    """Increment active job count and ensure Mullvad is connected (no flip)."""
    global _active_jobs
    with _state_lock:
        _active_jobs += 1
    mullvad_connect_if_needed(MULLVAD_LOCATION)
    if not mullvad_wait_connected():
        with _state_lock:
            _active_jobs = max(0, _active_jobs - 1)
        raise RuntimeError("Could not establish Mullvad VPN connection.")

def _end_job() -> None:
    """Decrement active job count; DO NOT disconnect when last job ends."""
    global _active_jobs
    with _state_lock:
        _active_jobs = max(0, _active_jobs - 1)

# =========================
# yt-dlp helpers
# =========================
def _extract_printed_filepath(stdout: str) -> Optional[str]:
    """
    Find the last printed path from yt-dlp:
      --print after_move:filepath
      --print filepath
    Prefer the last line that looks like a path and exists.
    """
    if not stdout:
        return None
    candidate = None
    for line in (stdout or "").splitlines():
        s = (line or "").strip()
        if not s:
            continue
        # Heuristic: path-like
        if os.path.sep in s or s.startswith("/") or ":" in s:
            candidate = s
    if candidate and os.path.exists(candidate):
        return candidate
    return None

def _common_flags_list() -> List[str]:
    return [
        "--user-agent", MODERN_UA,
        "--no-playlist",
        "--no-call-home",
        "--restrict-filenames",
        "--no-color",
        "--no-check-certificates",
        "--no-part",
        "--no-cache-dir",
        "--concurrent-fragments", "2",
        "--retries", "3",
        "--fragment-retries", "3",
        "--socket-timeout", "15",
        "--no-mtime",
    ]

def _try_fmt(url: str, out_tpl: str, fmt: str, sort: Optional[str], merge_to_mp4: bool) -> Optional[str]:
    argv = [YTDLP_BIN]
    if fmt:
        argv += ["-f", fmt]
    if sort:
        argv += ["-S", sort]
    argv += _common_flags_list()
    if merge_to_mp4:
        argv += ["--merge-output-format", "mp4"]
    argv += [
        "--no-progress",
        "--print", "after_move:filepath",
        "--print", "filepath",
        "--output", out_tpl,
        url,
    ]
    out = _run_argv(argv, check=False)
    return _extract_printed_filepath(out)

# =========================
# Public API
# =========================
def download_video(
    url: str,
    resolution: int | None = 1080,
    extension: Optional[str] = None,
    out_dir: str = "/root",
) -> str:
    """
    Download media using yt-dlp with no transcoding.

    Args:
        url: Source URL.
        resolution: Preferred cap (e.g., 1080). None means best.
        extension: Optional forced extension (e.g., "mp3" for audio-only).
        out_dir: Destination directory.

    Returns:
        Absolute path to the downloaded file.
    """
    if not url:
        raise RuntimeError("Missing URL.")
    os.makedirs(out_dir, exist_ok=True)

    validate_environment()
    require_mullvad_login()

    # Optional local limiter so CLI usage can't overload; API also limits.
    _slots.acquire()
    try:
        _begin_job()
        try:
            out_tpl = os.path.join(out_dir, "%(title).80s-%(id)s.%(ext)s")

            # ---------- Audio-only fast path ----------
            if extension and extension.lower() == "mp3":
                argv = [
                    YTDLP_BIN, "-x", "--audio-format", "mp3",
                    *(_common_flags_list()),
                    "--no-progress",
                    "--print", "after_move:filepath",
                    "--print", "filepath",
                    "--output", out_tpl, url
                ]
                out = _run_argv(argv, check=True)
                path = _extract_printed_filepath(out)
                if not path or not os.path.exists(path):
                    raise RuntimeError("Audio download finished but file not found.")
                return os.path.abspath(path)

            # ---------- Video ----------
            cap = int(resolution or 4320)

            # A) Prefer H.264/AVC up to cap (Apple-friendly), try to merge to MP4
            fmt_avc_upto = f"bv*[vcodec~=avc1][height<={cap}]+ba/b[vcodec~=avc1][height<={cap}]"
            sort_avc_upto = "codec:avc1,res,fps,br,filesize"
            path = _try_fmt(url, out_tpl, fmt_avc_upto, sort_avc_upto, merge_to_mp4=True)
            if path:
                return os.path.abspath(path)

            # B) Fallback to best<=cap in any codec/container (no forced MP4)
            fmt_best_upto = f"bv*[height<={cap}]+ba/b[height<={cap}]"
            sort_best_upto = "res,fps,br,filesize"
            path = _try_fmt(url, out_tpl, fmt_best_upto, sort_best_upto, merge_to_mp4=False)
            if not path or not os.path.exists(path):
                raise RuntimeError("Video download finished but file not found.")
            return os.path.abspath(path)

        finally:
            _end_job()
    finally:
        try:
            _slots.release()
        except ValueError:
            pass
