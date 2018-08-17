# ========================= CodeGenerator CLASS

class CodeGenerator(object):
    """
    CodeGenerator generates code from parsed input.
    """
    def __init__(self):
        """
        Initialises CodeGenerator.
        input:
            file_name   -file name without any folder structure;
                         used for generating static variables
        """
        self._counter = 0
        self._file_name = ''
        self._fct_name = ''

    def reset(self, file_name, fct_name):
        """
        Resets the jump counter and file name.
        input:
            file_name   -file name without any folder structure;
                         used for generating static variables
            fct_name    -name of the current function;
                         used for labels
        """
        self._counter = 0
        self._file_name = file_name
        self._fct_name = fct_name

    def set_new_file_name(self, file_name):
        """
        Sets the file name.
        input:
            file_name   -file name without any folder structure;
                         used for generating static variables
        """
        self._file_name = file_name

    def generate_code(self, parsed):
        """
        Generates code for parsed line.
        input:
            parsed is a dictionary of parsed key-value pairs
            keys:            values:
                cmd_type         'C_ARITHMETIC', 'C_PUSH', 'C_POP', 'C_LABEL', 'C_GOTO', 'C_IFGOTO', 'C_FUNCTION', 'C_RETURN', 'C_CALL', None
                arg1             'constant', 'temp', 'pointer', 'static', 'local', 'argument', 'this', 'that'
                arg2             str(int)
                file_line        int
        output:
            code in Hack Assembly
        """
        if   parsed['cmd_type'] == 'C_PUSH':
            output_code = self._push(segment=parsed['arg1'], i=parsed['arg2'], line=parsed['file_line'])
        elif parsed['cmd_type'] == 'C_POP':
            output_code = self._pop(segment=parsed['arg1'], i=parsed['arg2'], line=parsed['file_line'])
        elif parsed['cmd_type'] == 'C_ARITHMETIC':
            output_code = self._arithmetic(operation=parsed['arg1'])
        elif parsed['cmd_type'] == 'C_LABEL':
            output_code = self._label(label=parsed['arg1'])
        elif parsed['cmd_type'] == 'C_GOTO':
            output_code = self._goto(label=parsed['arg1'])
        elif parsed['cmd_type'] == 'C_IFGOTO':
            output_code = self._ifgoto(label=parsed['arg1'])
        elif parsed['cmd_type'] == 'C_FUNCTION':
            output_code = self._function(fctname=parsed['arg1'], nVars=parsed['arg2'])
        elif parsed['cmd_type'] == 'C_CALL':
            output_code = self._call(fctname=parsed['arg1'], nArgs=parsed['arg2'])
        elif parsed['cmd_type'] == 'C_RETURN':
            output_code = self._return()
        return output_code


    # --------------- Helper functions

    # --------------- PUSH

    def _push(self, segment, i, line):
        """
        Generate code for push command.
        input:
            segment     -is one of ['constant', 'temp', 'pointer', 'static', 'local', 'argument', 'this', 'that']
            i           -is str(int)
            line        -line number of the input file
        output:
            code in Hack Assembly
        """
        code  = self._addr_to_D(segment, i, line)
        code += self._D_to_stack()
        return code

    def _addr_to_D(self, segment, i, line):
        """
        Generates code for copying value from the 'segment i' to the D register.
        input:
            segment     -is one of ['constant', 'temp', 'pointer', 'static', 'local', 'argument', 'this', 'that']
            i           -is str(int)
            line        -line number of the input file
        output:
            code in Hack Assembly
        """
        if   segment == 'constant':
            code  = '@'+i+'\n'      # A=i
            code += 'D=A'+'\n'      # D=i
            return code
        elif segment == 'temp':
            if int(i) < 0 or int(i) > 7:
                raise ValueError('File line {}: Reaching outside of temp part, i must be in the interval [0,7]'.format(line))
            code  = '@'+str(int(i)+5)+'\n'  # A=i+5, M=*(i+5)
            code += 'D=M'+'\n'              # D=*(i+5)
            return code
        elif segment == 'pointer':
            if int(i) < 0 or int(i) > 1:
                raise ValueError('File line {}: for pointer i must be in the interval [0,1]'.format(line))
            if   int(i) == 0: VS = 'THIS'
            elif int(i) == 1: VS = 'THAT'
            code  = '@'+VS+'\n'     # A=VS,  M=*VS
            code += 'D=M'+'\n'      # D=*VS
            return code
        elif segment == 'static':
            code  = '@'+self._file_name+'.'+i+'\n'
            code += 'D=M'+'\n'
            return code
        elif segment == 'local':
            VS = 'LCL'              # virtual segment
        elif segment == 'argument':
            VS = 'ARG'              # virtual segment
        elif segment == 'this':
            VS = 'THIS'             # virtual segment
        elif segment == 'that':
            VS = 'THAT'             # virtual segment

        if int(i) == 0:
            code  = '@'+VS+'\n'     # A=VS,  M=*VS
            code += 'A=M'+'\n'      # A=*VS, M=**VS
            code += 'D=M'+'\n'      # D=*(i+*VS)
        else:
            code  = '@'+i+'\n'      # A=i
            code += 'D=A'+'\n'      # D=i
            code += '@'+VS+'\n'     # A=VS,  M=*VS
            code += 'A=D+M'+'\n'    # A=i+*VS, M=*(i+*VS)
            code += 'D=M'+'\n'      # D=*(i+*VS)
        # alternative to the first 4 lines
        # code  = '@VS'               # A=VS,  M=*VS
        # code += 'D=M'               # D=*VS
        # code += '@'+i               # A=i
        # code += 'A=D+A'             # A=*VS+i, M=*(*VS+i)
        # code += 'D=M'+'\n'          # D=*(i+*VS)
        return code

    def _D_to_stack(self):
        """
        Generates code for copying value from the D register to the stack.
        output:
            code in Hack Assembly
        """
        code  = '@SP'+'\n'          # A=SP,  M=*SP  (=RAM[SP])
        code += 'AM=M+1'+'\n'       # A=*SP_new (=*SP+1), *SP_new = *SP+1
        code += 'A=A-1'+'\n'        # A=*SP_new-1 (=*SP)
        code += 'M=D'+'\n'          # **SP=D
        return code


    # --------------- POP
    def _pop(self, segment, i, line):
        """
        Generate code for pop command.
        input:
            segment     -is one of ['temp', 'pointer', 'static']
            i           -is str(int)
            line        -line number of the input file
        output:
            code in Hack Assembly
        """
        if segment in ['temp', 'pointer', 'static']:
            code  = self._stack_to_D()
            code += self._D_to_addr(segment, i, line)
        elif segment in ['local', 'argument', 'this', 'that']:
            code  = self._addr_to_R1X(segment, i, x=3)
            code += self._stack_to_D()
            code += '@R13'+'\n'     # because x=3 above
            code += 'A=M'+'\n'
            code += 'M=D'+'\n'
        return code

    def _stack_to_D(self):
        """
        Generate code for copying value from the stack to the D register.
        output:
            code in Hack Assembly
        """
        code  = '@SP'+'\n'          # A=SP,  M=*SP  (=RAM[SP])
        code += 'AM=M-1'+'\n'       # *SP--, A=*SP--, M=*(*SP--)
        code += 'D=M'+'\n'          # D=**SP
        return code

    def _D_to_R1X(self, x):
        """
        Generate code for copying value from the D register to one of R13, R14, R15 registers.
        input:
            x           -3,4 or 5; specifies the R1X register
        output:
            code in Hack Assembly
        """
        if x < 3 or x > 5:
            raise ValueError('x must be in the interval [3,5]')
        x = str(x)
        code  = '@R1'+x+'\n'
        code += 'M=D'+'\n'
        return code

    # def _R1X_to_D(self, x):
    #     """
    #     Generate code for copying value from one of R13, R14, R15 registers to the D register.
    #     input:
    #         x           -3,4 or 5; specifies the R1X register
    #     output:
    #         code in Hack Assembly
    #     """
    #     if x < 3 or x > 5:
    #         raise ValueError('x must be in the interval [3,5]')
    #     x = str(x)
    #     code  = '@R1'+x+'\n'
    #     code += 'D=M'+'\n'
    #     return code

    def _D_to_addr(self, segment, i, line):
        """
        Generates code for copying value from the D register to the 'segment i'.
        input:
            segment     -is one of ['temp', 'pointer', 'static']
            i           -is str(int)
            line        -line number of the input file
        output:
            code in Hack Assembly
        """
        if   segment == 'temp':
            if int(i) < 0 or int(i) > 7:
                raise ValueError('File line {}: Reaching outside of temp part, i must be in the interval [0,7]'.format(line))
            code  = '@'+str(int(i)+5)+'\n'  # A=i+5, M=*(i+5)
            code += 'M=D'+'\n'              # *(i+5)=D
            return code
        elif segment == 'pointer':
            if int(i) < 0 or int(i) > 1:
                raise ValueError('File line {}: for pointer i must be in the interval [0,1]'.format(line))
            if   int(i) == 0: VS = 'THIS'
            elif int(i) == 1: VS = 'THAT'
            code  = '@'+VS+'\n'     # A=VS,  M=*VS
            code += 'M=D'+'\n'      # *VS=D
            return code
        elif segment == 'static':
            code  = '@'+self._file_name+'.'+i+'\n'
            code += 'M=D'+'\n'
            return code

    def _addr_to_R1X(self, segment, i, x):
        """
        Generates code for copying value from the 'segment i' to one of R13, R14, R15 registers.
        input:
            segment     -is one of ['local', 'argument', 'this', 'that']
            i           -is str(int)
            x           -3,4 or 5; specifies the R1X register
        output:
            code in Hack Assembly
        """
        if   segment == 'local':
            VS = 'LCL'              # virtual segment
        elif segment == 'argument':
            VS = 'ARG'              # virtual segment
        elif segment == 'this':
            VS = 'THIS'             # virtual segment
        elif segment == 'that':
            VS = 'THAT'             # virtual segment

        if int(i) == 0:
            code  = '@'+VS+'\n'     # A=VS,  M=*VS
            code += 'D=M'+'\n'      # D=*VS
            code += self._D_to_R1X(x)
        else:
            code  = '@'+i+'\n'      # A=i
            code += 'D=A'+'\n'      # D=i
            code += '@'+VS+'\n'     # A=VS,  M=*VS
            code += 'D=D+M'+'\n'    # D=i+*VS
            code += self._D_to_R1X(x)
            # alternative to the first 4 lines
            # code  = '@VS'           # A=VS,  M=*VS
            # code += 'D=M'           # D=*VS
            # code += '@'+i           # A=i
            # code += 'D=D+A'         # D=*VS+i
        return code


    # --------------- ARITHMETIC
    def _arithmetic(self, operation):
        """
        Generates code for arithmetic operations.
        input:
            operation   -is one of ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        output:
            code in Hack Assembly
        """
        if   operation == 'add': code = self._add()
        elif operation == 'sub': code = self._sub()
        elif operation == 'neg': code = self._neg()
        elif operation == 'eq':  code = self._eq()
        elif operation == 'gt':  code = self._gt()
        elif operation == 'lt':  code = self._lt()
        elif operation == 'and': code = self._and()
        elif operation == 'or':  code = self._or()
        elif operation == 'not': code = self._not()
        return code

    def _add(self):
        """
        Generates code for:
            adding two values from the stack, and
            putting the result back on the stack.
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()  # put the first operand to D and perform *SP--
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'M=D+M'+'\n'        # paste the result to M
        return code

    def _sub(self):
        """
        Generates code for:
            subtracting two values from the stack, and
            putting the result back on the stack.
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()  # put the first operand to D and perform *SP--
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'M=M-D'+'\n'        # paste the result to M
        return code

    def _neg(self):
        """
        Generates code for:
            negating the value on the stack, and
            putting the result back on the stack.
        output:
            code in Hack Assembly
        """
        code  = '@SP'+'\n'          # M points to one past the operand
        code += 'A=M-1'+'\n'        # M points to the operand
        code += 'M=-M'+'\n'
        return code

    def _D_is_EGL_0(self, EGL):
        """
        Generates code for comparing if the value in the D register is equal, greater or less than 0.
        input:
            EGL         - one of ['JEQ', 'JGT', 'JLT']
        output:
            code in Hack Assembly
        """
        code  = '@TRUE__'+str(self._counter)+'\n'
        code += 'D;'+EGL+'\n'
        code += 'D=0'+'\n'
        code += '@D_TO_STACK__'+str(self._counter)+'\n'
        code += '0;JMP'+'\n'
        code += '(TRUE__'+str(self._counter)+')'+'\n'
        code += 'D=-1'+'\n'
        code += '(D_TO_STACK__'+str(self._counter)+')'+'\n'
        self._counter += 1
        return code

    def _eq(self):
        """
        Generates code for:
            comparing two values from the stack, and
            putting the result back on the stack.
        The result is true (-1) if they are equal, false (0) otherwise.
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()  # put the first operand to D and perform *SP--
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'D=M-D'+'\n'
        code += self._D_is_EGL_0('JEQ')
        code += '@SP'+'\n'          # M points to one past the place to paste the result
        code += 'A=M-1'+'\n'        # adjust the place
        code += 'M=D'+'\n'          # paste the result
        return code

    def _gt(self):
        """
        Generates code for:
            comparing two values from the stack, and
            putting the result back on the stack.
        The result is true (-1) if second is greater, false (0) otherwise.
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'D=M-D'+'\n'
        code += self._D_is_EGL_0('JGT')
        code += '@SP'+'\n'          # M points to one past the place to paste the result
        code += 'A=M-1'+'\n'        # adjust the place
        code += 'M=D'+'\n'          # paste the result
        return code

    def _lt(self):
        """
        Generates code for:
            comparing two values from the stack, and
            putting the result back on the stack.
        The result is true (-1) if second is smaller, false (0) otherwise.
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'D=M-D'+'\n'
        code += self._D_is_EGL_0('JLT')
        code += '@SP'+'\n'          # M points to one past the place to paste the result
        code += 'A=M-1'+'\n'        # adjust the place
        code += 'M=D'+'\n'          # paste the result
        return code

    def _and(self):
        """
        Generates code for:
            performing bit-wise 'and' on two values from the stack, and
            putting the result back on the stack .
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'M=D&M'+'\n'
        return code

    def _or(self):
        """
        Generates code for:
            performing bit-wise 'or' on two values from the stack, and
            putting the result back on the stack .
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()
        code += 'A=A-1'+'\n'        # M points to the second operand
        code += 'M=D|M'+'\n'
        return code

    def _not(self):
        """
        Generates code for:
            performing bit-wise 'not' the value from the stack, and
            putting the result back on the stack .
        output:
            code in Hack Assembly
        """
        code  = '@SP'+'\n'          # M points to one past the operand
        code += 'A=M-1'+'\n'        # M points to the operand
        code += 'M=!M'+'\n'
        return code


    # --------------- LABEL, GOTO, IFGOTO
    def _label(self, label):
        """
        Generates code for creating a label.
        input:
            label       - label name
        output:
            code in Hack Assembly
        """
        code  = '('+self._file_name+'.'+self._fct_name+'$'+label+')'+'\n'
        return code

    def _goto(self, label):
        """
        Generates code for unconditional jump to a label.
        input:
            label       - label name
        output:
            code in Hack Assembly
        """
        code  = '@'+self._file_name+'.'+self._fct_name+'$'+label+'\n'
        code += '0; JMP'+'\n'
        return code

    def _ifgoto(self, label):
        """
        Generates code for conditional jump to a label based on a value from the stack.
        input:
            label       - label name
        output:
            code in Hack Assembly
        """
        code  = self._stack_to_D()
        code += '@'+self._file_name+'.'+self._fct_name+'$'+label+'\n'
        code += 'D; JNE'+'\n'
        return code

    # --------------- FUNCTION
    def _function(self, fctname, nVars):
        """
        Generates code for function initialisation.
        input:
            fctname     - function name
            nVars       - number of function's local variables
        return:
            code in Hack Assembly
        """
        self._fct_name = fctname
        code  = '('+fctname+')'+'\n'
        if int(nVars) != 0:
            code += '@SP'+'\n'
            code += 'A=M'+'\n'
            for _ in range(int(nVars)):
                code += 'M=0'+'\n'
                code += 'A=A+1'+'\n'
            code += '@'+nVars+'\n'
            code += 'D=A'+'\n'
            code += '@SP'+'\n'
            code += 'M=D+M'+'\n'
        return code


    # --------------- CALL
    def _call(self, fctname, nArgs):
        """
        Generates code for function call.
        input:
            fctname     - function name
            nVars       - number of function's local variables
        return:
            code in Hack Assembly
        """
        code  = '@'+fctname+'$ret'+'.'+str(self._counter)+'\n'
        code += 'D=A'+'\n'
        code += self._D_to_stack()  # push return address
        code += '@LCL'+'\n'
        code += 'D=M'+'\n'
        code += self._D_to_stack()  # push LCL
        code += '@ARG'+'\n'
        code += 'D=M'+'\n'
        code += self._D_to_stack()  # push ARG
        code += '@THIS'+'\n'
        code += 'D=M'+'\n'
        code += self._D_to_stack()  # push THIS
        code += '@THAT'+'\n'
        code += 'D=M'+'\n'
        code += self._D_to_stack()  # push THAT
        code += '@5'+'\n'
        code += 'D=A'+'\n'
        code += '@'+nArgs+'\n'
        code += 'D=D+A'+'\n'        # D = 5+nArgs
        code += '@SP'+'\n'
        code += 'D=M-D'+'\n'        # D = SP-(5+nArgs)
        code += '@ARG'+'\n'
        code += 'M=D'+'\n'          # ARG = SP-(5+nArgs)
        code += '@SP'+'\n'
        code += 'D=M'+'\n'
        code += '@LCL'+'\n'
        code += 'M=D'+'\n'          # LCL = SP
        code += '@'+fctname+'\n'
        code += '0; JMP'+'\n'       # GOTO function
        code += '('+fctname+'$ret'+'.'+str(self._counter)+')'+'\n'
        self._counter += 1
        return code


    # --------------- RETURN
    def _return(self):
        """
        Generates code for returning from a function.
        return:
            code in Hack Assembly
        """
        code  = '@LCL'+'\n'
        code += 'A=M'+'\n'
        code += 'D=A'+'\n'
        code += '@5'+'\n'
        code += 'A=D-A'+'\n'
        code += 'D=M'+'\n'
        code += self._D_to_R1X(3)   # the return address to R13
        code += self._stack_to_D()
        code += '@ARG'+'\n'
        code += 'A=M'+'\n'
        code += 'M=D'+'\n'          # *ARG = pop()
        code += '@ARG'+'\n'
        code += 'D=M+1'+'\n'
        code += '@SP'+'\n'
        code += 'M=D'+'\n'          # SP = ARG+1
        code += self._LCL_to_D()    # D = *(LCL-1); LCL = LCL-1
        code += '@THAT'+'\n'
        code += 'M=D'+'\n'          # THAT = *(LCL-1)
        code += self._LCL_to_D()    # D = *(LCL-1); LCL = LCL-1
        code += '@THIS'+'\n'
        code += 'M=D'+'\n'          # THIS = *(LCL-1)
        code += self._LCL_to_D()    # D = *(LCL-1); LCL = LCL-1
        code += '@ARG'+'\n'
        code += 'M=D'+'\n'          # ARG = *(LCL-1)
        code += self._LCL_to_D()    # D = *(LCL-1); LCL = LCL-1
        code += '@LCL'+'\n'
        code += 'M=D'+'\n'          # LCL = *(LCL-1)
        code += '@R13'+'\n'
        code += 'A=M'+'\n'
        code += '0; JMP'+'\n'       # jump to the return address
        return code


    def _LCL_to_D(self):
        """
        Generates code for:
            copying the value from LCL-1 to the D register, and
            decreasing LCL value by 1.
        return:
            code in Hack Assembly
        """
        code  = '@LCL'+'\n'
        code += 'AM=M-1'+'\n'
        code += 'D=M'+'\n'
        return code
