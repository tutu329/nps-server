"""The singleton metaclass for ensuring only one instance of a class."""
import abc

# def Singleton(cls, *args, **kwargs):
#     _instance = None
#
#     def wrapper(*args, **kwargs):
#         if not _instance:
#             _instance = cls(*args, **kwargs)
#         return _instance
#     return wrapper

class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            # print("cls is:", cls)
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class AbstractSingleton(abc.ABC, metaclass=Singleton):
    """
    Abstract singleton class for ensuring only one instance of a class.
    """

    pass