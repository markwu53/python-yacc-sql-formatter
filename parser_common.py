
token_source = None

def check_token(good):
    def fn(p):
        if p == len(token_source):
            return [False, p, [], []]
        token = token_source[p]
        if not good(token):
            return [False, p, [], []]
        return [True, p+1, [token], []]
    return fn

