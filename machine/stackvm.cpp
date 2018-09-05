
#include <iostream>
#include <iomanip>
#include <string>

#include "stackvm.hpp"
#include "instcodes.hpp"

constexpr auto initial_memory_size = 1000000;

StackVM::StackVM() {
    pmemory.reserve(initial_memory_size);
}

// public methods

void StackVM::loadprogram(std::vector<word> progdata) {
    pmemory.clear();
    pmemory.reserve(progdata.size());
    pmemory.insert(std::begin(pmemory), std::begin(progdata), std::end(progdata));
}


void StackVM::setdata(std::vector<word> inputdata) {
    data = inputdata;
}

std::vector<word> StackVM::getdata() {
    return data;
}

void StackVM::reset() {
    data.clear();
    call.clear();
    call_levels.clear();
    ip = 0;
}

void StackVM::halt() {
    exitstatus = ExitStatus::user;
}

void StackVM::run(long maxsteps) {
    done = false;
    call_levels.push_back(0);

    while (!done) {
        if (maxsteps != -1 && steps >= maxsteps) {
            exitstatus = ExitStatus::maxsteps;
            break;
        }
        step();
        if (exitstatus != ExitStatus::ok) {
            break;
        }
    }

}

void StackVM::step() {
    fetch();
    auto ok = execute();
    steps++;

    if (strict && !ok) {
        exitstatus = ExitStatus::error;
    }
}

ExitStatus StackVM::getstatus() {
    return exitstatus;
}

void StackVM::loadstate(std::istream sin) {
}

void StackVM::savestate(std::ostream sout) {
}

// private methods
void StackVM::fetch() {
    // Fetch ic, target, value from pmemory starting at instruction
    // pointer ip; ip points at last word of instruction combined with
    // arguments. (Next instruction should start at ip.)

    ic = static_cast<ICs>(pmemory[ip]);
    target = 0;
    value = 0;
    auto pos = 0;

    std::cout << "step: " << steps << std::endl;
    std::cout << "ip: " << ip << " ["
              << std::setfill('0') << std::setw(2) << std::hex
              << static_cast<int>(ic) << std::dec << "]\t";

    switch(ic) {
        // nullary instructions: nothing else to fetch
        case ICs::NOP:
        case ICs::DROP:
        case ICs::POP:
        case ICs::PUSH:
        case ICs::DUP:
        case ICs::SWAP:
        case ICs::INC:
        case ICs::DEC:
        case ICs::RET:
            break;

        // unary value instruction(s)
        case ICs::PUSHVAL:
            ip++;
            value = pmemory[ip];
            break;

        // binary (value, target) instruction(s)
        case ICs::JMPIF:
            ip++;
            value = pmemory[ip];
            // fall through

        // unary target instructions
        case ICs::CALL:
        case ICs::GOTO:
            ip++;
            target = pmemory[ip];
            ip++;
            while (pmemory[ip] != (word) ICs::ENDMARK) {
                target += (pmemory[ip] << 8*pos*sizeof(word));
                pos++;
            }
            break;
        default:
            // Invalid instruction fails on execute.
            return;
    }

    ++ip;
}

bool StackVM::execute() {
    std::cout << "value: " << static_cast<int>(value) << "\ttarget: " << static_cast<int>(target) << std::endl;
    if (!data.empty()) {
        std::cout << "data[-1]: " << static_cast<int>(data.back()) << std::endl;
    }
    if (!call.empty()) {
        std::cout << "call[-1]: " << static_cast<int>(call.back()) << std::endl;
    }
    std::cout << std::endl;

    switch(ic) {
        case ICs::NOP:     return true;
        case ICs::DROP:    return drop();
        case ICs::POP:     return pop();
        case ICs::PUSH:    return push();
        case ICs::PUSHVAL:
            pushvalue(value);
            return true;
        case ICs::DUP:     return dup();
        case ICs::SWAP:    return swap();
        case ICs::INC:     return inc();
        case ICs::DEC:     return dec();
        case ICs::JMPIF:   return jumpif(value, target);
        case ICs::RET:     return ret();
        case ICs::CALL:
            call_proc(target);
            return true;
        case ICs::GOTO:
            vm_goto(target);
            return true;
        default:
            return false;  // Invalid instruction code.
    }
}

bool StackVM::drop() {
    if (data.empty()) {
        return false;
    }
    data.pop_back();
    return true;
}

bool StackVM::pop() {
    if (data.empty()) {
        return false;
    }
    call.push_back(data.back());
    data.pop_back();
    return true;
}

bool StackVM::push() {
    if (call.size() <= call_levels.back()) {
        return false;
    }
    data.push_back(call.back());
    call.pop_back();
    return true;
}

void StackVM::pushvalue(word val) {
    data.push_back(val);
}

bool StackVM::dup() {
    if (data.empty()) {
        return false;
    }
    data.push_back(data.back());
    return true;
}

bool StackVM::swap() {
    if (data.size() < 2) {
        return false;
    }
    std::iter_swap(data.end() - 2, data.end() - 1);
    return true;
}

bool StackVM::inc() {
    if (data.empty()) {
        return false;
    }
    data.back()++;
    return true;
}

bool StackVM::dec() {
    if (data.empty()) {
        return false;
    }
    data.back()--;
    return true;
}

bool StackVM::jumpif(word testval, ip_type tar) {
    if (data.empty()) {
        return false;
    }
    if (data.back() == testval) {
        vm_goto(tar);
    }

    data.pop_back();
    return true;
}

void StackVM::vm_goto(ip_type tar) {
    ip = tar;
}

void StackVM::call_proc(ip_type tar) {
    pushaddress(ip);  // After fetch, `ip` is the next instruction to
                      // be executed assuming no jumps; that is where
                      // we should continue execution.
    call_levels.push_back(call.size());
    vm_goto(tar);
}

bool StackVM::ret() {
    if (call.size() != call_levels.back()) {
        return false;
    }
    if (call.empty()) {
        done = true;
        return true;
    }

    if (popaddress()) {
        call_levels.pop_back();
        vm_goto(target);
        return true;
    }
    return false;
}

bool StackVM::popaddress() {
    target = 0;
    auto pos = 0;

    while (!call.empty() && call.back() != (word) ICs::ENDMARK) {
        target += (call.back() << (8 * pos * sizeof(word)));
        pos += 1;
        call.pop_back();
    }
    if (call.empty()) {
        return false;
    } else if (pos == 0 && target == 0) {  // check for double zero case: [0, ICs::ENDMARK == 0]
        call.pop_back();
    }
    call.pop_back();

    return true;
}

bool StackVM::pushaddress(ip_type addr) {
    // double zero case (ICs::ENDMARK == 0)
    call.push_back((word) ICs::ENDMARK);
    if (addr == 0) {
        call.push_back(0);
        return true;
    }

    // Note that this could be slighlty improved by using
    // sizeof(ip_type), and directly starting with most significant
    // word, checking for zero; however, the logic is a bit more
    // convoluted that way.

    // push in reverse order onto data...
    auto num_words = 0;
    while (addr > 0) {
        data.push_back((word)(addr & 0xff));
        num_words += 1;
        addr >>= (sizeof(word) * 8);
    }

    // ...then pop in correct order onto call stack.
    while (num_words > 0) {
        call.push_back(data.back());
        data.pop_back();
        num_words--;
    }

    return true;
}
