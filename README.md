
Stack
=====

Splashing around in the Turing tarpit...

This is a stack machine emulator and assembler. The motivation is to
have a simple imperative turing complete language to explore automated
code search/generation. The instruction set architecture is
intentionally extremely tiny. Human usage of the stack assembly language
is contraindicated.

Basic Usage
-----------

The assembler is currently written in python 3:

    $ cd sasm
    $ python3 sasm.py ../examples/not.sasm

After the above, the virtual stack machine can be run as:

    $ cd ../machine
    $ ./stackvm ../examples/not.stk 13 42

Exit status and data stack are displayed on `stdout`.

For more details see `NOTES.md`.

References/Inspiration/Related Stuff
------------------------------------

You may be better served by looking at:

 * [Stack Machine](https://en.wikipedia.org/wiki/Stack_machine) wikipedia entry
 * [Stack VM Tutorials](https://github.com/pbohun/stack-vm-tutorials)
 * [Push](http://faculty.hampshire.edu/lspector/push.html) programming
   language for genetic programming.
 * Java virtual machine specification.
 * The [Forth](https://en.wikipedia.org/wiki/Forth_(programming_language)) programming language.
