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

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        in_name = arg
        out_name = arg.replace(".asm", ".hack")
        print("Assembling %s -> %s..." % (in_name, out_name))
        with open(in_name, "rt") as infd:
            p = Parser()
            c = Code()
            with open(out_name, "wt") as outfd:
                for text in infd:
                    p.advance(text)
                    if p.command_type:
                        if p.command_type == p.A_COMMAND:
                            outfd.write("0{:015b}\n".format(int(p.symbol())))
                        elif p.command_type == p.L_COMMAND:
                            print("(%s)" % p.symbol())
                        elif p.command_type == p.C_COMMAND:
                            outfd.write("111%s%s%s\n" % (c.comp(p.comp()), c.dest(p.dest()), c.jump(p.jump())))
                        
