// push constant 17
@17
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 17
@17
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// eq
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_EQ_0
D;JEQ
D=0
@END_JMP_EQ_0
0;JMP
(JMP_EQ_0)
D=-1
(END_JMP_EQ_0)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 17
@17
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 16
@16
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// eq
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_EQ_1
D;JEQ
D=0
@END_JMP_EQ_1
0;JMP
(JMP_EQ_1)
D=-1
(END_JMP_EQ_1)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 16
@16
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 17
@17
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// eq
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_EQ_2
D;JEQ
D=0
@END_JMP_EQ_2
0;JMP
(JMP_EQ_2)
D=-1
(END_JMP_EQ_2)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 892
@892
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 891
@891
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// lt
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_LT_3
D;JLT
D=0
@END_JMP_LT_3
0;JMP
(JMP_LT_3)
D=-1
(END_JMP_LT_3)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 891
@891
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 892
@892
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// lt
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_LT_4
D;JLT
D=0
@END_JMP_LT_4
0;JMP
(JMP_LT_4)
D=-1
(END_JMP_LT_4)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 891
@891
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 891
@891
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// lt
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_LT_5
D;JLT
D=0
@END_JMP_LT_5
0;JMP
(JMP_LT_5)
D=-1
(END_JMP_LT_5)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 32767
@32767
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 32766
@32766
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// gt
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_GT_6
D;JGT
D=0
@END_JMP_GT_6
0;JMP
(JMP_GT_6)
D=-1
(END_JMP_GT_6)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 32766
@32766
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 32767
@32767
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// gt
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_GT_7
D;JGT
D=0
@END_JMP_GT_7
0;JMP
(JMP_GT_7)
D=-1
(END_JMP_GT_7)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 32766
@32766
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 32766
@32766
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// gt
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=M-D
@JMP_GT_8
D;JGT
D=0
@END_JMP_GT_8
0;JMP
(JMP_GT_8)
D=-1
(END_JMP_GT_8)
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 57
@57
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 31
@31
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 53
@53
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
// push constant 112
@112
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
// neg
@SP
D=M-1
M=D
A=D
D=M
D=-D
@SP
A=M
M=D
D=A+1
@SP
M=D
// and
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=D&M
@SP
A=M
M=D
D=A+1
@SP
M=D
// push constant 82
@82
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
// or
@SP
D=M-1
D=D-1
M=D
A=D+1
D=M
A=A-1
D=D|M
@SP
A=M
M=D
D=A+1
@SP
M=D
// not
@SP
D=M-1
M=D
A=D
D=M
D=!D
@SP
A=M
M=D
D=A+1
@SP
M=D
