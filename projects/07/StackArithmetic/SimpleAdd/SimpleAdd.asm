// push constant 7
@7
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 8
@8
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
