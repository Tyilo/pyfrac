import code
import codeop
import parser
import argparse
import fractions
import itertools


CONSTRUCTOR_VAR = '_F'


def parse(source, filename, symbol):
    PyCF_DONT_IMPLY_DEDENT = 0x200          # Matches pythonrun.h
    from ast import PyCF_ONLY_AST
    flags = PyCF_DONT_IMPLY_DEDENT | PyCF_ONLY_AST
    return compile(source, filename, symbol, flags)


def map_flat(st, f):
    path = []

    def visit(node):
        yield f(node, path)
        if isinstance(node, list):
            path.append(node)
            for c in node:
                yield from visit(c)
            path.pop()

    return visit(st)


def get_atom_and_number_id():
    st = parser.suite('1').tolist()
    it = map_flat(st, lambda node, path: node == '1' and path[-2])
    atom, = filter(None, it)
    (atom_id, (number_id, number)) = atom
    return atom_id, number_id


def make_patch_literals():
    atom_id, number_id = get_atom_and_number_id()

    def find_numbers(st):
        def f(node, path):
            if isinstance(node, list) and node[0] == number_id:
                return node

        return filter(None, map_flat(st, f))

    def patch_literals(source):
        lines = source.splitlines(True)
        st = parser.suite(source).tolist(True, True)
        numbers = find_numbers(st)
        groups = itertools.groupby(numbers, key=lambda n: n[2])
        line_i = 0
        output_lines = []
        for lineno, group in groups:
            line_j = lineno - 1
            output_lines += lines[line_i:line_j]
            line_i = line_j + 1

            col_i = 0
            line = lines[line_j]
            output_line = []
            for _n, lit, _lineno, col in group:
                assert _n == number_id
                assert _lineno == lineno
                assert line[col:col+len(lit)] == lit
                col_j = col
                output_line.append(line[col_i:col_j])
                col_i = col_j + len(lit)

                output_line.append('(%s(%r))' % (CONSTRUCTOR_VAR, lit))
            output_line.append(line[col_i:])
            output_lines.append(''.join(output_line))
        return ''.join(output_lines)

    return patch_literals


patch_literals = make_patch_literals()


class CommandCompiler(codeop.CommandCompiler):
    def __call__(self, source, filename="<input>", symbol="single"):
        assert symbol == 'single'
        code = super().__call__(source, filename)
        if code is not None:
            source = patch_literals(source)
            code = super().__call__(source, filename)
        return code


class InteractiveConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename='<console>'):
        if locals is None:
            locals = {}
        assert CONSTRUCTOR_VAR not in locals
        locals[CONSTRUCTOR_VAR] = fractions.Fraction
        super().__init__(locals, filename)
        self.compile = CommandCompiler()


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    local = banner = None
    console = InteractiveConsole(local)
    console.interact(banner)


if __name__ == "__main__":
    main()
