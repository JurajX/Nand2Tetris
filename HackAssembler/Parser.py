# ========================= Parser CLASS

class Parser(object):
    """
    Parser for Hack Assembler
    """
    def __init__(self):
        self.prev_cmd_line = -1
        self.prev_file_line = -1

    def reset(self):
        """
        Resets the command line to 0.
        """
        self.prev_cmd_line = -1
        self.prev_file_line = -1


    def _purify(self, line_str):
        """
        This function removes all spaces and comments.
        """
        string = line_str.replace(" ", "").strip('\n')
        comment_idx = string.find('//')
        if comment_idx == -1:
            return string
        elif comment_idx == 0:
            return None
        else:
            return string[0:comment_idx]


    def parse(self, line_str):
        """
        args:
          - line    strings to be parsed
        ret:
          - type    of command:
                            None for comment, white space
                            'JS' for jump symbol, i.e. (LOOP)
                            'A'  for A-instruction (@XXX)
                            'C'  for C-instruction (dest = comp; jump)
          - key     key value           (for jump instruction, i.e. (LOOP))
          - adrs    address/jump line   (if A instruction or jump symbol)
          - dest    destination         (if C instruction)
          - comp    commputation        (if C instruction)
          - jump    jump directive      (if C instruction)
          - fline   file line           (used for reporting errors)
        """
        string = self._purify(line_str)
        self.prev_file_line +=1
        if not string: # if string is empty or None
            return [None, None, None, None, None, None, self.prev_file_line]
        elif string[0] == '(':
            idx = string.find(')')
            if idx == -1:
                raise SyntaxError("Missing ')' in the Jump symbol on the line {}.".format(self.prev_file_line))
            key = string[1:idx]
            type = 'JS'
            adrs = str(self.prev_cmd_line + 1)
            return [type, key, adrs, None, None, None, self.prev_file_line]
        elif string[0]=='@':
            type = 'A'
            adrs = string[1:]
            self.prev_cmd_line += 1
            return [type, None, adrs, None, None, None, self.prev_file_line]
        else:
            jmp_idx = string.find(';')
            if jmp_idx == -1:
                jmp_idx = len(string)
                jump = None
            else:
                jump = string[jmp_idx+1:]

            eq_idx = string.find('=')
            if eq_idx == -1:
                dest = None
                comp = string[0:jmp_idx]
            else:
                dest = string[0:eq_idx]
                comp = string[eq_idx+1:jmp_idx]
            type = 'C'
            self.prev_cmd_line += 1
            return [type, None, None, dest, comp, jump, self.prev_file_line]
