from collections.abc import Iterable

import numpy as np


class LabelCoder:
    def __init__(self, na_values=None) -> None:
        if isinstance(na_values, str) or not isinstance(na_values, Iterable):
            na_values = [na_values]
        self.na_values = na_values
        self._code_dict = {
            na_value: 0
            for na_value in na_values
        }

    def _to_1d_(array):
        # convert to array and reshape to 1-d array
        np_arr = np.asarray(array)
        original_shape = np.shape(np_arr)

        np_arr = np.ravel(np_arr)
        return np_arr, original_shape

    def encode(self, array, return_value=True, expand=True):
        np_arr, original_shape = LabelCoder._to_1d_(array)

        if expand:
            start_code = max(self._code_dict.values()) + 1
            updating_code = set(np_arr) - set(self._code_dict)
            updating_code = {value: start_code + index for index, value in enumerate(updating_code)}
            self._code_dict.update(updating_code)

        if not return_value:
            return

        np_encoded = np.asarray([self._code_dict.get(value, 0) for value in np_arr])
        np_encoded = np.reshape(np_encoded, original_shape)
        return np_encoded

    def decode(self, array):
        np_arr, original_shape = LabelCoder._to_1d_(array)
        # since Python 3.7, the order of inserting to dict is preserved.
        np_codes = np.asarray(list(self._code_dict.keys()))
        # keep only the last NA values in the code list
        np_codes = np_codes[max(0, len(self.na_values) - 1):]

        # decode and reshape
        np_decoded = np_codes[np_arr]
        np_decoded = np.reshape(np_decoded, original_shape)
        return np_decoded
