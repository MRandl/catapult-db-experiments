import diskannpy
import numpy as np

index_directory: str = ""
index_prefix = "ann"
num_threads: int = 4
initial_search_complexity = 100
distance_metric = "l2"
vector_dtype = np.float32
dimensions = 768
enable_filters = True

diskannpy.StaticMemoryIndex(
    index_directory,
    num_threads,
    initial_search_complexity,
    index_prefix,
    distance_metric,
    vector_dtype,
    dimensions,
    enable_filters,
)
