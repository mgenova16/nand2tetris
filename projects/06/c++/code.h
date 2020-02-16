#ifndef HACK_ASSEMBLER_CODE_H_
#define HACK_ASSEMBLER_CODE_H_

#include "symbol_table.h"
#include <string>
#include <map>

struct AInstruction
{
    AInstruction () : ibit {0} {}
    unsigned short ibit : 1;
    unsigned short address : 15;
};

struct CInstruction
{
    CInstruction () : ibits {7} {}
    unsigned short ibits : 3;
    unsigned short cbits : 7;
    unsigned short dbits : 3;
    unsigned short jbits : 3;
};

class Code
{
    public:
        Code();
        AInstruction getAInstruction(std::string symbol, SymbolTable& symbolTable);
        CInstruction getCInstruction(std::string dest, std::string comp, std::string jump);

    public:
        std::map<std::string, int> destMap;
        std::map<std::string, int> compMap;
        std::map<std::string, int> jumpMap;
};

#endif // HACK_ASSEMBLER_CODE_H_
