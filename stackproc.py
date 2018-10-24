from __future__ import absolute_import
from __future__ import print_function


class ExecutionError(Exception):
    pass


class StopExecution(Exception):
    pass


class StackProcessor:
    '''
    A simple implementation of a stack processor in Python, since Donnie
    doesn't feel like writing it in C right now.
    '''

    def __init__(self):
        self.reset()

    def reset(self):
        self.data_stack = []
        self.return_stack = []
        self.program = None
        self.program_counter = StopExecution()

    def set_program(self, program):
        self.program = program
        self.program_counter = StopExecution()

    def check_stack(self, n):
        if len(self.data_stack) < n:
            raise Exception("Data stack must have at least %d values" % n)

    def check_return_stack(self, n):
        if len(self.return_stack) < n:
            raise Exception("Return stack must have at least %d values" % n)

    def check_program(self):
        if self.program is None:
            raise Exception("No program is loaded")

    def check_label(self, label):
        self.check_program()

        if not self.program.has_label(label):
            raise Exception("Program has no label %s" % label)

    def push_data(self, value):
        self.data_stack.append(value)

    def peek_data(self):
        return self.data_stack[-1]

    def pop_data(self):
        return self.data_stack.pop()

    def push_return(self, value):
        self.return_stack.append(value)

    def peek_return(self):
        return self.return_stack[-1]

    def pop_return(self):
        return self.return_stack.pop()

    def can_execute_next(self):
        return (self.program is not None) and \
               (not self.program.has_errors()) and \
               self.program_counter < len(self.program.instructions)

    def update_program_counter(self):
        if type(self.program_counter) == int:
            self.program_counter += 1

    def execute_next(self):
        self.check_program()

        if self.program_counter < 0 or \
           self.program_counter >= len(self.program.instructions):
            raise Exception('Program counter falls outside the loaded program')

        instruction = self.program.instructions[self.program_counter]
        self.execute(instruction)


    def execute(self, instruction, pc_next=None):
        parts = instruction.split()
        opcode = parts[0].upper()

        if pc_next is None:
            if type(self.program_counter) == int:
                pc_next = self.program_counter + 1
            else:
                pc_next = self.program_counter

        if opcode == 'ADD':
            self.check_stack(2)
            self.push_data(self.pop_data() + self.pop_data())
            self.update_program_counter()

        elif opcode == 'SUB':
            self.check_stack(2)
            self.push_data(-self.pop_data() + self.pop_data())
            self.update_program_counter()

        elif opcode == 'AND':
            self.check_stack(2)
            self.push_data(self.pop_data() & self.pop_data())
            self.update_program_counter()

        elif opcode == 'OR':
            self.check_stack(2)
            self.push_data(self.pop_data() | self.pop_data())
            self.update_program_counter()

        elif opcode == 'NOT':
            self.check_stack(1)
            self.push_data(~self.pop_data())
            self.update_program_counter()

        elif opcode == 'XOR':
            self.check_stack(2)
            self.push_data(self.pop_data() ^ self.pop_data())
            self.update_program_counter()

        elif opcode == 'SHL':
            self.check_stack(1)
            self.push_data(self.pop_data() << 1)
            self.update_program_counter()

        elif opcode == 'SHR':
            self.check_stack(1)
            self.push_data(self.pop_data() >> 1)
            self.update_program_counter()

        elif opcode == 'LIT':
            self.push_data(int(parts[1]))
            self.update_program_counter()

        elif opcode == 'DUP':
            self.check_stack(1)
            self.push_data(self.peek_data())
            self.update_program_counter()

        elif opcode == 'SWAP':
            self.check_stack(2)
            a = self.pop_data()
            b = self.pop_data()
            self.push_data(a)
            self.push_data(b)
            self.update_program_counter()

        elif opcode == 'DROP':
            self.check_stack(1)
            self.pop_data()
            self.update_program_counter()

        elif opcode == 'TO_RS':
            self.check_stack(1)
            self.push_return(self.pop_data())
            self.update_program_counter()

        elif opcode == 'FROM_RS':
            self.check_return_stack(1)
            self.push_data(self.pop_return())
            self.update_program_counter()

        elif opcode == 'JMP':
            self.check_label(parts[1])
            self.program_counter = self.program.resolve_label(parts[1])

        elif opcode == 'JZ':
            self.check_stack(1)
            self.check_label(parts[1])
            if (self.pop_data() == 0):
                self.program_counter = self.program.resolve_label(parts[1])
            else:
                self.program_counter += 1

        elif opcode == 'JNZ':
            self.check_stack(1)
            self.check_label(parts[1])
            if (self.pop_data() != 0):
                self.program_counter = self.program.resolve_label(parts[1])
            else:
                self.program_counter += 1

        elif opcode == 'CALL':
            self.check_label(parts[1])
            self.push_return(pc_next)
            self.program_counter = self.program.resolve_label(parts[1])

        elif opcode == 'RET':
            self.check_program()
            self.check_return_stack(1)
            pc_next = self.pop_return()
            self.program_counter = pc_next

        else:
            raise Exception('Unrecognized instruction:  %s' % instruction)

    def stack_to_string(self, stack):
        s = '['
        if len(stack) > 5:
            s += '... '
            stack = stack[-5:]

        first = True
        for v in stack:
            if first:
                first = False
            else:
                s += ' '

            if type(v) == StopExecution:
                s += 'STOP'
            else:
                s += str(v)

        s += ']'

        return s


    def print_state(self):
        print('Data Stack:    %s' % self.stack_to_string(self.data_stack))
        print('Return Stack:  %s' % self.stack_to_string(self.return_stack))

        if self.program is not None and type(self.program_counter) == int:
            print('Program Counter:  %s\t\tInstruction:  %s' % \
                (self.program_counter,
                self.program.instructions[self.program_counter]))
        else:
            print('Program Counter:  STOP')

