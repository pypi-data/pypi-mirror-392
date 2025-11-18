"""Application launcher tools for opening and verifying applications."""

import os
import platform
import subprocess
import time
from typing import Any, Dict

from pydantic import Field


def _success_response(message: str, **kwargs) -> Dict[str, Any]:
    """Build a success response dictionary."""
    return {"status": "success", "message": message, **kwargs}


def _error_response(message: str) -> Dict[str, Any]:
    """Build an error response dictionary."""
    return {"status": "error", "message": message}


def _decode_error(result: subprocess.CompletedProcess) -> str:
    """Extract error message from subprocess result."""
    return result.stderr.decode().strip() if result.stderr else "Unknown error"


def _check_process_running(process_name: str, system: str) -> bool:
    """Check if a process is running on the current platform."""
    if system in ("Darwin", "Linux"):
        result = subprocess.run(
            ["pgrep", "-x", process_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.returncode == 0

    elif system == "Windows":
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
            capture_output=True,
            text=True,
        )
        return process_name.lower() in result.stdout.lower()

    return False


def open_application(
    app_name: str = Field(
        description="Name of the application to open (e.g., 'Messages', 'Calculator', 'notepad')"
    ),
) -> Dict[str, Any]:
    """Open an application using the appropriate platform-specific launcher."""
    try:
        system = platform.system()

        if system == "Darwin":
            result = subprocess.run(["open", "-a", app_name], capture_output=True)
            if result.returncode == 0:
                return _success_response(f"Launched {app_name}", app_name=app_name)
            return _error_response(
                f"Failed to launch {app_name}: {_decode_error(result)}"
            )

        elif system == "Windows":
            try:
                os.startfile(app_name)
                return _success_response(f"Launched {app_name}", app_name=app_name)
            except OSError:
                result = subprocess.run(
                    ["start", "", app_name], shell=True, capture_output=True
                )
                if result.returncode == 0:
                    return _success_response(f"Launched {app_name}", app_name=app_name)
                return _error_response(
                    f"Failed to launch {app_name}: {_decode_error(result)}"
                )

        elif system == "Linux":
            result = subprocess.run(["xdg-open", app_name], capture_output=True)
            if result.returncode == 0:
                return _success_response(f"Launched {app_name}", app_name=app_name)
            return _error_response(
                f"Failed to launch {app_name}: {_decode_error(result)}"
            )

        else:
            return _error_response(f"Unsupported operating system: {system}")

    except Exception as e:
        return _error_response(f"Failed to launch application: {str(e)}")


def verify_application(
    process_name: str = Field(
        description="Name of the process to verify (e.g., 'Messages', 'Calculator', 'notepad.exe')"
    ),
    timeout: float = Field(
        default=5.0,
        description="Maximum time in seconds to wait for process verification",
    ),
) -> Dict[str, Any]:
    """Verify that an application process is running."""
    try:
        system = platform.system()
        start_time = time.time()

        while time.time() - start_time < timeout:
            if _check_process_running(process_name, system):
                return _success_response(
                    f"Process {process_name} is running",
                    verified=True,
                    process_name=process_name,
                )
            time.sleep(0.2)

        return _success_response(
            f"Process {process_name} not found after {timeout}s",
            verified=False,
            process_name=process_name,
        )

    except Exception as e:
        return _error_response(f"Failed to verify process: {str(e)}")
