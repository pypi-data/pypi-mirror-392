import concurrent.futures
import itertools
import os
from collections import deque
from collections.abc import Collection, Iterable, Set, Sized
from typing import Callable, List

import numpy as np

_DEFAULT_N_WORKERS_ = os.cpu_count() or 4


def parallelize_iterable(iterable: Iterable, func: Callable, *args, preserve_order=True,
                         executor: concurrent.futures.Executor = None,
                         n_workers: int = _DEFAULT_N_WORKERS_, use_process: bool = False,
                         **kwargs):
    # check if exe is provided
    if executor is None:
        if use_process:
            my_executor = concurrent.futures.ProcessPoolExecutor(max_workers=n_workers)
        else:
            my_executor = concurrent.futures.ThreadPoolExecutor(max_workers=n_workers)
    else:
        my_executor = executor

    # submit tasks
    task_list = deque([my_executor.submit(func, item, *args, **kwargs) for item in iterable])

    # collect results
    # note to remove completed task from the list for memory efficiency
    for task in concurrent.futures.as_completed(task_list):
        if preserve_order:
            while len(task_list) > 0 and task_list[0].done():
                yield task_list.popleft().result()
        else:
            task_list.remove(task)
            yield task.result()

            # if is my exe, then shutdown
    if executor is None:
        my_executor.shutdown()


def apply_cache(l_key: List, d_cache: dict, func: Callable):
    l_result = [None] * len(l_key)
    l_miss_index = []
    l_miss_key = []

    for index, key in enumerate(l_key):
        if key in d_cache:
            l_result[index] = d_cache[key]
        else:
            l_miss_index.append(index)
            l_miss_key.append(key)

    l_miss_result = func(l_miss_key)
    # add to result and add to cache
    for index, key, result in zip(l_miss_index, l_miss_key, l_miss_result):
        l_result[index] = result
        d_cache[key] = result

    return l_result


def get_as_iterable(arr: List, indices: List[int]):
    for index in indices:
        yield arr[index]


def get_many(arr: List, indices: List[int]):
    return list(get_as_iterable(arr, indices))


def set_many(arr: List, indices: List[int], values: Iterable):
    for index, value in zip(indices, values):
        arr[index] = value


def unique(arr: List):
    seen = set()
    seen_add = seen.add
    return [x for x in arr if not (x in seen or seen_add(x))]


def shape_max(arr: List):
    """Get the maximum shape of the array"""
    if isinstance(arr, str) or not isinstance(arr, Sized):
        return []

    i_shape = map(shape_max, arr)
    i_shape = itertools.zip_longest(*i_shape, fillvalue=0)
    shape = [len(arr)] + list(map(max, i_shape))
    return shape


def pad(arr: List, shape=None, fill_value=0, dtype=None):
    """Pad the array to a specific shape"""
    if shape is None:
        shape = shape_max(arr)
    elif isinstance(shape, int):
        shape = [shape]

    if isinstance(arr, str) or not isinstance(arr, Collection):
        if len(shape) == 0:
            return arr
        return np.tile(np.asarray(arr, dtype=dtype), shape)
    elif isinstance(arr, Set):
        arr = list(arr)

    if len(shape) > 1:
        arr = [
            pad(child, shape=shape[1:], fill_value=fill_value)
            for child in arr
        ]
        arr = np.stack(arr, axis=0, dtype=dtype)

    if len(arr) < shape[0]:
        padding = np.tile(
            np.asarray(fill_value, dtype=dtype),
            [shape[0] - len(arr)] + list(shape[1:])
        )

        arr = np.concatenate([arr, padding], axis=0, dtype=dtype)

    return arr
