import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from singleton import Singleton

# @Singleton
# class Config():
#     def __init__(self):
#         self.start_from_console = False

class Config(metaclass=Singleton):
    def __init__(self):
        self.start_from_console = False