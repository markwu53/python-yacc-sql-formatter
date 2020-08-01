
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
#M = lambda f: O(S(f, lambda p: M(f)(p)))
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
#M1 = lambda f: S(f, M(f))
def M1(f):
    def fn(p):
        [s, p, a, b] = S(f, M(f))(p)
        if s:
            a = [a[0]] + a[1]
            b = [b[0]] + b[1]
        return [s, p, a, b]
    return fn

def pp(f, pf):
    def fn(p):
        p0 = p
        [s, p, a, b] = f(p)
        if s:
            b = pf(a, b)
        return [s, p, a, b]
    return fn

def flatten_list(input):
    if not isinstance(input, list):
        return [input]
    return [e for item in input for e in flatten_list(item)]


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

p_lexer_yacc_identifier = lambda a, b: ("identifier", "".join(flatten_list(a)))
p_lexer_yacc_space = lambda a, b: ("space", "".join(flatten_list(a)))
p_lexer_yacc_string = lambda a, b: ("string", "".join(flatten_list(a)))
p_lexer_yacc_line_comment = lambda a, b: ("line_comment", "".join(flatten_list(a)))
p_lexer_yacc_block_comment = lambda a, b: ("block_comment", "".join(flatten_list(a)))
p_lexer_symbol = lambda a, b: ("symbol", "".join(flatten_list(a)))
p_lexer = lambda a, b: [e for e in flatten_list(b) if e[0] not in ("space", "line_comment", "block_comment")]

def one_token(p): return P(S(lexer_yacc_identifier), S(lexer_yacc_space), S(lexer_yacc_string), S(lexer_yacc_line_comment), S(lexer_yacc_block_comment), S(lexer_symbol))(p)
def lexer(p): return pp(P(S(M(one_token))), p_lexer)(p)
def lexer_identifier(p): return P(S(identifier_first_char, M(identifier_next_char)))(p)
def identifier_first_char(p): return P(S(is_char('_')), S(is_alpha))(p)
def identifier_next_char(p): return P(S(identifier_first_char), S(is_digit))(p)
def lexer_space(p): return P(S(M1(is_space)))(p)
def lexer_block_comment(p): return P(S(is_char('/'), is_char('*'), M(S(lex_negate(S(is_char('*'), is_char('/'))))), is_char('*'), is_char('/')))(p)
def lexer_symbol(p): return pp(P(S(get_char)), p_lexer_symbol)(p)
def lexer_yacc_identifier(p): return pp(P(S(lexer_identifier)), p_lexer_yacc_identifier)(p)
def lexer_yacc_space(p): return pp(P(S(lexer_space)), p_lexer_yacc_space)(p)
def lexer_yacc_string(p): return pp(P(S(yacc_string_1), S(yacc_string_2)), p_lexer_yacc_string)(p)
def yacc_string_1(p): return P(S(is_char('"'), M(S(lex_negate(is_char('"')))), is_char('"')))(p)
def yacc_string_2(p): return P(S(is_char("'"), M(S(lex_negate(is_char("'")))), is_char("'")))(p)
def lexer_yacc_line_comment(p): return pp(P(S(is_char('#'), M1(S(lex_negate(is_eol))), is_eol)), p_lexer_yacc_line_comment)(p)
def lexer_yacc_block_comment(p): return pp(P(S(lexer_block_comment)), p_lexer_yacc_block_comment)(p)

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

kword = lambda word: check_token(lambda t: t[0] == "identifier" and t[1] == word)
symbol = lambda s: check_token(lambda to: to[0] == "symbol" and to[1] == s)
token_type = lambda type: check_token(lambda t: t[0] == type)
identifier = token_type("identifier")

def p_identifier(a, b): return [flatten_list(a)[0][1]]
def p_parser(a, b): return flatten_list(b)
def p_rdef(a, b):
    if len(b[3]) == 0:
        body = flatten_list(b[2])[0]
    else:
        body = "pp({}, {})".format(flatten_list(b[2])[0], flatten_list(b[3])[0])
    result = ["def {}(p): return {}(p)".format(flatten_list(b[0])[0], body)]
    return result
def p_process(a, b): return flatten_list(b[2])
def p_def_body(a, b): return ["P({})".format(", ".join(flatten_list(b)))]
def p_branch(a, b): return ["S({})".format(", ".join(flatten_list(b)))]
def p_qobject(a, b):
    if len(b[1]) == 0:
        return flatten_list(b[0])
    q = flatten_list(b[1])[0]
    if q == "?": return ["O({})".format(flatten_list(b[0])[0])]
    if q == "*": return ["M({})".format(flatten_list(b[0])[0])]
    if q == "+": return ["M1({})".format(flatten_list(b[0])[0])]
    return [""]
def p_quantifier(a, b): return [flatten_list(a)[0][1]]
def p_mobject(a, b):
    if len(b[1]) == 0:
        return flatten_list(b[0])
    return ["{}({})".format(flatten_list(b[1])[0], flatten_list(b[0])[0])]
def p_modifier(a, b): return [flatten_list(a)[1][1]]
def p_eobject(a, b):
    if len(b[1]) == 0:
        return flatten_list(b[0])
    e = flatten_list(b[1])[0]
    if e == "delay":
        return ["lambda p: {}(p)".format(b[0][0])]
    return flatten_list(b[0])
def p_extension(a, b): return flatten_list(b)
def p_group_object(a, b): return ["S({})".format(", ".join(flatten_list(b[1])))]
def p_identifier(a, b): return [flatten_list(a)[0][1]]
def p_keyword(a, b): return ["kword('{}')".format(flatten_list(b)[0])]
def p_symbol(a, b):
    s = flatten_list(b[0])[0]
    if file_type == "lex":
        result = "is_char('{}')".format(s) if s != "'" else 'is_char("{}")'.format(s)
    elif file_type == "yacc":
        result = "symbol('{}')".format(s) if s != "'" else 'symbol("{}")'.format(s)
    else:
        result = ""
    return [result]

def p_ndef(a, b): return flatten_list(b)
def p_object(a, b): return flatten_list(b)

def skeyword(p):
    [s, q, a, b] = token_type("string")(p)
    if s:
        content = a[0][1][1:-1]
        if len(content) > 1:
            return [s, q, a, [content]]
    return [False, p, [], []]

def ssymbol(p):
    [s, q, a, b] = token_type("string")(p)
    if s:
        content = a[0][1][1:-1]
        if len(content) == 1:
            return [s, q, a, [content]]
    return [False, p, [], []]

def parser(p): return pp(P(S(M1(rdef))), p_parser)(p)
def rdef(p): return pp(P(S(ndef, symbol('='), def_body, O(process), symbol(';'))), p_rdef)(p)
def process(p): return pp(P(S(symbol('-'), symbol('>'), pname)), p_process)(p)
def ndef(p): return pp(P(S(name)), p_ndef)(p)
def def_body(p): return pp(P(S(branch, M(S(symbol('|'), branch)))), p_def_body)(p)
def branch(p): return pp(P(S(M1(qobject))), p_branch)(p)
def qobject(p): return pp(P(S(mobject, O(quantifier))), p_qobject)(p)
def quantifier(p): return pp(P(S(symbol('?')), S(symbol('*')), S(symbol('+'))), p_quantifier)(p)
def mobject(p): return pp(P(S(eobject, O(modifier))), p_mobject)(p)
def modifier(p): return pp(P(S(symbol('$'), mmethod)), p_modifier)(p)
def eobject(p): return pp(P(S(object, O(extension))), p_eobject)(p)
def extension(p): return pp(P(S(symbol('!'), ext)), p_extension)(p)
def object(p): return pp(P(S(name), S(ykeyword), S(ysymbol), S(group_object)), p_object)(p)
def group_object(p): return pp(P(S(symbol('('), M1(qobject), symbol(')'))), p_group_object)(p)
def pname(p): return P(S(name))(p)
def mmethod(p): return P(S(name))(p)
def ext(p): return P(S(name))(p)
def name(p): return pp(P(S(identifier)), p_identifier)(p)
def ykeyword(p): return pp(P(S(skeyword)), p_keyword)(p)
def ysymbol(p): return pp(P(S(ssymbol)), p_symbol)(p)

file_type = None

def gencode(rfile, ftype):
    global char_source, token_source, file_type
    file_type = ftype
    with open(rfile) as fd:
        char_source = fd.read()
    [s, p, a, b] = lexer(0)
    if s:
        token_source = b
    [s, p, a, b] = parser(0)
    return b

def assembly(lang):
    with open("general_code.py") as fd: general_code = fd.read()
    with open("lexer_common.py") as fd: lexer_common = fd.read()
    with open("parser_common.py") as fd: parser_common = fd.read()
    with open("{}_lexer_pp.py".format(lang)) as fd: lexer_pp = fd.read()
    with open("{}_parser_pp.py".format(lang)) as fd: parser_pp = fd.read()
    lexer_code = gencode("{}.lex".format(lang), "lex")
    parser_code = gencode("{}.yacc".format(lang), "yacc")
    with open("test.py") as fd: assembly_code = fd.read()
    with open("{}_parser.py".format(lang), "w") as fd:
        fd.write(general_code)
        fd.write(lexer_common)
        fd.write(lexer_pp)
        fd.write("\n")
        fd.write("\n".join(lexer_code))
        fd.write("\n")
        fd.write(parser_common)
        fd.write(parser_pp)
        fd.write("\n")
        fd.write("\n".join(parser_code))
        fd.write("\n")
        #fd.write(assembly_code)

if __name__ == "__main__":
    assembly("sql")
