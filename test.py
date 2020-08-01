import sql_parser

def test():
    with open("test.sql") as fd:
        sql_parser.char_source = fd.read()
    [s, p, a, b] = sql_parser.lexer(0)
    if s:
        sql_parser.token_source = b
        #for item in sql_parser.token_source: print(item)
    [s, p, a, b] = sql_parser.parser(0)
    print(s, p)
    if s: print(b[0][0])

if __name__ == "__main__":
    test()
