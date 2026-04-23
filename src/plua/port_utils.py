"""
Port-cleanup helpers used by the CLI before binding the FastAPI server.

Both branches are best-effort: we try to free a TCP port that an earlier PLua
process may have left bound. Failure is logged and ignored — the caller will
still attempt to bind and surface a real error if the port is unavailable.
"""

from __future__ import annotations

import logging
import platform
import subprocess
import time

logger = logging.getLogger(__name__)


def _cleanup_port_windows(port: int) -> bool:
    """Windows-specific port cleanup using netstat + taskkill."""
    max_retries = 2

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            if result.returncode == 0 and result.stdout:
                killed_any = False
                for line in result.stdout.split("\n"):
                    if "LISTENING" in line and f":{port} " in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            if pid.isdigit() and pid != "0":
                                logger.info(f"Killing process {pid} using port {port}")
                                kill_result = subprocess.run(
                                    ["taskkill", "/F", "/PID", pid],
                                    capture_output=True,
                                    check=False,
                                )
                                if kill_result.returncode == 0:
                                    killed_any = True

                if killed_any:
                    time.sleep(0.1)
                    check_result = subprocess.run(
                        ["netstat", "-ano", "-p", "TCP"],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        check=False,
                    )
                    if check_result.returncode == 0:
                        still_used = any(
                            "LISTENING" in line and f":{port} " in line
                            for line in check_result.stdout.split("\n")
                        )
                        if not still_used:
                            logger.info(f"Port {port} successfully cleaned up")
                            return True
                else:
                    return True

        except Exception as e:
            logger.debug(f"Port cleanup attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            time.sleep(0.2)

    return False


def _cleanup_port_unix(port: int) -> bool:
    """Unix/Linux/macOS port cleanup using lsof + kill -9."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.stdout.strip():
            for pid in result.stdout.strip().split("\n"):
                if pid:
                    subprocess.run(["kill", "-9", pid], check=False)
        return True
    except Exception:
        return False


def free_port(port: int) -> bool:
    """
    Best-effort: kill whatever process is currently bound to `port`.

    Returns True on success or when nothing was holding the port; False if a
    cleanup attempt was made but the port still appears in use. Exceptions are
    swallowed and logged — never raised.
    """
    try:
        if platform.system() == "Windows":
            success = _cleanup_port_windows(port)
        else:
            success = _cleanup_port_unix(port)
        if not success:
            logger.warning(f"Could not fully clean up port {port}, but continuing...")
        return success
    except Exception as e:
        logger.warning(f"Port cleanup failed: {e}")
        return False
