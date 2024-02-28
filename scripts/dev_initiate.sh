#!/bin/bash

echo "Running this script will delete the python venv"
read -r -p "Are you sure? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        :
        ;;
    *)
        exit 1
        ;;
esac

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -z $(which uv) ]
then
    echo "Installing uv (https://astral.sh/uv/install.sh), blazingly fast drop in pip replacement"
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

rm -rf "$ROOT_DIR/.venv"
uv venv -p 3.12 "$ROOT_DIR/.venv"
source "$ROOT_DIR/.venv/bin/activate"

uv pip install --upgrade pip
uv pip install --editable "$ROOT_DIR[dev]"
