# coding=utf-8
"""
author = jamon
"""


class Singleton(type):
    """Singleton Metaclass"""

    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None
        print("init")

    def __call__(self, *args, **kwargs):
        print("call:", self.instance, id(self.instance))
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance


class A(metaclass=Singleton):

    # __metaclass__ = Singleton
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = A()
        return cls._instance

    def __init__(self):
        self.name = {"age":10}


# A.get_instance().name = {"daa": 12}
A().name = {"daab": 12}

print(id(A()), id(A.get_instance()), id(A.get_instance().name), id(A().name), A().get_instance().name, A().name)