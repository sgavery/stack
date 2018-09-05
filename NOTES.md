
## Stack

### The "machine"

We imagine a stack machine with the following components:
1. random-access read-only instruction memory
2. instruction pointer register, pointing to instruction memory, we
   shall assume this register is always big enough for our program;
   its serialization onto the call stack is described below.
3. data stack of fixed word size
4. call stack of same fixed word size

Program and input are loaded with the following initialization:
1. program code is loaded into memory as an array of *instructions*
2. input is placed on top of data stack
3. instruction pointer register is initialized to offset 0 of the program

Code execution follows the instruction pointer until a top-level
return is reached. Upon which, the value of the top of the data stack
is taken as the output.

A well-behaved procedure should never over-pop the data or call
stacks, and should not leave anything extra on the call stack. This
means that we can easily combine programs into more complicated
procedures. We need only add a `ret` to the last line of the program
if it isn't there, and change the semantics depending on whether the
call stack is empty or not. If the call stack is non-empty `ret` pops
the next instruction off the call stack into the instruction register
and execution continues there.

The *values* on the stack will be some fixed data type, which we take
to be integers of a fixed word size to be specified. We use unsigned
8-bit integers, single bytes with mod-256 arithmetic; whereas, for
greater concordance with the underlying machine CPU architecture and
expressiveness, we may consider 32 or 64 bit signed integers in the
future.

The instruction and jump targets shall be absolute; this could
severely limit jump distance and therefore program size, if we do not
allow for multi-word addresses. Instead, we use an unlimited
addressing system. The location in machine memory is specified in
little endian fashion, starting with the least significant byte, then
there is an `ENDMARK`, `0x0`, which signifies the end of the
address. This simplifies the assembler process and seems
straightforward to implement; without making program size limits
sharply related to word size. This serialization of the address is
used to push and pop addresses off of the stack. Note that currently
the underlying stack machine emulator implements the address as `long`
integers.

Additional types, like floats, can either be treated in terms of type
conversions to/from unsigned integers; or, by adding additional
stacks. How much type-safety is desired influences the design
decision. In principle, we could even introduce a boolean stack, that
`jmpif` pops from... I think for now, we shall bask in the full
freedom of living without types. One could even move the instructions
onto an instruction stack as well, but I wanted an imperative language
that is close to actual assembly and most traditionally successful
programming languages.


### Instructions

Let us start with the following basic instructions. These are
sufficient to build up all a complete set of procedures without too
much fuss:
 - `nop`: do nothing
 - `drop`: discards top element of data stack
 - `pop`: pops top element of data stack, and pushes onto call stack
 - `dup`: duplicate top element of stack
 - `swap`: swap top two elements of stack
 - `push`: pops top element off of call stack, and pushes onto data stack
 - `push <value>`: push literal `value` onto stack
 - `inc`: adds 1 to top element of stack
 - `dec`: subtracts 1 from top element of stack
 - `jumpif <value> <n>`: pop data stack, if it equals literal `value`, jump to offset `n`, otherwise continue
 - `ret`: current value(s) on top of data stack are taken as output,
   if call stack is empty end program, otherwise jump to instruction
   on call stack.
 - `call n`: increments instruction pointer and pushes it onto call
   stack, then places `n` into instruction register, and continues
   execution there.

Extended instructions:
 - comparisons: `<`, `>`, `>=`, `<=`, `==`
 - control: `jumpifnot`, `goto`
 - arithmetic: `add`, `sub`, `mul`, `div`, `exp`
 - bitwise: `|`, `^`, `&`, `~`, `<<`, `>>`
 - floating point arithmetic
 - memory access
 - peripheral access
 - IO

For human use we could make a dramatically more powerful language by
adding higher level code manipulation. This would be more for human
use.

Meta/assembler extensions:
 - definitions: `procedure`, `extension`, `define`
 - modules, libraries, namespaces: note that currently labels meant
   for outside use start with a capital letter.

### Examples

See `./examples/`.

### Design Decisions

 - Goedel number using sasm with line-number targets
 - assembler will insert an implicit `ret` at the end of the program,
   if missing.
 - Put target labels and other debugging/disassembling metadata at end
   of binary.
 - We could make the machine have some default behavior for empty
   stacks, etc.; but, I would rather thow an Exception. Even if we did
   make all programs run, we would still have the halting problem to
   contend with. Programs that do not respect the stack, will behave
   poorly when composed into larger programs.
 - Currently the machine enforces call stack integrity. This is
   stronger requirement than actual assembly, but when searching in
   space of programs should lead to more structured code.
 - Stack Machine should keep track of number of steps of execution,
   and accept limits before "timing out".
 - Note: it could be fun to consider a code stack instead of RAM
   program, but this would be harder to relate to standard/traditional
   human programming.
 - should `goto` be in the basic instruction set, or `call`?

