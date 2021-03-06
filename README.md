# stackproc

A simple stack processor emulator.

I wrote this emulator for exploring stack processor behavior in some visible
and clear way.  The program implements a Read-Eval-Print Loop for a very
simple stack processor, and it also supports running stack programs from
input files, and single-stepping through a program.

The stack machine follows the basic architecture described in the book "Stack
Computers:  the new wave";
see [section 3.2](http://users.ece.cmu.edu/~koopman/stack_computers/sec3_2.html).

## Instruction Set

Note that the instruction-set is not identical to the one described at the
above link, but it is very close.  A number of extra instructions were
excluded for the sake of simplicity.

| Instruction	| Description	|
| ------------- | ------------- |
| ADD	| Pops two values off of the data stack, and pushes their sum onto the data stack. |
| SUB	| Pops two values off of the data stack, and pushes their difference onto the data stack. |
| AND	| Pops two values off of the data stack, and pushes their bitwise-AND onto the data stack. |
| OR	| Pops two values off of the data stack, and pushes their bitwise-OR onto the data stack. |
| NOT	| Pops a value off of the data stack, and pushes its ones-complement inversion onto the data stack. |
| XOR	| Pops two values off of the data stack, and pushes their bitwise-XOR onto the data stack. |
| SHL	| Pops a value off the data stack, performs an unsigned shift-left by one bit, then pushes the shifted value back onto the data stack. |
| SHR	| Pops a value off the data stack, performs an unsigned shift-right by one bit, then pushes the shifted value back onto the data stack. |
| LIT N	| Pushes the unsigned literal value N onto the top of the stack. |
| DUP	| Duplicates the value on the top of the stack. |
| SWAP	| Swaps the top two values on the stack. |
| DROP	| Pops and discards the topmost value off the top of the stack. |
| TO_RS	| Pops the value off the top of the data stack, and pushes it onto the top of the return stack. |
| FROM_RS	| Pops the value off the top of the return stack, and pushes it onto the top of the data stack. |
| JMP Addr	| Sets the Program Counter to the specified address. |
| JZ Addr	| Jump-if-Zero.  Pops a value off the data stack; if the value is zero, the Program Counter is set to the specified address.  Otherwise, the Program Counter continues on to the next instruction. |
| JNZ Addr	| Jump-if-Not-Zero.  Pops a value off the data stack; if the value is nonzero, the Program Counter is set to the specified address.  Otherwise, the Program Counter continues on to the next instruction. |
| CALL Addr	| Pushes the Program Counter of the next instruction onto the top of the return-stack, then sets the Program Counter to Addr. |
| RET	| Pops the top of the return-stack into the Program Counter. |

## Stack-Machine Programs

Stack-machine programs are text files that include a sequence of instructions,
labels and comments.  The instructions are simply what are described above.

Comments start with a `#` character and extend to the end of the line.
(In other words, they are like Python comments.)

Labels must appear on a line by themselves.  The label itself must end with
a colon `:` character.

The recommended extension is `.sm` for "stack machine."

Here is an example program `collatz.sm` that computes the number of iterations
it takes to go from an input number N to 1, following the rules of the
Collatz Conjecture:

    #=============================================================================
    # A simple program to compute how many iterations it takes to get from a
    # given input N back to 1, following the rules of the Collatz Conjecture.
    #
    # The function is invoked by pushing N onto the stack, then calling the
    # collatz function.  When the function returns, N will be removed from
    # the stack, and the number of iterations will be on top of the stack.
    #
    # Example:
    #     LIT  97
    #     CALL collatz
    # Top of stack should be 118 at return.
    #=============================================================================
    collatz:
        # Store the count on the return-stack.
        LIT    0
        TO_RS
    
    collatz_loop:
        # Is the input number 1 yet?
        DUP
        LIT    1
        SUB
        JZ    done
    
        # Is the number even or odd?  AND with 1.
        DUP
        LIT    1
        AND
        JZ    is_even
    
    is_odd:        # Compute 3N + 1
        DUP        # DS = [N N ...]
        SHL        # DS = [2N N ...]
        LIT    1    # DS = [1 2N N ...]
        ADD        # DS = [2N+1 N ...]
        ADD        # DS = [3N+1 ...]
    
        JMP    end_comp
    
    is_even:    # Divide number by 2.
        SHR
    
    end_comp:
        # Update our iteration count.
        FROM_RS
        LIT    1
        ADD
        TO_RS
    
        # Back to the start of the loop
        JMP    collatz_loop
    
    done:
        # Top of stack should be 1.  Return the iteration count.
        DROP
        FROM_RS
        RET

Labels and instructions may be lowercase or uppercase.  Indentation may use
tabs or spaces.  Tabs and uppercase instructions are recommended for
readability.

## Running the Interpreter

The entry point of the program is `repl.py`.

    python repl.py

The program will print the current state of the stack machine, then let you
enter instructions like the above.

    $ python repl.py
    Welcome to the stack processor.
    
    Data Stack:    []
    Return Stack:  []
    Program Counter:  STOP
    
    > lit 3
    Data Stack:    [3]
    Return Stack:  []
    Program Counter:  STOP
    
    > lit 4
    Data Stack:    [3 4]
    Return Stack:  []
    Program Counter:  STOP
    
    > add
    Data Stack:    [7]
    Return Stack:  []
    Program Counter:  STOP
    
    > shr 
    Data Stack:    [3]
    Return Stack:  []
    Program Counter:  STOP
    
    > quit
    Goodbye!

The `HELP` command will enumerate other options for interacting with the program:

    > help
    Commands:
    
    HELP
        Show this help information.
    
    QUIT
    EXIT
        Exits the program.
    
    LOAD filename.sm
        Load the instructions in the specified file.
    
    DEBUG
        Turn on debug output during execution.
    
    NODEBUG
        Turn off debug output during execution.
    
    RESET
        Completely reset the processor state, including program.
    
    All stack processor instructions may be invoked as well, but
    CALL/JZ/JNZ/JMP/RET instructions won't work unless a program
    is loaded.

Finally, the program can optionally load a program and run commands using
the command-line invocation:

    python repl.py myprog.sm "LIT 3" "LIT 4" "CALL fn"

This will cause the program `myprog.sm` to be loaded, and then the three
instructions "`LIT 3`", "`LIT 4`", and "`CALL fn`" to be executed.

For example, to run the above `collatz.sm` program, one might do this:

    python repl.py collatz.sm "LIT 97" "CALL collatz"
    Welcome to the stack processor.
    
    Data Stack:    []
    Return Stack:  []
    Program Counter:  STOP
    
    Loaded program from collatz.sm
    ... <program text here>
    
    Data Stack:    [97]
    Return Stack:  []
    Program Counter:  STOP
    
    Data Stack:    [118]
    Return Stack:  []
    Program Counter:  STOP

The final result of the calculation, 118, is on the top of the stack after
the function has returned.
