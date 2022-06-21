class SampleCommonClass():
    def __init__(self):
        

    def method1(self, a, b):
        return a + b

    @staticmethod
    def methodstat(a, b):
        return a + b

    @classmethod
    def methodcls(cls, a, b):
        return cls.methodstat(a, b)