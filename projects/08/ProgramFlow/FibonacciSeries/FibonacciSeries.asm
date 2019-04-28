// push argument 1
@ARG
A=M
A=A+1
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop pointer 1
@SP
D=M-1
M=D
A=D
D=M
@R4
M=D
// push constant 0
@0
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop that 0
@SP
D=M-1
M=D
A=D
D=M
@THAT
A=M
M=D
// push constant 1
@1
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop that 1
@SP
D=M-1
M=D
A=D
D=M
@THAT
A=M
A=A+1
M=D
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 2
@2
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// sub
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop argument 0
@SP
D=M-1
M=D
A=D
D=M
@ARG
A=M
M=D
// label MAIN_LOOP_START
(FibonacciSeries$MAIN_LOOP_START)
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// if-goto COMPUTE_ELEMENT
@SP
D=M-1
M=D
A=D
D=M
@FibonacciSeries$COMPUTE_ELEMENT
D;JLT
D;JGT
// goto END_PROGRAM
@FibonacciSeries$END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(FibonacciSeries$COMPUTE_ELEMENT)
// push that 0
@THAT
A=M
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// push that 1
@THAT
A=M
A=A+1
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// add
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=D+M
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop that 2
@SP
D=M-1
M=D
A=D
D=M
@THAT
A=M
A=A+1
A=A+1
M=D
// push pointer 1
@R4
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 1
@1
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// add
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=D+M
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop pointer 1
@SP
D=M-1
M=D
A=D
D=M
@R4
M=D
// push argument 0
@ARG
A=M
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 1
@1
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// sub
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop argument 0
@SP
D=M-1
M=D
A=D
D=M
@ARG
A=M
M=D
// goto MAIN_LOOP_START
@FibonacciSeries$MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(FibonacciSeries$END_PROGRAM)
