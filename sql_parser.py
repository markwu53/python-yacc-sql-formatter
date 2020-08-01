
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
p_lexer_sql_identifier = lambda a, b: ("identifier", "".join(flatten_list(a)))
p_lexer_sql_space = lambda a, b: ("space", "".join(flatten_list(a)))
p_lexer_sql_string = lambda a, b: ("string", "".join(flatten_list(a)))
p_lexer_sql_number = lambda a, b: ("number", "".join(flatten_list(a)))
p_lexer_sql_quoted = lambda a, b: ("quoted", "".join(flatten_list(a)))
p_lexer_sql_bracketed = lambda a, b: ("bracketed", "".join(flatten_list(a)))
p_lexer_sql_line_comment = lambda a, b: ("line_comment", "".join(flatten_list(a)))
p_lexer_sql_block_comment = lambda a, b: ("block_comment", "".join(flatten_list(a)))
p_lexer_symbol = lambda a, b: ("symbol", "".join(flatten_list(a)))
p_lexer = lambda a, b: [e for e in flatten_list(b) if e[0] not in ("space", "line_comment", "block_comment")]

def one_token(p): return P(S(lexer_sql_identifier), S(lexer_sql_space), S(lexer_sql_string), S(lexer_sql_number), S(lexer_sql_quoted), S(lexer_sql_bracketed), S(lexer_sql_line_comment), S(lexer_sql_block_comment), S(lexer_symbol))(p)
def lexer(p): return pp(P(S(M(one_token))), p_lexer)(p)
def lexer_identifier(p): return P(S(identifier_first_char, M(identifier_next_char)))(p)
def identifier_first_char(p): return P(S(is_char('_')), S(is_alpha))(p)
def identifier_next_char(p): return P(S(identifier_first_char), S(is_digit))(p)
def lexer_space(p): return P(S(M1(is_space)))(p)
def lexer_block_comment(p): return P(S(is_char('/'), is_char('*'), M(S(lex_negate(S(is_char('*'), is_char('/'))))), is_char('*'), is_char('/')))(p)
def lexer_symbol(p): return pp(P(S(get_char)), p_lexer_symbol)(p)
def lexer_sql_identifier(p): return pp(P(S(lexer_identifier)), p_lexer_sql_identifier)(p)
def lexer_sql_space(p): return pp(P(S(lexer_space)), p_lexer_sql_space)(p)
def lexer_sql_string(p): return pp(P(S(is_char("'"), M(string_char), is_char("'"))), p_lexer_sql_string)(p)
def string_char(p): return P(S(is_char("'"), is_char("'")), S(lex_negate(is_char("'"))))(p)
def lexer_sql_number(p): return pp(P(S(digits, is_char('.'), digits), S(digits, O(is_char('.'))), S(is_char('.'), digits)), p_lexer_sql_number)(p)
def digits(p): return P(S(M1(is_digit)))(p)
def lexer_sql_quoted(p): return pp(P(S(is_char('"'), M1(S(lex_negate(is_char('"')))), is_char('"'))), p_lexer_sql_quoted)(p)
def lexer_sql_bracketed(p): return pp(P(S(is_char('['), M1(S(lex_negate(is_char(']')))), is_char(']'))), p_lexer_sql_bracketed)(p)
def lexer_sql_line_comment(p): return pp(P(S(is_char('-'), is_char('-'), M(S(lex_negate(is_eol))), is_eol)), p_lexer_sql_line_comment)(p)
def lexer_sql_block_comment(p): return pp(P(S(lexer_block_comment)), p_lexer_sql_block_comment)(p)

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

def parser(p): return P(S(dline_join(S(M(one_statement)))))(p)
def one_statement(p): return P(S(concat(S(select_statement, O(symbol(';'))))), S(concat(S(declare_statement, O(symbol(';'))))), S(concat(S(exec_statement, O(symbol(';'))))), S(symbol(';')))(p)
def declare_statement(p): return P(S(space_join(S(kword('declare'), line_join(S(one_var_dec, M(S(indent(next_var_dec)))))))))(p)
def one_var_dec(p): return P(S(space_join(S(var_name, var_type, O(var_init)))))(p)
def next_var_dec(p): return P(S(space_join(S(symbol(','), one_var_dec))))(p)
def var_name(p): return P(S(concat(S(symbol('@'), name))))(p)
def var_type(p): return P(S(function), S(name))(p)
def var_init(p): return P(S(space_join(S(symbol('='), arithmetic_expression))))(p)
def exec_statement(p): return P(S(line_join(S(exec_command, with_result_set, with_result_set_2))))(p)
def exec_command(p): return P(S(concat(S(kword('exec'), symbol('('), is_string, symbol(')')))))(p)
def with_result_set(p): return P(S(space_join(S(kword('with'), kword('result'), kword('sets')))))(p)
def with_result_set_2(p): return P(S(line_join(S(symbol('('), indent(S(one_exec_set, M(next_exec_set))), symbol(')')))))(p)
def next_exec_set(p): return P(S(space_join(S(symbol(','), one_exec_set))))(p)
def one_exec_set(p): return P(S(line_join(S(symbol('('), indent(S(line_join(S(one_column_dec, M(next_column_dec))))), symbol(')')))))(p)
def next_column_dec(p): return P(S(space_join(S(symbol(','), one_column_dec))))(p)
def one_column_dec(p): return P(S(space_join(S(name, var_type))))(p)
def select_statement(p): return P(S(dline_join(S(O(with_cte), rowset))))(p)
def rowset(p): return P(S(dline_join(S(rowset_comp, M(S(dline_join(S(set_op, rowset_comp))))))))(p)
def set_op(p): return P(S(space_join(S(kword('union'), O(kword('all'))))), S(kword('intersect')), S(kword('except')))(p)
def rowset_comp(p): return P(S(select), S(rowset_group))(p)
def rowset_group(p): return P(S(symbol('('), lambda p: rowset(p), symbol(')')))(p)
def select(p): return P(S(line_join(S(space_join(S(kword('select'), O(kword('distinct')))), indent(S(line_join(S(select_column, M(S(space_join(S(symbol(','), select_column)))))))), O(S(space_join(S(kword('into'), table)))), O(from_struct), O(orderby), O(for_xml)))))(p)
def with_cte(p): return P(S(dline_join(S(kword('with'), cte_def, M(S(space_join(S(symbol(','), cte_def))))))))(p)
def cte_def(p): return P(S(line_join(S(space_join(S(concat(S(cte_name, O(cte_col_spec))), kword('as'), symbol('('))), indent(rowset), symbol(')')))))(p)
def cte_name(p): return P(S(name))(p)
def cte_col_spec(p): return P(S(concat(S(symbol('('), cte_col_name, M(S(space_join(S(symbol(','), cte_col_name)))), symbol(')')))))(p)
def cte_col_name(p): return P(S(name))(p)
def select_column(p): return P(S(concat(S(M(S(name, symbol('.'))), symbol('*')))), S(space_join(S(arithmetic_expression, O(S(O(kword('as')), column_alias))))))(p)
def column_alias(p): return P(S(name))(p)
def from_struct(p): return P(S(line_join(S(space_join(S(kword('from'), table_expression)), M(S(indent(S(space_join(S(symbol(','), table_expression)))))), O(where), O(groupby)))))(p)
def table_expression(p): return P(S(line_join(S(table_comp, M(S(indent(next_table_comp)))))))(p)
def table_comp(p): return P(S(table_function), S(table_literal), S(subquery), S(table_group))(p)
def table_group(p): return P(S(line_join(S(symbol('('), indent(S(lambda p: table_expression(p))), symbol(')')))))(p)
def next_table_comp(p): return P(S(table_join), S(table_apply), S(cross_join), S(table_pivot))(p)
def table_join(p): return P(S(space_join(S(join, table_comp, kword('on'), join_condition))))(p)
def join_condition(p): return P(S(boolean_expression))(p)
def join(p): return P(S(O(join_modifier), O(join_hint), kword('join')))(p)
def join_modifier(p): return P(S(kword('inner')), S(outer_modifier, O(kword('outer'))))(p)
def outer_modifier(p): return P(S(kword('left')), S(kword('right')), S(kword('full')))(p)
def join_hint(p): return P(S(kword('hash')))(p)
def table_apply(p): return P(S(space_join(S(apply_option, kword('apply'), table_comp))))(p)
def apply_option(p): return P(S(kword('cross')), S(kword('outer')))(p)
def cross_join(p): return P(S(space_join(S(kword('cross'), kword('join'), table_comp))))(p)
def table_pivot(p): return P(S(line_join(S(kword('pivot'), symbol('('), indent(S(line_join(S(function, space_join(S(kword('for'), pivot_column, kword('in'), in_list2)))))), space_join(S(symbol(')'), O(table_as_alias)))))))(p)
def pivot_column(p): return P(S(name))(p)
def in_list2(p): return P(S(line_join(S(symbol('('), indent(S(line_join(S(in_item, M(S(space_join(S(symbol(','), in_item)))))))), symbol(')')))))(p)
def where(p): return P(S(space_join(S(kword('where'), where_condition))))(p)
def where_condition(p): return P(S(boolean_expression))(p)
def groupby(p): return P(S(line_join(S(space_join(S(kword('group'), kword('by'), concat(S(groupby_col, M(S(space_join(S(symbol(','), groupby_col)))))))), O(having)))))(p)
def groupby_col(p): return P(S(arithmetic_expression))(p)
def having(p): return P(S(indent(S(space_join(S(kword('having'), having_condition))))))(p)
def having_condition(p): return P(S(boolean_expression))(p)
def table_function(p): return P(S(space_join(S(concat(S(M(S(name, symbol('.'))), function)), O(table_as_alias)))))(p)
def table_literal(p): return P(S(space_join(S(table, O(table_as_alias), O(table_hint)))))(p)
def table_hint(p): return P(S(concat(S(kword('with'), symbol('('), name, M(S(space_join(S(symbol(','), name)))), symbol(')')))))(p)
def table(p): return P(S(concat(S(name, symbol('.'), M(S(O(name), symbol('.'))), name))), S(name), S(concat(S(symbol('#'), name))))(p)
def subquery(p): return P(S(line_join(S(symbol('('), indent(rowset), space_join(S(symbol(')'), table_as_alias))))))(p)
def table_as_alias(p): return P(S(space_join(S(O(kword('as')), table_alias))))(p)
def table_alias(p): return P(S(concat(S(cte_name, O(cte_col_spec)))))(p)
def orderby(p): return P(S(space_join(S(kword('order'), kword('by'), concat(S(orderby_comp, M(S(space_join(S(symbol(','), orderby_comp))))))))))(p)
def orderby_comp(p): return P(S(space_join(S(orderby_col, O(orderby_modifier)))))(p)
def orderby_modifier(p): return P(S(kword('asc')), S(kword('desc')))(p)
def orderby_col(p): return P(S(arithmetic_expression))(p)
def for_xml(p): return P(S(space_join(S(kword('for'), kword('xml'), concat(S(xml_mode, O(S(space_join(S(symbol(','), xml_directive))))))))))(p)
def xml_mode(p): return P(S(kword('raw')), S(kword('auto')), S(kword('explicit')), S(concat(S(kword('path'), O(S(symbol('('), name, symbol(')')))))))(p)
def xml_directive(p): return P(S(kword('type')), S(kword('root')))(p)
def boolean_expression(p): return P(S(line_join(S(boolean_comp, M(S(indent(S(space_join(S(boolean_op, boolean_comp))))))))))(p)
def boolean_op(p): return P(S(kword('and')), S(kword('or')))(p)
def boolean_comp(p): return P(S(O(kword('not')), boolean_group), S(comparison_form), S(in_form), S(like_form), S(between_form), S(exist_form), S(is_null_form))(p)
def boolean_group(p): return P(S(concat(S(symbol('('), lambda p: boolean_expression(p), symbol(')')))))(p)
def comparison_form(p): return P(S(space_join(S(arithmetic_expression, concat(comparison_op), arithmetic_expression))))(p)
def comparison_op(p): return P(S(symbol('=')), S(symbol('!'), symbol('=')), S(symbol('>'), symbol('=')), S(symbol('<'), symbol('=')), S(symbol('<'), symbol('>')), S(symbol('>')), S(symbol('<')))(p)
def in_form(p): return P(S(in_form_1), S(in_form_2))(p)
def in_form_1(p): return P(S(space_join(S(arithmetic_expression, O(kword('not')), kword('in'), in_list))))(p)
def in_list(p): return P(S(concat(S(symbol('('), in_item, M(S(space_join(S(symbol(','), in_item)))), symbol(')')))))(p)
def in_item(p): return P(S(string_literal), S(concat(S(O(sign), number_literal))), S(is_identifier), S(is_bracketed), S(is_quoted))(p)
def in_form_2(p): return P(S(line_join(S(space_join(S(arithmetic_expression, O(kword('not')), kword('in'), symbol('('))), indent(rowset), symbol(')')))))(p)
def like_form(p): return P(S(space_join(S(arithmetic_expression, O(kword('not')), kword('like'), arithmetic_expression))))(p)
def between_form(p): return P(S(space_join(S(arithmetic_expression, kword('between'), arithmetic_expression, kword('and'), arithmetic_expression))))(p)
def is_null_form(p): return P(S(space_join(S(arithmetic_expression, kword('is'), O(kword('not')), kword('null')))))(p)
def exist_form(p): return P(S(line_join(S(space_join(S(O(kword('not')), kword('exists'), symbol('('))), indent(rowset), symbol(')')))))(p)
def arithmetic_expression(p): return P(S(arithmetic_comp, M(S(arithmetic_op, arithmetic_comp))))(p)
def arithmetic_op(p): return P(S(symbol('+')), S(symbol('-')), S(symbol('*')), S(symbol('/')))(p)
def arithmetic_comp(p): return P(S(string_literal), S(signed_number), S(number_literal), S(symbol('?')), S(kword('null')), S(var_name), S(concat(S(line_join(S(symbol('('), indent(select), symbol(')'))), O(S(symbol('.'), function))))), S(is_quoted), S(is_bracketed), S(O(sign), arithmetic_group), S(over_form), S(count_form), S(iif_form), S(concat(S(M(S(name, symbol('.'))), function))), S(space_join(S(one_column, O(S(kword('collate'), name))))), S(case_form), S(cast_form))(p)
def sign(p): return P(S(symbol('+')), S(symbol('-')))(p)
def signed_number(p): return P(S(concat(S(sign, number_literal))))(p)
def arithmetic_group(p): return P(S(concat(S(symbol('('), lambda p: arithmetic_expression(p), symbol(')')))))(p)
def function(p): return P(S(concat(S(function_name, symbol('('), O(function_para), symbol(')')))))(p)
def function_para(p): return P(S(one_para, M(S(space_join(S(symbol(','), one_para))))))(p)
def one_para(p): return P(S(arithmetic_expression))(p)
def one_column(p): return P(S(concat(column_name)))(p)
def column_name(p): return P(S(name, M(S(symbol('.'), name))))(p)
def case_form(p): return P(S(case_form_1), S(case_form_2))(p)
def case_form_1(p): return P(S(line_join(S(kword('case'), indent(S(line_join(S(M1(when), O(else_part), kword('end')))))))))(p)
def when(p): return P(S(space_join(S(kword('when'), boolean_expression, kword('then'), arithmetic_expression))))(p)
def else_part(p): return P(S(space_join(S(kword('else'), arithmetic_expression))))(p)
def case_form_2(p): return P(S(kword('case'), arithmetic_expression, M1(when2), O(else_part), kword('end')))(p)
def when2(p): return P(S(kword('when'), arithmetic_expression, kword('then'), arithmetic_expression))(p)
def cast_form(p): return P(S(concat(S(kword('cast'), symbol('('), space_join(S(arithmetic_expression, kword('as'), make_upper(var_type))), symbol(')')))))(p)
def count_form(p): return P(S(concat(S(kword('count'), symbol('('), count_item, symbol(')')))))(p)
def count_item(p): return P(S(space_join(S(O(kword('distinct')), arithmetic_expression))), S(symbol('*')))(p)
def over_form(p): return P(S(space_join(S(function, kword('over'), concat(S(symbol('('), partition_orderby, symbol(')')))))))(p)
def partition_orderby(p): return P(S(space_join(S(partition, O(orderby)))), S(orderby))(p)
def partition(p): return P(S(space_join(S(kword('partition'), kword('by'), concat(S(arithmetic_expression, M(S(space_join(S(symbol(','), arithmetic_expression))))))))))(p)
def iif_form(p): return P(S(concat(S(kword('iif'), symbol('('), boolean_expression, space_join(S(symbol(','), arithmetic_expression)), space_join(S(symbol(','), arithmetic_expression)), symbol(')')))))(p)
def name(p): return P(S(is_identifier), S(is_quoted), S(is_bracketed), S(is_string))(p)
def function_name(p): return P(S(is_function_name), S(is_quoted), S(is_bracketed))(p)
def string_literal(p): return P(S(is_string))(p)
def number_literal(p): return P(S(is_number))(p)
