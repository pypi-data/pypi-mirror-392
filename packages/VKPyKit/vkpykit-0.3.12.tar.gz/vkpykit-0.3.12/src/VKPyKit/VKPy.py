from abc import ABC, abstractmethod

class VKPy:

    def __init__(self):
        pass

    RANDOM_STATE = 42
    NUMBER_OF_DASHES = 100
    
    @classmethod
    def get_info(cls):
        print(f"{cls.RANDOM_STATE}")
        print(f"{cls.NUMBER_OF_DASHES}")