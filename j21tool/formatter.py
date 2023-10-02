import io
from enum import Enum
import re

class PieceType(Enum):
    GENERAL = 1
    LPARENTHESIS = 2
    RPARENTHESIS = 3
    BEGIN_BLOCK = 4
    END_BLOCK = 5
    COMMA = 6
    ASSIGN = 7
    BINARY_OP = 8
    TIGHT_BINARY_OP = 9
    SELECTOR = 10
    END_OF_STATEMENT = 11

class Formatter(object):
    """ 
    Formatter
    """
    def __init__(self, out, original_code):
        self._out = out
        self._original_code = original_code
        self._indent = 0
        self._line = ''
        self._last_is_id = False
        self._is_continue = False
        self._indent_width = 2
        self._continue_width = 4
        self._max_line_width = 100

    #def to_code(self):
    #    """get the generated Java code"""
    #    return self._out.getvalue()
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def write(self, item):
        """Alias of add"""
        return self.add(item)
    
    def write_original(self, node):
        self._out.write(self._original_code[node.position.start:node.position.end])
    
    def add(self, item, type = PieceType.GENERAL):
        if type == PieceType.END_BLOCK:
            self._indent -= self._indent_width
        is_id = re.search(r'[\w_]+', item) != None

        proposed_len = len(self._line) + len(item) + (1 if self._last_is_id and is_id else 0)
        if proposed_len > self._max_line_width:
            self._line += '\n'
            self._is_continue = True
            self.flush()

        if self._line == '':
            self._line = ' ' * (self._indent + self._is_continue * self._continue_width)
        elif self._last_is_id and is_id:
            self._line += ' '

        self._line += item        
        if type == PieceType.END_OF_STATEMENT:
            self._line += '\n'
            self._is_continue = False

        if '\n' in self._line:
            self.flush()
        else:
            self._last_is_id = is_id

        if type == PieceType.BEGIN_BLOCK:
            self._indent += self._indent_width

        return self
    
    def flush(self):
        self._out.write(self._line)
        self._out.flush()

        self._line = ''
        self._last_is_id = False
        pass

    def close(self):
        self.flush()
        self._out.close()

