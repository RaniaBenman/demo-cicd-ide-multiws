class SampleCommonClass():
    
    def method(self, a, b):
        return a + b

    @staticmethod
    def methodstat(a, b):
        return a + b

    @classmethod
    def methodcls(cls, a, b):
        return cls.methodstat(a, b)