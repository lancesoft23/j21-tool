from collections import namedtuple
from javalang.tokenizer import JavaTokenizer

PositionEx = namedtuple('Position', ['line', 'column', 'start', 'end'])

class JavaTokenizerEx(JavaTokenizer):
    """
    To extend the javalang JavaTokenizer to support original code positions and new Java features.
    """

    def tokenize(self):
        """Adding start (inclusive) and end (exclusive) in original source in the token.position."""
        token = JavaTokenizer.tokenize(self)
        p = token.position
        token.postion = PositionEx(line = p.line, column = p.column, start = self.i, end = self.j)
        return token
    
    def read_string(self):
        if self.read_text_block():
            print("found a text block")
            return
        else:
            return JavaTokenizer.read_string(self)
        
    def read_text_block(self):
        # start Java 15 text block
        if self.i + 7 < self.length and self.data[self.i] == '"' and self.data[self.i + 1] == '"' \
            and self.data[self.i + 2] == '"' and (self.data[self.i + 3] == '\n' or self.data[self.i + 3] == '\r'):
            j = self.i + 7
            while j < self.length:
                if self.data[j - 2] == '"' and self.data[j - 1] == '"' and self.data[j] == '"':
                    # found the end
                    self.j = j + 1
                    return True
                j += 1
        # Does not match
        return False

    # TODO to support spring template such as STR."...\(x)..".
    #def read_string_template(self):
    #    self.i += 4
    #    # tofix
    #    self.read_string()


def tokenize(code, ignore_errors=False):
    tokenizer = JavaTokenizer(code, ignore_errors)
    return tokenizer.tokenize()
