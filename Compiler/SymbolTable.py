# ========================= SymbolTable CLASS

class SymbolTable(object):
    """
    Symbol table for the CompilationEngine of the Jack compiler.
    """
    def __init__(self):
        self._file_name = ''
        self._class_table = {}
        self._subroutine_table = {}
        self._static_count = 0
        self._field_count = 0
        self._arg_count = 0
        self._var_count = 0

    def reset(self, file_name):
        """
        Resets both class and subroutine table, sets a new file name, and sets
        counters to zero.
        args:
            file_name: (str) name of a new Jack file.
        """
        self._file_name = file_name
        self._class_table = {}
        self._subroutine_table = {}
        self._static_count = 0
        self._field_count = 0
        self._arg_count = 0
        self._var_count = 0

    def resetSubroutine(self, subroutine_kind):
        """
        Resets only subroutine table, sets var counter to zero and arg counter
        to one if subroutine is method else to zero.
        args:
            subroutine_kind: (str) method, constructor or function
        """
        self._subroutine_table = {}
        if subroutine_kind == 'method':
            self._arg_count = 1
        else:
            self._arg_count = 0
        self._var_count = 0

    def define(self, name, type, kind, line_number):
        """
        Adds a variable to the symbol table. If the variable already exists an
        exception is raised. Static and field variables are added to te class
        table, arg and local variables to the subroutine table.
        args:
            name:        (str) name of the variable to be added
            type:        (str) built-in type or object type
            kind:        (str) one of static, field, arg or local
            line_number: (int) current line number of a Jack file being compiled
        """
        if   kind == 'static':
            if name not in self._class_table:
                index = self._static_count
                self._static_count += 1
                self._class_table[name] = {'type': type, 'kind': kind, 'index': index}
        elif kind == 'field':
            if name not in self._class_table:
                index = self._field_count
                self._field_count += 1
                self._class_table[name] = {'type': type, 'kind': kind, 'index': index}
        elif kind == 'arg':
            if name not in self._subroutine_table:
                index = self._arg_count
                self._arg_count += 1
                self._subroutine_table[name] = {'type': type, 'kind': kind, 'index': index}
        elif kind == 'local':
            if name not in self._subroutine_table:
                index = self._var_count
                self._var_count += 1
                self._subroutine_table[name] = {'type': type, 'kind': kind, 'index': index}
        else:
            raise NameError("File {}, line number {}: variable '{}' already declared."
                            .format(self._file_name, line_number, name))

    def varCount(self, kind):
        """
        Returns number of variables in the symbol table of a given kind.
        args:
            kind: (str) one of static, field, arg or local
        """
        if   kind == 'static': return self._static_count
        elif kind == 'field':  return self._field_count
        elif kind == 'arg':    return self._arg_count
        elif kind == 'local':  return self._var_count

    def kindOf(self, name, line_number):
        """
        Returns the kind of a given variable. Unknown variables raise an exception.
        args:
            name:        (str) name of the variable to be added
            line_number: (int) current line number of a Jack file being compiled
        """
        if name in self._subroutine_table:
            return self._subroutine_table[name]['kind']
        elif name in self._class_table:
            return self._class_table[name]['kind']
        else:
            raise NameError("File {}, line number {}: variable {} not found."
                            .format(self._file_name, line_number, name))

    def typeOf(self, name, line_number):
        """
        Returns the type of a given variable. Unknown variables raise an exception.
        args:
            name:        (str) name of the variable to be added
            line_number: (int) current line number of a Jack file being compiled
        """
        if name in self._subroutine_table:
            return self._subroutine_table[name]['type']
        elif name in self._class_table:
            return self._class_table[name]['type']
        else:
            raise NameError("File {}, line number {}: variable {} not found."
                            .format(self._file_name, line_number, name))

    def indexOf(self, name, line_number):
        """
        Returns the index of a given variable. Unknown variables raise an exception.
        args:
            name:        (str) name of the variable to be added
            line_number: (int) current line number of a Jack file being compiled
        """
        if name in self._subroutine_table:
            return self._subroutine_table[name]['index']
        elif name in self._class_table:
            return self._class_table[name]['index']
        else:
            raise NameError("File {}, line number {}: variable {} not found."
                            .format(self._file_name, line_number, name))
