import copy

class TreeCounter(object):
    def __init__(self):
        self.t = {}

    def AddInstance(self,l):
        t = self.t
        for i in l:
            if (i not in t):
                t[i] = {}
            t = t[i]
        if ('_count' not in t):            
            t['_count'] = 0
        t['_count'] += 1

    def DumpCounts(self):
        self.counts = []
        self._DumpCounts(self.t,[])
        return self.counts

    def _DumpCounts(self,t,l):
        for k in sorted(t.keys()):
            l2 = copy.copy(l)            
            if (k == '_count'):
                l2.append(t['_count'])
                self.counts.append(l2)
            else:                
                l2.append(k)
                self._DumpCounts(t[k],l2)

        
        
