#include <cstdio>
#include <lexy/action/parse.hpp>
#include <lexy/action/parse_as_tree.hpp>
#include <lexy/action/trace.hpp>
#include <lexy/callback.hpp>
#include <lexy/dsl.hpp>
#include <lexy_ext/compiler_explorer.hpp>
#include <lexy_ext/report_error.hpp>
#include <vector>
#include <string>
#include <iostream>
#include <sstream>
#include <iterator>
#include <fstream>
#include <map>
// using namespace std;

/*
lexy::match -> true or false
lexy::validate -> explains why it did not match
*/

namespace {
    namespace grammar_clak {
        namespace dsl = lexy::dsl;

        struct identifier {
            static constexpr auto rule = [] {
                auto head = dsl::ascii::alpha_underscore;
                auto tail = dsl::ascii::alpha_digit_underscore;

                //auto kw_int = LEXY_KEYWORD("return", id);
                //auto kw_struct = LEXY_KEYWORD("struct", id);
                auto id = dsl::identifier(head, tail);

                auto kw_return = LEXY_KEYWORD("return", id);
                auto kw_break = LEXY_KEYWORD("break", id);
                auto kw_continue = LEXY_KEYWORD("continue", id);

                return id
                    .reserve(kw_return, kw_break, kw_continue)
                    //return dsl::identifier(head, tail);

                        //.reserve()

                    ;
            }();
        };
        struct string_literal {
            static constexpr auto rule = [] {
                // Arbitrary code points that aren't control characters.
                auto c = -dsl::ascii::control;
                return dsl::quoted(c);
            }();
        };
        struct number : lexy::token_production {
            // A signed integer parsed as int64_t.
            struct integer : lexy::transparent_production {
                static constexpr auto rule
                    = dsl::minus_sign + dsl::integer<std::int64_t>(dsl::digits<>.no_leading_zero());
            };

            // The fractional part of a number parsed as the string.
            struct fraction : lexy::transparent_production {
                static constexpr auto rule = dsl::lit_c<'.'> >> dsl::capture(dsl::digits<>);
            };

            // The exponent of a number parsed as int64_t.
            struct exponent : lexy::transparent_production {
                static constexpr auto rule = [] {
                    auto exp_char = dsl::lit_c<'e'> | dsl::lit_c<'E'>;
                    return exp_char >> dsl::sign + dsl::integer<std::int16_t>;
                }();
            };
            struct float_literal {
                // not just a float, also an int (lexy can't differentiate)
                struct period_opt_digits {
                    static constexpr auto rule =
                        dsl::period >> dsl::opt(dsl::digits<>);
                };

                static constexpr auto rule =
                    dsl::opt(dsl::lit_c<'-'>)
                    + (dsl::digits<> >> dsl::opt(dsl::p<period_opt_digits>)
                        | dsl::period >> dsl::digits<>)
                    ;
            };


            static constexpr auto rule
                = dsl::peek(dsl::lit_c<'-'> / dsl::digit<>)
                >> dsl::p<integer> +dsl::opt(dsl::p<fraction>) + dsl::opt(dsl::p<exponent>);
        };

        struct expression : lexy::expression_production {

            struct paren_expr {
                static constexpr auto rule =
                    dsl::parenthesized.list(dsl::p<struct expression>, dsl::sep(dsl::comma));
            };

            struct identifier_not_func {
                static constexpr auto rule =
                    dsl::p<identifier> +dsl::peek_not(dsl::lit<'('>);
                //dsl::if_(dsl::p<paren_expr>)
                ;
            };
            //dsl::p<identifier> +dsl::if_(dsl::p<paren_expr>);
                    //dsl::if_(dsl::p<identifier> +dsl::p<paren_expr>);
                    //dsl::p<identifier> >> dsl::p<paren_expr>;
            struct expected_func_or_idft { static constexpr auto name = "expected function call or identifier"; };
            struct expected_operand { static constexpr auto name = "expected operand"; };
            static constexpr auto atom = [] {
                //auto var_or_call_inside = dsl::p<identifier> >> dsl::if_(dsl::p<paren_expr>);
                //| dsl::p<var_or_call_old>
                //| var_or_call_inside
                //| dsl::p<var_or_call_new>
                return
                    dsl::p<paren_expr>
                    //| dsl::p<idtf_of_fcall>
                    | dsl::p<identifier>
                    | dsl::p<string_literal>
                    | dsl::p<number>
                    | dsl::error<expected_operand>;
            }();

            struct call : dsl::postfix_op {
                static constexpr auto op = dsl::op(
                    dsl::parenthesized.list(dsl::p<struct expression>, dsl::sep(dsl::comma)));
                using operand = dsl::atom;
            };

            struct prefix : dsl::prefix_op {
                static constexpr auto op = dsl::op(dsl::lit_c<'-'>);
                // static constexpr auto op = dsl::op(dsl::lit_c<'-'>) / dsl::op(dsl::lit_c<'~'>);
                //using operand = dsl::atom;
                using operand = call;
            };
            struct product : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(dsl::lit_c<'*'>)
                    / dsl::op(dsl::lit_c<'/'>)
                    / dsl::op(dsl::lit_c<'%'>);

                using operand = prefix;
            };
            struct sum : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(dsl::lit_c<'+'>)
                    / dsl::op(dsl::lit_c<'-'>);

                using operand = product;
            };

            struct bit_shift : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(LEXY_LIT(">>"))
                    / dsl::op(LEXY_LIT("<<"));

                using operand = sum;
            };
            struct inequality : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(LEXY_LIT(">"))
                    / dsl::op(LEXY_LIT("<"))
                    / dsl::op(LEXY_LIT("<="))
                    / dsl::op(LEXY_LIT(">="));

                using operand = bit_shift;
            };
            struct equality : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(LEXY_LIT("=="))
                    / dsl::op(LEXY_LIT("!="));

                using operand = inequality;
            };
            struct bit_and : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(dsl::lit_c<'&'>); using operand = equality;
            };
            struct bit_xor : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(dsl::lit_c<'^'>); using operand = bit_and;
            };
            struct bit_or : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(dsl::lit_c<'|'>); using operand = bit_xor;
            };
            struct bool_and : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(LEXY_LIT("&&")); using operand = bit_or;
            };
            struct bool_or : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(LEXY_LIT("||")); using operand = bool_and;
            };

            struct equal : dsl::infix_op_left {
                static constexpr auto op =
                    dsl::op(LEXY_LIT("=")) /
                    dsl::op(LEXY_LIT("*=")) / dsl::op(LEXY_LIT("/=")) / dsl::op(LEXY_LIT("%=")) /
                    dsl::op(LEXY_LIT("+=")) / dsl::op(LEXY_LIT("-=")) /
                    dsl::op(LEXY_LIT(">>=")) / dsl::op(LEXY_LIT("<<=")) /
                    dsl::op(LEXY_LIT("&=")) / dsl::op(LEXY_LIT("|=")) / dsl::op(LEXY_LIT("^="))
                    ;

                using operand = bool_or;
            };

            // using operation = bool_or;
            using operation = equal;

        };

        // statements
        struct statement;
        struct compound_stmt {
            static constexpr auto rule =
                lexy::dsl::brackets(LEXY_LIT("__INDENT__"),
                    LEXY_LIT("__DEDENT__")).list(dsl::recurse<statement>);
        };
        struct else_stmt {
            static constexpr auto rule =
                LEXY_LIT("else") >> LEXY_LIT(":") + dsl::p<compound_stmt>;
        };
        struct elif_stmt {
            // unused!
            static constexpr auto rule =
                LEXY_LIT("elif") >> LEXY_LIT(":") + dsl::p<compound_stmt>;
        };
        struct while_stmt {
            static constexpr auto rule =
                LEXY_LIT("while") >> dsl::p<expression>
                +LEXY_LIT(":") + dsl::p<compound_stmt>;
        };
        struct for_stmt {
            static constexpr auto rule =
                LEXY_LIT("for") >> dsl::p<expression>
                +LEXY_LIT(";") + dsl::p<expression>
                +LEXY_LIT(";") + dsl::p<expression>
                +LEXY_LIT(":") + dsl::p<compound_stmt>;
        };
        struct if_stmt {
            static constexpr auto rule =
                LEXY_LIT("if") >> dsl::p<expression>
                +LEXY_LIT(":") + dsl::p<compound_stmt>
                // please implement this
                // + dsl::opt(dsl::p<elif_stmt> | dsl::p<else_stmt>)
                +dsl::opt(dsl::p<else_stmt>);
        };

        struct continue_stmt {
            static constexpr auto rule = LEXY_LIT("continue")
                >> LEXY_LIT("__ENDLINE__")
                ;
        };

        struct break_stmt {
            static constexpr auto rule = LEXY_LIT("break")
                >> LEXY_LIT("__ENDLINE__")
                ;
        };

        struct return_stmt {
            static constexpr auto rule =
                LEXY_LIT("return")
                >> LEXY_LIT("__ENDLINE__")
                ;
        };

        //struct empty_expr {
        //    static constexpr auto rule =
        //        dsl::if_(dsl::p<expression>)
        //        >>
        //        dsl::nullopt
        //        ;
        //};

        struct return_stmt_value {
            //static constexpr auto rule = [] {
            //    auto expr = dsl::p<expression>;
            //    return
            //        LEXY_LIT("return")
            //        >> dsl::if_(expr)
            //        //>> dsl::p<expression>
            //        //>> dsl::if_(dsl::p<expression>);
            //        ;
            //        //+ LEXY_LIT("__ENDLINE__");
            //}();

            static constexpr auto rule =
                LEXY_LIT("return")
                //+ dsl::opt(dsl::else_ >> dsl::p<expression>)
                //+ dsl::opt(dsl::p<expression>)
                //+ dsl::opt(dsl::p<expression>)
                //+ dsl::p<expression>
                //+ LEXY_LIT("__ENDLINE__");
                //+ LEXY_LIT("__ENDLINE__");
                >> (
                    LEXY_LIT("__ENDLINE__")
                    | dsl::else_ >> dsl::p<expression> +LEXY_LIT("__ENDLINE__")

                    )
                //>> dsl::if_(dsl::p<expression>);
                //>> dsl::if_(expression);
                //+ LEXY_LIT("__ENDLINE__"); 
                //+dsl::opt(dsl::p<expression>)
                //static constexpr auto rule = [] {
                ;
            //{
            //auto maybe_expr = dsl::try_(dsl::p<expression>);
            //return
        //+maybe_expr
                // + dsl::p<expression>)
                // >> dsl::p<expression>
                //+ dsl::opt(dsl::else_ >> dsl::p<expression>)
        //}();
        };
#if 0

        struct return_stmt_expr : lexy::expression_production {
            struct expected_operand { static constexpr auto name = "expected operand"; };

            struct return_expr : dsl::postfix_op {
                static constexpr auto op =
                    dsl::op(dsl::p<struct expression>);
                //dsl::op<>(
                //dsl::op<expression>();
                //dsl::p<struct expression>);
            //dsl::parenthesized.list(dsl::p<struct expression>, dsl::sep(dsl::comma)));
                using operand = dsl::atom;
            };
            static constexpr auto atom =
                LEXY_LIT("return")
                //>> dsl::p<expression>
                >> LEXY_LIT("__ENDLINE__");
            using operation = return_expr;
        };
#endif
        // ██████████████████████████████████████████
        constexpr auto identifier2 = dsl::identifier(dsl::ascii::alpha);
        struct base_type {
            static constexpr auto rule = [] { return
                dsl::capture(LEXY_KEYWORD("char", identifier2))
                | dsl::capture(LEXY_KEYWORD("int", identifier2))
                | dsl::capture(LEXY_KEYWORD("float", identifier2));
            }();
        };
        
        struct return_values { // example: (char, int, float)
            //static constexpr auto whitespace = dsl::ascii::blank;
            static constexpr auto rule = dsl::parenthesized.list(
                dsl::p<base_type>, dsl::sep(dsl::comma));
        };
        
        struct decl_ltr { // example: f:float
            //static constexpr auto whitespace = dsl::ascii::blank;
            //static constexpr auto rule = dsl::p<var_name> +LEXY_LIT(":") + dsl::p <base_type>;
            static constexpr auto rule = 
                dsl::p<identifier> +LEXY_LIT(":") + dsl::p <base_type>;
        };

        
        struct func_args { // example: (f:float, c:char, i: int)
            static constexpr auto rule = dsl::parenthesized.list(
                dsl::p<decl_ltr>, dsl::sep(dsl::comma));
        };

        struct func_signature {
            //static constexpr auto whitespace = dsl::ascii::blank;
            static constexpr auto whitespace = dsl::ascii::space;

            static constexpr auto rule =
                LEXY_LIT("func")
                + dsl::p<identifier>
                +dsl::p<func_args>
                //+ LEXY_LIT("->")
                +dsl::p<return_values>
                ;
        };

        struct func_decl {
            static constexpr auto whitespace = dsl::ascii::space;
            static constexpr auto rule =
                dsl::p<func_signature> +LEXY_LIT(":") + dsl::p<compound_stmt>;

        };

        // ██████████████████████████████████████████


        struct jump_stmt {
            static constexpr auto rule =
                dsl::p<continue_stmt>
                | dsl::p<break_stmt>
                //| dsl::p<return_stmt>
                | dsl::p<return_stmt_value>
                //| dsl::p<return_stmt_expr>
                //| dsl::error<expected_operand>
                //>> LEXY_LIT("__ENDLINE__")
                ;
        };

        // struct assignment_operator {
        //     static constexpr auto rule = dsl::literal_set(
        //         LEXY_LIT("="),
        //         LEXY_LIT("*="), LEXY_LIT("/="), LEXY_LIT("%="),
        //         LEXY_LIT("+="), LEXY_LIT("-="),
        //         LEXY_LIT(">>="), LEXY_LIT("<<="),
        //         LEXY_LIT("&="), LEXY_LIT("|="), LEXY_LIT("^=")
        //     );
        // };

        struct expression_stmt {
            static constexpr auto rule =
                dsl::p<expression> +LEXY_LIT("__ENDLINE__");
        };

        struct statement {
            static constexpr auto whitespace = dsl::ascii::space;
            static constexpr auto rule =
                dsl::p<compound_stmt>
                | dsl::p<if_stmt>
                | dsl::p<while_stmt>
                | dsl::p<for_stmt>
                | dsl::p<jump_stmt>
                | dsl::else_ >> dsl::p<expression_stmt>
                //| dsl::p<expression_stmt>
                ;
        };
    }
}

int main(int n, char* argv[])
{
    using namespace std;
    std::string input_filename;
    if (n == 2) {
        input_filename = std::string(argv[1]);
    }
    else if (n == 1) {
        input_filename = std::string("default_text.indented.nogit.txt");
    }
    else {
        std::cout << "only one argument" << std::endl;
    }

    std::ifstream ifs(input_filename);
    std::string indentized;

    if (ifs.is_open()) {
        indentized = std::string(
            (std::istreambuf_iterator<char>(ifs)),
            (std::istreambuf_iterator<char>()));
    }
    else {
        std::cout << "could not open " << input_filename << std::endl;
        return -1;
    }

    // lexy objects
    lexy::buffer<lexy::utf8_encoding> input(indentized);
    lexy::parse_tree_for<decltype(input)> tree;

    //lexy::parse_as_tree<grammar_clak::compound_stmt>(tree, input, lexy_ext::report_error);
    lexy::parse_as_tree<grammar_clak::func_decl>(tree, input, lexy_ext::report_error);

    // 3 different output formats
    std::ofstream of_json("parse_tree.nogit.json");
    std::ofstream of_raw("raw_tree.nogit.txt");
    std::ofstream of_tree_fancy("tree_fancy.nogit.txt");
    std::ofstream traceoutput("trace.nogit.txt");

    std::string str_for_fancy;
    std::string str_for_trace;

    lexy::trace_to<grammar_clak::compound_stmt>(
        std::back_inserter(str_for_trace), input
        // {lexy::visualize_fancy }
        );

    // lexy::visualize(std::back_inserter(str_for_fancy), tree, {lexy::visualize_fancy});

    lexy::visualize_to(std::back_inserter(str_for_fancy), tree,
        // {lexy::visualize_use_symbols | lexy::visualize_space});
        // {lexy::visualize_use_symbols | lexy::visualize_use_unicode,});
        {
            lexy::visualize_use_symbols
            | lexy::visualize_use_unicode
            | lexy::visualize_space
        });
    traceoutput << str_for_trace;
    of_tree_fancy << str_for_fancy;

    // hacky way of generate something that looks like json
    // each ast node will be an json object with a single key+val with key being the ast type
    // the val will just be an array of nodes and sub-trees
    int indent = 0;
    auto spaces = [](int indent) {return std::string(indent * 2, ' '); };


    for (auto [event, node] : tree.traverse()) {
        switch (event) {
        case lexy::traverse_event::enter: {
            of_json << spaces(indent)
                << "{ \""
                << node.kind().name()
                << "\": ["
                << std::endl;
            of_raw << "enter:" << node.kind().name() << std::endl;
            indent += 1;
            break;
        }
        case lexy::traverse_event::exit: {
            of_raw << spaces(indent)
                << "exit:"
                << node.kind().name() << std::endl;

            string comma_or_not = "] }";

            if (!node.is_last_child()) {
                comma_or_not += ',';
            }

            indent -= 1;
            of_json << spaces(indent)
                << comma_or_not
                << std::endl;
            break;
        }
        case lexy::traverse_event::leaf: {
            string comma_or_not = "\"";
            if (!node.is_last_child()) {
                comma_or_not += ',';
            }

            std::string s;
            lexy::visualize_to(
                std::back_inserter(s), node.lexeme());
            if (
                !node.is_last_child()
                && (s[0] == ' '
                    || s[0] == '\\'
                    || s[0] == '\n'
                    || s == "__INDENT__"
                    || s == "__ENDLINE__"
                    || s == "__DEDENT__"
                    || s == ":"
                    // || s== "\n"
                    // || s== " "
                    || s == ","
                    || s == "("
                    || s == ")"
                    )) break;
            of_raw << "leaf:" << s << std::endl;
            of_json << spaces(indent)
                << ("\"" + s + comma_or_not)
                << std::endl;
            break;
        }
        }
    }

    return  0;
}

