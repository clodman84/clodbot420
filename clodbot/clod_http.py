import aiohttp

"""wonky way of reusing one aiohttp.ClientSession everywhere"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonSession(aiohttp.ClientSession, metaclass=Singleton):
    pass
