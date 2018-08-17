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

  // set number of screen registers
    @8192
    D=A
    @n
    M=D

  // create a screen status, default screen colour is white
    @is_black
    M=0


(SCAN)
  // set the loop variable to 0
    @i
    M=0
    
  // check for keyboard input
    @KBD
    D=M
    
 // decide which loop to enter
    @DO_BLACK
    D;JNE      // if pressed, i.e. != 0, DO_BLACK
    @DO_WHITE
    D;JEQ      // if released, i.e. =0, DO_WHITE
    

(DO_BLACK)
  // if the screen is white, then change to black, else keep scanning
    @is_black
    D=M
    @BLACK
    D;JEQ
    @SCAN
    D;JNE
    

(DO_WHITE)
  // if the screen is already white, then keep scanning, else change to white
    @is_black
    D=M
    @SCAN
    D;JEQ
    @WHITE
    D;JNE


(BLACK)
  // check if to terminate the loop
    @i
    D=M        // D=i
    @n
    D=D-M      // D=i-n
    @SCAN
    D;JEQ      // If (i-n)>0 goto END
    
  // set register RAM to zero
    @SCREEN    // A = first register of the screen
    D=A
    @i
    D=D+M      // D = i-th register of the screen
    A=D        // A = SCREEN + i
    M=-1       // make the register with the address A black
    
  // increment i
    @i
    M=M+1      // i=i+1
    
  // change the screen status
    @is_black
    M=1
    
  // repeat the loop
    @BLACK
    0;JMP  // Goto BLACK


(WHITE)
  // check if to terminate the loop
    @i
    D=M        // D=i
    @n
    D=D-M      // D=i-n
    @SCAN
    D;JEQ      // If (i-n)>0 goto END
    
  // set register RAM to zero
    @SCREEN    // A = first register of the screen
    D=A
    @i
    D=D+M      // D = i-th register of the screen
    A=D        // A = SCREEN + i
    M=0        // make the register with the address A black
    
  // increment i
    @i
    M=M+1      // i=i+1
    
  // change the screen status
    @is_black
    M=0

  // repeat the loop
    @WHITE
    0;JMP  // Goto WHITE