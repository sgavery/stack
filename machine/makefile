CFLAGS = -std=c++11 -Wall -Wpedantic -Wextra

all: stackvm

stackvm: stackvm.o main.o
	$(CXX) $(CFLAGS) stackvm.o main.o -o stackvm

main.o: main.cpp
	$(CXX) $(CFLAGS) -c main.cpp

stackvm.o: instcodes.hpp stackvm.hpp stackvm.cpp
	$(CXX) $(CFLAGS) -c stackvm.cpp

clean:
	trash-put -v *.o
