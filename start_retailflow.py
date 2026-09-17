import subprocess
import sys
import os
import time
import shutil
import asyncio
from dotenv import load_dotenv

# Ensure UTF-8 output on all operating systems and Windows console pages
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def find_python_executable():
    """
    Dynamically finds the best Python executable without hardcoding any user or machine paths.
    Prioritizes:
    1. Currently executing Python interpreter (sys.executable)
    2. Active Virtualenv or Conda environment (CONDA_PREFIX / VIRTUAL_ENV)
    3. System PATH python / python3
    """
    if sys.executable and os.path.isfile(sys.executable):
        return sys.executable

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        conda_py = os.path.join(conda_prefix, "python.exe" if os.name == "nt" else "bin/python")
        if os.path.isfile(conda_py):
            return conda_py

    venv_prefix = os.environ.get("VIRTUAL_ENV")
    if venv_prefix:
        venv_py = os.path.join(venv_prefix, "Scripts/python.exe" if os.name == "nt" else "bin/python")
        if os.path.isfile(venv_py):
            return venv_py

    system_py = shutil.which("python") or shutil.which("python3")
    return system_py or "python"

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    py_exec = find_python_executable()
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    print("=" * 75)
    print(">> Starting RetailFlow -- Real-Time Marketplace Fulfilment Recovery Agent")
    print("=" * 75)
    print(f"Project Root:        {root_dir}")
    print(f"Python Runtime:      {py_exec}")
    print(f"Active Environment:  {os.environ.get('CONDA_DEFAULT_ENV', os.environ.get('VIRTUAL_ENV', 'System/Default'))}")
    
    load_dotenv(os.path.join(backend_dir, ".env"), override=False)

    provider = os.environ.get("LLM_PROVIDER", "bedrock")
    model = os.environ.get("BEDROCK_MODEL", "us.amazon.nova-lite-v1:0")
    region = os.environ.get("AWS_REGION", "us-east-1")
    print(f"Selected provider:   {provider.upper()}")
    print(f"Selected model:      {model}")
    print(f"AWS Region:          {region}")

    if provider == "bedrock":
        sys.path.insert(0, backend_dir)
        try:
            from app.agents.llm_provider import llm_provider
            status = asyncio.run(llm_provider.preflight_health_check())
        except (ImportError, ModuleNotFoundError) as exc:
            print(f"Readiness:           NOT READY ({exc})")
            print("Install backend requirements, including boto3, before launching.")
            raise SystemExit(1) from exc
        
        if status["ready"]:
            print("Readiness:           READY (AWS Bedrock)")
        else:
            print("Readiness:           DEMO FALLBACK (Simulated High-Fidelity Mode)")
            print(f"Bedrock notice:      {status['last_error']}")
            print("Notice:              Running in offline demo fallback mode. For live Bedrock, set up AWS credentials.")
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
    print("[SUCCESS] RetailFlow is up and running!")
    print(">> Operations Dashboard: http://localhost:5173")
    print(">> Swagger API Docs:     http://localhost:8000/docs")
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
