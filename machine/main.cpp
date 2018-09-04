
#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include <iterator>

#include "stackvm.hpp"

int main(int argc, char** argv){
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <filename> [data]" << std::endl;
        return 0;
    }

    // Read in program from file
    std::ifstream fin(argv[1], std::ios::binary);
    std::istreambuf_iterator<char> start(fin), end;
    std::vector<word> programdata(start, end);

    // Read in data from commandline
    std::vector<word> inputdata;
    inputdata.reserve(argc - 2);
    std::string arg;
    auto x = 0;
    for(int j = 2; j < argc; ++j) {
        arg = argv[j];
        x = std::stoi(arg, nullptr);
        inputdata.push_back(x);
    }

    std::cout << "Program (" << programdata.size() << " words): ";
    std::cout << std::hex;
    for(auto j = programdata.begin(); j != programdata.end(); ++j) {
        std::cout << std::setfill('0') << std::setw(2) << static_cast<int>(*j) << " ";
    }
    // std::copy(programdata.begin(), programdata.end(), std::ostream_iterator<int>(std::cout, " "));
    std::cout << std::endl;

    std::cout << "Data (" << inputdata.size() << " words): ";
    std::cout << std::dec;
    std::copy(inputdata.begin(), inputdata.end(), std::ostream_iterator<int>(std::cout, " "));
    std::cout << std::endl;

    auto machine = StackVM();
    machine.loadprogram(programdata);
    machine.setdata(inputdata);

    std::cout << "Running Program...\n";
    machine.run(1000);
    std::cout << "Finished with exitstatus = " << static_cast<int>(machine.getstatus()) << std::endl;
    std::cout << "Data Stack: ";
    auto output = machine.getdata();
    std::copy(output.begin(), output.end(), std::ostream_iterator<int>(std::cout, " "));
    std::cout << std::endl;

    return 0;
}
