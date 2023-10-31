import sys
def leading_spaces(s):
    spaces = 0
    for c in s:
        if c == ' ':
            spaces += 1
        else:
            break
    return spaces//4


def token_indenter(source, endline, indents = ('{', '}'), print_diagnose = False):

    indent_token, dedent_token = indents
    # adding \n to improve the thing
    if source[-2:] != '\n\n':
        print('added\\n')
        source += '\n\n'
    lines = [line for line in source.split('\n')]

    # counting indenting space (no tab)
    lines = [(line, leading_spaces(line))
        for line in lines]

    lines = [(
        line,
        (lines[i-1][1] if line == '' else ldspc)
            if 1<=i<len(lines) else 0)
        for (i, (line, ldspc)) in enumerate(lines)]

    # prev None . . . .
    # next  . . . . None

    # assigning prev/next line count for each line
    lines = [
        (
            lines[i-1][1] if 1<=i<len(lines) else None, # prev: 1 to len-1
            lines[i+1][1] if 0<=i<len(lines)-1 else None, # next: 0 to len-2
            line, spaces
         )
        for (i, (line, spaces)) in enumerate(lines)]

    # difference of spaces between lines
    lines = [
        (spaces - prev if prev!=None else None,
        spaces - nextt if nextt!=None else None,
        line, spaces)
        for (prev, nextt, line, spaces) in lines]

    lines_tokens = []
    # we only insert tokens on the same line to keep the context, hence redundancy

    # generating indent/dedent tokens
    for (diffprev, diffnext, line, spaces) in lines:
        lines_tokens.append((
            line,
            diffprev, diffnext,
            1 if diffprev == 1 else 0, # indent
            diffnext if diffnext else 0, # dedent
            spaces,
            diffnext >= 0
            # True
                if diffnext != None and line
                else False, # endline
            ))

    laidout = ''
    laidout_better = ''
    dent_width = max(len(indent_token), len(dedent_token)) + 1
    for (line, diffprev, diffnext, indent, dedent, spaces, newline) in lines_tokens:

        # indent_tok = '{' if indent else ''
        # dedent_tok = '}'*dedent if dedent else ''

        indent_tok = indent_token if indent else ''
        dedent_tok = (dedent_token+' ') * dedent if dedent else ''
        # symbol = line.replace(' ','')
        # symbol = line.lstrip()
        # symbol = line
        spaces_brace = spaces - 1
        spaces *= 4
        spaces_brace *= 4
        cool_line = (
            (((' '*spaces_brace) + indent_tok + '\n') if indent_tok else '')
            +f'{line if line else " "*spaces} {endline if newline else ""}\n'
            # +f'{line if line else " "*spaces}{endline}\n'
            +(((' '*spaces_brace) + dedent_tok + '\n') if dedent_tok else '')
            )

        laidout += f'{indent_tok} {line} {dedent_tok}'

        diagnose = (f'dfpv {str(diffprev):>5} dfnx {str(diffnext):>5} {indent_tok:12} {dedent_tok:12} | {repr(line)}')
        laidout_better += cool_line

        if print_diagnose:
            print(diagnose)
    return laidout_better


def main():
    filename = sys.argv[1]
    # print(sys.argv)

    # ' --;'

    open(filename+".indent.txt", 'w', encoding='utf8').write(token_indenter(
        open(filename, encoding='utf8').read(),
        '__ENDLINE__', ('__INDENT__', '__DEDENT__'))
    )

if __name__ == '__main__':
    main()

# endline = ' --;' if endline_arg == None else ' --;'
# if __name__ == '__main__':
#     pass
# else:
#     print(__name__, 'loading as module')
'''
indent can be inserted
    only once per line
    at the beginning of the line
dedent can be inserted
    multiple times per line
    at the end of the line

                        dfnx   dfpr
if                   |  1      None
    sttmt;           |  0      1
    sttmt;           |  0      0
    for              |  1      0
        sttmt;       |  0      1
        if           |  1      0
            sttmt;   |  -2     1
    sttmt;           |  0      -2
    sttmt;           |  0      0


newline:

-1
if < no
    thing
0
    thing < yes
    thing

1
    thing < yes
thing

1
        thing < yes
thing



diffprev is about indent only
diffprev(a):

case 1: we care
    a
        b
    > 1

case 2:
        a
    b
    > -1

case 3:
            a
    b
    > -2

diffnext is about dedent only
diffnext(a):

case 1:
    a
        b
    > 1

case 2: we care
        a
    b
    > -1

case 3: we care
            a
    b
    > -2


'''
