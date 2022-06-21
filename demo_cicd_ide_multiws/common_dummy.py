class SampleCommonClass():
    
    def add(self, a, b):#i
        return a + b

    @staticmethod
    def addstat(a, b):
        return a + b

    @classmethod
    def addcls(cls, a, b):
        return cls.addstat(a, b)