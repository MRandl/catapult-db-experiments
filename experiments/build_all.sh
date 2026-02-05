#!/bin/bash

# assumes rust + python 3.11 are available on path

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$BASE_DIR"

if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade setuptools wheel build maturin
else
    source venv/bin/activate
fi

# building catapultdb
cd "$BASE_DIR/catapult-db/"
cd bindings
maturin develop -r

# building DiskANN
cd "$BASE_DIR/DiskANN"
git switch cpp_main
python3.11 -m build
pip install dist/diskannpy-0.7.1-cp311-cp311-linux_x86_64.whl

# building proximity
cd "$BASE_DIR/proximity"
cd bindings
maturin develop -r


cd "$BASE_DIR"
