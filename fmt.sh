#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

git diff --staged --name-only | grep ".py" | poetry run black -  