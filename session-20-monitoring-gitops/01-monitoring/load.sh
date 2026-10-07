#!/usr/bin/env bash
# Sends a mix of traffic to the demo app so the dashboards have something to show.
# Usage: ./load.sh [normal|errors|slow|cpu] [seconds]
MODE="${1:-normal}"
SECONDS_TO_RUN="${2:-60}"
BASE="http://localhost:8000"
END=$((SECONDS + SECONDS_TO_RUN))

echo "Sending '$MODE' traffic to $BASE for ${SECONDS_TO_RUN}s. Press Ctrl+C to stop."
while [ $SECONDS -lt $END ]; do
  case "$MODE" in
    normal) curl -s "$BASE/" >/dev/null; curl -s "$BASE/health" >/dev/null ;;
    errors) curl -s "$BASE/error" >/dev/null; curl -s "$BASE/" >/dev/null ;;
    slow)   curl -s "$BASE/slow" >/dev/null & curl -s "$BASE/slow" >/dev/null & wait ;;
    cpu)    curl -s "$BASE/cpu" >/dev/null & curl -s "$BASE/cpu" >/dev/null & wait ;;
    *) echo "Unknown mode: $MODE"; exit 1 ;;
  esac
  sleep 0.2
done
echo "Done."
