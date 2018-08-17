# ========================= Parser CLASS

class CodeGenerator(object):
    """
    CodeGenerator generates code from parsed input.
    """
    def __init__(self):
        self.next_symbol_address = 16

        self.comp_table = {
        # a-bit = 0
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        # a-bit = 1
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
        }

        self.dest_table = {
        None: "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
        }

        self.jump_table = {
        None: "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
        }

        self.symb_table = {
        "SP":     '{0:015b}'.format(0),
        "LCL":    '{0:015b}'.format(1),
        "ARG":    '{0:015b}'.format(2),
        "THIS":   '{0:015b}'.format(3),
        "THAT":   '{0:015b}'.format(4),
        "R0":     '{0:015b}'.format(0),
        "R1":     '{0:015b}'.format(1),
        "R2":     '{0:015b}'.format(2),
        "R3":     '{0:015b}'.format(3),
        "R4":     '{0:015b}'.format(4),
        "R5":     '{0:015b}'.format(5),
        "R6":     '{0:015b}'.format(6),
        "R7":     '{0:015b}'.format(7),
        "R8":     '{0:015b}'.format(8),
        "R9":     '{0:015b}'.format(9),
        "R10":    '{0:015b}'.format(10),
        "R11":    '{0:015b}'.format(11),
        "R12":    '{0:015b}'.format(12),
        "R13":    '{0:015b}'.format(13),
        "R14":    '{0:015b}'.format(14),
        "R15":    '{0:015b}'.format(15),
        "SCREEN": '{0:015b}'.format(16384),
        "KBD":    '{0:015b}'.format(24576),
        }


    def reset(self):
        self.next_symbol_address = 16


    def add_jump_symb(self, key, value, file_line=None):
        if key not in self.symb_table:
            self.symb_table[key] = '{0:015b}'.format(int(value))
        else:
            raise ValueError("Jump symbol {0} already in the table. File line: {1}.".format(key, file_line))

    def add_adrs_symb(self, key, file_line=None):
        if key not in self.symb_table:
            self.symb_table[key] = '{0:015b}'.format(self.next_symbol_address)
            self.next_symbol_address += 1

    def generate_code(self, parsed_input):
        """
        input:                [ 0     1    2     3     4     5        6    ]
            parsed_input    - [type, key, adrs, dest, comp, jump, file_line]
        """
        if parsed_input[0] == 'A':
            if parsed_input[2].isdigit():
                return "0"+'{0:015b}'.format(int(parsed_input[2]))
            else:
                self.add_adrs_symb(parsed_input[2], parsed_input[6])
                return "0"+self.symb_table[parsed_input[2]]

        elif parsed_input[0] == 'C':
            if parsed_input[4] not in self.comp_table:
                raise SyntaxError('Invalid comp part of the command. File line: {}.'.format(parsed_input[6]))
            elif parsed_input[3] not in self.dest_table:
                raise SyntaxError('Invalid dest part of the command. File line: {}.'.format(parsed_input[6]))
            elif parsed_input[5] not in self.jump_table:
                raise SyntaxError('Invalid jump part of the command. File line: {}.'.format(parsed_input[6]))
            else:
                return "111"+self.comp_table[parsed_input[4]] +self.dest_table[parsed_input[3]] +self.jump_table[parsed_input[5]]
