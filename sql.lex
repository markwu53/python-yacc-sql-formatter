#target
one_token = lexer_sql_identifier | lexer_sql_space | lexer_sql_string | lexer_sql_number
    | lexer_sql_quoted | lexer_sql_bracketed
    | lexer_sql_line_comment | lexer_sql_block_comment | lexer_symbol;
lexer = one_token* -> p_lexer;

#common
lexer_identifier = identifier_first_char identifier_next_char*;
identifier_first_char = "_" | is_alpha;
identifier_next_char = identifier_first_char | is_digit;
lexer_space = is_space+;
lexer_block_comment = "/" "*" (("*" "/") $ lex_negate)* "*" "/";
lexer_symbol = get_char -> p_lexer_symbol;

#sql
lexer_sql_identifier = lexer_identifier -> p_lexer_sql_identifier;
lexer_sql_space = lexer_space -> p_lexer_sql_space;
lexer_sql_string = "'" string_char* "'" -> p_lexer_sql_string;
string_char = "'" "'" | "'" $lex_negate;
lexer_sql_number = digits "." digits | digits "."? | "." digits -> p_lexer_sql_number;
digits = is_digit+;
lexer_sql_quoted = '"' ('"' $ lex_negate)+ '"' -> p_lexer_sql_quoted;
lexer_sql_bracketed = "[" ("]" $ lex_negate)+ "]" -> p_lexer_sql_bracketed;
lexer_sql_line_comment = "-" "-" (is_eol $ lex_negate)* is_eol -> p_lexer_sql_line_comment;
lexer_sql_block_comment = lexer_block_comment -> p_lexer_sql_block_comment;
