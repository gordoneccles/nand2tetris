// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

@R0
D=M
@a
M=D  // load a

@R1
D=M
@b
M=D  // load b

@i
M=0  // initialize i

@R2
M=0

@sum
M=0

(LOOP)
@b
D=M
@i
D=D-M
@STORE
D;JEQ

@sum
D=M
@a
D=D+M // sum += a
@sum
M=D  // store sum
@i
D=M
D=D+1
M=D

@LOOP
0;JMP  // restart loop


(STORE)
@sum
D=M
@R2
M=D  // store sum in R2

(END)
@END
0;JMP
