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


@8192
D=A
@SCREENLEN
M=D

@state
M=0


(PROGLOOP)
@KBD
D=M
@BLACKEN
D;JGT


// Whiten loop
(WHITEN)
@state
D=M
@PROGLOOP
D;JEQ  // screen is already white

@i
M=0  // initialize i = 0
@state
M=0

(WHITENLOOP)
@i
D=M
@SCREENLEN
D=D-M
@PROGLOOP
D;JEQ  // screen has been fully painted black

@SCREEN
D=A
@i
A=D+M
M=0 // paint SCREEN + i white
@i
M=M+1  // i++

@WHITENLOOP
0;JMP

// Blacken loop
(BLACKEN)
@state
D=M
@PROGLOOP
D;JGT  // screen is already black

@i
M=0  // initialize i = 0
@state
M=1

(BLACKENLOOP)
@i
D=M
@SCREENLEN
D=D-M
@PROGLOOP
D;JEQ  // screen has been fully painted black

@SCREEN
D=A
@i
A=D+M
M=-1  // paint SCREEN + i black
@i
M=M+1  // i++

@BLACKENLOOP
0;JMP
