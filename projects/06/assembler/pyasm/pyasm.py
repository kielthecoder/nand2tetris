import os.path
import sys

class Parser:
    A_COMMAND = 1
    L_COMMAND = 2
    C_COMMAND = 3
    
    def __init__(self):
        self.text = None
        self.command_type = None
        
    def advance(self, text):
        try:
            i = text.index("//")
            text = text[0:i]
        except ValueError:
            pass
        self.text = text.strip()
        if len(self.text) < 1:
            self.text = None
        if self.text:
            if self.text[0:1] == "@":
                self.command_type = self.A_COMMAND
            elif self.text[0:1] == "(":
                self.command_type = self.L_COMMAND
            else:
                self.command_type = self.C_COMMAND
        else:
            self.command_type = None

    def symbol(self):
        if self.command_type == self.A_COMMAND:
            return self.text[1:]
        elif self.command_type == self.L_COMMAND:
            i = self.text.find(")")
            return self.text[1:i]
        return None

    def dest(self):
        if self.command_type == self.C_COMMAND:
            try:
                i = self.text.index("=")
            except ValueError:
                return None
            return self.text[0:i]
        return None

    def comp(self):
        if self.command_type == self.C_COMMAND:
            try:
                i = self.text.index("=")
                i = i + 1
            except ValueError:
                i = 0
            try:
                j = self.text.index(";")
            except ValueError:
                j = len(self.text)
            return self.text[i:j]
        return None

    def jump(self):
        if self.command_type == self.C_COMMAND:
            try:
                i = self.text.index(";")
                i = i + 1
            except ValueError:
                return None
            return self.text[i:]
        return None

class Code:
    dests = {
        None:  "000",
        "M":   "001",
        "D":   "010",
        "MD":  "011",
        "A":   "100",
        "AM":  "101",
        "AD":  "110",
        "AMD": "111",
    }

    comps = {
        "0":   "0101010",
        "1":   "0111111",
        "-1":  "0111010",
        "D":   "0001100",
        "A":   "0110000",
        "!D":  "0001101",
        "!A":  "0110001",
        "-D":  "0001111",
        "-A":  "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M":   "1110000",
        "!M":  "1110001",
        "-M":  "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
    }

    jumps = {
        None:  "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }
    
    def dest(self, mnem):
        return self.dests[mnem]

    def comp(self, mnem):
        return self.comps[mnem]

    def jump(self, mnem):
        return self.jumps[mnem]

class SymbolTable:
    symbols = {
        "SP":     "0",
        "LCL":    "1",
        "ARG":    "2",
        "THIS":   "3",
        "THAT":   "4",
        "R0":     "0",
        "R1":     "1",
        "R2":     "2",
        "R3":     "3",
        "R4":     "4",
        "R5":     "5",
        "R6":     "6",
        "R7":     "7",
        "R8":     "8",
        "R9":     "9",
        "R10":    "10",
        "R11":    "11",
        "R12":    "12",
        "R13":    "13",
        "R14":    "14",
        "R15":    "15",
        "SCREEN": "16384",
        "KBD":    "24576",
    }

    def add(self, symb, addr):
        self.symbols[symb] = addr

    def contains(self, symb):
        return symb in self.symbols

    def address(self, symb):
        return self.symbols[symb]

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        in_name = arg
        out_name = arg.replace(".asm", ".hack")
        print("Assembling %s -> %s..." % (in_name, out_name))
        with open(out_name, "wt") as outfd:
            p = Parser()
            c = Code()
            s = SymbolTable()
            print("   First pass...")
            pc = 0
            with open(in_name, "rt") as infd:
                for text in infd:
                    p.advance(text)
                    if p.command_type:
                        if p.command_type == p.A_COMMAND:
                            pc = pc + 1
                        elif p.command_type == p.L_COMMAND:
                            s.add(p.symbol(), pc)
                        elif p.command_type == p.C_COMMAND:
                            pc = pc + 1
            print("   Second pass...")
            var = 16
            with open(in_name, "rt") as infd:
                for text in infd:
                    p.advance(text)
                    if p.command_type:
                        if p.command_type == p.A_COMMAND:
                            try:
                                addr = int(p.symbol())
                            except ValueError:
                                if (s.contains(p.symbol())):
                                    addr = int(s.address(p.symbol()))
                                else:
                                    addr = var
                                    var = var + 1
                                    s.add(p.symbol(), addr)
                            outfd.write("0{:015b}\n".format(addr))
                        elif p.command_type == p.C_COMMAND:
                            outfd.write("111%s%s%s\n" % (c.comp(p.comp()), c.dest(p.dest()), c.jump(p.jump())))
        print("   Done!")
