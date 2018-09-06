import stackcode
import collections
import sys
import os


# Grammar
#
# Program := Lines
# Lines := '' | Line '\n' Lines
# Line := [LabelSpec] [Statement] [Comment]
# LabelSpec := Labelname ':'
# Statement := Instruction [Value] [Target]
# Comment := ';' [CommentText]
#
# Labelname must be alphanumeric starting with alpha (identifier
# rules)
#
# Target can be a line number or a Labelname. Targets are resolved by
# the assembler.
#
# Comment is a string of any whitespace (excluding newlines),
# alphanumeric, or punctuation characters.
#
# Tokens are whitespace separated (excluding newlines). Beyond
# separating tokens whitespace is ignored.


WORDSIZE = 1
MINVALUE = 0
MAXVALUE = (0x1 << (8 * WORDSIZE)) - 1
SIGNED_MINVALUE = -(0x1 << (8*WORDSIZE - 1))
SIGNED_MAXVALUE = -SIGNED_MINVALUE - 1


keytable = {(stackcode.numargs(s), s.ASMkeyword): s for s in stackcode.specs}
codetable = {s.code: s for s in stackcode.specs}

ParsedLine = collections.namedtuple('ParsedLine', ['label', 'IC', 'arg1', 'arg2', 'comment'])  # TODO: change from (arg1, arg2) to (val, target)


class AssemblyException(Exception):
    """Exception during assembling"""


class ParseException(AssemblyException):
    """Parse Error"""


class TargetException(AssemblyException):
    """Target resolution error"""


class JumpTarget:
    pass


class LineNumber(int, JumpTarget):
    pass


class LabelName(str, JumpTarget):
    pass


class Literal(int):
    pass


def convert(atype, s):
    if atype is stackcode.ArgType.value:
        return convertLiteral(s)
    elif atype is stackcode.ArgType.target:
        return convertTarget(s)
    raise ParseException('Unknown Type')


def convertLiteral(literalstring):
    n = int(literalstring)
    if MINVALUE <= n <= MAXVALUE:
        return Literal(n)
    raise ParseException('Invalid Literal')


def convertTarget(targetstring):
    if targetstring.isidentifier():
        return LabelName(targetstring)
    # Line numbers shall be 1-indexed, since that seems the standard
    # in text editors, etc.
    return LineNumber(int(targetstring) - 1)


def signedtounsigned(num):
    return num & (0x1 << (8*WORDSIZE) - 1)


def locationtowords(num):
    """Takes a target location and returns list of words in little endian
    order."""
    wordlist = []

    if num == 0:
        wordlist.append(0)

    while num > 0:
        wordlist.append(num & 0xff)
        num >>= 8*WORDSIZE

    return wordlist


def tokenize(line):
    """Breaks line into pieces: (label, inst_spec, value_arg, target_arg, comment)"""
    # Assumes that there will never be an instruction that takes more
    # than one value_arg and one target_arg. This could change.
    commenttext = ''
    labelname = ''
    valarg = ''
    targetarg = ''
    spec = None

    lineparts = line.split(';')
    if len(lineparts) > 1:
        commenttext = ';'.join(lineparts[1:])
        commenttext = commenttext.strip()

    codetext = lineparts[0].strip()
    if ':' in codetext:
        labelname, statement = codetext.split(':')
        if not labelname.isidentifier():
            raise TargetException('Invalid label {}'.format(labelname))
    else:
        statement = codetext

    toks = statement.split()
    if toks:
        try:
            spec = keytable[len(toks) - 1, toks[0]]
        except KeyError:
            raise AssemblyException('Invalid Instruction or number of arguments: {}'.format(toks))

        if len(toks) == 3:
            valarg, targetarg = toks[1], toks[2]
        elif len(toks) == 2:
            if spec.atype1 is stackcode.ArgType.value:
                valarg = toks[1]
            else:
                targetarg = toks[1]

    return labelname, spec, valarg, targetarg, commenttext


def parseline(line):
    """Takes line, returns parsed_line, target

    labelname is left as a string
    inst_code is converted the parsed code point
    value arguments are converted to word-sized int
    line number arguments are converted to 0-indexed int
    label arguments are left as strings
    commenttext is left as a string

    """
    labelname, spec, valarg, targetarg, commenttext = tokenize(line)

    inst_code = None
    if spec:
        inst_code = spec.code

    target = None
    arg1, arg2 = None, None
    if targetarg:
        target = convertTarget(targetarg)

    if valarg != '':
        valarg = convertLiteral(valarg)
        arg1, arg2 = valarg, target
    else:
        arg1 = target

    return ParsedLine(labelname, inst_code, arg1, arg2, commenttext), target


# This should be tested!
def resolvejumps(jumps, linestowords):
    """Takes jumps as a list of line number (src, dest) pairs in src
    order, and an estimated listmap of IC word starts. Returns a map
    from dest line number to dest word position.
    """
    # in src order [(dest_line, cur_dest_budget)]
    # {dest_line: cur_dest_word}
    wordjumps = [(destline, 2) for _, destline in jumps]
    destmap = {destline: linestowords[destline] for _, destline in jumps}

    for j in range(len(wordjumps)):
        destline, curbudget = wordjumps[j]
        newbudget = len(locationtowords(destmap[destline])) + 1
        if newbudget == curbudget:
            continue

        shift = newbudget - curbudget
        wordjumps[j] = destline, newbudget
        for l2 in destmap:
            if l2 > destline:
                destmap[l2] += shift

    return destmap


def parsestream(fout):
    lines = []
    jumps = []
    pendinglabels = []
    labelmap = {}
    lastIC = keytable[0, 'nop'].code
    linestowords = []
    word_est = 0
    lineno = 0

    for line in fout:
        parsed_line, target = parseline(line)

        if parsed_line.label:
            # Wait until there is an actual instruction to assign label
            pendinglabels.append(parsed_line.label)

        linestowords.append(word_est)
        if parsed_line.IC is not None:
            lastIC = parsed_line.IC
            word_est += 1

            if pendinglabels:
                for label in pendinglabels:
                    if label in labelmap:
                        raise TargetException('Duplicate label: {}'.format(parsed_line.label))
                    labelmap[label] = lineno
                pendinglabels.clear()
            word_est += int(parsed_line.arg1 is not None) + int(parsed_line.arg2 is not None)
            if target is not None:  # 0 is a valid target
                word_est += 1  # extra for ENDMARK
                jumps.append((lineno, target))

        lines.append(parsed_line)
        lineno += 1

        # Handle implicit ret
    if lastIC != keytable[0, 'ret'].code:
        # Any unattached labels are attached to implicit 'ret'; this
        # may be questionable behavior.
        linestowords.append(word_est)
        word_est += 1
        if pendinglabels:
            for label in pendinglabels:
                if label in labelmap:
                    raise TargetException('Duplicate label: {}'.format(parsed_line.label))
                labelmap[label] = lineno
            pendinglabels.clear()
        lines.append(ParsedLine('', keytable[0, 'ret'].code, None, None, 'implicit ret added'))

    if pendinglabels:
        raise TargetException('Unattached Labels: {}'.format(pendinglabels))

    # jumps is a list of (occurance line number, dest label or line
    # number), e.g.: [(4, 'case0'), (10, 'case1'), (50, 23),
    #                 (75, 'cat'), (77, 0), (88, 'dog')]
    #
    # Resolve labelnames to line numbers and check line numbers
    for j in range(len(jumps)):
        src, dest = jumps[j]
        if isinstance(dest, LabelName):
            try:
                jumps[j] = (src, labelmap[dest])
            except KeyError:
                raise TargetException('Unknown jump destination: {}'.format(dest))
        elif dest >= len(lines) or dest < 0:
            raise TargetException('Invalid line number: {}'.format(dest))

    # Resolve line numbers to bytes
    destmap = resolvejumps(jumps, linestowords)

    codestream = []
    for l in lines:
        if l.IC is None:
            continue
        codestream.append(l.IC)
        codestream.extend(argtowords(l.arg1, labelmap, destmap))
        codestream.extend(argtowords(l.arg2, labelmap, destmap))
    return bytes(codestream)


# This should probably be refactored
def parsefile(fname):
    with open(fname) as fout:
        return parsestream(fout)


def argtowords(arg, labelmap, wordmap):
    if arg is None:
        return []
    if isinstance(arg, LabelName):
        arg = LineNumber(labelmap[arg])
    if isinstance(arg, LineNumber):
        return locationtowords(wordmap[arg]) + [stackcode.ENDMARK]
    return [int(arg)]


def assemble(fname, outname=''):
    if not outname:
        outname = os.path.splitext(fname)[0] + '.stk'
    outstring = parsefile(fname)
    with open(outname, 'wb') as fout:
        fout.write(outstring)


# Currently doesn't handle jump targets correctly.
def dis(bstring):
    """Dissassembles sasm byte string into list of human-readable instructions"""
    biter = iter(bstring)
    lines = []
    args = []
    while True:
        try:
            ins_code = next(biter)
        except StopIteration:
            break
        spec = codetable[ins_code]
        args.clear()
        for atype in (spec.atype1, spec.atype2):
            if not atype:
                continue
            try:
                args.append(str(next(biter)))
            except StopIteration:
                raise AssemblyException('Missing arguments')
        lines.append(' '.join([spec.ASMkeyword, *args]))

    return '\n'.join(lines)


def main(argv=[]):
    for fname in argv[1:]:
        assemble(fname)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
