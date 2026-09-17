import os
import sys
import subprocess
import json
import shutil
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(root_dir, ".env"), override=False)
    load_dotenv(os.path.join(root_dir, "backend", ".env"), override=False)

    print("=" * 75)
    print(">> Starting RetailFlow in Docker with Live AWS Bedrock Connection")
    print("=" * 75)

    profile = os.environ.get("AWS_PROFILE", "divyang")
    region = os.environ.get("AWS_REGION", "us-east-1")
    model = os.environ.get("BEDROCK_MODEL", "us.amazon.nova-lite-v1:0")

    print(f"Target AWS Profile: {profile}")
    print(f"Target AWS Region:  {region}")
    print(f"Target Model:       {model}")

    # Prepare environment for docker compose
    env = os.environ.copy()
    env["AWS_PROFILE"] = profile
    env["AWS_REGION"] = region
    env["AWS_DEFAULT_REGION"] = region
    env["BEDROCK_MODEL"] = model

    # If AWS CLI is present, attempt to export active session credentials
    aws_cmd = shutil.which("aws")
    if aws_cmd and profile:
        try:
            print(f"Attempting to resolve AWS credentials for profile '{profile}'...")
            res = subprocess.check_output(
                [aws_cmd, "configure", "export-credentials", "--profile", profile, "--region", region],
                timeout=8,
                stderr=subprocess.PIPE
            )
            creds = json.loads(res.decode("utf-8"))
            if "AccessKeyId" in creds:
                env["AWS_ACCESS_KEY_ID"] = creds["AccessKeyId"]
                env["AWS_SECRET_ACCESS_KEY"] = creds["SecretAccessKey"]
                env["AWS_SESSION_TOKEN"] = creds.get("SessionToken", "")
                print(">> [SUCCESS] Successfully exported active AWS session credentials to Docker environment!")
        except Exception as e:
            print(f"Note: Standard AWS credentials lookup will be used ({e}).")

    # Check docker command
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        print("[ERROR] Docker executable was not found on PATH. Please install and start Docker Desktop.")
        sys.exit(1)

    print("\nLaunching Docker Compose (building and starting containers)...")
    print("---------------------------------------------------------------------------")
    print(">> Frontend UI:       http://localhost:5173")
    print(">> Backend API:      http://localhost:8000/docs")
    print(">> MCP Server:       http://localhost:8001/health")
    print("---------------------------------------------------------------------------")
    print("Press Ctrl+C to stop all containers.\n")

    cmd = [docker_cmd, "compose", "up", "--build"]
    try:
        subprocess.run(cmd, cwd=root_dir, env=env)
    except KeyboardInterrupt:
        print("\nStopping RetailFlow Docker containers...")
        subprocess.run([docker_cmd, "compose", "down"], cwd=root_dir)
        print("Containers stopped.")

if __name__ == "__main__":
    main()
