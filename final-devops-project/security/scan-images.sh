#!/usr/bin/env bash
# Runs the same image gate as the CI pipeline, locally:
# fail on fixable HIGH or CRITICAL vulnerabilities in either image.
# Usage: ./security/scan-images.sh   (from final-devops-project/)
set -euo pipefail
status=0
for component in backend frontend; do
  echo "== Building stockwise-$component:scan"
  docker build -q -t "stockwise-$component:scan" "application/$component" >/dev/null
  echo "== Scanning stockwise-$component:scan"
  if ! docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image \
      --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 "stockwise-$component:scan"; then
    status=1
  fi
done
[ "$status" -eq 0 ] && echo "Both images passed the gate." || echo "Gate FAILED: fix the vulnerabilities above."
exit "$status"
