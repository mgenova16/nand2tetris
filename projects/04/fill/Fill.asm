// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// if key is pressed:
//   fill with black (1)
// else
//   fill with white (0)


(START)
    @SCREEN
    D=A    // Store start address of screen in D-Register
    @pixel
    M=D    // Use M[pixel] to store current pixel
    @KBD
    D=M    // Keyboard input
    @FILLBLACK
    D;JGT
    @FILLWHITE
    D;JEQ

(FILLBLACK)
    @R0    // store -1 (black) in M[0]
    M=-1
    @FILL
    0;JMP

(FILLWHITE)
    @R0    // store 0 (white) in M[0]
    M=0
    @FILL
    0;JMP

(FILL)
    @R0
    D=M    // get the color
    @pixel
    A=M    // set A-register to pixel we need to color
    M=D    // set the color
    @pixel
    MD=M+1 // increment pixel and store value in D-Register
    @KBD
    D=A-D  // # remaining pixels = keyboard address - current pixel address 
    @FILL
    D;JGT
    @START
    0;JMP
