// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
    
    @i
    M=0
    @R2        // this will be used as sum variable
    M=0
    
    @R0
    D=M        // D=R0
    @R1
    D=D-M      // D=R0-R1
    @R0_GE_R1
    D;JGE      // If R0 >= R1, go to R0_GE_R1
    @R0_LT_R1
    D;JLT      // If R0 < R1, go to R0_LT_R1

// use the smaller number (R1) for number of loops
// and the bigger (R0) for number of loops
(R0_GE_R1)
    @R0
    D=M
    @summand
    M=D        // add = R0
    
    @R1
    D=M
    @n
    M=D        // n = R1

    @LOOP
    0;JMP

// use the smaller number (R0) for number of loops
// and the bigger (R1) for number of loops
(R0_LT_R1)
    @R1
    D=M
    @summand
    M=D        // add = R1
    
    @R0
    D=M
    @n
    M=D        // n = R0

    @LOOP
    0;JMP
    

(LOOP)
  // check if to terminate the loop
    @i
    D=M        // D=i
    @n
    D=D-M      // D=i-n
    @END
    D;JEQ      // If (i-n)>0 goto END
    
  // R2 = R2 + summand
    @summand
    D=M
    @R2
    M=D+M
    
  // increment i
    @i
    M=M+1      // i=i+1
    
  // repeat the loop
    @LOOP
    0;JMP  // Goto LOOP
    
(END)
    @END
    0;JMP