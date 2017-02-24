import code
import codeop
import parser
import argparse
import fractions


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

    def find_atoms(st):
        def f(node, path):
            if isinstance(node, list) and node[0] == atom_id:
                return node

        return filter(None, map_flat(st, f))

    def patch_literals(st):
        if isinstance(st, list) and st[0] == atom_id:
            if isinstance(st[1], list) and st[1][0] == number_id:
                replacement = parser.suite(
                    '(%s(%r))' % (CONSTRUCTOR_VAR, st[1][1]))
                st[:] = next(find_atoms(replacement.tolist()))
        elif isinstance(st, list):
            for c in st:
                patch_literals(c)

    return patch_literals


patch_literals = make_patch_literals()


class CommandCompiler(codeop.CommandCompiler):
    def __call__(self, source, filename="<input>", symbol="single"):
        assert symbol == 'single'
        code = super().__call__(source, filename)
        if code is not None:
            st = parser.suite(source).tolist()
            patch_literals(st)
            code = parser.sequence2st(st).compile(filename)
        return code


class InteractiveConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename='<console>'):
        if locals is None:
            locals = {}
        assert CONSTRUCTOR_VAR not in locals
        locals[CONSTRUCTOR_VAR] = fractions.Fraction
        super().__init__(locals, filename)
        self.compile = CommandCompiler()

    def runcode(self, code):
        try:
            res = exec(code, self.locals)
        except SystemExit:
            raise
        except:
            self.showtraceback()
        else:
            print(res)


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    local = banner = None
    console = InteractiveConsole(local)
    console.interact(banner)


if __name__ == "__main__":
    main()
