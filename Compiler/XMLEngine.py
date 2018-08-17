# ========================= XMLEngine CLASS

class XMLEngine(object):
    """
    XMLEngine for the Jack compiler.
    """
    def __init__(self):
        self._subroutines  = ['constructor', 'function', 'method']
        self._classVarDec  = ['field', 'static']
        self._types        = ['int', 'char', 'boolean']
        self._keywordConst = ['true', 'false', 'null', 'this']
        self._statements   = ['let', 'if', 'while', 'do', 'return']
        self._ops          = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
        self._unitary_ops  = ['-', '~']
        self._file_name    = ''

    def set_new_file_name(self, file_name):
        """
        Sets the name of the compiled Jack file, used in exception messages.
        args:
            file_name: (str) name of a new Jack file.
        """
        self._file_name = file_name

    def compile(self, tokens):
        """
        Compiles given tokens into a xml commands. Tokens must contain an
        entire class.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        value for:
          - tokens_kind (str) is one of the following:
            stringConstant, integerConstant, keyword, symbol, identifier
          - token (str) is an element of Jack syntax
          - file_line (int) is the line of the jack file on which the token is located
        ret:
            string containing xml commands from the given tokens
        """
        tokens.reverse()
        compiled_cmds = []
        if tokens[-1][1] == 'class':
            compiled_cmds.append('<class>')
            compiled_cmds += self._compile_class(tokens)
            compiled_cmds.append('</class>')
        return compiled_cmds

    # --------------- Helper functions

    def _generate_cmd(self, tokens):
        """
        Generates xml command from the last token in tokens.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string containing a xml command
        """
        token = tokens.pop()
        return '<'+token[0]+'> '+token[1]+' </'+token[0]+'>'

    def _generate_cmd_if(self, cond, tokens, error_msg):
        """
        Generates xml command from the last token in tokens if cond is true.
        Raise SyntaxError otherwise.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string containing a xml command
        """
        token = tokens.pop()
        if cond:
            return '<'+token[0]+'> '+token[1]+' </'+token[0]+'>'
        else:
            raise SyntaxError("File {}, file line {}: {}."
                              .format(self._file_name, token[2], error_msg))

    # --------------- Function _compile_class

    def _compile_class(self, tokens):
        """
        Compiles the class contained in the tokens.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing the whole class to be writen in a
            .xml file
        """
        cmds = []
        cmds.append( self._generate_cmd(tokens) )
        cond = tokens[-1][0] == 'identifier'
        cmds.append( self._generate_cmd_if(cond, tokens, "invalid class name") )
        cond = tokens[-1][1] == '{'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '{' after the class name"))
        cmds += self._compile_classVarDec(tokens)
        cmds += self._compile_subroutineDec(tokens)
        cond = tokens[-1][1] == '}'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '}' after the class"))
        return cmds

    # --------------- Functions used in _compile_class

    def _compile_classVarDec(self, tokens):
        """
        Compiles a variable declaration part of a class.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing a variable declaration part of
            a class
        """
        cmds = []
        while tokens[-1][1] in self._classVarDec:
            cmds.append('<classVarDec>')
            cmds.append( self._generate_cmd(tokens) )
            cond = (tokens[-1][1] in self._types) or (tokens[-1][0] == 'identifier')
            cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing class variable type") )
            while (tokens[-1][1] != ';'):
                cond = tokens[-1][0] == 'identifier'
                cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing class variable name") )
                if (tokens[-1][1] == ',') and (tokens[-2][1] != ';'):
                    cmds.append( self._generate_cmd(tokens) )
            cmds.append( self._generate_cmd(tokens) )
            cmds.append('</classVarDec>')
        return cmds

    def _compile_subroutineDec(self, tokens):
        """
        Compile all subroutines of a class.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing subroutines of a class
        """
        cmds = []
        while tokens[-1][1] in self._subroutines:
            cmds.append('<subroutineDec>')
            cmds.append( self._generate_cmd(tokens) )
            cond = tokens[-1][1] in (self._types + ['void']) or tokens[-1][0] == 'identifier'
            cmds.append( self._generate_cmd_if(cond, tokens, "invalid subroutine type") )
            cond = tokens[-1][0] == 'identifier'
            cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing subroutine name") )
            cond = tokens[-1][1] == '('
            cmds.append( self._generate_cmd_if(cond, tokens, "missing bracket '('") )
            cmds += self._compile_parameterList(tokens)
            cond = tokens[-1][1] == ')'
            cmds.append( self._generate_cmd_if(cond, tokens, "missing bracket ')'") )
            cmds += self._compile_subroutineBody(tokens)
            cmds.append('</subroutineDec>')
        return cmds

    # --------------- Functions used in _compile_subroutineDec

    def _compile_parameterList(self, tokens):
        """
        Compiles the parameter list of a subroutine.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml code representing the parameter list of a subroutine
        """
        cmds = []
        cmds.append('<parameterList>')
        while tokens[-1][1] != ')':
            cond = (tokens[-1][1] in self._types) or (tokens[-1][0] == 'identifier')
            cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing parameter type"))
            cond = tokens[-1][0] == 'identifier'
            cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing parameter name"))
            if (tokens[-1][1] == ',') and (tokens[-2][1] != ')'):
                cmds.append( self._generate_cmd(tokens) )
        cmds.append('</parameterList>')
        return cmds

    def _compile_subroutineBody(self, tokens):
        """
        Compiles the body a subroutine.
        args:
            tokens:          list of sets, the format of a set is
                             ( tokens_kind, token, file_line )
            subroutine_name: (str) identifier
            subroutine_type: (str) int, char, boolean, void or identifier
            subroutine_kind: (str) constructor, function or method
        ret:
            list of xml commands representing the subroutine's body
        """
        cmds = []
        cmds.append('<subroutineBody>')
        cond = tokens[-1][1] == '{'
        cmds.append( self._generate_cmd_if(cond, tokens,
                                           "missing '{' after the subroutine declaration"))
        cmds += self._compile_varDec(tokens)
        cmds += self._compile_statements(tokens)
        cond = tokens[-1][1] == '}'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '}' at the end of subroutine"))
        cmds.append('</subroutineBody>')
        return cmds

    # --------------- Functions used in _compile_subroutineBody

    def _compile_varDec(self, tokens):
        """
        Compiles the variable declarations of a subroutine.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing the variable list of a subroutine
        """
        cmds = []
        while tokens[-1][1] == 'var':
            cmds.append('<varDec>')
            cmds.append( self._generate_cmd(tokens) )
            cond = (tokens[-1][1] in self._types) or (tokens[-1][0] == 'identifier')
            cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing variable type") )
            while (tokens[-1][1] != ';'):
                cond = tokens[-1][0] == 'identifier'
                cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing variable name") )
                if (tokens[-1][1] == ',') and (tokens[-2][1] != ';'):
                    cmds.append( self._generate_cmd(tokens) )
            cmds.append( self._generate_cmd(tokens) )
            cmds.append('</varDec>')
        return cmds

    def _compile_statements(self, tokens):
        """
        Compiles Jack statements.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing the Jack statements
        """
        cmds = []
        cmds.append('<statements>')
        while tokens[-1][1] in self._statements:
            if   tokens[-1][1] == 'let':    cmds += self._compile_letStatement(tokens)
            elif tokens[-1][1] == 'if':     cmds += self._compile_ifStatement(tokens)
            elif tokens[-1][1] == 'while':  cmds += self._compile_whileStatement(tokens)
            elif tokens[-1][1] == 'do':     cmds += self._compile_doStatement(tokens)
            elif tokens[-1][1] == 'return': cmds += self._compile_returnStatement(tokens)
        cmds.append('</statements>')
        return cmds

    # --------------- Functions used in _compile_statements

    def _compile_letStatement(self, tokens):
        """
        Compiles let statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing let statement
        """
        cmds = []
        cmds.append('<letStatement>')
        cmds.append( self._generate_cmd(tokens) )
        cond = tokens[-1][0] == 'identifier'
        cmds.append( self._generate_cmd_if(cond, tokens, "wrong or missing variable name") )
        if tokens[-1][1] == '[':
            cmds.append( self._generate_cmd(tokens) )
            cmds += self._compile_expression(tokens)
            cond = tokens[-1][1] == ']'
            cmds.append( self._generate_cmd_if(cond, tokens, "missing ']'") )
        cond = tokens[-1][1] == '='
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '=' in the let statement") )
        cmds += self._compile_expression(tokens)
        cond = tokens[-1][1] == ';'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing ';' in the let statement") )
        cmds.append('</letStatement>')
        return cmds

    def _compile_ifStatement(self, tokens):
        """
        Compiles if statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing if statement
        """
        cmds = []
        cmds.append('<ifStatement>')
        cmds.append( self._generate_cmd(tokens) )
        cond =  tokens[-1][1] == '('
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '(' in the if statement") )
        cmds += self._compile_expression(tokens)
        cond = tokens[-1][1] == ')'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing ')' in the if statement") )
        cond = tokens[-1][1] == '{'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '{' in the if statement") )
        cmds += self._compile_statements(tokens)
        cond = tokens[-1][1] == '}'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '}' in the if statement") )
        if tokens[-1][1] == 'else':
            cmds.append( self._generate_cmd(tokens) )
            cond = tokens[-1][1] == '{'
            cmds.append( self._generate_cmd_if(cond, tokens, "missing '{' in the else statement") )
            cmds += self._compile_statements(tokens)
            cond = tokens[-1][1] == '}'
            cmds.append( self._generate_cmd_if(cond, tokens, "missing '}' in the else statement") )
        cmds.append('</ifStatement>')
        return cmds

    def _compile_whileStatement(self, tokens):
        """
        Compiles while statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing while statement
        """
        cmds = []
        cmds.append('<whileStatement>')
        cmds.append( self._generate_cmd(tokens) )
        cond = tokens[-1][1] == '('
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '(' in the while statement") )
        cmds += self._compile_expression(tokens)
        cond = tokens[-1][1] == ')'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing ')' in the while statement") )
        cond = tokens[-1][1] == '{'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '{' in the while statement") )
        cmds += self._compile_statements(tokens)
        cond = tokens[-1][1] == '}'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '}' in the while statement") )
        cmds.append('</whileStatement>')
        return cmds

    def _compile_doStatement(self, tokens):
        """
        Compiles do statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing do statement
        """
        cmds = []
        cmds.append('<doStatement>')
        cmds.append( self._generate_cmd(tokens) )
        cmds += self._compile_subroutineCall(tokens)
        cond = tokens[-1][1] == ';'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing ';' in the do statement") )
        cmds.append('</doStatement>')
        return cmds

    def _compile_returnStatement(self, tokens):
        """
        Compiles return statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing return statement
        """
        cmds = []
        cmds.append('<returnStatement>')
        cmds.append( self._generate_cmd(tokens) )
        if tokens[-1][1] != ';':
            cmds += self._compile_expression(tokens)
        cond = tokens[-1][1] == ';'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing ';' in the return statement") )
        cmds.append('</returnStatement>')
        return cmds

    # --------------- _compile_subroutineCall

    def _compile_subroutineCall(self, tokens):
        """
        Compiles a subroutine call.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing a subroutine call
        """
        cmds = []
        cond = tokens[-1][0] == 'identifier'
        cmds.append( self._generate_cmd_if(cond, tokens,
                                           "wrong or missing identifier in subroutineCall") )
        if tokens[-1][1] == '.':
            cmds.append( self._generate_cmd(tokens) )
            cond = tokens[-1][0] == 'identifier'
            cmds.append( self._generate_cmd_if(cond, tokens,
                                               "wrong or missing identifier in subroutineCall") )
        cond = tokens[-1][1] == '('
        cmds.append( self._generate_cmd_if(cond, tokens, "missing '(' in subroutineCall") )
        cmds += self._compile_expressionList(tokens)
        cond = tokens[-1][1] == ')'
        cmds.append( self._generate_cmd_if(cond, tokens, "missing ')' in subroutineCall") )
        return cmds

    def _compile_expressionList(self, tokens):
        """
        Compiles an expression list.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing an expression list
        """
        cmds = []
        cmds.append('<expressionList>')
        while tokens[-1][1] != ')':
            cmds += self._compile_expression(tokens)
            if (tokens[-1][1] == ',') and (tokens[-2][1] != ')'):
                cmds.append( self._generate_cmd(tokens) )
        cmds.append('</expressionList>')
        return cmds

    # --------------- _compile_expression

    def _compile_expression(self, tokens):
        """
        Compiles an expression.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing an expression
        """
        cmds = []
        cmds.append('<expression>')
        cmds += self._compile_term(tokens)
        while tokens[-1][1] in self._ops:
            cmds.append( self._generate_cmd(tokens) )
            cmds += self._compile_term(tokens)
        cmds.append('</expression>')
        return cmds

    def _compile_term(self, tokens):
        """
        Compiles a term.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            list of xml commands representing a term
        """
        cmds = []
        cmds.append('<term>')
        cond1 = tokens[-1][0] in ['integerConstant', 'stringConstant']
        cond2 = tokens[-1][1] in self._keywordConst
        if   cond1 or cond2:
            cmds.append( self._generate_cmd(tokens) )
        elif tokens[-1][1] == '(':
            cmds.append( self._generate_cmd(tokens) )
            cmds += self._compile_expression(tokens)
            cond = tokens[-1][1] == ')'
            cmds.append( self._generate_cmd_if(cond, tokens, "missing ')' in the expression") )
        elif tokens[-1][1] in self._unitary_ops:
            cmds.append( self._generate_cmd(tokens) )
            cmds += self._compile_term(tokens)
        elif tokens[-1][0] == 'identifier':
            if   tokens[-2][1] == '[':
                cmds.append( self._generate_cmd(tokens) )
                cmds.append( self._generate_cmd(tokens) )
                cmds += self._compile_expression(tokens)
                cond = tokens[-1][1] == ']'
                cmds.append( self._generate_cmd_if(cond, tokens, "missing ']'") )
            elif tokens[-2][1] in ['(', '.']:
                cmds += self._compile_subroutineCall(tokens)
            elif tokens[-2][1] in (self._ops + [';', ')', ']', ',']):
                cmds.append( self._generate_cmd(tokens) )
            else: raise SyntaxError("File {}, file line {}: suitable term not found."
                                    .format(self._file_name, tokens[-1][2]))
        else: raise SyntaxError("File {}, file line {}: suitable term not found."
                                .format(self._file_name, tokens[-1][2]))
        cmds.append('</term>')
        return cmds
