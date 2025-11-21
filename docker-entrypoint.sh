#!/bin/bash
set -e

# Start XMPP server in the background
# Redirect both stdout and stderr to a log file to reduce noise (harmless XML parsing errors from connection attempts)
echo "Starting XMPP server for SPADE..."
uv run spade run >/tmp/xmpp-server.log 2>&1 &
XMPP_PID=$!

# Wait for XMPP server to start (check if process is still running)
echo "Waiting for XMPP server to start..."
sleep 3

# Check if XMPP server is still running
if ! kill -0 $XMPP_PID 2>/dev/null; then
    echo "Error: XMPP server failed to start"
    exit 1
fi

echo "XMPP server started (PID: $XMPP_PID)"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down XMPP server..."
    kill $XMPP_PID 2>/dev/null || true
    wait $XMPP_PID 2>/dev/null || true
}

# Trap signals to cleanup
trap cleanup SIGTERM SIGINT

# Run the main application with provided arguments or defaults
if [ $# -eq 0 ]; then
    # Default command if no arguments provided
    uv run python ./src/run.py \
        --algorithm all \
        --service_time 30 \
        --places_file data/places.json \
        --travel_times_file data/travel_times.json \
        --params params_example.json \
        --plot
else
    # Run with provided arguments
    uv run python ./src/run.py "$@"
fi

# Cleanup on exit
cleanup

