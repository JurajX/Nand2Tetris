@0
D=A
@SP
AM=M+1
A=A-1
M=D
@LCL
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
(BasicLoop.$LOOP_START)
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@LCL
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
AM=M-1
D=M
A=A-1
M=D+M
@LCL
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@1
D=A
@SP
AM=M+1
A=A-1
M=D
@SP
AM=M-1
D=M
A=A-1
M=M-D
@ARG
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
@ARG
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
@SP
AM=M-1
D=M
@BasicLoop.$LOOP_START
D; JNE
@LCL
A=M
D=M
@SP
AM=M+1
A=A-1
M=D
