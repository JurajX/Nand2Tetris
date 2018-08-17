# ========================= Tokeniser CLASS

class JackTokeniser(object):
    """
    JackTokeniser for JackCompiler.
    """
    def __init__(self):
        self._keywords = ['class', 'constructor', 'function', 'method', 'field', 'static',
                          'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
                          'this', 'let', 'do', 'if', 'else', 'while', 'return']
        self._sybmols = [ '{', '}', '(', ')', '[', ']', '.', ',', ';',
                          '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
        self._max_int = 32767
        self._in_comment = False
        self._in_srting = False
        self._file_name = ''
        self._file_line = 0


    def set_new_file_name(self, file_name):
        """
        Set the name of the compiled Jack file. Used in exception messages.
        args:
            file_name: (str) name of a new Jack file.
        """
        self._file_name = file_name
        self._file_line = 0

    def tokenise(self, line_str):
        """
        Parse the input line to tokens.
        args:
            line_str: string from a Jack file
        ret:
            list of sets: the format of a set is ( tokens_kind, token, file_line )
        value for:
          - tokens_kind (str) is one of the following:
            stringConstant, integerConstant, keyword, symbol, identifier
          - token (str) is an element of Jack syntax
          - file_line (int) is the line of the jack file on which the token is located
        """
        self._file_line += 1
        s = self._purify(line_str)
        if not s:
            return None

        tokens = []
        token = ''
        for ch in s:
            if self._in_srting:
                if ch == '"':
                    self._in_srting = False
                    tokens.append( ('stringConstant', token, self._file_line) )
                    token = ''
                    continue
                else:
                    token += ch
                    continue

            elif (ch == ' ') or (ch in self._sybmols) or (ch == '"'):
                if   token in self._keywords:
                    tokens.append( ('keyword', token, self._file_line) )
                elif token in self._sybmols:
                    tokens.append( ('symbol', token, self._file_line) )
                elif self._is_int(token):
                    if int(token) > self._max_int:
                        raise ValueError("File {}, line number {}: integer can't be bigger than {}"
                                         .format(self._file_name, self._file_line, self._max_int))
                    tokens.append( ('integerConstant', token, self._file_line) )
                elif (token) and (not self._is_int(token[0])):
                    tokens.append( ('identifier', token, self._file_line) )
                elif token:
                    raise SyntaxError("File {}, line number {}: invalid syntax befor the character {}"
                                      .format(self._file_name, self._file_line, ch))

                if ch == '"':
                    self._in_srting = True
                elif ch in self._sybmols:
                    if   ch == '<': ch = '&lt;'
                    elif ch == '>': ch = '&gt;'
                    elif ch == '&': ch = '&amp;'
                    tokens.append( ('symbol', ch, self._file_line) )
                token = ''
            else:
                token += ch
        return tokens

    # --------------- Helper functions

    def _delete_multi_comment(self, line_str):
        """
        Deletes multi-line comments from the given line.
        args:
            line_str: string from a Jack file
        ret:
            None:   if multi-line comment
            string: containing tokens and white spaces
        """
        if '/*' in line_str:
            if self._in_comment:
                raise SyntaxError('File {}, line number {}: a comment inside another comment.'
                                  .format(self._file_name, self._file_line))
            if '*/' not in line_str:
                self._in_comment = True
            return None

        if '*/' in line_str:
            if self._in_comment:
                self._in_comment = False
            else:
                raise SyntaxError('File {}, line number {}: end of a comment without beginning of a comment.'
                                  .format(self._file_name, self._file_line))
            return None

        if self._in_comment:
            return None
        else:
            return line_str

    def _purify(self, line_str):
        """
        This function removes end of line character, comments, and emty space at
        the beginning and end of the command.
        args:
            line_str: string from a Jack file
        ret:
            None:   if only comments or multi-line comment
            string: line_str without any comments
        """
        string = self._delete_multi_comment(line_str)
        if not string:
            return None

        string = string.strip('\n')
        string = string.strip()
        comment_idx = string.find('//')
        if   comment_idx == 0:
            return None
        elif comment_idx == -1:
            return string.strip()
        else:
            return string[0:comment_idx].strip()

    def _is_int(self, string):
        """
        args:
            string
        ret:
            boolean depending if string represents an integer
        """
        try:
            int(string)
        except ValueError:
            return False
        return True
