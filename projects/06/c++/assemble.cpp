#include "parser.h"
#include "code.h"
#include "symbol_table.h"
#include <string>
#include <iostream>
#include <fstream>
#include <bitset>


void printAInstruction(AInstruction aInstruction, std::ofstream& out)
{
    std::bitset<1> ibit = std::bitset<1> (aInstruction.ibit);
    std::bitset<15> address = std::bitset<15> (aInstruction.address);
    out << ibit << address << "\n";
}

void printCInstruction(CInstruction cInstruction, std::ofstream& out)
{
    std::bitset<3> ibits = std::bitset<3> (cInstruction.ibits);
    std::bitset<7> cbits = std::bitset<7> (cInstruction.cbits);
    std::bitset<3> dbits = std::bitset<3> (cInstruction.dbits);
    std::bitset<3> jbits = std::bitset<3> (cInstruction.jbits);
    out << ibits << cbits << dbits << jbits << "\n";
}

int main(int argc, char** argv)
{
    std::string filename = argv[1];
    std::size_t ext_start = filename.find(".asm");
    if (ext_start == std::string::npos) {
        std::cout << "File must be .asm file\n";
        exit(1);
    }
    
    std::string outfilename = filename.substr(0, ext_start) + ".cpp.hack";
    std::ofstream out;
    out.open(outfilename);
    
    Parser parser(filename);
    Code code;
    SymbolTable symbolTable;
    
    AInstruction aInstruction;
    CInstruction cInstruction;

    int ROMAddress = 0;
    int nextAddress = 16;
    int address;
    std::string command, symbol, dest, comp, jump;
  
    while (parser.hasMoreCommands()) {
        parser.advance();
        switch (parser.getCommandType()) {
            case (L_COMMAND):
                symbol = parser.getSymbol();
                symbolTable.addEntry(symbol, ROMAddress);
                break;
            default:
                ROMAddress++;
                break;
        }
    }

    parser.resetFile();

    while (parser.hasMoreCommands()) {
        parser.advance();
        command = parser.curCommand;
        if (!parser.isValidCommand) {
            continue;
        }
        switch (parser.getCommandType()) {
            case (A_COMMAND):
                symbol = parser.getSymbol();
                aInstruction = code.getAInstruction(symbol, symbolTable);
                printAInstruction(aInstruction, out);
                break;
            case (C_COMMAND):
                dest = parser.getDestMnemonic();
                comp = parser.getCompMnemonic();
                jump = parser.getJumpMnemonic();
                cInstruction = code.getCInstruction(dest, comp, jump);
                printCInstruction(cInstruction, out);
                break;
        }
    }
    out.close();
    return 0;
}
