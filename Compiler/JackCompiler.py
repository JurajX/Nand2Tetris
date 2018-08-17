import os.path
import copy
from sys import argv

from JackTokeniser import JackTokeniser
from XMLEngine import XMLEngine
from CompilationEngine import CompilationEngine

# ========================= VM_Translator

if __name__ == "__main__":
    path = argv[1]
    file_names = []
    # set to False in case you don't want to output tokens (project 10) in .xml file
    output_tokens_in_xml_file = False
    # set to False in case you don't want to output commands (project 10) in .xml file
    output_comds_in_xml_file = False
    # set to False in case you don't want to output commands (project 11) in .vm file
    output_comds_in_vm_file = True

    if   os.path.isfile(path):
        path, src_file = os.path.split(path)
        if not src_file.endswith('.jack'):
            raise ValueError("The file has to end with '.vm' extension.")
        f_name = src_file.split('.')[0]
        file_names.append(f_name)

    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith('.jack'):
                f_name = file.split('.')[0]
                file_names.append(f_name)
        if len(file_names) == 0:
            raise ValueError("No files having '.jack' extension in the given directory.")

    tokeniser = JackTokeniser()
    xml_engine = XMLEngine()
    compilation_engine = CompilationEngine()

    for f_name in file_names:
        tokeniser.set_new_file_name(f_name+'.jack')
        xml_engine.set_new_file_name(f_name+'.jack')
        compilation_engine.set_new_file_name(f_name+'.jack')

        tokens = []
        src_file = open(os.path.join(path, f_name+'.jack'), 'r')
        src_line = src_file.readline()

        # get tokens from an input file
        while src_line:
            toks = tokeniser.tokenise(src_line)
            src_line = src_file.readline()
            if toks: tokens += toks

        # if desired, output tokens in a .xml file
        if output_tokens_in_xml_file:
            output_tokens = '<tokens>\n'
            for token in tokens: output_tokens += '<'+token[0]+'> '+ token[1] + ' </'+token[0]+'>\n'
            output_tokens += '</tokens>\n'
            token_file = open(os.path.join(path, f_name+'_T.xml'), 'w+')
            token_file.write(output_tokens)
            token_file.close()

        # if desired, output commands in a .xml file
        if output_comds_in_xml_file:
            # deepcopy needed since xml_engine pops from the list of tokens
            tokens_copy = copy.deepcopy(tokens)
            xml_cmds = xml_engine.compile(tokens_copy)
            xml_cmd_file = open(os.path.join(path, f_name+'_C.xml'), 'w+')
            for command in xml_cmds:
                xml_cmd_file.write(command+'\n')
            xml_cmd_file.close()

        # if desired, output commands in a .vm file
        if output_comds_in_vm_file:
            # compilation_engine also pops from the list of tokens
            vm_commands = compilation_engine.compile(tokens)
            vm_file = open(os.path.join(path, f_name+'.vm'), 'w+')
            vm_file.write(vm_commands)
            vm_file.close()
