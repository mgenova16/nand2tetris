#include "code.h"
#include "symbol_table.h"
#include <iostream>
#include <string>
#include <map>

Code::Code()
{
    this->destMap = 
    {
        {"",    0}, {"M",   1}, {"D",   2}, {"MD",  3},
        {"A",   4}, {"AM",  5}, {"AD",  6}, {"AMD", 7},
    };

    this->compMap = 
    {
        {"0",    42}, {"1",    63}, {"-1",   58}, {"D",    12},
        {"A",    48}, {"!D",   13}, {"!A",   49}, {"-D",   15},
        {"-A",   51}, {"D+1",  31}, {"A+1",  55}, {"D-1",  14},
        {"A-1",  50}, {"D+A",   2}, {"D-A",  19}, {"A-D",   7},
        {"D&A",   0}, {"D|A",  21}, {"M",   112}, {"!M",  113},
        {"-M",  115}, {"M+1", 119}, {"M-1", 114}, {"D+M",  66},
        {"D-M",  83}, {"M-D",  71}, {"D&M",  64}, {"D|M",  85},
    };

    this->jumpMap =
    {
        {"",    0}, {"JGT", 1}, {"JEQ", 2}, {"JGE", 3},
        {"JLT", 4}, {"JNE", 5}, {"JLE", 6}, {"JMP", 7},
    };
}

AInstruction Code::getAInstruction(std::string symbol, SymbolTable& symbolTable)
{
    AInstruction aInstruction;
    int address;
    try {
        address = std::stoi(symbol);
    } catch (std::invalid_argument const &e) {
        if (!symbolTable.contains(symbol)) {
            symbolTable.addEntry(symbol);
        }
        address = symbolTable.getAddress(symbol);
    }
    aInstruction.address = address;
    return aInstruction;
}

CInstruction Code::getCInstruction(std::string dest, std::string comp, std::string jump)
{
    CInstruction cInstruction;
    cInstruction.dbits = this->destMap[dest];
    cInstruction.cbits = this->compMap[comp];
    cInstruction.jbits = this->jumpMap[jump];
    return cInstruction;
}

