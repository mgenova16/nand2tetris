// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

    @R2
    M=0    // set R2 to zero
    @R0
    D=M    // load R0
    @ADD
    D;JGT  // If D > 0, start adding
    @END
    0;JMP

(ADD)
    @R2
    D=M    // load R2
    @R1
    D=D+M  // load R1 and add it to D
    @R2
    M=D    // save result back to R2
    @R0
    D=M-1  // decrement R0
    M=D
    @ADD
    D;JGT  // if D > 0, keep adding

(END)
    @END
    0;JMP    
