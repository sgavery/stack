#!/usr/bin/env python3

import sys
import sasm


LABELWIDTH = 10
INSTRUCTIONWIDTH = 7
VALWIDTH = 3
TARGETWIDTH = LABELWIDTH

linetemplate = ('{label:<' + str(LABELWIDTH) + '} {inst_name:<' + str(INSTRUCTIONWIDTH) +
                '} {valarg:<' + str(VALWIDTH) + '} {targetarg:<' + str(TARGETWIDTH) +
                '} {comment}')


def formatline(line):
    labelname, spec, valarg, tararg, commenttext = sasm.tokenize(line)

    label = labelname + ':' if labelname else ''
    comment = ''
    if commenttext:
        if commenttext.startswith(';'):
            comment = ';' + commenttext
        else:
            comment = '; ' + commenttext

    inst_name = spec.ASMkeyword if spec else ''
    return linetemplate.format(label=label,
                               inst_name=inst_name,
                               valarg=valarg,
                               targetarg=tararg,
                               comment=comment).rstrip()


def autoformat(fname):
    with open(fname) as fin:
        lines = [formatline(line) for line in fin]
    with open(fname, 'w') as fout:
        fout.write('\n'.join(lines))


def main(argv):
    if len(argv) < 2:
        print('Usage...')
        return 0

    for fname in argv[1:]:
        print('Formatting ', fname, '...', end='')
        autoformat(fname)
        print(' done.')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
