#include "symbol_table.h"
#include <string>
#include <iostream>
#include <map>


SymbolTable::SymbolTable()
{
    this->symbolTable = 
    {
        {"SP",         0}, {"LCL",        1}, {"ARG",        2},
        {"THIS",       3}, {"THAT",       4}, {"R0",         0},
        {"R1",         1}, {"R2",         2}, {"R3",         3},
        {"R4",         4}, {"R5",         5}, {"R6",         6},
        {"R7",         7}, {"R8",         8}, {"R9",         9},
        {"R10",       10}, {"R11",       11}, {"R12",       12},
        {"R13",       13}, {"R14",       14}, {"R15",       15},
        {"SCREEN", 16384}, {"KBD",    24576},
    };
    this->nextAddress = 16;
};

void SymbolTable::addEntry(std::string symbol)
{
    this->symbolTable.insert(std::pair<std::string, int> (symbol, this->nextAddress));
    this->nextAddress++;
}

void SymbolTable::addEntry(std::string symbol, int address)
{
    this->symbolTable.insert(std::pair<std::string, int> (symbol, address));
}

bool SymbolTable::contains(std::string symbol)
{
    return !(this->symbolTable.find(symbol) == this->symbolTable.end());
}

int SymbolTable::getAddress(std::string symbol)
{
    if (!this->contains(symbol)) {
        std::cout << "ERROR: Symbol " << symbol << " not found\n";
        exit(1);
    }
    return this->symbolTable[symbol];
}
