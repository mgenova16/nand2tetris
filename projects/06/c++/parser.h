#ifndef HACK_ASSEMBLER_PARSER_H_
#define HACK_ASSEMBLER_PARSER_H_

#include <fstream>
#include <string>

typedef enum {
    A_COMMAND,
    C_COMMAND,
    L_COMMAND,
} CommandType;

class Parser
{
    public:
        Parser(std::string& filename);
        ~Parser();
        
        void advance();
        CommandType getCommandType();
        std::string getDestMnemonic();
        std::string getCompMnemonic();
        std::string getJumpMnemonic();
        bool hasMoreCommands();
        std::string getSymbol();
        void resetFile();
        
        bool isValidCommand;

    private:
        int lineNo = 0;
        std::string curCommand;
        std::string nextCommand;
        std::ifstream file;
};

#endif // HACK_ASSEMBLER_PARSER_H_
