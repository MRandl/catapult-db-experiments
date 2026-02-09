import csv
import os
import time

import diskannpy as dap
import numpy as np
from proximipy import LshLruCache

# Goal of this script: To demonstrate the proximity collapse effect in a dynamic DiskANN index.
# We query a bunch of vectors, cache the results, insert a bunch of new unseen vectors in the DB, and repeat a few dozen times.
# Eventually, the cache will be filled with stale information, leading to a decrease in recall.

# --- Configuration ---
DIM = 768
K = 5
TOLERANCE = 2.5
NUM_HASH = 10
BUCKET_CAP = 20
INDEX_DIR = "dynamic_diskann_index"
NUM_THREADS = os.cpu_count()

# File paths
VECTORS_PATH = "path/to/35m_vectors.npy"
QUERIES_PATH = "path/to/5m_queries.npy"

# --- Ratio Configuration ---
SEED_RATIO = 0.15  # Initial database size (e.g., 15% of total available DB vectors)
STEP_RATIO = 0.005  # How much of the vectors to insert at every query-cache-insert cycle (0.5% of the total unseen database vectors). Starting with a 15% full DB, we reach 100% in ~170 cycles.


def run_mutation_experiment():
    # 1. Initialization
    cache = LshLruCache(num_hash=NUM_HASH, dim=DIM, bucket_capacity=BUCKET_CAP)

    # Mmap datasets for memory efficiency
    all_queries = np.load(QUERIES_PATH, mmap_mode="r")
    all_vectors = np.load(VECTORS_PATH, mmap_mode="r")

    total_vectors = all_vectors.shape[0]
    total_queries = all_queries.shape[0]

    # Calculate absolute sizes based on the ratios
    initial_seed_size = int(total_vectors * SEED_RATIO)
    inserts_per_cycle = int(total_vectors * STEP_RATIO)
    queries_per_cycle = int(total_queries * STEP_RATIO)

    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)

    print(f"Dataset Stats: {total_vectors} vectors, {total_queries} queries")
    print(f"Building initial DiskANN index with {initial_seed_size} vectors...")

    dap.build_memory_index(
        all_vectors[:initial_seed_size],
        "l2",
        INDEX_DIR,
        complexity=100,
        graph_degree=64,
        num_threads=NUM_THREADS,
    )

    index = dap.DynamicMemoryIndex(INDEX_DIR)

    vector_ptr = initial_seed_size
    query_ptr = 0
    cycle = 0

    with open("proximity_dynamic_recall.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cycle", "query_id", "is_hit", "recall"])

        # Loop until all vectors have been inserted into the index
        while vector_ptr < total_vectors:
            cycle_start_time = time.time()

            # A. Process Query Batch
            # Ensure we don't go out of bounds if queries are exhausted before vectors
            q_end = min(query_ptr + queries_per_cycle, total_queries)
            batch = all_queries[query_ptr:q_end]

            # If we run out of new queries, we could loop back or stop;
            # here we just process whatever is left.
            num_queries_in_batch = len(batch)

            print(
                f"Cycle {cycle:03d} | DB Size: {vector_ptr} | Queries: {num_queries_in_batch}"
            )

            for i, q in enumerate(batch):
                q_list = q.tolist()
                cached_ids = cache.find(q_list)

                # Ground Truth Search
                true_response = index.search(q.reshape(1, -1), K, complexity=100)
                true_ids = true_response[0]
                true_set = set(true_ids[0])

                if cached_ids is not None:
                    intersection = true_set.intersection(set(cached_ids[0]))
                    recall = len(intersection) / K
                    is_hit = 1
                else:
                    cache.insert(q_list, true_ids.tolist(), TOLERANCE)
                    recall = 1.0
                    is_hit = 0

                writer.writerow([cycle, query_ptr + i, is_hit, recall])

            # Update query pointer
            query_ptr = q_end

            # B. Dynamic Mutation: Insert new vectors
            print(f"Cycle {cycle:03d} | Inserting {inserts_per_cycle} vectors...")
            end_ptr = min(vector_ptr + inserts_per_cycle, total_vectors)
            new_vectors = all_vectors[vector_ptr:end_ptr]

            for i in range(len(new_vectors)):
                index.insert(new_vectors[i], np.uint32(vector_ptr + i))

            vector_ptr = end_ptr
            elapsed = time.time() - cycle_start_time
            print(f"Cycle {cycle:03d} completed in {elapsed:.2f}s")

            cycle += 1

            # Safety break if queries are exhausted and you don't want to keep inserting
            if query_ptr >= total_queries:
                print("All queries processed. Ending experiment.")
                break

    print(f"Experiment concluded at Cycle {cycle}. Results logged.")


if __name__ == "__main__":
    run_mutation_experiment()
