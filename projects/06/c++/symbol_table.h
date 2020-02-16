#ifndef HACK_ASSEMBLER_SYMBOL_TABLE_H_
#define HACK_ASSEMBLER_SYMBOL_TABLE_H_

#include <string>
#include <map>

class SymbolTable
{
    public:
        SymbolTable();
        void addEntry(std::string& symbol);
        void addEntry(std::string& symbol, int address);
        bool contains(std::string& symbol);
        int getAddress(std::string& symbol);

    private:
        std::map<std::string, int> symbolTable;
        int nextAddress;

};

#endif // HACK_ASSEMBLER_SYMBOL_TABLE_H_
