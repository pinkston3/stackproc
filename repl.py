from __future__ import absolute_import
from __future__ import print_function

from stackproc import *
from program import *

import sys
import os.path

try:
    input = raw_input
except NameError:
    pass


def show_help():
    print('Commands:\n')
    print('HELP\n\tShow this help information.\n')
    print('QUIT\nEXIT\n\tExits the program.\n')
    print('LOAD filename.sm\n\tLoad the instructions in the specified file.\n')
    print('DEBUG\n\tTurn on debug output during execution.\n')
    print('NODEBUG\n\tTurn off debug output during execution.\n')
    print('All stack processor instructions may be invoked as well, but')
    print('CALL/JZ/JNZ/JMP/RET instructions won\'t work unless a program')
    print('is loaded.')


def process_command(cmd, proc, verbose=False):
    parts = cmd.split()
    operation = parts[0].upper()

    if operation == 'LOAD':
        try:
            program = load_program(parts[1])
            if program.has_errors():
                print('Program contains errors!')
                for err in program.errors:
                    print(err)
            else:
                print('Loaded program from %s' % parts[1])
                program.print()
                print()

                proc.set_program(program)
        except Exception as e:
            print('ERROR:  Couldn\'t load file %s' % parts[1])
            print(e)

    elif operation == 'RESET':
        print('Resetting processor.')
        proc.reset()

    else:
        if operation == 'CALL':
            try:
                proc.execute(cmd)

                while type(proc.program_counter) != StopExecution:
                    if verbose:
                        proc.print_state()
                        print()

                    proc.execute_next()

            except Exception as e:
                print('ERROR:  %s' % str(e))
                print('(you may need to RESET the processor)')
        else:
            try:
                proc.execute(cmd)
            except Exception as e:
                print('ERROR:  %s' % str(e))


def usage():
    print('usage: repl.py [program.sm [cmd1 cmd2 ...]]')
    print('\tStarts the stack processor emulator.  Optionally, a program can')
    print('\tbe loaded into the emulator.  If a program is loaded then one or')
    print('\tmore instructions can also be specified on the command-line for')
    print('\texecution.')
    print()
    print('\tprogram.sm - an optional program to load at startup')
    print()
    print('\tcmd1 ... - instructions to run against the processor')


if __name__ == '__main__':
    print('Welcome to the stack processor.')
    print()

    program = None
    commands = []
    if len(sys.argv) > 1:
        program = sys.argv[1]
        if not os.path.isfile(program):
            print("ERROR:  %s is not a file" % program_to_load)
            usage()
            sys.exit(1)

        if len(sys.argv) > 2:
            commands = sys.argv[2:]

    proc = StackProcessor()
    proc.print_state()
    print()

    # Take care of command-line operations

    if program is not None:
        process_command('LOAD ' + program, proc)

    # If commands are specified on the command-line, run them and then exit.
    if len(commands) > 0:
        for cmd in commands:
            process_command(cmd, proc)
            proc.print_state()
            print()

        sys.exit(0)

    # Normal interactive operation.
    verbose = False
    while True:
        cmd = input('> ')
        cmd = cmd.strip()
        if len(cmd) == 0:
            continue

        if cmd.upper() in ['QUIT', 'EXIT']:
            break

        elif cmd.upper() == 'HELP':
            show_help()

        elif cmd.upper() == 'DEBUG':
            print('Turning on debug output')
            verbose = True

        elif cmd.upper() == 'NODEBUG':
            print('Turning off debug output')
            verbose = False

        else:
            process_command(cmd, proc, verbose)
            proc.print_state()
            print()

    print('Goodbye!')

