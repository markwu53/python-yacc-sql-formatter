
def S(*fs):
    def fn(p):
        p0, o, bs = p, [], []
        for f in fs:
            [s, p, a, b] = f(p)
            if not s:
                return [False, p0, [], []]
            o.append(a)
            bs.append(b)
        return [True, p, o, bs]
    return fn

def P(*fs):
    def fn(p):
        for f in fs:
            [s, p, a, b] = f(p)
            if s:
                return [s, p, a, b]
        return [False, p, [], []]
    return fn

Z = lambda p: [True, p, [], []]
O = lambda f: P(f, Z)
#M = lambda f: O(M1(f))
#M = lambda f: O(lambda p: M1(f)(p))
#M = lambda f: O((lambda f: M1(f))(f))
def M(f):
    def fn(p):
        o, bs = [], []
        [s, p, a, b] = f(p)
        while s:
            o.append(a)
            bs.append(b)
            [s, p, a, b] = f(p)
        return [True, p, o, bs]
    return fn

M1 = lambda f: S(f, M(f))

def pp(f, pf):
    def fn(p):
        [s, p, a, b] = f(p)
        if s:
            b = pf(a, b)
        return [s, p, a, b]
    return fn

def flatten_list(input):
    if not isinstance(input, list):
        return [input]
    return [e for item in input for e in flatten_list(item)]

