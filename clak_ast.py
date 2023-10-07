import json, sys

from pprint import pformat
import pprint
def write_raw_named(raw_data, filename = None):
    if not filename:
        filename = sys.argv[0].replace('.py', '.txt')
    f = open(filename,'w',encoding='utf8')
    # f.write(pprint.pformat(raw_data, width=60,
    #     indent = 4, compact = True))
    f.write(raw_data)
def write_debug(text):
    filename = sys.argv[0]+'.nogit.txt'
    f = open(filename,'w',encoding='utf8')
    f.write(text)
def get_data(fname):
    return eval(open(fname,encoding='utf8').read())

def is_valid_token(s):

    if(type(s) is list or type(s) is dict):
        return True

    if (
        s[0] == ' '
        or s[0] == '\\'
        or s[0] == '\n'
        or s == "__INDENT__"
        or s == "__ENDLINE__"
        or s == "__DEDENT__"
        or s == ":"
        or s == ","
        or s == "("
        or s == ")"
        ):
        return False
    return True

def iter_test():
    lis = [" ", (1,2), [1,2], 2]
    for a in lis:
        match a:
            case " ":
                a = 'space'
            case (1,2):
                a = 'tuple'
            case list([1,2]):
                a = [1,2]
            case 2:
                a = 3
    print(lis)
    exit()
# iter_test()

def clean_ast(ast):
    def iterate(node):
        match node:
            case list():
                node[:] = [n for n in node
                    if is_valid_token(n)]
                node[:] = [iterate(n) for n in node]
            case dict():
                for k, v in node.items():
                    v = iterate(v)
        return node
    def iterate2(node):
        match node:
            case list():
                print('list', node)
                node[:] = [n for n in node
                # node = [n for n in node
                    if is_valid_token(n)]
                # node2 = [n for n in node
                #     if is_valid_token(n)]
                # node = node2
                # print('list', node2)
                print('list', node)
                # for n in node:
                #     n = iterate(n)
                node[:] = [iterate(n) for n in node]
                # node = [iterate(n) for n in node]
                # node = []

            case dict():
                for k, v in node.items():
                # for k, v in node.copy().items():
                    v = iterate(v)
        return node
    ast2 = iterate(ast)

    open('ast_clean.nogit.json', 'w',
         encoding='utf8').write(
         json.dumps(ast2, indent = 2))

    return ast
# clean_json()
# exit()
# ██████████████████████████████████████████████████████████
body = []
spaces = lambda n: 2*n*' '
def write(thing, indent = None):
    # print('adding ', repr(thing))
    body.append(
        (spaces(indent) if indent else '')
        +thing
    )


'''


'''

def walk(entry, indent = 0):
    '''
        case {'compound_stmt':_}:
        case {'if_stmt':_}:
        case {'identifier':_}:
        case {'assignment_stmt':_}:
        case {'number':_}:
        case {'statement':_}:
        case {'statement':_}:'''

    # easy diag
    spc = ' '*indent*2
    # match entry:
    #     case dict():
    #         print(spc, list(entry.keys()))
    #     case list():
    #         print(spc, [
    #             (
    #                 'list' if type(e) is list else
    #                 'dict' if type(e) is dict else
    #                 e
    #             ) for e in entry
    #             ])
    #     case str():
    #         print(spc, entry)
    #     case _:
    #         print(spc, entry)
    match entry:

        # statements
        case {'statement':stmts}:
            for st in stmts:
                walk(st, indent+1)
        case {'compound_stmt':stmts}:
            write('{\n')
            for stmt in stmts:
                walk(stmt, indent)
            write('}\n', indent)

        # expression
        case {'expression':exprs}:
            for expr in exprs:
                walk(expr, indent)

        # selection and iteration
        case {'while_stmt':while_stmt}:
            (
                wh,
                # space,
                expr,
                # semicol,
                # lineret,
                compounded
            ) = while_stmt
            write('while(', indent)
            walk(expr)
            write(') ')
            walk(compounded, indent)
            # write('}\n', indent)

        case {'if_stmt':if_stmt}:
            # done
            (if_, expr, compounded) = if_stmt
            write('if(', indent)
            walk(expr)
            write(') ')
            walk(compounded, indent)


        # values
        case {'identifier':[n]}:
            # print(n)
            write(n)
        case {'number':[n]}:
            write(n)
        case {'number':[n,dot,f]}:
            write(''.join([n,dot,f]))
        case {'expression_stmt':[expr]}:
            write('', indent)
            walk(expr)
            write(';\n')

        # equal
        case {'expression::equal':things}:
            (idtf, equal, expr_or_else) = things
            walk(idtf)
            write(equal)
            walk(expr_or_else)
        case {'expression::paren_expr':paren_expr}:
            write('(')
            last = len(paren_expr)
            for i, p in enumerate(paren_expr):
                walk(p)
                if i+1!= last:
                    write(', ')

            write(')')
            # write(equal)
        case {'expression::call':call}:
            (idtf, args) = call[0], call[1:]
            walk(idtf)
            write('(')
            last = len(args)
            for i, arg in enumerate(args):
                walk(arg)
                if i+1!= last:
                    write(', ')

            write(')')
        case {'expression::gdfgfdks':[expr]}:
            walk(expr)
        case {'expression::gdfgfdks':[expr]}:
            walk(expr)
        case _:
            if type(entry) is list:
                print(spc, '████ untreated: ████', indent, list(entry.keys()))
            if type(entry) is dict:
                print(spc, '████ untreated: ████', indent,
                    [
                    (
                        'list' if type(e) is list else
                        'dict' if type(e) is dict else
                        e
                    ) for e in entry
                    ])

ast = json.loads(open(sys.argv[1]).read())
ast2 = clean_ast(ast)
walk(ast2)

write_raw_named(''.join(body))