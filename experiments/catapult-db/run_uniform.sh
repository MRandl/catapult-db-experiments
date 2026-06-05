#!/usr/bin/env bash
# Uniform (unbiased) workload runs for catapult / vanilla(DiskANN) / LSH-APG.
#
# Reproducibility notes
# ---------------------
# - The catapult-db submodule must include the LSH-APG loader fix
#   ("Populate the LSH-APG index at load time", commit 1af04f7). Earlier pins
#   (<= ca1f7d1) never populated the LSH index, so --mode lshapg silently ran
#   as vanilla (identical recall/traversal). This submodule is pinned to the fix.
# - LSH-APG parameters are the binary defaults: num_hash=8, w=1.0,
#   stored_vectors_dim = full payload dim (768). The graph medoid is kept as an
#   additional entry point (same beam search as vanilla, plus the LSH-selected
#   entry points). With these settings, uniform lshapg recall@16 = 0.337.
# - Recall is computed in uniform_plots.ipynb from the *_neighbors.json outputs
#   against the vanilla beam-64 ground truth (uniform_vanilla_ground_truth.json).
set -euo pipefail

# --- throughput / traversal stats ---
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/uniform_catapult.json --mode catapult
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/uniform_vanilla.json --mode vanilla
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/uniform_lshapg.json --mode lshapg

# --- per-query neighbors (used to compute recall) ---
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/uniform_catapult_neighbors.json --mode catapult --output-neighbors
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/uniform_vanilla_neighbors.json --mode vanilla --output-neighbors
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 4,8,12,16 --beam-width 1,2,4,8,16 --seeds 42,43,44 --output ./results/uniform_lshapg_neighbors.json --mode lshapg --output-neighbors

# --- ground truth (vanilla, beam 64); filename must match uniform_plots.ipynb ---
cargo run --release -- -q uniform_query.npy --graph ann --payload ann.data -t 62 --beam-width 64 --seeds 42 --output ./results/uniform_vanilla_ground_truth.json --mode vanilla --output-neighbors
