import copy
from SymbolTable import SymbolTable
from VMEncoder import VMEncoder

# ========================= CompilationEngine CLASS

class CompilationEngine(object):
    """
    CompilationEngine for the Jack compiler.
    """
    def __init__(self):
        self._symbol_table = SymbolTable()
        self._vm_encoder = VMEncoder()
        self._file_name    = ''
        self._class_name   = ''
        self._label_count  = 0

        self._subroutines  = ['constructor', 'function', 'method']
        self._classVarDec  = ['field', 'static']
        self._types        = ['int', 'char', 'boolean']
        self._keywordConst = ['true', 'false', 'null', 'this']
        self._statements   = ['let', 'if', 'while', 'do', 'return']
        self._ops          = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
        self._unitary_ops  = ['-', '~']

    def set_new_file_name(self, file_name):
        """
        Sets the name of the compiled Jack file, used in exception messages.
        Resets label count and class name.
        args:
            file_name: (str) name of a new Jack file.
        """
        self._file_name    = file_name
        self._class_name   = ''
        self._label_count  = 0

    def compile(self, tokens):
        """
        Compiles given tokens into a VM commands. Tokens must contain an
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
            string containing VM commands from the given tokens
        """
        tokens.reverse()
        compiled_cmds = ''
        token = tokens.pop()
        if token[1] == 'class':
            compiled_cmds += self._compile_class(tokens)
        else:
            raise SyntaxError("File {} does not start with a class declaration.".format(self._file_name))
        return compiled_cmds

    # --------------- Helper functions

    def _checkToken(self, tokens, error_msg, idx1=None, neq=None, idx2=None, not_in_list=None):
        """
        Pops a token from tokens. Checkes if (token[idx1] != neq) and
        (token[idx2] not in not_in_list). Either one or both pairs must be given.
        If the condition is true an exception is raised. Returns the popped token.
        args:
            tokens:      list of sets, the format of a set is
                         ( tokens_kind, token, file_line )
            error_msg:   error message to be displayed in the exception
            idx1:        0 or 1
            neq:         (string)
            idx2:        0 or 1
            not_in_list: list of strings
        ret:
            token
        """
        token = tokens.pop()
        if   idx1 is not None and idx2 is None:
            cond = token[idx1] != neq
        elif idx1 is None     and idx2 is not None:
            cond = token[idx2] not in not_in_list
        elif idx1 is not None and idx2 is not None:
            cond = token[idx1] != neq and token[idx2] not in not_in_list
        if cond:
            raise SyntaxError("File {}, file line {}: {}.".format(self._file_name, token[2], error_msg))
        return token

    # --------------- Function _compile_class

    def _compile_class(self, tokens):
        """
        Compiles the class contained in the tokens.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing the whole class to be writen in a
            .vm file
        """
        cmds = ''
        token = self._checkToken(tokens, "invalid class name", idx1=0, neq='identifier')
        self._class_name = token[1]
        token = self._checkToken(tokens, "missing '{' after the class name", idx1=1, neq='{')
        self._compile_classVarDec(tokens)
        cmds += self._compile_subroutines(tokens)
        token = self._checkToken(tokens, "missing '}' at the end of the class", idx1=1, neq='}')
        return cmds

    # --------------- Functions used in _compile_class

    def _compile_classVarDec(self, tokens):
        """
        Compiles a variable declaration part of a class, i.e. adds the class
        variables into the symbol table.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        """
        self._symbol_table.reset(self._file_name)
        while tokens[-1][1] in self._classVarDec:
            token = tokens.pop()
            kind = token[1]
            token = self._checkToken(tokens, "wrong or missing class variable type",
                                     idx1=0, neq='identifier', idx2=1, not_in_list=self._types)
            type = token[1]
            while (tokens[-1][1] != ';'):
                token = self._checkToken(tokens, "wrong or missing class variable name",
                                         idx1=0, neq='identifier')
                name = token[1]
                self._symbol_table.define(name, type, kind, token[2])
                if (tokens[-1][1] == ',') and (tokens[-2][1] != ';'):
                    tokens.pop()
            tokens.pop()

    def _compile_subroutines(self, tokens):
        """
        Compile all subroutines of a class.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing subroutines of a class
        """
        cmds  = ''
        while tokens[-1][1] in self._subroutines:
            subrtn_name, subrtn_type, subrtn_kind = self._compile_subroutineDec(tokens)
            cmds += self._compile_subroutineBody(tokens, subrtn_name, subrtn_type, subrtn_kind)
        return cmds

    # --------------- Functions used in _compile_subroutines

    def _compile_subroutineDec(self, tokens):
        """
        Compiles a subroutine declaration of a class, i.e. add subroutine's
        parameters into the symbolt table, and extract subroutine's name, type,
        and kind.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            subroutine_name: (str) identifier
            subroutine_type: (str) int, char, boolean, void or identifier
            subroutine_kind: (str) constructor, function or method
        """
        token = tokens.pop()
        subroutine_kind = token[1]
        token = self._checkToken(tokens, "invalid subroutine type",
                                 idx1=0, neq='identifier', idx2=1, not_in_list=self._types+['void'])
        subroutine_type = token[1]
        token = self._checkToken(tokens, "wrong or missing subroutine name", idx1=0, neq='identifier')
        subroutine_name = token[1]
        token = self._checkToken(tokens, "missing '(' in the parameter list", idx1=1, neq='(')
        self._compile_parameterList(tokens, subroutine_kind)
        token = self._checkToken(tokens, "missing ')' in the parameter list", idx1=1, neq=')')
        return subroutine_name, subroutine_type, subroutine_kind

    def _compile_subroutineBody(self, tokens, subroutine_name, subroutine_type, subroutine_kind):
        """
        Compiles the body a subroutine.
        args:
            tokens:          list of sets, the format of a set is
                             ( tokens_kind, token, file_line )
            subroutine_name: (str) identifier
            subroutine_type: (str) int, char, boolean, void or identifier
            subroutine_kind: (str) constructor, function or method
        ret:
            string of VM commands representing the subroutine's body
        """
        cmds = ''
        token = self._checkToken(tokens, "missing '{' after the subroutine declaration", idx1=1, neq='{')
        self._compile_varDec(tokens)
        fct_name = self._class_name+'.'+subroutine_name
        nVars = self._symbol_table.varCount('local')
        cmds += self._vm_encoder.encodeFunction(fct_name, nVars)
        if   subroutine_kind == 'constructor':
            number = self._symbol_table.varCount('field')
            cmds += self._vm_encoder.encodePush('const', number)
            cmds += self._vm_encoder.encodeCall('Memory.alloc', 1)
            cmds += self._vm_encoder.encodePop('pointer', 0)
        elif subroutine_kind == 'method':
            cmds += self._vm_encoder.encodePush('arg', 0)
            cmds += self._vm_encoder.encodePop('pointer', 0)
        cmds += self._compile_statements(tokens)
        token = self._checkToken(tokens, "missing '}' at the end of subroutine", idx1=1, neq='}')
        return cmds

    # --------------- Functions used in _compile_subroutineDec

    def _compile_parameterList(self, tokens, subroutine_kind):
        """
        Compiles the parameter list of a subroutine, i.e. adds the arguments into
        the symbol table.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        """
        self._symbol_table.resetSubroutine(subroutine_kind)
        while tokens[-1][1] != ')':

            token = self._checkToken(tokens, "wrong or missing parameter type",
                                     idx1=0, neq='identifier', idx2=1, not_in_list=self._types)
            type = token[1]
            kind = 'arg'
            token = self._checkToken(tokens, "wrong or missing parameter name",
                                     idx1=0, neq='identifier')
            name = token[1]
            self._symbol_table.define(name, type, kind, token[2])
            if (tokens[-1][1] == ',') and (tokens[-2][1] != ')'):
                tokens.pop()

    # --------------- Functions used in _compile_subroutineBody

    def _compile_varDec(self, tokens):
        """
        Compiles the variable declarations of a subroutine, i.e. adds the
        variables into the symbol table.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        """
        kind = 'local'
        while tokens[-1][1] == 'var':
            tokens.pop()
            token = self._checkToken(tokens, "wrong or missing variable type",
                                     idx1=0, neq='identifier', idx2=1, not_in_list=self._types)
            type = token[1]
            while (tokens[-1][1] != ';'):
                token = self._checkToken(tokens, "wrong or missing variable name",
                                         idx1=0, neq='identifier')
                name = token[1]
                self._symbol_table.define(name, type, kind, token[2])
                if (tokens[-1][1] == ',') and (tokens[-2][1] != ';'):
                    tokens.pop()
            tokens.pop()

    def _compile_statements(self, tokens):
        """
        Compiles Jack statements.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing the Jack statements
        """
        cmds = ''
        while tokens[-1][1] in self._statements:
            token = tokens.pop()
            if   token[1] == 'let':    cmds += self._compile_letStatement(tokens)
            elif token[1] == 'if':     cmds += self._compile_ifStatement(tokens)
            elif token[1] == 'while':  cmds += self._compile_whileStatement(tokens)
            elif token[1] == 'do':     cmds += self._compile_doStatement(tokens)
            elif token[1] == 'return': cmds += self._compile_returnStatement(tokens)
        return cmds

    # --------------- Functions used in _compile_statements

    def _compile_letStatement(self, tokens):
        """
        Compiles let statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing let statement
        """
        cmds = ''
        token = self._checkToken(tokens, "wrong or missing variable name", idx1=0, neq='identifier')
        var_name, var_type, var_kind, var_index, var_segment = self._look_up_var(token)
        if tokens[-1][1] == '[':
            cmds += self._compile_array(tokens, var_type, var_index, var_segment)
            token = self._checkToken(tokens, "missing '=' in the let statement", idx1=1, neq='=')
            cmds += self._compile_expression(tokens)
            cmds += self._vm_encoder.encodePop('temp', 0)
            cmds += self._vm_encoder.encodePop('pointer', 1)
            cmds += self._vm_encoder.encodePush('temp', 0)
            cmds += self._vm_encoder.encodePop('that', 0)
        else:
            token = self._checkToken(tokens, "missing '=' in the let statement", idx1=1, neq='=')
            cmds += self._compile_expression(tokens)
            cmds += self._vm_encoder.encodePop(var_segment, var_index)
        token = self._checkToken(tokens, "missing ';' in the let statement", idx1=1, neq=';')
        return cmds

    def _compile_ifStatement(self, tokens):
        """
        Compiles if statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing if statement
        """
        label1 = 'IF_ELSE'+str(self._label_count)
        label2 = 'IF_END'+str(self._label_count)
        self._label_count += 1
        cmds = ''
        token = self._checkToken(tokens, "missing '(' in the if statement", idx1=1, neq='(')
        cmds += self._compile_expression(tokens)
        token = self._checkToken(tokens, "missing ')' in the if statement", idx1=1, neq=')')
        token = self._checkToken(tokens, "missing '{' in the if statement", idx1=1, neq='{')
        cmds += self._vm_encoder.encodeArithmetic('not')
        cmds += self._vm_encoder.encodeIfgoto(label1)
        cmds += self._compile_statements(tokens)
        token = self._checkToken(tokens, "missing '}' in the if statement", idx1=1, neq='}')
        cmds += self._vm_encoder.encodeGoto(label2)
        cmds += self._vm_encoder.encodeLabel(label1)
        if tokens[-1][1] == 'else':
            tokens.pop()
            token = self._checkToken(tokens, "missing '{' in the else statement", idx1=1, neq='{')
            cmds += self._compile_statements(tokens)
            token = self._checkToken(tokens, "missing '}' in the else statement", idx1=1, neq='}')
        cmds += self._vm_encoder.encodeLabel(label2)
        return cmds

    def _compile_whileStatement(self, tokens):
        """
        Compiles while statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing while statement
        """
        label1 = 'WHILE_EXP'+str(self._label_count)
        label2 = 'WHILE_END'+str(self._label_count)
        self._label_count += 1
        cmds = ''
        token = self._checkToken(tokens, "missing '(' in the while statement", idx1=1, neq='(')
        cmds += self._vm_encoder.encodeLabel(label1)
        cmds += self._compile_expression(tokens)
        cmds += self._vm_encoder.encodeArithmetic('not')
        cmds += self._vm_encoder.encodeIfgoto(label2)
        token = self._checkToken(tokens, "missing ')' in the while statement", idx1=1, neq=')')
        token = self._checkToken(tokens, "missing '{' in the while statement", idx1=1, neq='{')
        cmds += self._compile_statements(tokens)
        token = self._checkToken(tokens, "missing '}' in the while statement", idx1=1, neq='}')
        cmds += self._vm_encoder.encodeGoto(label1)
        cmds += self._vm_encoder.encodeLabel(label2)
        return cmds

    def _compile_doStatement(self, tokens):
        """
        Compiles do statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing do statement
        """
        cmds = ''
        cmds += self._compile_subroutineCall(tokens)
        token = self._checkToken(tokens, "missing ';' in the do statement", idx1=1, neq=';')
        cmds += self._vm_encoder.encodePop('temp', 0)
        return cmds

    def _compile_returnStatement(self, tokens):
        """
        Compiles return statement.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing return statement
        """
        cmds = ''
        if tokens[-1][1] != ';':
            cmds += self._compile_expression(tokens)
        else:
            cmds += self._vm_encoder.encodePush('const', 0)
        token = self._checkToken(tokens, "missing ';' in the return statement", idx1=1, neq=';')
        cmds += self._vm_encoder.encodeReturn()
        return cmds

    # --------------- _compile_subroutineCall

    def _compile_subroutineCall(self, tokens):
        """
        Compiles a subroutine call.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing a subroutine call
        """
        cmds = ''
        nArgs = 0
        token = self._checkToken(tokens, "wrong or missing identifier in subroutineCall",
                                 idx1=0, neq='identifier')
        if tokens[-1][1] == '.':
            classORobj_name = token[1]
            tokens.pop()
            token = self._checkToken(tokens, "wrong or missing identifier in subroutineCall",
                                     idx1=0, neq='identifier')
            subroutine_name = token[1]
            try:              type = self._symbol_table.typeOf(classORobj_name, None)
            except NameError: type = None
            if type in ['int', 'boolean', 'char', 'void']:
                raise SyntaxError("File {}, file line {}: build-in type var '{}' has no methods."
                                  .format(self._file_name, token[2], classORobj_name))
            elif type == None:
                class_name = classORobj_name
            else:
                class_name = type
                obj_segment = self._symbol_table.kindOf(classORobj_name, token[2])
                obj_index = self._symbol_table.indexOf(classORobj_name, token[2])
                if obj_segment == 'field': obj_segment = 'this'
                cmds += self._vm_encoder.encodePush(obj_segment, obj_index)
                nArgs = 1
        else:
            class_name = self._class_name
            subroutine_name = token[1]
            cmds += self._vm_encoder.encodePush('pointer', 0)
            nArgs = 1
        token = self._checkToken(tokens, "missing '(' in subroutineCall", idx1=1, neq='(')
        n_temp, cmd_temp = self._compile_expressionList(tokens)
        nArgs += n_temp
        cmds += cmd_temp
        token = self._checkToken(tokens, "missing ')' in subroutineCall", idx1=1, neq=')')
        fct_name = class_name+'.'+subroutine_name
        cmds += self._vm_encoder.encodeCall(fct_name, nArgs)
        return cmds

    def _compile_expressionList(self, tokens):
        """
        Compiles an expression list.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing an expression list
        """
        count = 0
        cmds = ''
        while tokens[-1][1] != ')':
            cmds += self._compile_expression(tokens)
            count += 1
            if (tokens[-1][1] == ',') and (tokens[-2][1] != ')'):
                tokens.pop()
        return count, cmds

    # --------------- _compile_expression

    def _compile_expression(self, tokens):
        """
        Compiles an expression.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing an expression
        """
        cmds = ''
        cmds += self._compile_term(tokens)
        while tokens[-1][1] in self._ops:
            token = tokens.pop()
            operator = token[1]
            cmds += self._compile_term(tokens)
            cmds += self._vm_encoder.encodeArithmetic(operator)
        return cmds

    def _compile_term(self, tokens):
        """
        Compiles a term.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            string of VM commands representing a term
        """
        cmds = ''
        if   tokens[-1][1] in self._keywordConst:
            token = tokens.pop()
            if   token[1] == 'true':
                cmds += self._vm_encoder.encodePush('const', 1)
                cmds += self._vm_encoder.encodeArithmetic('neg')
            elif token[1] in ['false', 'null']:
                cmds += self._vm_encoder.encodePush('const', 0)
            elif token[1] == 'this':
                cmds += self._vm_encoder.encodePush('pointer', 0)
        elif tokens[-1][0] == 'integerConstant':
            token = tokens.pop()
            cmds += self._vm_encoder.encodePush('const', token[1])
        elif tokens[-1][0] == 'stringConstant':
            token = tokens.pop()
            cmds += self._vm_encoder.encodePush('const', len(token[1]))
            cmds += self._vm_encoder.encodeCall('String.new', 1)
            for ch in token[1]:
                cmds += self._vm_encoder.encodePush('const', ord(ch))
                cmds += self._vm_encoder.encodeCall('String.appendChar', 2)
        elif tokens[-1][1] == '(':
            tokens.pop()
            cmds += self._compile_expression(tokens)
            token = self._checkToken(tokens, "missing ')' in the expression", idx1=1, neq=')')
        elif tokens[-1][1] in self._unitary_ops:
            token = tokens.pop()
            cmds += self._compile_term(tokens)
            if   token[1] == '~': cmds += self._vm_encoder.encodeArithmetic('not')
            elif token[1] == '-': cmds += self._vm_encoder.encodeArithmetic('neg')
        elif tokens[-1][0] == 'identifier':
            if   tokens[-2][1] in ['(', '.']:
                cmds += self._compile_subroutineCall(tokens)
            elif tokens[-2][1] == '[':
                token = tokens.pop()
                var_name, var_type, var_kind, var_index, var_segment = self._look_up_var(token)
                cmds += self._compile_array(tokens, var_type, var_index, var_segment)
                cmds += self._vm_encoder.encodePop('pointer', 1)
                cmds += self._vm_encoder.encodePush('that', 0)
            elif tokens[-2][1] in (self._ops + [';', ')', ']', ',']):
                token = tokens.pop()
                var_name = token[1]
                var_name, var_type, var_kind, var_index, var_segment = self._look_up_var(token)
                cmds += self._vm_encoder.encodePush(var_segment, var_index)
            else: raise SyntaxError("File {}, file line {}: suitable term not found."
                                    .format(self._file_name, tokens[-1][2]))
        else: raise SyntaxError("File {}, file line {}: suitable term not found."
                                .format(self._file_name, tokens[-1][2]))
        return cmds

    def _look_up_var(self, token):
        """
        Looks up a variable from token in the symbol table.
        args:
            tokens: list of sets, the format of a set is
                    ( tokens_kind, token, file_line )
        ret:
            var_name:    (str) identifier
            var_type:    (str) int, char, boolean or identifier
            var_kind:    (str) one of static, field, arg or local
            var_index:   (int) index of the variable in the symbol table
            var_segment: (str) one of static, arg, local or this
        """
        var_name = token[1]
        var_type = self._symbol_table.typeOf(var_name, token[2])
        var_kind = self._symbol_table.kindOf(var_name, token[2])
        var_index = self._symbol_table.indexOf(var_name, token[2])
        if var_kind == 'field': var_segment = 'this'
        else:                   var_segment = var_kind
        return var_name, var_type, var_kind, var_index, var_segment

    def _compile_array(self, tokens, var_type, var_index, var_segment):
        """
        Compiles an array of the form 'var_name[expression]'. i.e. puts the
        memory index of the array element on the stack.
        args:
            tokens:      list of sets, the format of a set is
                         ( tokens_kind, token, file_line )
            var_type:    (str) int, char, boolean or identifier
            var_index:   (int) index of the variable in the symbol table
            var_segment: (str) one of static, arg, local or this
        ret:
            string of VM commands putting the memory index of an array on the
            stack
        """
        cmds = ''
        if var_type != 'Array':
            raise SyntaxError("File {}, file line {}: indexing non-Array type."
                              .format(self._file_name, token[2]))
        tokens.pop()            # discard '['
        cmds += self._vm_encoder.encodePush(var_segment, var_index)
        cmds += self._compile_expression(tokens)
        cmds += self._vm_encoder.encodeArithmetic('add')
        token = self._checkToken(tokens, "missing ']'", idx1=1, neq=']')
        return cmds
