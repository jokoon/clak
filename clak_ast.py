import json, sys
import indentoken
import sys, os
import subprocess
import platform, pathlib

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

parser_path = pathlib.Path("Debug")/"lexy_example.exe"
parser_path = pathlib.Path("..")/"clak"/"Debug"/"clak.exe"

'''
        break

'''
src = ('''
if nope:
    hum = cally(1,2)
    duh = (43, fcall(2.4,(abc, 5)))
while 1:
    continue
    return
    return 32-2*4%3
''')

src = ('''
func sunrungunbunpunfunjunction(roubidou:char, i: int) (float, char):
    if nope:
        hum = cally(1,2)
        duh = (43, fcall(2.4,(abc, 5)))
    while 1:
        continue
        return
        return 32-2*4%3
''')



def struple_duck(li):
    types = []
    for el in li:
        if isfloat(el):
            types.append('float')
        elif isint(el):
            types.append('int')
        elif el in ['true', 'false']:
            types.append('bool')
        elif '"' in el:
            types.append('str')
        else:
            types.append(None)

def struple_signature(types):
    return 'tuple_'+'_'.join([t[0] for t in types if t != ','])
def struple_decl_body(struples_decl):
    predecl = '\n'.join([
        f'typedef struct {name} {name};'
        for name, types in struples_decl])
    decl = '\n'.join([(
        f'struct {name} {{\n'
        +'    \n'.join([
            f'    {type_id} var_{type_id[0]}_{i} ;'
            for i,type_id in enumerate(type_list) if type_id != ','])
        +f'\n}};')
        for name, type_list in struples_decl
        ])
    return predecl+'\n\n'+decl+'\n\n'


def parse():
    global src
    if len(sys.argv)>1:
        src = open(sys.argv[1]).read()
    if src[0] == '\n':
        src = src[1:]
    # generating indent tokens etc
    indented_source = indentoken.token_indenter(src, '__ENDLINE__', ('__INDENT__', '__DEDENT__'))

    # writing indented to a file
    indented_filename = "src_indented.nogit.txt"
    open(indented_filename, 'w', encoding = 'utf8').write(indented_source)

    match platform.system():
        case 'Windows':
            clak_exe = parser_path
        case 'Linux':
            clak_exe = './clak'

    thing = subprocess.run([clak_exe, indented_filename])
    # print(thing)
# ████████████████████████████████████████████
def emit_c():
    def clean_ast(ast):
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
             json.dumps(ast2, indent = 1))

        return ast

    # parser will output to this json file
    parse_tree_json = 'parse_tree.nogit.json'

    # using an array instead of raw string, for efficiency (I think?)
    body = []
    spaces = lambda n: 2*n*' '

    # emiting C
    def write(thing, indent = None):
        # print('adding ', repr(thing))
        body.append(
            (spaces(indent) if indent else '')
            +thing
        )
    '''
    problem is that (1, 'f', (3.4, true))
    can be expressed as
    typedef struct {
        int i;
        char c;
        struct {
            float f;
            bool b;
        };


    };


    #include <stdio.h>

    typedef struct {
        int i;
        struct {
            char c;
        } a;

    } thing;

    int main(){
        thing th;
        th.i;
        th.a.c;

        th = (thing){5.5,{'c'}};
        printf("%d %c", th.i, th.a.c );

    };


    '''
    def make_struct(types):
        decl = '\n'.join([(
            f'struct {name} {{\n'
            +'    \n'.join([
                f'    {type_id} var_{type_id[0]}_{i} ;'
                for i,type_id in enumerate(type_list) if type_id != ','])
            +f'\n}};')
            for name, type_list in struples_decl
            ])



    def extract_types(ast):
        types = [t['base_type'] for t in ast]


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
                    # write('\n')
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
                # print('while compounded', compounded)
                walk(compounded, indent)
                # write('}\n', indent)

            case {'if_stmt':if_stmt}:
                # done
                (if_, expr, compounded) = if_stmt
                write('if(', indent)
                walk(expr)
                write(') ')
                walk(compounded, indent)

        # jump statements
            case {'jump_stmt':[jump_stmt]}:
                # print('jump_stmt', jump_stmt)
                walk(jump_stmt,indent)
            case {'return_stmt_value':[return_]}:
                write('return;\n', indent)
            case {'return_stmt_value':[return_, return_expr]}:
                write('return ', indent)
                walk(return_expr)

                write(';\n')

            case {'break_stmt':cont_ret_break}|{'return_stmt':cont_ret_break}|{'continue_stmt':  cont_ret_break}:
                write(f'{cont_ret_break[0]};\n', indent)

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

        # expressions
            case (
                {'expression::product':[left, op, right]}
                | {'expression::sum':[left, op, right]}
                | {'expression::sum':[left, op, right]}
                ):
                walk(left)
                write(op)
                walk(right)
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

        # functions
            case {'func_args':func_args}:
                for farg in func_args:
                    walk(farg)
            # case {'func_decl':[f, function_argument_list, func_args, return_values, compound_st]}:
            #     walk(function_argument_list)
            #     walk(func_args)
            #     extract_types()
            #     walk(return_values)
            #     walk(compound_st)
            case {'func_decl':[func_signature, compound_st]}:
                # walk(function_argument_list)
                # walk(func_args)
                # extract_types()
                # walk(return_values)
                walk(func_signature)
                walk(compound_st)
            case {'func_signature':['func', idtf, func_args, return_values]}:

                walk(return_values)
                walk(idtf)
                walk(func_args)

            case {'decl_ltr':[idtf, {"base_type":[base_type]}]}:
                # write(f'{base_type} {idtf};', indent)
                write('', indent)
                walk(idtf)
                write(f' {base_type};')



            # rest
            case {'expression::gdfgfdks':[expr]}:
                walk(expr)
            case {'expression::gdfgfdks':[expr]}:
                walk(expr)
            case _:
                if type(entry) is list:
                    print(spc, '████ untreated: ████ (list)',
                        indent, entry)
                elif type(entry) is dict:
                    print(spc, '████ untreated: ████ (dict)', indent, [(
                            'list' if type(e) is list else
                            'dict' if type(e) is dict else
                            f'type(e): {type(e)} e:{e}'
                        ) for e in entry
                        ])
                elif type(entry) is str:
                    print(spc, '████ untreated: ████ (str)', indent, entry)

    # this parse tree has some noisy token removed
    ast = json.loads(open(parse_tree_json).read())

    # we still clean it up some more
    ast2 = clean_ast(ast)
    walk(ast2)
    print()
    print(''.join(body))
    print()
    write_raw_named(''.join(body))

parse()
emit_c()