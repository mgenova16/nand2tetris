
#include <iostream>
#include "parser.h"

void stripComments(std::string &line)
{
    std::size_t len = line.size();
    std::size_t commentBegin = line.find("//");
    if (commentBegin != std::string::npos) {
        std::size_t commentLength = line.size() - commentBegin;
        line.erase(commentBegin, commentLength);
    }
}

void stripWhiteSpace(std::string &line)
{
    std::size_t nextSpace = line.find(" ");
    while (nextSpace != std::string::npos) {
        line.erase(nextSpace, 1);
        nextSpace = line.find(" ");
    }

    std::size_t nextTab = line.find("\t");
    while (nextTab != std::string::npos) {
        line.erase(nextTab, 1);
        nextTab = line.find("\t");
    }
}

Parser::Parser(std::string& filename)
{
    this->file.open(filename);
    if (file.fail()) {
        std::cout << "Can't open file " << filename << "\n";
        exit(1);
    }
    getline(this->file, this->nextLine);
    this->isValidCommand = false;
}

Parser::~Parser()
{
    this->file.close();
}

bool Parser::hasMoreCommands()
{
    return !(this->file.eof());
}

void Parser::advance()
{
    do {
        this->line = this->nextLine;
        stripComments(this->line);
        stripWhiteSpace(this->line);
        this->lineNo++;
        getline(this->file, this->nextLine);
    } while (this->line.empty() && this->hasMoreCommands());

    // handles case when there are non-command lines at end of file
    if (!this->line.empty()) {
        this->isValidCommand = true;
    } else {
        this->isValidCommand = false;
    }
    this->curCommand = this->line;
}

void Parser::resetFile()
{
    this->file.clear();
    this->file.seekg(0, std::ios::beg);
}

CommandType Parser::getCommandType()
{
    CommandType curType;
    char commandStart = this->curCommand[0];
    switch (commandStart) {
        case '@':
            curType = A_COMMAND;
            break;
        case '(':
            curType = L_COMMAND;
            break;
        default:
            curType = C_COMMAND;
    }
    return curType;
}

std::string Parser::getSymbol()
{
    std::size_t len = this->curCommand.size();
    int begin = 1;
    int end;
    switch (this->getCommandType()) {
        case A_COMMAND:
            end = len;
            break;
        case L_COMMAND:
            end = len - 1;
            break;
        default:
            std::cout << "ERROR: Invalid command type. C Commands do not have symbols";
            exit(1);
    }
    return this->curCommand.substr(begin, end-begin);
}

std::string Parser::getDestMnemonic()
{
    std::string destMnemonic = "";
    std::size_t len = this->curCommand.size();
    std::size_t dest_end = this->curCommand.find("=");
    if (dest_end != std::string::npos) {
        destMnemonic = this->curCommand.substr(0, dest_end);
    }
    return destMnemonic;
}

std::string Parser::getCompMnemonic()
{
    std::string compMnemonic = "";
    std::size_t compStart = this->curCommand.find("=") + 1;
    if (compStart == std::string::npos) {
        compStart = 0;
    }
    std::size_t compEnd = this->curCommand.find(";");
    return this->curCommand.substr(compStart, compEnd);
}

std::string Parser::getJumpMnemonic()
{
    std::string jumpMnemonic = "";
    std::size_t len = this->curCommand.size();
    std::size_t jumpStart = this->curCommand.find(";");
    if (jumpStart != std::string::npos) {
        jumpMnemonic = this->curCommand.substr(jumpStart + 1, len - jumpStart);
    }
    return jumpMnemonic;
}
