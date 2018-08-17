import os.path
from sys import argv

from Parser import Parser
from CodeGenerator import CodeGenerator

# ========================= VM_Translator

if __name__ == "__main__":
    path = argv[1]
    file_names = []

    if   os.path.isfile(path):
        path, src_file = os.path.split(path)
        if not src_file.endswith('.vm'):
            raise ValueError("The file has to end with '.vm' extension.")
        f_name = src_file.split('.')[0]
        file_names.append(f_name)
        dst_file = f_name+'.asm'
        bootstrap = False

    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith('.vm'):
                f_name = file.split('.')[0]
                file_names.append(f_name)
        if len(file_names) == 0:
            raise ValueError("No files having '.vm' extension in the given directory.")
        if path[-1] == os.sep:          # in case path ends with an os separator (i.e. 'os.sep')
            dst_file = os.path.basename(path[:-1])
        else:
            dst_file = os.path.basename(path)
        dst_file += '.asm'
        bootstrap = True

    dst_file = open(os.path.join(path, dst_file), 'w+')

    parser = Parser()
    generator = CodeGenerator()

    bootstrap_code = ''
    if bootstrap:
        parsed_line = parser.parse('call Sys.init 0')
        bootstrap_code += '@256\n' + 'D=A\n' + '@SP\n' + 'M=D\n'
        bootstrap_code += generator.generate_code(parsed_line)
    dst_file.write(bootstrap_code)

    for f_name in file_names:
        generator.set_new_file_name(file_name=f_name)
        src_file = open(os.path.join(path, f_name+'.vm'), 'r')
        src_line = src_file.readline()
        while src_line:
            parsed_line = parser.parse(src_line)
            if parsed_line:
                output_code = generator.generate_code(parsed_line)
                # print(output_code)
                dst_file.write(output_code)
            src_line = src_file.readline()
        src_file.close()
    dst_file.close()
