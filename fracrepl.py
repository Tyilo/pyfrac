import sys
import code
import codeop
import parser
import argparse
import readline
import fractions
import itertools


CONSTRUCTOR_VAR = '_F'


def factor_bases(n, *bases):
    for b in bases:
        exp = 0
        q, r = divmod(n, b)
        while q > 0 and r == 0:
            n = q
            exp += 1
            q, r = divmod(n, b)
        yield exp
    yield n


def display_hook(v=None):
    if v is None:
        pass
    if isinstance(v, fractions.Fraction):
        if v.denominator == 1:
            print(v.numerator)
        else:
            fives, twos, rest = factor_bases(v.denominator, 5, 2)
            assert v.denominator == rest * 2**twos * 5**fives
            if rest == 1:
                tens = max(fives, twos)
                whole = v * 10 ** tens
                assert whole.denominator == 1
                s = str(whole.numerator).rjust(tens, '0')
                s = (s[:-tens] or '0') + '.' + s[-tens:].rstrip('0')
                assert fractions.Fraction(s) == v
                print(s)
            else:
                print('%s \N{ALMOST EQUAL TO} %s' % (v, float(v)))
    elif isinstance(v, float):
        print('float(%r)' % v)
    else:
        print(repr(v))


sys.displayhook = display_hook


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


def replace_atoms(source, atoms, repl):
    '''
    Replace given atoms in given Python source code using given function.
    atoms: Iterable of 4-tuples (n, s, lineno, col) sorted on (lineno, col).
    repl: Function accepting (n, s) and returning a replacement string.
    '''

    lines = source.splitlines(True)
    groups = itertools.groupby(atoms, key=lambda n: n[2])
    line_i = 0
    output = []
    for lineno, group in groups:
        line_j = lineno - 1
        output += lines[line_i:line_j]
        line_i = line_j + 1

        col_i = 0
        line = lines[line_j]
        for node_type, lit, _lineno, col in group:
            assert _lineno == lineno
            assert line[col:col+len(lit)] == lit
            col_j = col
            output.append(line[col_i:col_j])
            col_i = col_j + len(lit)

            output.append(repl(node_type, lit))
        output.append(line[col_i:])
    output += lines[line_i:]
    return ''.join(output)


def make_patch_literals():
    atom_id, number_id = get_atom_and_number_id()

    def find_numbers(st):
        def f(node, path):
            if isinstance(node, list) and node[0] == number_id:
                return node

        return filter(None, map_flat(st, f))

    def patch_literals(source):
        st = parser.suite(source).tolist(True, True)
        numbers = find_numbers(st)

        def repl(node_type, literal):
            assert node_type == number_id
            return '(%s(%r))' % (CONSTRUCTOR_VAR, literal)

        return replace_atoms(source, numbers, repl)

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


class FractionalInteractiveConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename='<console>'):
        if locals is None:
            locals = {}
        assert CONSTRUCTOR_VAR not in locals
        locals[CONSTRUCTOR_VAR] = fractions.Fraction
        super().__init__(locals, filename)
        self.compile = CommandCompiler()


def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()

    local = banner = None
    console = FractionalInteractiveConsole(local)
    console.interact(banner)


if __name__ == "__main__":
    main()
