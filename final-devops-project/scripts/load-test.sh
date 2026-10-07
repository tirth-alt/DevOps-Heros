#!/usr/bin/env bash
# Sends a mix of API traffic so dashboards, alerts and the HPA have something to show.
# Usage: ./scripts/load-test.sh [base-url] [seconds]
#   ./scripts/load-test.sh http://localhost:8000 120
#   HOST_HEADER=stockwise.local ./scripts/load-test.sh http://localhost:8088 120   (through the Ingress)
BASE="${1:-http://localhost:8000}"
DURATION="${2:-60}"
H=()
[ -n "${HOST_HEADER:-}" ] && H=(-H "Host: $HOST_HEADER")
END=$((SECONDS + DURATION))
echo "Sending traffic to $BASE for ${DURATION}s"
while [ $SECONDS -lt $END ]; do
  for _ in 1 2 3 4; do
    curl -s -o /dev/null "${H[@]}" "$BASE/api/products" &
    curl -s -o /dev/null "${H[@]}" "$BASE/api/stats" &
    curl -s -o /dev/null "${H[@]}" "$BASE/api/products?low_stock=true" &
  done
  curl -s -o /dev/null "${H[@]}" "$BASE/api/products/999999" &   # 404, a client error
  wait
done
echo "Done."
