Below is a **clean, comprehensive, production-ready Markdown report** your AI Agent can use to implement **cross-platform application-open and verification handlers**.

---

# 📘 Cross-Platform Application Launch & Verification

### **Technical Specification for Agent Tooling**

**Version:** 1.0
**Audience:** AI Agent Developers / Automation Tooling
**Platforms:** macOS, Windows, Linux

---

## 🧭 Overview

This document specifies how to implement robust, cross-platform Python handlers that:

1. **Open (launch) any application** dynamically by name or path
2. **Verify that the application actually launched**, via:

   * system-level return codes
   * process existence detection
   * optional window detection (macOS)

These handlers support macOS, Windows, and Linux.

---

# 1. Opening Applications (Cross-Platform)

## 1.1 Platform Behavior Summary

| Platform    | API                       | Mechanism                                            |
| ----------- | ------------------------- | ---------------------------------------------------- |
| **macOS**   | `open -a <AppName>`       | Launch app bundle by name via LaunchServices         |
| **Windows** | `os.startfile` or `start` | Launch `.exe` or registered application              |
| **Linux**   | `xdg-open`                | Delegate to desktop environment application launcher |

---

## 1.2 Python Implementation

### **macOS**

```python
import subprocess

def open_app_mac(app_name: str) -> bool:
    """Launch a macOS application using LaunchServices."""
    p = subprocess.run(["open", "-a", app_name])
    return p.returncode == 0
```

---

### **Windows**

```python
import subprocess, os

def open_app_windows(app_name: str) -> bool:
    """Launch a Windows application or executable."""
    try:
        os.startfile(app_name)
        return True
    except:
        p = subprocess.run(["start", "", app_name], shell=True)
        return p.returncode == 0
```

---

### **Linux**

```python
import subprocess

def open_app_linux(app_name: str) -> bool:
    """Launch a Linux application via xdg-open."""
    p = subprocess.run(["xdg-open", app_name])
    return p.returncode == 0
```

---

### **Unified Cross-Platform Handler**

```python
import platform

def open_application(app_name: str) -> bool:
    system = platform.system()

    if system == "Darwin":
        return open_app_mac(app_name)
    elif system == "Windows":
        return open_app_windows(app_name)
    elif system == "Linux":
        return open_app_linux(app_name)
    else:
        raise OSError(f"Unsupported OS: {system}")
```

---

# 2. Verifying Application Launch

Verification can be one or more of the following:

---

## ✔️ 2.1 Return Code Verification (Basic)

Confirms the OS accepted the launch request, but not that the app is running.

Already implemented in each open handler.

---

## ✔️ 2.2 Process-Level Verification (Reliable)

Confirms the process exists after launch.
This is the recommended default across all platforms.

### macOS/Linux: `pgrep`

```python
import subprocess

def process_running(process_name: str) -> bool:
    result = subprocess.run(
        ["pgrep", "-x", process_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0
```

---

### Windows: `tasklist`

```python
import subprocess

def process_running_windows(process_name: str) -> bool:
    result = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
        capture_output=True, text=True
    )
    return process_name.lower() in result.stdout.lower()
```

---

### Unified Process Checker

```python
def is_process_running(name: str) -> bool:
    system = platform.system()

    if system in ("Darwin", "Linux"):
        return process_running(name)
    elif system == "Windows":
        return process_running_windows(name)
    else:
        return False
```

---

## ✔️ 2.3 Optional macOS Window-Level Verification (UI Confirm)

Used only when visual confirmation is required.

```python
import subprocess

def window_exists_mac(app_name: str) -> bool:
    script = f'''
    tell application "System Events"
        return exists window 1 of process "{app_name}"
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script],
                            capture_output=True, text=True)
    return "true" in result.stdout.lower()
```

---

## ✔️ Combined “Open + Verify” Handler

This is the recommended function for your agent.

```python
import time

def open_and_verify(app_name: str,
                    process_name: str = None,
                    timeout: float = 5.0) -> bool:
    """Opens an application and verifies if it's running."""
    if not open_application(app_name):
        return False

    # Allow system launch delay
    time.sleep(1.0)

    process_name = process_name or app_name

    start = time.time()
    while time.time() - start < timeout:
        if is_process_running(process_name):
            return True
        time.sleep(0.2)

    return False
```

---

# 3. Dynamic Application Discovery (Optional for Agents)

Your agent can search installed apps dynamically.

### macOS

```python
mdfind 'kMDItemKind == "Application"'
```

### Windows

Search Start Menu `.lnk` shortcuts.

### Linux

Parse `/usr/share/applications/*.desktop`.

---

# 4. Recommended Agent Tool API

Your AI agent should expose something like:

```json
{
  "tool": "open_application",
  "args": {
    "name": "Messages",
    "verify": true
  }
}
```

Expected output:

```json
{
  "success": true,
  "verified": true,
  "processName": "Messages"
}
```

---

# 5. Edge Cases & Safety Notes

* Some apps launch multiple processes → agent should support fallback patterns
* App names do not always match process names → allow tool user to specify both
* Windows `startfile` may fail silently for non-registered apps
* Linux desktop environments vary — `xdg-open` is a best-effort launcher
* macOS window detection requires Accessibility permissions

---

# ✔️ Conclusion

This document provides a **complete cross-platform specification** for:

* Opening applications
* Verifying launches (process-level + optional UI verification)
* Combining handlers into an agent-friendly API
* Adding dynamic discovery

Your AI agent now has everything needed to implement reliable tooling for automation across macOS, Windows, and Linux.

---

If you want, I can also produce:

📁 **Ready-to-run Python module**
📦 **Package structure for agent tools**
🧩 **OpenAPI/JSON schema for tool definition**

Just tell me!
