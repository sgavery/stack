
## Stack

### The "machine"

We imagine a stack machine with the following components:
1. random-access read-only instruction memory
2. instruction pointer register, pointing to instruction memory, we
   shall assume this register is always big enough for our program;
   it's serialization onto the call stack is described below.
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
to be integers of a fixed word size to be specified. At the most
primitive level, we may consider unsigned 8-bit integers, single bytes
with mod-256 arithmetic; whereas, for greater concordance with the
underlying machine CPU architecture and expressiveness, we may
consider 32 or 64 bit signed integers.

The instruction and jump targets shall be absolute; this would limit
jump distance. Instead, we use an unlimited addressing system. The
location in machine memory is specified in little endian fashion,
starting with the least significant byte, then there is an `ENDMARK`,
`0x0`, which signifies the end of the address. This simplifies the
assembler process and seems straightforward to implement; without
making program size limits sharply related to word size.

Additional types, like floats, can either be treated in terms of type
conversions to unsigned integers; or, by adding an additional
stack. Depends how much type-safety we want. In principle, we could
even introduce a boolean stack, that `jmpif` pops from... I think for
now, we shall bask in the full freedom of living without types. One
could even move the instructions onto a stack as well, but I wanted an
imperative language that is close to actual assembly and most
traditionally successful programming languages.


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
 - `push value`: push literal `value` onto stack
 - `inc`: adds 1 to top element of stack
 - `dec`: subtracts 1 from top element of stack
 - `jumpif value n`: pop data stack, if it equals literal `value`, jump to offset `n`, otherwise continue
 - `ret`: current value(s) on top of data stack are taken as output,
   if call stack is empty end program, otherwise jump to instruction
   on call stack.
 - `call n`: increments instruction pointer and pushes it onto call
   stack, then places `n` into instruction register, and continues
   execution there.

Extended instructions:
 - comparisons: `<`, `>`, `>=`, `<=`, `==`
 - control: `jumpifnot`, `goto`, `longjump`
 - arithmetic: `add`, `sub`, `mul`, `div`, `exp`
 - bitwise: `|`, `^`, `&`, `~`, `<<`, `>>`
 - floating point arithmetic
 - memory access
 - peripheral access
 - IO

For human use we could make a dramatically more powerful language by
adding higher level code manipulation. This would be more for human
use.

Meta extensions:
 - control: `label`
 - definitions: `procedure`, `extension`, `define`
 - modules, libraries, namespaces

### Examples

## Reverse

let's define a procedure that pushes the top element of the stack down
to the kth item. In psuedo-code, it looks something like:

    def pushdown(k):
       if k == 0:
          ret
       if k == 1:
          swap
          ret
       else:
          swap
          pop
          pushdown(k-1)
          push
          ret

which we can translate into

    ;; pushdown
    ; expects
    ; k, number of items to push down the top element on top of data stack, followed by
    ; at least k items
    ;
    0: dup           ; so we don't lose k
    1: jumpif 0 13
    2: dup
    3: jumpif 1 15
    4: dec           ; set up call recursive call with k-1
    5: pop           ; (k - 1) onto call stack
    6: swap          ; swap top two elements of the data
    7: push          ; push (k - 1) back onto data
    8: swap          ; now data top of stack looks like [2], (k-1), [1], [3]
    9: pop           ; put [2] onto call stack to save for after recursion
    10: call 0       ; pushdown(k - 1)
    11: push         ; put [2] back onto data stack
    12: ret
    13: drop         ; handle k=0 case
    14: ret
    15: drop         ; handle k=1 case
    16: swap
    17: ret

Now we can implement reverse in psuedo-code as

    def reverse(k):
       if k == 0:
          ret
       else:
          pop
          reverse(k-1)
          push
          pushdown(k)
          ret

which we can translate to

    0: dup
    1: jumpif 0 13      ; if k == 0, finish up
    2: dup              ; put a second copy of k onto stack to save for later
    3: dec              ; k-1, k, [0], ...
    4: swap             ; k, k-1, [0], ...
    5: pop              ; k-1, [0], ...
    6: swap             ; [0], k-1, ...
    7: pop              ; k-1, ...
    8: call 0           ; reverse(k - 1)
    9: push             ; [0], reverse(...)
    10: push            ; k, [0], reverse(...)
    11: call [pushdown] ; pushdown(k)
    12: ret
    13: drop            ; drop k from stack and done
    14: ret

## Not

    0: jumpif 0 3
    1: push 0
    2: ret
    3: push 1
    4: ret

## Less-than

Let's write a procedure that takes two arguments and returns 1 (true)
if the first (top) argument is less than the second; otherwise returns
0 (false). This assumes values are all positive!

    [<]:
    swap
    dup
    jumpif 0 [R0]    ; if second argument is 0 then return false
    dec
    swap
    dup
    jumpif 0 [R1]    ; second argument was non-zero, and first argument is 0; return true
    dec
    push 0           ; these two lines give an unconditional jump
    jumpif 0 [<]     ; this is tail-call optimization

    [R0]:
    drop
    drop
    push 0
    ret

    [R1]:
    drop
    drop
    push 1
    ret

## Add

Let's write a procedure to add two arguments.

    [add]:
    swap
    dup             ; check if second argument is zero
    jumpif 0 [R1]
    swap

    [add2]:
    dup             ; check if first argument is zero
    jumpif 0 [R1]
    dec             ; decrement first argument
    pop
    inc             ; increment second argument
    push
    push 0
    jumpif 0 [add2]  ; add(m, n) -> add(m - 1, n + 1)

    [R1]:
    drop
    ret



## Increment

Let us start with single-bit values, in which case `inc` and `dec`
have same effect. Let us see if we can write code to add one to the
binary number on the input stack.

As a warm up, let's write a procedure to add (mod 2) two bits:

00 -> 0
01 -> 1
10 -> 1
11 -> 0

    0: jumpif 0 2
    1: inc
    2: ret

Now we need to be able to and two bits to compute the carry bit:

00 -> 0
01 -> 0
10 -> 0
11 -> 1

    0: jumpif 0 4
    1: jumpif 1 5
    2: push 1
    3: ret
    4: drop
    5: push 0
    6: ret

### Design Decisions

 - should `jumpif` consume an entry off the stack?
 - for machine code, make jumps relative in word size so that program
   size is not limited by word size
 - Goedel number using sasm with line-number targets
 - assembler is responsible for managing and checking targets; if
   targets are more than a single jump away, then assembler should do
   arrange for multiple jumps.
 - assembler will insert an implicit `ret` at the end of the program,
   if missing.
 - Put target labels and other debugging/disassembling metadata at end
   of binary.
 - We could make the machine have some default behavior for empty
   stacks, etc.; but, I would rather thow an Exception. Even if we did
   make all programs run, we would still have the halting problem to
   contend with.
 - Stack Machine should keep track of number of steps of execution,
   and accept limits before "timing out".
 - Note: it could be fun to consider a code stack instead of RAM
   program, but this would be harder to relate to standard/traditional
   human programming.
 - should `goto` be in the basic instruction set, or `call`?
 - how should we handle "long jumps"?
