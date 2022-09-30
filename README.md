# CZ4031

We have provided 2 methods of running the application
1) via command prompt
2) via docker

==== METHOD 1 ========
for errors related to issues such as the following:
    - cannot compile *.cpp
    - "nullptr" not in scope
    - use -std=c++11 or -std=gnu++11
Please ensure to install the latest version of c++ compiler with the guide from https://www.freecodecamp.org/news/how-to-install-c-and-cpp-compiler-on-windows/

Check and ensure that your g++ version is the correct version(12.2.0) as indicated in the link above by typing the following command
in the command prompt terminal:
g++ --version

If you used the guide, you should see the following output:
g++ (Rev1, Built by MSYS2 project) 12.2.0

run the following command, to compile all files ending with .cpp, with output file named "output", then execute the output file
g++ *.cpp -o output
./output