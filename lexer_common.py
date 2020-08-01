
char_source = None

def get_char(p):
    if p == len(char_source):
        return [False, p, [], []]
    return [True, p+1, [char_source[p]], []]

def check_char(good):
    def fn(p):
        if p == len(char_source):
            return [False, p, [], []]
        c = char_source[p]
        if not good(c):
            return [False, p, [], []]
        return [True, p+1, [c], []]
    return fn

def lex_negate(f):
    def fn(p):
        [s, q, a, b] = f(p)
        if not s:
            return get_char(p)
        return [False, p, [], []]
    return fn

is_char = lambda ch: check_char(lambda c: c == ch)
is_alpha = check_char(lambda c: c.isalpha())
is_digit = check_char(lambda c: c.isdigit())
is_space = check_char(lambda c: c.isspace())
is_eol = P(S(is_char("\n"), is_char("\r")), S(is_char("\r"), is_char("\n")), is_char("\n"), is_char("\r"))
