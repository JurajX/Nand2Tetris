import os.path
from sys import argv

from Parser import Parser
from CodeGenerator import CodeGenerator

# ========================= Parser CLASS

if __name__ == "__main__":

    path = argv[1]
    if not os.path.isfile(path):
        raise ValueError("Provided argument is not a file.")
    if not path.endswith('.asm'):
        raise ValueError("The file has to end with '.asm' extension.")

    path, src_file = os.path.split(path)
    f_name = src_file.split('.')[0]
    dst_file = f_name+'.hack'

    src_file = open(os.path.join(path, src_file), 'r')
    dst_file = open(os.path.join(path, dst_file), 'w+')

    parser = Parser()
    generator = CodeGenerator()

    parsed_lines = []
    src_line = src_file.readline()

    while src_line:
        parsed_line = parser.parse(src_line)
        if parsed_line[0]:
            if parsed_line[0] == 'JS':
                generator.add_jump_symb(key=parsed_line[1], value=parsed_line[2], file_line=parsed_line[6])
            else:
                parsed_lines.append(parsed_line)
        src_line = src_file.readline()


    for parsed_line in parsed_lines:
        output_line = generator.generate_code(parsed_line)
        dst_file.write(output_line+'\n')

    dst_file.close()
    src_file.close()
