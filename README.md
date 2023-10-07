# clak "sugar" language

## THIS IS AN EXPERIMENT, IT'S A LEARNING PROJECT, THE SYNTAX IS STILL EVOLVING

clak is an experimental "sugar" language, it's not really a programming language because it just generate C code.

Parsing is done thanks to lexy, a fast parser combinator based on templates and `constexpr`, check it out! :

https://github.com/foonathan/lexy

# Aimed features:

* pythonic indentation
* Compiles to C for faster compilation and compatibility with existing libraries
* containers:
    * string
    * hashmap/dict
    * dynamic array
    * tuples as struct
    * vec2/vec3/vec4, maybe matrix and quaternion
* "barebone" language, features are kept to a minimum to be easy to learn:
    * no inheritance or polymorphism
    * no generics
    * no garbage collection
    * no pointers
* maybe explore more advanced features regarding safety, like escape analysis

# How to use:

1. `cmake .`
2. build the parser executable
3. write some code and launch the parser with clak_parse.py yourfile.txt
4. run clak_ast.py to generate C code

Some incomplete syntax sample:

```
func bingbong(i: int) (float, char):
    return 543

func main()():
    # tuples

    tup: (char, float) = {'c', 0.}
    # -> typedef struct {char field1; float field2;} charfloat1;

    # -> charfloat1 tup = {'c', 0.};

    tup = ('a', 3.)
    # -> tup = (charfloat1){'a', 3.f};

    # automatic type deduction
    f = 4. # float
    c = 'z' # char
    s = "text" # string
    tup2 = (424, "text") # or {424, "text"}

    shop: list(int, 321) # fixed sized array
    # -> int * shop = NULL;
    # -> arrfree(shop);
    # -> arrsetlen(shop, 321);
    shop.append(32)
    # -> arrput(shop, 32)
    listint = [2, 5, 8] # same type
    shop[32] = 123

    # string (immutables?)
    sblourg = "dada ofond"
    sblarg: str = "dada ofond"
    bloob = "36473dhhhdhdhsswury" # type deduction
    sub = bloob[3:6]

    # dict
    dic = {"765": 655}
    book: dict(int -> str)
    book[2342] = "hobbits"

    # vectors
    v: vec2i = (54, 65)
    v = 3.3 * v

    struct pod_type:
        f: float
        i, j, k: int

    # enforced multi line patterns, no code golf
    enum typething
        thing1
        thing2 = 321
        thfsdfs
        s1231 = 3

    # switch
    switch ghjj:
        1:
            shop[12] = 45
        2: f = 123.
        431|432|1231|enumthing:
            v = (2,3)
            # translates to:
            # case 431:
            # case 432:
            # case 1231:
            # case enumthing:
            #     v = (2,3)
            #     break;

        45..667:
        20..25:
            #  case 20: case 21: case 22: case 23: case 24: case 25:
            break;
        # no default

    if 1231 < 12 or b == 12 and 32 & 48:
        return 0
    else:
        if false or true:
            for i in v1..v2:
                printf(432121)

    return 0