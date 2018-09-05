
import collections

SPECIFICATIONFILE = '../specs.tsv'


def generate(fname=SPECIFICATIONFILE):
    with open(fname) as fin:
        rows = fin.read().splitlines()

    keys = rows[0].split('\t')
    Spec = collections.namedtuple('Spec', keys)
    enum_text = 'enum class ICs {\n'

    for row in rows[1:]:
        if row:
            s = Spec(*row.split('\t'))
            enum_text += '  {} = {},\n'.format(s.name, s.code)

    enum_text += '};'

    return enum_text


if __name__ == '__main__':
    print(generate())
