#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

echo "Secure AI Agent for IT Operations"
echo "Checking Docker runtime..."

if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running."
    exit 1
fi

if [ ! -f compose.yaml ]; then
    echo "ERROR: compose.yaml not found."
    exit 1
fi

if ! docker compose config --quiet; then
    echo "ERROR: Invalid Docker Compose configuration."
    exit 1
fi

existing=$(docker ps -q --filter volume=hermes-itops-data)

if [ -n "$existing" ]; then
    echo "ERROR: Another container is using hermes-itops-data."
    echo "Running containers:"
    docker ps --filter volume=hermes-itops-data \
        --format "table {{.Names}}\t{{.Status}}"
    echo "Stop the existing container before starting another."
    exit 1
fi

echo "Starting the hardened Hermes container..."

prompt="${1:-Use only the approved itops MCP tools to assess INC-1001. Report its category, priority and human-review requirement. Do not modify systems.}"

docker compose run --rm -T \
    --name itops-single-run \
    itops \
    chat -q "$prompt"
