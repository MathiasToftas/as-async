#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
source "$ROOT_DIR/.venv/bin/activate"

rm -rf "$ROOT_DIR/dist"
python -m build "$ROOT_DIR"
python -m twine upload --repository pypi "$ROOT_DIR/dist/*"
