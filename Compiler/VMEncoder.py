# ========================= VMWriter CLASS

class VMEncoder(object):
    """
    VM encoder for the CompilationEngine of the Jack compiler.
    """

    def encodePush(self, segment, index):
        """
        Creates VM push command based on the input.
        args:
            segment: (str) segment to operate on
            index:   (int) index of the desired segment
        ret:
            string containing VM push command
        """
        if   segment == 'const':
            return 'push constant '+ str(index) +'\n'
        elif segment == 'arg':
            return 'push argument '+ str(index) +'\n'
        elif segment == 'local':
            return 'push local '+ str(index) +'\n'
        elif segment == 'static':
            return 'push static '+ str(index) +'\n'
        elif segment == 'this':
            return 'push this '+ str(index) +'\n'
        elif segment == 'that':
            return 'push that '+ str(index) +'\n'
        elif segment == 'pointer':
            return 'push pointer '+ str(index) +'\n'
        elif segment == 'temp':
            return 'push temp '+ str(index) +'\n'
        else:
            raise TypeError("Invalid segment type for writePush operation. Segment type: '{}'"
                            .format(segment))

    def encodePop(self, segment, index):
        """
        Creates VM pop command based on the input.
        args:
            segment: (str) segment to operate on
            index:   (int) index of the desired segment
        ret:
            string containing VM push command
        """
        if   segment == 'arg':
            return 'pop argument '+ str(index) +'\n'
        elif segment == 'local':
            return 'pop local '+ str(index) +'\n'
        elif segment == 'static':
            return 'pop static '+ str(index) +'\n'
        elif segment == 'this':
            return 'pop this '+ str(index) +'\n'
        elif segment == 'that':
            return 'pop that '+ str(index) +'\n'
        elif segment == 'pointer':
            return 'pop pointer '+ str(index) +'\n'
        elif segment == 'temp':
            return 'pop temp '+ str(index) +'\n'
        else:
            raise TypeError("Invalid segment type for writePop operation. Segment type: '{}'"
                            .format(segment))

    def encodeArithmetic(self, command):
        """
        Creates VM arithmetic commands based on the input.
        args:
            command: (str) command to be encoded
        ret:
            string containing VM arithmetic command
        """
        if   command in ['+', 'add']:
            return 'add'+'\n'
        elif command in ['-', 'sub']:
            return 'sub'+'\n'
        elif command == '*':
            return 'call Math.multiply 2'+'\n'
        elif command == '/':
            return 'call Math.divide 2'+'\n'
        elif command == '&amp;':
            return 'and'+'\n'
        elif command == '|':
            return 'or'+'\n'
        elif command == '&lt;':
            return 'lt'+'\n'
        elif command == '&gt;':
            return 'gt'+'\n'
        elif command == '=':
            return 'eq'+'\n'
        elif command == 'not':
            return 'not'+'\n'
        elif command == 'neg':
            return 'neg'+'\n'
        else:
            raise TypeError("Invalid command for writeArithmetic operation. Command given: '{}'"
                            .format(command))

    def encodeLabel(self, label):
        """
        Creates VM label command based on the input.
        args:
            label: (str) label to encode
        ret:
            string containing VM label command
        """
        return 'label '+ label +'\n'

    def encodeGoto(self, label):
        """
        Creates VM goto command based on the input.
        args:
            label: (str) label to go to
        ret:
            string containing VM goto command
        """
        return 'goto '+ label +'\n'

    def encodeIfgoto(self, label):
        """
        Creates VM if-goto command based on the input.
        args:
            label: (str) label to go to if latest stack entry is true
        ret:
            string containing VM if-goto command
        """
        return 'if-goto '+ label +'\n'

    def encodeCall(self, name, nArgs):
        """
        Creates VM function call command based on the input.
        args:
            name:  (str) name of the function to be called
            nArgs: (int) number of arguments the function should expect
        ret:
            string containing VM function call command
        """
        return 'call '+ name +' '+ str(nArgs) +'\n'

    def encodeFunction(self, name, nVars):
        """
        Creates VM function declaration command based on the input.
        args:
            name:  (str) name of the function to be declared
            nVars: (int) number of local variables the function has
        ret:
            string containing VM function declaration command
        """
        return 'function '+ name +' '+ str(nVars) +'\n'

    def encodeReturn(self):
        """
        Creates VM return command.
        """
        return 'return'+'\n'
