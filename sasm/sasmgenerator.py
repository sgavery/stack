# sasmgenerator.py

import itertools

import sasm
from sasm import MINVALUE, MAXVALUE
from stackcode import specs, ArgType
from autoformat import linetemplate


OPSTOGENERATE = ['DROP', 'POP', 'DUP', 'SWAP', 'PUSH', 'INC', 'DEC', 'RET',
                 'PUSHVAL', 'CALL', 'JMPIF']

spectable = {s.name: s for s in specs}


def expand_op(opname, numlines):
    s = spectable[opname]
    valargs = range(MINVALUE, MAXVALUE + 1)
    tarargs = range(1, numlines + 1)
    if s.atype1 is None:
        valargs = ['']
        tarargs = ['']
    elif s.atype2 is None:
        if s.atype1 is ArgType.target:
            valargs = ['']
        else:
            tarargs = ['']
    return [(s.ASMkeyword, valarg, tararg) for valarg in valargs for tararg in tarargs]


def generateline(expandedop, lineno):
    return linetemplate.format(label='L' + str(lineno) + ':',
                               inst_name=expandedop[0],
                               valarg=expandedop[1],
                               targetarg=expandedop[2],
                               comment='').rstrip()


def printprograms(numlines):
    allops = itertools.chain(*(expand_op(opname, numlines) for opname in OPSTOGENERATE))
    allprograms = itertools.product(allops, repeat=numlines)
    for prog in allprograms:
        print('\n'.join(generateline(eop, n + 1) for n, eop in enumerate(prog)))
        print()


def printbins(numlines):
    allops = itertools.chain(*(expand_op(opname, numlines) for opname in OPSTOGENERATE))
    allprograms = itertools.product(allops, repeat=numlines)
    for prog in allprograms:
        progtext = '\n'.join(generateline(eop, n + 1) for n, eop in enumerate(prog))
        print(progtext)
        print(sasm.parsestream(progtext.splitlines()))
        print()
