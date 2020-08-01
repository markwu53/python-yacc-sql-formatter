
#parser

parser = (one_statement*) $dline_join;
one_statement = (select_statement ";"?) $concat 
        | (declare_statement ";"?) $concat 
        | (exec_statement ";"?) $concat 
        | ";";

declare_statement = ("declare" (one_var_dec (next_var_dec $indent)*) $line_join) $space_join;
one_var_dec = (var_name var_type var_init?) $space_join;
next_var_dec = ("," one_var_dec) $space_join;
var_name = ("@" name) $concat;
var_type = function | name;
var_init = ("=" arithmetic_expression) $space_join;

exec_statement = (exec_command with_result_set with_result_set_2) $line_join;
exec_command = ("exec" "(" is_string ")") $concat;
with_result_set = ("with" "result" "sets") $space_join;
with_result_set_2 = ("(" (one_exec_set next_exec_set*) $indent ")") $line_join;
next_exec_set = ("," one_exec_set) $space_join;
one_exec_set = ("(" ((one_column_dec next_column_dec*) $line_join) $indent ")") $line_join;
next_column_dec = ("," one_column_dec) $space_join;
one_column_dec = (name var_type) $space_join;

select_statement = (with_cte? rowset) $dline_join;
rowset = (rowset_comp ((set_op rowset_comp) $dline_join)*) $dline_join;
set_op = ("union" "all"?) $space_join | "intersect" | "except";
rowset_comp = select | rowset_group;
rowset_group = "(" rowset !delay ")";
select = (("select" "distinct"?) $space_join
    ((select_column (("," select_column) $ space_join)*) $line_join) $indent
    (("into" table) $space_join)?
    from_struct? orderby? for_xml?) $ line_join;
with_cte = ("with" cte_def (("," cte_def) $space_join)*) $ dline_join;
cte_def = (((cte_name cte_col_spec?) $ concat "as" "(") $ space_join rowset $indent ")") $ line_join;
cte_name = name;
cte_col_spec = ("(" cte_col_name (("," cte_col_name) $ space_join)* ")") $ concat;
cte_col_name = name;
select_column = ((name ".")* "*") $concat | (arithmetic_expression ("as"? column_alias)?) $space_join;
column_alias = name;

#from_struct
from_struct = (("from" table_expression) $space_join ((("," table_expression) $space_join) $indent)* where? groupby?) $line_join;
table_expression = (table_comp (next_table_comp $indent)*) $line_join;
table_comp = table_function | table_literal | subquery | table_group;
table_group = ("(" (table_expression !delay) $indent ")") $line_join;
next_table_comp = table_join | table_apply | cross_join | table_pivot;
#table_expression = (table_object (table_ext $indent)*) $line_join;
#table_ext = table_join | table_pivot;
#table_join = ((join table_comp) $space_join (("on" join_condition) $space_join) $indent) $line_join;
table_join = (join table_comp "on" join_condition) $space_join;
join_condition = boolean_expression;
join = join_modifier? join_hint? "join";
join_modifier = "inner" | outer_modifier "outer"?;
outer_modifier = "left" | "right" | "full";
join_hint = "hash";
table_apply = (apply_option "apply" table_comp) $space_join;
apply_option = "cross" | "outer";
cross_join = ("cross" "join" table_comp) $space_join;
table_pivot = ("pivot" "(" ((function ("for" pivot_column "in" in_list2) $space_join) $line_join) $indent (")" table_as_alias?) $space_join) $line_join;
pivot_column = name;
in_list2 = ("(" ((in_item (("," in_item) $space_join)*) $line_join) $indent ")") $line_join;
where = ("where" where_condition) $space_join;
where_condition = boolean_expression;
groupby = (("group" "by" (groupby_col (("," groupby_col) $space_join)*) $concat) $space_join having?) $line_join;
groupby_col = arithmetic_expression;
having = (("having" having_condition) $space_join) $indent;
having_condition = boolean_expression;

#table_object
table_function = (((name ".")* function) $concat table_as_alias?) $space_join;
table_literal = (table table_as_alias? table_hint?) $space_join;
table_hint = ("with" "(" name (("," name) $space_join)* ")") $concat;
#table = (name ("." name)*) $concat;
table = (name "." (name? ".")* name) $concat | name | ("#" name) $concat;
subquery = ("(" rowset $indent (")" table_as_alias) $space_join) $line_join;
table_as_alias = ("as"? table_alias) $space_join;
table_alias = (cte_name cte_col_spec?) $ concat;

#orderby
orderby = ("order" "by" (orderby_comp (("," orderby_comp) $space_join)*) $concat) $space_join;
orderby_comp = (orderby_col orderby_modifier?) $space_join;
orderby_modifier = "asc" | "desc";
orderby_col = arithmetic_expression;

#for_xml
for_xml = ("for" "xml" (xml_mode (("," xml_directive) $space_join)?) $concat) $space_join;
xml_mode = "raw" | "auto" | "explicit" | ("path" ("(" name ")")?) $concat;
xml_directive = "type" | "root";

#boolean_expression
boolean_expression = (boolean_comp (((boolean_op boolean_comp) $space_join) $indent)*) $line_join;
boolean_op = "and" | "or";
boolean_comp = "not"? boolean_group 
        | comparison_form
        | in_form 
        | like_form 
        | between_form 
        | exist_form
        | is_null_form;
boolean_group = ("(" boolean_expression ! delay ")") $concat;
comparison_form = (arithmetic_expression comparison_op $concat arithmetic_expression) $space_join;
comparison_op = "=" | "!" "=" | ">" "=" | "<" "=" | "<" ">" | ">" | "<";
in_form = in_form_1 | in_form_2;
in_form_1 = (arithmetic_expression "not"? "in" in_list) $space_join;
in_list = ("(" in_item (("," in_item) $space_join)* ")") $concat;
in_item = string_literal | (sign? number_literal) $concat | is_identifier | is_bracketed | is_quoted;
in_form_2 = ((arithmetic_expression "not"? "in" "(") $space_join rowset $indent ")") $line_join;
like_form = (arithmetic_expression "not"? "like" arithmetic_expression) $space_join;
between_form = (arithmetic_expression "between" arithmetic_expression "and" arithmetic_expression) $space_join;
is_null_form = (arithmetic_expression "is" "not"? "null") $space_join;
exist_form = (("not"? "exists" "(") $space_join rowset $indent ")") $line_join;

#arithmetic_expression
arithmetic_expression = arithmetic_comp (arithmetic_op arithmetic_comp)*;
arithmetic_op = "+" | "-" | "*" | "/";
arithmetic_comp = string_literal | signed_number | number_literal
        | "?" | "null"
        | var_name
        | (("(" select $indent ")") $line_join ("." function)?) $concat
        | is_quoted | is_bracketed
        | sign? arithmetic_group 
        | over_form
        | count_form
        | iif_form
        | ((name ".")* function) $concat
        | (one_column ("collate" name)?) $space_join
        | case_form 
        | cast_form;
sign = "+" | "-";
signed_number = (sign number_literal) $concat;
arithmetic_group = ("(" arithmetic_expression ! delay ")") $concat;
function = (function_name "(" function_para? ")") $concat;
function_para = one_para (("," one_para) $space_join)*;
one_para = arithmetic_expression;
one_column = column_name $ concat;
column_name = name ("." name)*;
case_form = case_form_1 | case_form_2;
case_form_1 = ("case" ((when+ else_part? "end") $line_join) $indent) $line_join;
#when = (("when" boolean_expression) $space_join (("then" arithmetic_expression) $space_join) $indent) $line_join;
when = ("when" boolean_expression "then" arithmetic_expression) $space_join;
else_part = ("else" arithmetic_expression) $space_join;
case_form_2 = "case" arithmetic_expression when2+ else_part? "end";
when2 = "when" arithmetic_expression "then" arithmetic_expression;
cast_form = ("cast" "(" (arithmetic_expression "as" var_type $make_upper) $space_join ")") $concat;
count_form = ("count" "(" count_item ")") $concat;
count_item = ("distinct"? arithmetic_expression) $space_join | "*";
over_form = (function "over" ("(" partition_orderby ")") $concat) $space_join;
partition_orderby = (partition orderby?) $space_join | orderby;
partition = ("partition" "by" (arithmetic_expression (("," arithmetic_expression) $space_join)*) $concat) $space_join;
iif_form = ("iif" "(" boolean_expression ("," arithmetic_expression) $space_join ("," arithmetic_expression) $space_join ")") $concat;

name = is_identifier | is_quoted | is_bracketed | is_string;
function_name = is_function_name | is_quoted | is_bracketed;
string_literal = is_string;
number_literal = is_number;
