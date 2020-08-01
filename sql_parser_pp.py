
function_keywords = [
"select", "from", "where", "join", "group", "order", "by", "union",
"as", "with", "having", "case", "when", "then", "else", "end", "and", "or",
"is", "null", "in", "like", "between", "not", "cast", "inner",
"full", "except", "intersect", "pivot", "over", "distinct", "asc", "desc",
"cross", "apply", "exists", "on",
]

system_keywords = function_keywords + [
    "left", "right"
]

kword_ = lambda word: check_token(lambda t: t[0] == "identifier" and t[1].lower() == word.lower())
symbol_ = lambda s: check_token(lambda to: to[0] == "symbol" and to[1] == s)
token_type = lambda type: check_token(lambda t: t[0] == type)

def kword(word): return pp(kword_(word), lambda a, b: [flatten_list(a)[0][1].upper()])
def symbol(s): return pp(symbol_(s), lambda a, b: [flatten_list(a)[0][1]])
is_identifier = pp(check_token(lambda t: t[0] == "identifier" and t[1].lower() not in system_keywords), lambda a, b: [flatten_list(a)[0][1]])
is_function_name = pp(check_token(lambda t: t[0] == "identifier" and t[1].lower() not in function_keywords), lambda a, b: [flatten_list(a)[0][1]])
is_string = pp(token_type("string"), lambda a, b: [flatten_list(a)[0][1]])
is_number = pp(token_type("number"), lambda a, b: [flatten_list(a)[0][1]])
is_quoted = pp(token_type("quoted"), lambda a, b: [flatten_list(a)[0][1]])
is_bracketed = pp(token_type("bracketed"), lambda a, b: [flatten_list(a)[0][1]])

concat = lambda f: pp(f, lambda a, b: ["".join(flatten_list(b))])
space_join = lambda f: pp(f, lambda a, b: [" ".join(flatten_list(b))])
line_join = lambda f: pp(f, lambda a, b: ["\n".join(flatten_list(b))])
dline_join = lambda f: pp(f, lambda a, b: ["\n\n".join(flatten_list(b))])
make_upper = lambda f: pp(f, lambda a, b: ["".join(flatten_list(b)).upper()])

def indent(f):
    def fn(p):
        [s, p, a, b] = f(p)
        if s:
            lines = "".join(flatten_list(b)).splitlines()
            lines = ["    "+line if len(line) > 0 else line for line in lines]
            b = ["\n".join(lines)]
        return [s, p, a, b]
    return fn
