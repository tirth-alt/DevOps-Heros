#!/usr/bin/env bash
# Loads sample products through the public API.
# Usage: ./scripts/seed.sh [base-url]   (default http://localhost:8000)
set -euo pipefail
BASE="${1:-http://localhost:8000}"

add() {
  curl -sf -X POST "$BASE/api/products" -H "Content-Type: application/json" ${HOST_HEADER:+-H "Host: $HOST_HEADER"} -d "$1" >/dev/null \
    && echo "added: $(echo "$1" | sed -E 's/.*"name": *"([^"]+)".*/\1/')" \
    || echo "skipped (exists or error): $1"
}

add '{"name": "Mechanical Keyboard", "sku": "KEY-101", "category": "Peripherals", "quantity": 42, "price": 3499, "reorder_level": 10}'
add '{"name": "Wireless Mouse", "sku": "MOU-220", "category": "Peripherals", "quantity": 8, "price": 899, "reorder_level": 10}'
add '{"name": "27-inch Monitor", "sku": "MON-270", "category": "Displays", "quantity": 15, "price": 15999, "reorder_level": 5}'
add '{"name": "USB-C Hub", "sku": "HUB-007", "category": "Accessories", "quantity": 3, "price": 1999, "reorder_level": 6}'
add '{"name": "Laptop Stand", "sku": "STD-010", "category": "Accessories", "quantity": 27, "price": 1299, "reorder_level": 8}'
add '{"name": "Noise Cancelling Headphones", "sku": "AUD-500", "category": "Audio", "quantity": 12, "price": 8999, "reorder_level": 4}'
add '{"name": "HDMI Cable 2m", "sku": "CAB-002", "category": "Accessories", "quantity": 0, "price": 349, "reorder_level": 20}'
add '{"name": "Webcam 1080p", "sku": "CAM-108", "category": "Peripherals", "quantity": 19, "price": 2499, "reorder_level": 5}'
