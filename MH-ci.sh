#!/usr/bin/env bash

set -euo pipefail

export TZ=America/New_York
export PIPENV_VENV_IN_PROJECT=true

test -d .venv && rm -rf .venv

pip install pipenv
pipenv install --dev --deploy
npm ci

. .venv/bin/activate

cd tock
