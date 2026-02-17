from typing import Any, Optional, Union

import diskannpy
import numpy as np

data = "path"  # path to npy or ndarray of float/uint8/int8
distance_metric = "l2"
index_directory = ""
complexity = 100
graph_degree = 64
num_threads = 4
vector_dtype = np.float32
tags: Union[str, np.ndarray[Any, np.dtype[np.uint32]]] = (
    ""  # only used for dynamic stuff -> not for us right now
)
filter_labels: Optional[list[list[str]]] = None
universal_label: str = ""
filter_complexity: int = 100
index_prefix: str = "ann"

diskannpy.build_memory_index(
    data,
    distance_metric,
    index_directory,
    complexity,
    graph_degree,
    num_threads,
    vector_dtype,
    tags,
    filter_labels,
    universal_label,
    filter_complexity,
    index_prefix,
)
