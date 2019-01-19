# helper.py

###########################################################################
## Copied from:
## https://github.com/fpoli/python-astexport/blob/master/astexport/export.py
## LICENSE: https://github.com/fpoli/python-astexport/blob/master/LICENSE
##
# The MIT License
#
# Copyright (c) 2015, Federico Poli <federpoli@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import ast
import json

def export_json(tree, pretty_print=False):
    assert(isinstance(tree, ast.AST))
    return json.dumps(
        export_dict(tree),
        indent=4 if pretty_print else None,
        sort_keys=True,
        separators=(",", ": ") if pretty_print else (",", ":")
    )


def export_dict(tree):
    assert(isinstance(tree, ast.AST))
    return DictExportVisitor().visit(tree)


class DictExportVisitor:
    ast_type_field = "ast_type"

    def visit(self, node):
        node_type = node.__class__.__name__
        meth = getattr(self, "visit_" + node_type, self.default_visit)
        return meth(node)

    def default_visit(self, node):
        node_type = node.__class__.__name__
        # Add node type
        args = {
            self.ast_type_field: node_type
        }
        # Visit fields
        for field in node._fields:
            assert field != self.ast_type_field
            meth = getattr(
                self, "visit_field_" + node_type + "_" + field,
                self.default_visit_field
            )
            args[field] = meth(getattr(node, field))
        # Visit attributes
        for attr in node._attributes:
            assert attr != self.ast_type_field
            meth = getattr(
                self, "visit_attribute_" + node_type + "_" + attr,
                self.default_visit_field
            )
            # Use None as default when lineno/col_offset are not set
            args[attr] = meth(getattr(node, attr, None))
        return args

    def default_visit_field(self, val):
        if isinstance(val, ast.AST):
            return self.visit(val)
        elif isinstance(val, list) or isinstance(val, tuple):
            return [self.visit(x) for x in val]
        else:
            return val

    # Special visitors

    def visit_str(self, val):
        return str(val)

    def visit_Bytes(self, val):
        return str(val.s)

    def visit_NoneType(self, val):
        return None

    def visit_field_NameConstant_value(self, val):
        return str(val)

    def visit_field_Num_n(self, val):
        if isinstance(val, int):
            return {
                self.ast_type_field: "int",
                "n": val,
                # JavaScript integers are limited to 2**53 - 1 bits,
                # so we add a string representation of the integer
                "n_str": str(val),
            }
        elif isinstance(val, float):
            return {
                self.ast_type_field: "float",
                "n": val
            }
        elif isinstance(val, complex):
            return {
                self.ast_type_field: "complex",
                "n": val.real,
                "i": val.imag
            }

###########################################################################

import sys

print(export_json(ast.parse(sys.argv[1]), pretty_print=True))
