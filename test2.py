import os
import sql_parser

source_dir = r"P:\Development\Workspaces\Programs\SQL\etl_source_query"
target_dir = r"P:\Development\Workspaces\Programs\SQL\etl_formatted"

def all_file():
    with open("all_file.txt", "w") as fd:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                path = "{}\\{}".format(root, file)
                fd.write("{}\n".format(path))

def parse_all():
    with open("all_file.txt") as fd:
        all_file = fd.readlines()
    with open("finished.txt") as fd:
        finished_file = fd.readlines()
    process_file = []
    for file in all_file:
        file = file.strip()
        if len(file) == 0: continue
        if file.startswith("*"): continue
        if file not in finished_file:
            process_file.append(file)
    for path in process_file:
        print(path)
        target = "{}{}".format(target_dir, path.split(source_dir)[1])
        print(target)
        dir_name = os.path.dirname(target)
        if not os.path.exists(dir_name): os.makedirs(dir_name)
        process_one(path, target)

def process_one(path, target):
        with open(path, encoding = "utf8") as fd:
            sql_parser.char_source = fd.read()
        [s, p, a, b] = sql_parser.lexer(0)
        sql_parser.token_source = b
        [s, p, a, b] = sql_parser.parser(0)
        if s:
            with open(target, "w") as fd:
                fd.write("{}\n".format(b[0][0]))
        if len(sql_parser.token_source) == p:
            with open("finished.txt", "a") as fd:
                fd.write("{}\n".format(path))
        else:
            print(s, p, len(sql_parser.token_source))

def not_processed():
    with open("all_file.txt") as fd:
        all_file = fd.readlines()
        all_file = [file.strip() for file in all_file if len(file.strip()) > 0]
    with open("finished.txt") as fd:
        finished_file = fd.readlines()
        finished_file = [file.strip() for file in finished_file if len(file.strip()) > 0]
    files = [file for file in all_file if file not in finished_file]
    with open("not_processed.txt", "w") as fd:
        for file in files:
            fd.write("{}\n".format(file))

if __name__ == "__main__":
    parse_all()
    not_processed()