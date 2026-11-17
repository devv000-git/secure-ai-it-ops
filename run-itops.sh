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

# Monitor the shutdown of the nested Hermes gateway supervisor.
# This workaround is specific to the tested s6-based Hermes image.
watch_shutdown() {
    local state gateway_state
    local attempt

    while kill -0 "$compose_pid" 2>/dev/null; do
        state=$(docker exec -u 0 itops-single-run \
            /package/admin/s6/command/s6-svstat \
            /run/s6-rc/servicedirs/profile-gateways \
            2>/dev/null || true)

        if [[ "$state" == *"want down"* ]]; then
            echo "Detected Hermes shutdown. Stopping nested gateway..."

            if ! docker exec -u 0 itops-single-run \
                /package/admin/s6/command/s6-svc -d \
                /run/hermes-service/gateway-default; then
                echo "WARNING: Gateway stop request failed." >&2
                return 1
            fi

            # Confirm the gateway is down before stopping its supervisor.
            for attempt in {1..15}; do
                gateway_state=$(docker exec -u 0 itops-single-run \
                    /package/admin/s6/command/s6-svstat \
                    /run/hermes-service/gateway-default \
                    2>/dev/null || true)

                if [[ "$gateway_state" == down* ]]; then
                    break
                fi
                sleep 1
            done

            if [[ "$gateway_state" != down* ]]; then
                echo "WARNING: Gateway did not report a stopped state." >&2
                return 1
            fi

            if ! docker exec -u 0 itops-single-run \
                /package/admin/s6/command/s6-svscanctl -t \
                /run/hermes-service; then
                echo "WARNING: Nested supervisor shutdown failed." >&2
                return 1
            fi

            echo "Nested gateway shutdown requested."
            return 0
        fi

        sleep 2
    done
}

docker compose run --rm -T \
    --name itops-single-run \
    itops \
    chat -q "$prompt" &

compose_pid=$!

watch_shutdown &
monitor_pid=$!

result=0
wait "$compose_pid" || result=$?

kill "$monitor_pid" 2>/dev/null || true
wait "$monitor_pid" 2>/dev/null || true

if [ "$result" -ne 0 ]; then
    echo "WARNING: Hermes launcher exited with status $result." >&2
fi

exit "$result"
