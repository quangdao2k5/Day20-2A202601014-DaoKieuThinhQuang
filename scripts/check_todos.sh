#!/usr/bin/env bash
set -euo pipefail
grep -R --exclude-dir='*.egg-info' "TODO(student)" -n src tests docs || true
