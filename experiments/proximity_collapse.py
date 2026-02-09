import csv
import os
import time

import diskannpy as dap
import numpy as np
from proximipy import LshLruCache

# --- Configuration ---
DIM = 768
K = 5
TOLERANCE = 2.5
NUM_HASH = 10
BUCKET_CAP = 20
INDEX_DIR = "dynamic_diskann_index"
NUM_THREADS = os.cpu_count()

# File paths
VECTORS_PATH = "/mnt/nfs/home/randl/datasets/medcpt_pubmed_embeddings/embeds_all.npy"
QUERIES_PATH = "/mnt/nfs/home/randl/datasets/tripclick_embeds.npy"

# --- Ratio Configuration ---
SEED_RATIO = 0.15
STEP_RATIO = 0.005


def run_mutation_experiment():
    cache = LshLruCache(num_hash=NUM_HASH, dim=DIM, bucket_capacity=BUCKET_CAP)

    all_queries = np.load(QUERIES_PATH, mmap_mode="r")
    all_vectors = np.load(VECTORS_PATH, mmap_mode="r")

    total_vectors = all_vectors.shape[0]
    total_queries = all_queries.shape[0]

    initial_seed_size = int(total_vectors * SEED_RATIO)
    inserts_per_cycle = int(total_vectors * STEP_RATIO)
    queries_per_cycle = int(total_queries * STEP_RATIO)

    print(f"Dataset Stats: {total_vectors} vectors, {total_queries} queries")
    print(f"Initializing empty DynamicMemoryIndex with capacity for {total_vectors} vectors...")

    index = dap.DynamicMemoryIndex(
        distance_metric="l2",
        vector_dtype=np.float32,
        dimensions=DIM,
        max_vectors=total_vectors,
        complexity=100,
        graph_degree=64,
        num_threads=NUM_THREADS,
        search_threads=NUM_THREADS
    )

    print(f"Seeding index with {initial_seed_size} vectors...")
    seed_vectors = all_vectors[:initial_seed_size]
    seed_ids = np.arange(1, initial_seed_size + 1, dtype=np.uint32)
    index.batch_insert(seed_vectors, seed_ids, num_threads=NUM_THREADS)

    vector_ptr = initial_seed_size
    query_ptr = 0
    cycle = 0

    with open("proximity_dynamic_recall.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cycle", "query_id", "is_hit", "recall"])

        while vector_ptr < total_vectors:
            cycle_start_time = time.time()

            q_end = min(query_ptr + queries_per_cycle, total_queries)
            batch = all_queries[query_ptr:q_end]
            num_queries_in_batch = len(batch)

            print(f"Cycle {cycle:03d} | DB Size: {vector_ptr} | Batch Querying {num_queries_in_batch} items...")

            # Using batch_search for better efficiency
            # returns QueryResponseBatch(identifiers=neighbors, distances=distances)
            batch_results = index.batch_search(
                queries=batch, 
                k_neighbors=K, 
                complexity=100, 
                num_threads=NUM_THREADS
            )
            
            all_true_ids = batch_results.identifiers

            for i, q in enumerate(batch):
                q_list = q.tolist()
                cached_ids = cache.find(q_list)

                true_ids = all_true_ids[i]
                true_set = set(true_ids)

                if cached_ids is not None:
                    intersection = true_set.intersection(set(cached_ids))
                    recall = len(intersection) / K
                    is_hit = 1
                else:
                    cache.insert(q_list, true_ids.tolist(), TOLERANCE)
                    recall = 1.0
                    is_hit = 0

                writer.writerow([cycle, query_ptr + i, is_hit, recall])

            query_ptr = q_end

            print(f"Cycle {cycle:03d} | Inserting {inserts_per_cycle} vectors...")
            end_ptr = min(vector_ptr + inserts_per_cycle, total_vectors)
            
            new_vectors = all_vectors[vector_ptr:end_ptr]
            new_ids = np.arange(vector_ptr + 1, end_ptr + 1, dtype=np.uint32)
            
            index.batch_insert(new_vectors, new_ids, num_threads=NUM_THREADS)

            vector_ptr = end_ptr
            elapsed = time.time() - cycle_start_time
            print(f"Cycle {cycle:03d} completed in {elapsed:.2f}s")

            cycle += 1

            if query_ptr >= total_queries:
                print("All queries processed. Ending experiment.")
                break

    print(f"Experiment concluded at Cycle {cycle}. Results logged.")


if __name__ == "__main__":
    run_mutation_experiment()
