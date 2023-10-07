import indentoken
import sys, os
import subprocess

indented_filename = ""
src = ""
# default_test = 'asd = (1+2+3,432)'
# default_test = 'asd = (1+2, call(4532,344), 321534)'
default_test = '''
while var:
    continue
    __EXPRESSION__
    if 1:
        duh = (43, call(2.4, 5))
        ret = fun(9)
        thing = stuff

    thing = (1, 34)
    something += 432
    fsdfs = 411

'''
default_test = '''
if nope:
    hum = dada(1,2)
    duh = (43, fcall(2.4,(abc, 5)))
    while 1:
        break
        cally(1)

'''
# while false:
#     nothing()

if 'expr' in sys.argv:
    default_test = "2+(43/3-5*3)/2+(1+2)"

filename = "default_text.nogit.txt"
indented_filename = "default_text.indented.nogit.txt"
open(filename,'w', encoding = 'utf8').write(default_test)
src = default_test

# print('################# source #################')
# print(src)

indented_source = indentoken.token_indenter(src, '__ENDLINE__', ('__INDENT__', '__DEDENT__'))

# print('################# indent-tokened #################')
# print(indented_source)


open(indented_filename, 'w', encoding='utf8').write(indented_source)

# subprocess.run(['./clak', indented_filename])
subprocess.run(['./clak', indented_filename])

# print('###################################################')
# print(open("tree_fancy.nogit.txt", encoding='utf8').read())