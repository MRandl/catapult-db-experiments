#!/bin/bash

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$BASE_DIR"
rm -rf venv

cd "$BASE_DIR/catapult-db/"
rm -rf target/

cd "$BASE_DIR/DiskANN"
rm -rf build/

cd "$BASE_DIR/proximity/"
rm -rf target/

cd "$BASE_DIR"
