class DictDict(object):
    def __init__(self):
        self.d = []

    def __iter__(self):
        for e in self.d:
            yield e['key']

    def len(self):
        return len(self.d)

    def items(self):
        for e in self.d:
            yield e['key'],e['val']

    def keys(self):
        return self.__iter__()

    def Set(self,k_d,v):
        for e in self.d:
            if (set(k_d.items()) == set(e['key'].items())):
                break
        else:
            self.d.append({
                    'key': k_d,
                    'val': None,
                    })
            e = self.d[-1]
        e['val'] = v

    def HasKey(self,k_d):
        for e in self.d:
            if (set(k_d.items()) == set(e['key'].items())):
                return True
        else:
            return False

    def Get(self,k_d):
        for e in self.d:
            if (set(k_d.items()) == set(e['key'].items())):
                return e['val']
        else:
            raise RuntimeError,'Cant find key %s in this dict' % (k_d)


