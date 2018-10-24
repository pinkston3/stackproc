from __future__ import absolute_import
from __future__ import print_function


class Program:
    def __init__(self, instructions, labels, errors):
        self.instructions = instructions
        self.labels = labels
        self.errors = errors

    def has_errors(self):
        return len(self.errors) > 0

    def has_label(self, label):
        return label in self.labels

    def resolve_label(self, label):
        return self.labels[label]

    def get_instruction(self, program_counter):
        return self.instructions[program_counter]

    def print(self):
        inv_labels = {v : k for k, v in self.labels.items()}
        for i in range(len(self.instructions)):
            if i in inv_labels:
                print(inv_labels[i] + ':')

            print('\t%s' % self.instructions[i])


def process_line(line):
    # Strip any comment that appears on the line
    i = line.find('#')
    if i != -1:
        line = line[:i]

    # Strip whitespace
    line = line.strip()

    return line


INSTRUCTIONS_0_ARG = ['ADD', 'SUB', 'AND', 'OR', 'NOT', 'XOR',
    'SHL', 'SHR', 'DUP', 'SWAP', 'DROP', 'TO_RS', 'FROM_RS', 'RET']
INSTRUCTIONS_1_ARG = ['LIT', 'JMP', 'JZ', 'JNZ', 'CALL']
INSTRUCTIONS_LABELS = ['JMP', 'JZ', 'JNZ', 'CALL']
ALL_INSTRUCTIONS = INSTRUCTIONS_0_ARG + INSTRUCTIONS_1_ARG

def load_program(filename):
    with open(filename) as f:
        lines = f.readlines()

    labels = {}
    program = []
    errors = []

    # Make a first pass to look for syntax errors, and to find all labels

    for line_no in range(len(lines)):
        line = lines[line_no]
        line = process_line(line)

        if len(line) == 0:
            continue

        if line[-1] == ':':
            # This is a label.
            label = line[:-1].strip()
            labels[label] = len(program)

        else:
            # This is an instruction.
            # Add the instruction to the program regardless of whether it is
            # valid or not, so that we can compute correct label offsets.
            # We will analyze the validity of instructions in the next pass.
            program.append(line)

    # Once we get here, we can make a second pass and resolve labels

    for line_no in range(len(lines)):
        line = lines[line_no]
        line = process_line(line)

        if len(line) == 0:
            continue

        if line[-1] == ':':
            # This is a label.  We did these in the previous pass.
            continue

        else:
            # This is an instruction.
            parts = line.split()
            opcode = parts[0].upper()

            # Make sure the opcode is valid
            if opcode not in ALL_INSTRUCTIONS:
                errors.append('Line %d:  opcode %s is unrecognized' % \
                    ((line_no + 1), opcode))
                continue

            elif opcode in INSTRUCTIONS_0_ARG and len(parts) != 1:
                errors.append('Line %d:  opcode %s takes no arguments' % \
                    ((line_no + 1), opcode))
                continue

            elif opcode in INSTRUCTIONS_1_ARG and len(parts) != 2:
                errors.append('Line %d:  opcode %s takes one argument' % \
                    ((line_no + 1), opcode))
                continue

            if opcode == 'LIT':
                # The argument should be an integer.
                try:
                    val = int(parts[1])
                except ValueError:
                    errors.append('Line %d:  LIT operand must be an int ' \
                        '(got %s)' % ((line_no + 1), parts[1]))

            elif opcode in INSTRUCTIONS_LABELS:
                if parts[1] not in labels:
                    errors.append('Line %d:  label %s not found' % \
                        ((line_no + 1), parts[1]))

    return Program(program, labels, errors)


