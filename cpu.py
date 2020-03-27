import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

# greater gtf == > flag, ltf == < flag, etf == = flag
ltf = 0b100
gtf = 0b010
etf = 0b001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.flags = 0b00000001
        self.branch_table = {
            HLT: self.HLT_operation,
            LDI: self.LDI_operation,
            PRN: self.PRN_operation,
            ADD: self.ADD_operation,
            MUL: self.MUL_operation,
            PUSH: self.PUSH_operation,
            POP: self.POP_operation,
            CALL: self.call_operation,
            RET: self.RET_operation,
            CMP: self.CMP_operation,
            JMP: self.JMP_operation,
            JEQ: self.JEQ_operation,
            JNE: self.JNE_operation
        }

    def HLT_operation(self, operand_a, operand_b):
        self.running = False

    def LDI_operation(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN_operation(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def ADD_operation(self, operand_a, operand_b):
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def MUL_operation(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def PUSH_operation(self, operand_a, operand_b):
        self.push(self.reg[operand_a])
        self.pc += 2

    def POP_operation(self, operand_a, operand_b):
        self.reg[operand_a] = self.pop()
        self.pc += 2

    def call_operation(self, operand_a, operand_b):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        update_reg = self.ram[self.pc + 1]
        self.pc = self.reg[update_reg]

    def RET_operation(self, operand_a, operand_b):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def CMP_operation(self, operand_a, operand_b):
        self.alu('CMP', operand_a, operand_b)
        self.pc += 3

    def JEQ_operation(self, operand_a, operand_b):
        if self.flags & etf:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def JMP_operation(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]


    def JNE_operation(self, operand_a, operand_b):
        if not self.flags & etf:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def push(self, value):
        self.reg[SP] -= 1
        self.ram_write(value, self.reg[7])

    def pop(self):
        value = self.ram_read(self.reg[7])
        self.reg[SP] += 1
        return value

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print("USAGE: ls8.py filename")
            sys.exit(1)

        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                line = line.split("#")[0]
                line = line.strip()  # remove spaces

                if line == "":
                    continue

                val = int(line, 2)

                self.ram[address] = val

                address += 1

    def alu(self, operation, reg_a, reg_b):
        """ALU operations."""
        if operation == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif operation == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif operation == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flags = ltf
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = gtf
            else:
                self.flags = etf
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if int(bin(IR), 2) in self.branch_table:
                self.branch_table[IR](operand_a, operand_b)
            else:
                raise Exception(f'Invalid {IR}, not in branch table \t {list(self.branch_table.keys())}')