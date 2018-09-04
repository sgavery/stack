#ifndef STACKVM_HPP
#define STACKVM_HPP

#include <vector>
#include <iostream>

#include "instcodes.hpp"

typedef std::vector<word>::size_type ip_type;

enum class ExitStatus {
    ok = 0,
    error,
    maxsteps,
    user,
};

// template <typename word>
class StackVM {
private:
    std::vector<word> pmemory;

    // Instruction Pointer
    ip_type ip = 0;

    // current instruction code
    ICs ic = ICs::NOP;
    // current value argument
    word value = 0;
    // current target argument
    ip_type target = 0;
    long steps = 0;

    std::vector<word> call;
    std::vector<word> data;

    bool done = true;
    ExitStatus exitstatus = ExitStatus::ok;

    // If true program stops running if invalid state is attempted,
    // eg.: invalid jump target, pop empty
    bool strict = true;

    // Internal tracking of call level to enforce call stack integrity.
    std::vector<ip_type> call_levels;

    // Private methods:
    // Loads instruction starting at `ip` in `pmemory` into (`ic`, `value`, `target`).
    void fetch();

    // Execute currently loaded instruction.
    bool execute();

    // Drop top of data stack.
    bool drop();

    // Pops top of data stack onto top of call stack.
    bool pop();

    // Pushes another copy of the top of the data stack.
    bool dup();

    // Swap top two elements of the data stack.
    bool swap();

    // Pop top of call stack onto top of data stack.
    bool push();

    // Push literal value onto data stack.
    void pushvalue(word val);

    // Increment top of the data stack.
    bool inc();

    // Decrement top of the data stack.
    bool dec();

    // Pop top of data stack, if equals `testval`, jump to `tar`, otherwise nothing.
    bool jumpif(word testval, ip_type tar);

    // Set `ip` so that `tar` executes next.
    void vm_goto(ip_type tar);

    // Push current `ip` onto call stack, then continue execution at `target`.
    void call_proc(ip_type tar);

    // If call stack is empty, `halt` execution of program; otherwise,
    // popaddress off call stack, and continue execution there.
    bool ret();

    // Pop full ENDMARKed address off of call stack into
    // `target`. Returns false if call stack is empty, no ENDMARK
    // found, or invalid address.
    bool popaddress();

    // Convert address into words, and push ENDMARK followed by
    // address in "most significant word first" order onto call
    // stack. Returns false if invalid target address.
    bool pushaddress(ip_type tar);

public:
    // Construct Stack Machine
    StackVM();

    // Load program into Stack Machine memory
    void loadprogram(std::vector<word> progdata);

    // Set the data stack
    void setdata(std::vector<word> inputdata);

    // Get data stack
    std::vector<word> getdata();

    // Reset machine
    void reset();

    // Start machine
    void run(long maxsteps=-1);

    // Get Exit status
    ExitStatus getstatus();

    // Take execution step
    void step();

    // Stop machine
    void halt();

    // Load machine state
    void loadstate(std::istream sin);

    // Save machine state, to be restored later
    void savestate(std::ostream sout);
};

#endif
