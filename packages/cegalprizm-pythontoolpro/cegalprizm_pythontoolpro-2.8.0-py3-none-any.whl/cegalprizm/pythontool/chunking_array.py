# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import functools
import typing
if typing.TYPE_CHECKING:
    from cegalprizm.pythontool.points import _PointsProvider

class _ChunkingArray:
    
    def __init__(self, provider: "_PointsProvider", chunk_size: int = 10):
        """An indexable data-structure which fetches chunks of data from
        `provider` transparently

        provider: datasource with `get_range` and `get_len` methods
        cache_width: size of chunks to fetch
        """
        self.provider = provider
        self._chunk_size = chunk_size

    # since people will usually iterate forwards, it's not really necessary to
    # cache much at all in this lru
    @functools.lru_cache(maxsize=128)
    def _get_range(self, start_incl, end_excl):
        if start_incl > len(self):
            return []
        if end_excl >= len(self):
            end_excl = len(self)
        return self.provider.get_range(start_incl, end_excl)

    def __getitem__(self, key):
        # always get ranges in multiples of window size so they can be cached
        if isinstance(key, int):
            if key >= len(self):
                raise IndexError("Index out-of-range [{key}]")

            d, m = divmod(key, self._chunk_size)
            return self._get_range(
                d * self._chunk_size, (d * self._chunk_size) + self._chunk_size
            )[m]
        if isinstance(key, slice):
            if (
                key.start >= len(self)
                or key.stop > len(self)
                or key.start < 0
                or key.stop <= 0
            ):
                raise IndexError("Slice out-of-range [" + key + "]")
            # assemble the chunks implied by the slice linearly
            d = key.start // self._chunk_size
            assembled = []
            idx = d * self._chunk_size
            while idx < key.stop:
                d = idx // self._chunk_size
                chunk = self._get_range(
                    d * self._chunk_size, (d * self._chunk_size) + self._chunk_size
                )
                assembled = assembled + chunk
                idx = idx + self._chunk_size

            # adjust the slice so it is offset to the chunk-assembly
            new_start = key.start % self._chunk_size
            new_stop = new_start + (key.stop - key.start)
            # return the applied slice
            return assembled[slice(new_start, new_stop, key.step)]
        raise ValueError("Must supply an int or slice")

    def __len__(self):
        return self.provider.get_len()