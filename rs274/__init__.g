#    This is a component of AXIS, a front-end for emc
#    Copyright 2004 Jeff Epler <jepler@unpythonic.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from rs274_ import *
from interpret import ArcsToSegmentsMixin, PrintCanon, execute_code, Interpreter, display_code
%%
parser Rs274:
    option: "use-new-regexps"
    ignore: "[ \r\t%]"
    token eof: "(?!.)"
    token mid_line_letter: "[abcdfghijklmpqrstxyz]"
    token comment: "\([ \t!-'*-~]*\)"
    token real_number: "[-+]?([0-9]+(\.[0-9]*)?|\.[0-9]+)"
    token digits: "[0-9]+"
    token endofline: "\n"
    token unary_op: '-|abs|acos|asin|cos|exp|fix|fup|ln|round|sin|sqrt|tan'
    token arith_op: "[-+]|and|or|xor"
    token term_op: "[/*]|mod"
    token pow_op: "[*][*]"
    token parameter_: "#[0-9]+"

    rule display: lines                   -> << display_code(lines) >>
    rule lines: line line_tail            -> << [line] + line_tail >>
    rule line_tail: eof                   -> << [] >>
        | line line_tail                  -> << [line] + line_tail >>

    rule line:
        "/" opt_lineno segments endofline -> << Deleted(opt_lineno, segments) >>
        | opt_lineno segments endofline   -> << Normal(opt_lineno, segments) >>

    rule opt_lineno:                      -> << None >>
        | "[Nn]" digits                   -> << int(digits) >>

    rule segments:                        -> << [] >>
        | segment segments                -> << [segment] + segments >>

    rule segment: mid_line_word           -> <<mid_line_word>>
        | comment                         -> <<Comment(comment[1:-1])>>
        | parameter_setting               -> <<parameter_setting>>

    rule mid_line_word: mid_line_letter real_value
                                          -> << mid_line_letter, real_value >>
 
    rule real_value: real_number          -> << float(real_number) >>
        | expression                      -> << expression >>
        | unary_combo                     -> << unary_combo >>
        | parameter                       -> << parameter >>

    rule expression: '\\[' arith_expr '\\]' -> <<Expression(arith_expr)>>

    rule arith_expr: term opt_arith_rhs<<term>>
                                          -> << opt_arith_rhs >>
    rule opt_arith_rhs<<lhs>>:            -> << lhs >>
        | arith_op term opt_arith_rhs<<BinOp(arith_op,lhs,term)>>
                                          -> << opt_arith_rhs >>

    rule term: pow opt_term_rhs<<pow>>    -> << opt_term_rhs >>
    rule opt_term_rhs<<lhs>>:             -> << lhs >>
        | term_op pow                     -> << BinOp(term_op, lhs, pow) >>

    rule pow:  real_value opt_pow_rhs<<real_value>> -> << opt_pow_rhs >>
    rule opt_pow_rhs<<lhs>>:              -> << lhs >>
        | pow_op real_value               -> << BinOp("**", lhs, real_value) >>

    rule unary_combo: "atan" expression opt_atan_rhs<<expression>>
                                          -> << opt_atan_rhs >>
        | unary_op expression             -> << UnOp(unary_op, expression) >>
    rule opt_atan_rhs<<lhs>>:             -> << UnOp("atan", lhs) >>
        | "/" expression                  -> << BinOp("atan",lhs,expression) >>

    rule parameter: "#" real_value        -> << Parameter(real_value) >>
    rule parameter_setting:
        parameter "=" real_value          -> << Let(parameter, real_value) >>
        
%%
# vim:sw=4:sts=4:et:
