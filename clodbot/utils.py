from ast import main
from collections import OrderedDict
from functools import update_wrapper, wraps
from textwrap import fill
import asyncio
import time


class Cache:
    """A cache decorator for functions. The function itself turns into an object of this class and gets a .remove()
    method which can be used to remove specific items from the cache. Returns an awaitable for asynchronous functions.

    Params:
        maxsize - Sets the maximum cache size
        ttl     - None by default, if pass in, each cached item gets set a fixed Time To Live
    Usage:
        @cache
        def test():
            ...

        @cache(maxsize=128, ttl=4):
        def test():
            ...

        test(34)
        test.remove(34) #removes 34 from the cache
    """

    def __init__(self, func=None, maxsize=128, ttl=None):
        self._cache = OrderedDict()
        self._func = func
        self._maxsize = maxsize
        self._ttl = ttl
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        if not self._func:
            return self.__class__(args[0], self._maxsize, self._ttl)

        cache = self._cache
        key = self._generate_hash_key(*args, **kwargs)
        if key in cache:
            if self._ttl:
                result, expiryDate = cache[key]
                if time.time() > expiryDate:
                    cache.pop(key)
                else:
                    cache.move_to_end(key)
                    return result
            else:
                cache.move_to_end(key)
                return cache[key]

        if asyncio.iscoroutinefunction(self._func):

            @wraps(self._func)
            async def tmp():
                return await self._func(*args, **kwargs)

            result = tmp()
        else:
            result = self._func(*args, **kwargs)

        cache[key] = result if not self._ttl else (result, time.time() + self._ttl)
        if len(cache) > self._maxsize:
            cache.popitem(last=False)
        return result

    @staticmethod
    def _generate_hash_key(*args, **kwargs):
        key = hash(args) + hash(frozenset(sorted(kwargs.items())))
        return key

    def remove(self, *args, **kwargs):
        cache = self._cache
        key = self._generate_hash_key(*args, **kwargs)
        if key in cache:
            return self._cache.pop(key)
        raise KeyError(f"{args, kwargs} not in cache for {self.__name__}")


class SimpleTimer:
    """
    with SimpleTimer("Test Timer") as timer:
        ...

    print(timer)
    > Test Timer completed in xyz seconds
    """

    def __init__(self, process_name=None):
        self.start = None
        self.total = None
        self.name = process_name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.total = time.perf_counter() - self.start

    def __str__(self):
        return (
            f"{self.name + ' ' if self.name else ''}completed in {self.total} seconds"
        )


def divideIterable(iterable, n):
    """Divides a given iterable into chunks of max size n, returns a list of chunks"""
    return [iterable[i * n : (i + 1) * n] for i in range((len(iterable) + n - 1) // n)]


def dictionaryFormatter(dictionary: dict, indent: int = 1):
    for key, value in dictionary.items():
        yield f"{'    '*(indent-1)}{str(key)}:"
        if isinstance(value, dict):
            yield from dictionaryFormatter(value, indent + 1)
        else:
            yield fill(
                str(value),
                width=75,
                initial_indent="    " * indent,
                subsequent_indent="    " * indent,
            )
