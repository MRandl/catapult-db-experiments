from typing import Any, Optional, Union

import diskannpy
import numpy as np

data = np.array([range(i, 16 + i) for i in range(100)], dtype=np.float32)
distance_metric = "l2"
index_directory = "./filtered"
complexity = 20
graph_degree = 10
num_threads = 4
vector_dtype = np.float32
tags: Union[str, np.ndarray[Any, np.dtype[np.uint32]]] = (
    ""  # only used for dynamic stuff -> not for us right now
)
filter_labels: Optional[list[list[str]]] = [["1", "2"]] * 50 + [["2"]] * 50
universal_label: str = ""
filter_complexity: int = 20
index_prefix: str = "ann"
alpha = 1.2

diskannpy.build_memory_index(
    data,
    distance_metric,
    index_directory,
    complexity,
    graph_degree,
    num_threads,
    vector_dtype=vector_dtype,
    tags=tags,
    filter_labels=filter_labels,
    universal_label=universal_label,
    filter_complexity=filter_complexity,
    index_prefix=index_prefix,
    alpha=alpha,
)
