#!/usr/bin/env bash
set -e

echo "==================================================="
echo "Launching RetailFlow with Docker and AWS Profile"
echo "==================================================="

python3 start_docker.py || python start_docker.py
