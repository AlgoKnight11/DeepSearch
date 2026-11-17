"""
DeepSearch: Biological rPPG Deepfake Recognition
Entrypoint Launcher Script
Starts the FastAPI server and launches the Forensic Command Center in the browser.
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time

# Auto-detect optimal Python environment with full MediaPipe & CV2 support
PREFERRED_PYTHON = r"C:\Users\bhavy\AppData\Local\Python\pythoncore-3.14-64\python.exe"

def ensure_optimal_environment():
    """If running in an incomplete Python interpreter, hand off to pythoncore-3.14-64."""
    if os.path.exists(PREFERRED_PYTHON) and sys.executable.lower() != PREFERRED_PYTHON.lower():
        try:
            import mediapipe
        except ImportError:
            # Current python lacks mediapipe, relaunch with preferred python
            print(f"[DeepSearch] Relaunching with optimal Python environment ({PREFERRED_PYTHON})...")
            cmd = [PREFERRED_PYTHON] + sys.argv
            subprocess.run(cmd)
            sys.exit(0)

def open_browser():
    time.sleep(1.5)
    print("\n[DeepSearch] Opening Forensic Dashboard at http://127.0.0.1:8000 ...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    ensure_optimal_environment()

    import uvicorn

    print("=" * 68)
    print("  DEEPSEARCH: BIOLOGICAL rPPG DEEPFAKE RECOGNITION SYSTEM")
    print("  System Architecture: HTML5 / CSS3 / JavaScript + FastAPI")
    print(f"  Runtime Python: {sys.executable}")
    print("=" * 68)

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start FastAPI Application
    uvicorn.run("backend.server:app", host="127.0.0.1", port=8000, reload=False)
