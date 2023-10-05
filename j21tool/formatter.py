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
    def __init__(self, original_code):
        self._out = io.StringIO()
        self._original_code = original_code
        self._indent = 0
        self._items = []
        self._indent_width = 2
        self._continue_width = 4
        self._max_line_width = 100

    def to_code(self):
        """get the generated Java code"""
        return self._out.getvalue()
    
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
        self._items.append((item, type))

        if item.endswith('\n') or type == PieceType.END_OF_STATEMENT:
            self.flush()

        return self
    
    def flush(self):
        start = 0
        items_len = len(self._items)
        assign_pos = -1
        while start < items_len:
            indent = self._indent + (self._continue_width if start > 0 else 0)
            end_index = estimate_line_width(self._items, start, items_len, self._max_line_width - indent)

            # single line fits.
            if end_index == items_len:
                indent_diff = count_indent(self._items, start, items_len) * self._indent_width
                if indent_diff < 0:
                    indent += indent_diff
                line = ' ' * indent + join(self._items, start, items_len)
                self._indent += indent_diff

                self._out.write(line)
                if not line.endswith('\n'):
                    self._out.write('\n')
                start = items_len
                break

            if assign_pos == -1:
                assign_pos = find_item_type(self._items, PieceType.ASSIGN)
                if assign_pos > 0 and assign_pos < end_index:
                    indent_diff = count_indent(self._items, start, assign_pos + 1) * self._indent_width
                    if indent_diff < 0:
                        indent += indent_diff
                    line = ' ' * indent + join(self._items, start, assign_pos + 1)
                    self._indent += indent_diff
                    self._out.write(line)
                    if not line.endswith('\n'):
                        self._out.write('\n')
                    start = assign_pos + 1
                    continue
            
            indent_diff = count_indent(self._items, start, end_index) * self._indent_width
            if indent_diff < 0:
                indent += indent_diff
            line = ' ' * indent + join(self._items, start, end_index)
            self._indent += indent_diff
            self._out.write(line)
            if not line.endswith('\n'):
                self._out.write('\n')
            start = end_index

        self._items = []

    def close(self):
        self.flush()
        self._out.close()

def find_item_type(items, t):
    for i in range(len(items)):
        if items[i][1] == t:
            return i
    return -1

def estimate_line_width(items, start, end, max_len):
    total_len = 0
    for i in range(start, end):
        if (i > 0) and needs_space(items[i-1], items[i]):
            total_len += 1
        total_len += len(items[i][0])
        if total_len >= max_len:
            return i + 1
    return end

def join(items, start, end):
    sio = io.StringIO()
    for i in range(start, end):
        if (i > 0) and needs_space(items[i-1], items[i]):
            sio.write(' ')
        sio.write(items[i][0])
    return sio.getvalue()

def count_indent(items, start, end):
    count = 0
    for i in range(start, end):
        if items[i][1] == PieceType.BEGIN_BLOCK:
            count += 1
        if items[i][1] == PieceType.END_BLOCK:
            count -= 1
    return count

def is_id(word):
    return re.search(r'[\w_]+', word) != None

#def last_line(text):
#    return text[-10:]

def needs_space(item1, item2):
    word1, type1 = item1
    word2, type2 = item2

    if type1 == PieceType.SELECTOR or type2 == PieceType.SELECTOR:
        return False

    if type1 == PieceType.BINARY_OP or type2 == PieceType.BINARY_OP \
        or type1 == PieceType.ASSIGN or type2 == PieceType.ASSIGN \
        or type1 == PieceType.COMMA:
        return True

    if is_id(word1) and is_id(word2):
        return True
    
    return False