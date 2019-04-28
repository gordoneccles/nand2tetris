// push constant 0
@0
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// pop local 0
@SP
D=M-1
M=D
A=D
D=M
@LCL
A=M
M=D
// label LOOP_START
(BasicLoop$LOOP_START)
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
// push local 0
@LCL
A=M
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
// pop local 0
@SP
D=M-1
M=D
A=D
D=M
@LCL
A=M
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
// if-goto LOOP_START
@SP
D=M-1
M=D
A=D
D=M
@BasicLoop$LOOP_START
D;JLT
D;JGT
// push local 0
@LCL
A=M
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
