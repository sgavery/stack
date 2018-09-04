# stackcode.py

import collections
import enum

SPECIFICATIONFILE = '../specs.tsv'


class ArgType(enum.Enum):
    value = 'value'
    target = 'target'

    @classmethod
    def classify(cls, s):
        if s == 'val':
            return cls.value
        if s == 'tar':
            return cls.target
        return None


def readspecs(fname):
    with open(fname) as fin:
        rows = fin.read().splitlines()
    specs = []
    keys = rows[0].split('\t')
    Spec = collections.namedtuple('Spec', keys)

    for row in rows[1:]:
        if row:
            entries = row.split('\t')
            for j, k in enumerate(keys):
                if k == 'code':
                    entries[j] = int(entries[j], 16)
                elif k in ('atype1', 'atype2'):
                    entries[j] = ArgType.classify(entries[j])
                elif k in ('consumes', 'returns'):
                    entries[j] = int(entries[j])
            specs.append(Spec(*entries))

    return specs


def numargs(s):
    return int(bool(s.atype1)) + int(bool(s.atype2))


specs = readspecs(SPECIFICATIONFILE)
nullary_ops = list(filter(lambda s: numargs(s) == 0, specs))
unary_ops = list(filter(lambda s: numargs(s) == 1, specs))
binary_ops = list(filter(lambda s: numargs(s) == 2, specs))
ENDMARK = [s.code for s in nullary_ops if s.name == 'ENDMARK'][0]
