#!/usr/bin/env bash
set -euo pipefail

echo "Running reference solution..."
./solution.sh

echo "Running tests..."
python3 -m pytest -q tests

echo "All tests passed successfully."
