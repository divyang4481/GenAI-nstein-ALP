import subprocess
import sys
import os
import time
import shutil

def find_python_executable():
    """
    Dynamically finds the best Python executable without hardcoding any user or machine paths.
    Prioritizes:
    1. Currently executing Python interpreter (sys.executable)
    2. Active Virtualenv or Conda environment (CONDA_PREFIX / VIRTUAL_ENV)
    3. System PATH python / python3
    """
    # 1. Check if current interpreter is valid
    if sys.executable and os.path.isfile(sys.executable):
        return sys.executable

    # 2. Check active Conda prefix
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        conda_py = os.path.join(conda_prefix, "python.exe" if os.name == "nt" else "bin/python")
        if os.path.isfile(conda_py):
            return conda_py

    # 3. Check active virtualenv
    venv_prefix = os.environ.get("VIRTUAL_ENV")
    if venv_prefix:
        venv_py = os.path.join(venv_prefix, "Scripts/python.exe" if os.name == "nt" else "bin/python")
        if os.path.isfile(venv_py):
            return venv_py

    # 4. Fallback to system PATH
    system_py = shutil.which("python") or shutil.which("python3")
    return system_py or "python"

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    py_exec = find_python_executable()
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    print("=" * 75)
    print("🚀 Starting RetailFlow — Real-Time Marketplace Fulfilment Recovery Agent")
    print("=" * 75)
    print(f"Project Root:        {root_dir}")
    print(f"Python Runtime:      {py_exec}")
    print(f"Active Environment:  {os.environ.get('CONDA_DEFAULT_ENV', os.environ.get('VIRTUAL_ENV', 'System/Default'))}")
    print(f"Backend Directory:   {backend_dir}")
    print(f"Frontend Directory:  {frontend_dir}")
    print("\n[1/2] Launching FastAPI Backend on http://localhost:8000 ...")

    # Start FastAPI backend process
    backend_proc = subprocess.Popen(
        [py_exec, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=backend_dir
    )

    time.sleep(2)
    print("[2/2] Launching React + Vite Frontend on http://localhost:5173 ...")

    # Start React frontend process
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir
    )

    print("\n" + "=" * 75)
    print("✅ RetailFlow is up and running!")
    print("👉 Operations Dashboard: http://localhost:5173")
    print("👉 Swagger API Docs:     http://localhost:8000/docs")
    print("=" * 75)
    print("\nPress Ctrl+C to stop both servers.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping RetailFlow servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
