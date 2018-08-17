# ========================= Parser CLASS

class Parser(object):
    """
    Parser for Stack Machine
    """
    def __init__(self):
        self._cmd_line = 0
        self._file_line = 0


    def reset(self):
        """
        Resets the command line to 0.
        """
        self._cmd_line = 0
        self._file_line = 0


    def parse(self, line_str):
        """
        args:
          - line_str: string to be parsed
        ret:
          - dict: containing cmd_type, arg1, arg2, and file_line

        value for:
          - cmd_type key is one of the following:
            C_PUSH, C_POP, C_ARITHMETIC,
            C_LABEL, C_GOTO, C_IFGOTO,
            C_FUNCTION, C_RETURN, C_CALL, None

          - arg1 key (is str and) returns the first argument of the command.
            If cmd_type == C_ARITHMETIC, then arg1 is the command itself (add, etc.)
            If cmd_type == C_RETURN, then the value = None

          - arg2 key (is str(int) and) returns the second argument of the command.
            If cmd_type == C_PUSH, C_POP, C_FUNCTION or C_CALL; then the value = None

          - file_line key is an int
        """
        string = self._purify(line_str)
        self._file_line +=1
        if not string: # if string is empty or None
            return None

        words = string.split()
        if self._is_push(words):
            self._cmd_line += 1
            return {'cmd_type':'C_PUSH', 'arg1':words[1], 'arg2':words[2], 'file_line': self._file_line}
        elif self._is_pop(words):
            self._cmd_line += 1
            return {'cmd_type':'C_POP', 'arg1':words[1], 'arg2':words[2], 'file_line': self._file_line}
        elif self._is_arithmetic(words):
            self._cmd_line += 1
            return {'cmd_type':'C_ARITHMETIC', 'arg1':words[0], 'arg2':None, 'file_line': self._file_line}
        elif self._is_label(words):
            self._cmd_line += 1
            return {'cmd_type':'C_LABEL', 'arg1':words[1], 'arg2':None, 'file_line': self._file_line}
        elif self._is_goto(words):
            self._cmd_line += 1
            return {'cmd_type':'C_GOTO', 'arg1':words[1], 'arg2':None, 'file_line': self._file_line}
        elif self._is_ifgoto(words):
            self._cmd_line += 1
            return {'cmd_type':'C_IFGOTO', 'arg1':words[1], 'arg2':None, 'file_line': self._file_line}
        elif self._is_function(words):
            self._cmd_line += 1
            return {'cmd_type':'C_FUNCTION', 'arg1':words[1], 'arg2':words[2], 'file_line': self._file_line}
        elif self._is_call(words):
            self._cmd_line += 1
            return {'cmd_type':'C_CALL', 'arg1':words[1], 'arg2':words[2], 'file_line': self._file_line}
        elif self._is_return(words):
            self._cmd_line += 1
            return {'cmd_type':'C_RETURN', 'arg1':None, 'arg2':None, 'file_line': self._file_line}


    # --------------- Helper functions

    def _purify(self, line_str):
        """
        This function removes end of line character, comments,
        and emty space at the beginning and end of command.
        """
        string = line_str.strip('\n')
        string = string.strip()
        comment_idx = string.find('//')
        if comment_idx == -1:
            return string.strip()
        elif comment_idx == 0:
            return None
        else:
            return string[0:comment_idx].strip()

    def _is_arithmetic(self, words):
        """
        Checks for arithmetic commands.
        """
        if words[0] in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            if len(words) != 1:
                raise SyntaxError("File line {}: Invalid number of arguments for C_ARITHMETIC command.".format(self._file_line))
            return True
        else:
            return False

    def _is_push(self, words):
        """
        Checks for push commands.
        """
        if words[0] == 'push':
            if len(words) != 3:
                raise SyntaxError("File line {}: Invalid number of arguments for C_PUSH command.".format(self._file_line))
            if words[1] not in ['constant', 'temp', 'pointer', 'static', 'local', 'argument', 'this', 'that']:
                raise SyntaxError("File line {}: Invalid second argument.".format(self._file_line))
            return True
        else:
            return False

    def _is_pop(self, words):
        """
        Checks for pop commands.
        """
        if words[0] == 'pop':
            if len(words) != 3:
                raise SyntaxError("File line {}: Invalid number of arguments for C_POP command.".format(self._file_line))
            if words[1] not in ['temp', 'pointer', 'static', 'local', 'argument', 'this', 'that']:
                raise SyntaxError("File line {}: Invalid second argument.".format(self._file_line))
            return True
        else:
            return False

    def _is_label(self, words):
        """
        Check for label commands.
        """
        if words[0] == 'label':
            if len(words) != 2:
                raise SyntaxError("File line {}: Invalid number of arguments for C_LABEL command.".format(self._file_line))
            return True
        else:
            return False

    def _is_goto(self, words):
        """
        Check for goto commands.
        """
        if words[0] == 'goto':
            if len(words) != 2:
                raise SyntaxError("File line {}: Invalid number of arguments for C_GOTO command.".format(self._file_line))
            return True
        else:
            return False

    def _is_ifgoto(self, words):
        """
        Check for if-goto commands.
        """
        if words[0] == 'if-goto':
            if len(words) != 2:
                raise SyntaxError("File line {}: Invalid number of arguments for C_IFGOTO command.".format(self._file_line))
            return True
        else:
            return False

    def _is_function(self, words):
        """
        Check for function commands.
        """
        if words[0] == 'function':
            if len(words) != 3:
                raise SyntaxError("File line {}: Invalid number of arguments for C_FUNCTION command.".format(self._file_line))
            return True
        else:
            return False

    def _is_call(self, words):
        """
        Check for call commands.
        """
        if words[0] == 'call':
            if len(words) != 3:
                raise SyntaxError("File line {}: Invalid number of arguments for C_CALL command.".format(self._file_line))
            return True
        else:
            return False

    def _is_return(self, words):
        """
        Check for return commands.
        """
        if words[0] == 'return':
            if len(words) != 1:
                raise SyntaxError("File line {}: Invalid number of arguments for C_RETURN command.".format(self._file_line))
            return True
        else:
            return False
