import collections.abc
from typing import Any, Dict, List, Union

DictKeyTypes = Union[str, int, float, bool, tuple, frozenset, bytes, None]


def update(default: Dict, modified: Dict):
    for k, v in modified.items():
        if isinstance(v, collections.abc.Mapping):
            default[k] = update(default.get(k, {}), v)
        else:
            default[k] = v
    return default


def get(obj: Dict, key: str, sep='.', default=None, suppress_error=True):
    l_key = key.split(sep)
    for k in l_key:
        try:
            obj = obj[k]
        except Exception:
            try:
                obj = obj[int(k)]
            except Exception:
                if suppress_error:
                    return default

                raise KeyError(f'{k} is not in {obj}')

    return obj


def set(obj: Dict, key: str, value, sep='.'):
    l_key = key.split(sep)
    for k in l_key[:-1]:
        try:
            obj = obj[k]
        except Exception:
            try:
                obj = obj[int(k)]
            except Exception:
                obj[k] = dict()
                obj = obj[k]

    obj[l_key[-1]] = value


def delete(obj: Dict, key: str, sep='.', suppress_error=False):
    l_key = key.split(sep)
    pre_obj = obj
    for k in l_key:
        if not isinstance(obj, collections.abc.MutableMapping) or k not in obj:
            if suppress_error:
                return None

            raise ValueError(f'{k} is not in {obj}')

        pre_obj = obj
        obj = obj[k]

    value = pre_obj[l_key[-1]]
    del pre_obj[l_key[-1]]
    return value


def delete_all(obj: Dict, values: Union[List[Any], Any] = None, recursive=True):
    if not isinstance(obj, collections.abc.MutableMapping):
        return obj

    if not isinstance(values, (list, tuple)):
        values = [values]

    if recursive:
        obj = {
            k: delete_all(v, values) for k, v in obj.items() if v not in values
        }
    else:
        obj = {
            k: v for k, v in obj.items() if v not in values
        }

    return obj
