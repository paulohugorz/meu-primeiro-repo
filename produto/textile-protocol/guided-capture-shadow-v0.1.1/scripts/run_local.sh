#!/usr/bin/env bash
set -euo pipefail
python src/cli.py init-db
python src/cli.py serve
