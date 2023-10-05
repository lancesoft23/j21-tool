from javalang.tree import Literal, BinaryOperation
from j21tool.utils import search_tree
import j21tool.javagen as javagen

def to_text_block(ast):
    """Rewrite to java 15 text block"""

    _, node = search_tree(ast, \
        lambda x: isinstance(x, BinaryOperation) and x.operator == '+')
    if node and is_chain_of_string(node.operandl):
        print('---------------------------------------------------------')
        print(f"found a chain of string [{javagen.to_snippet(node)}]")
        print('---------------------------------------------------------')
    pass

def is_chain_of_string(node):
    if isinstance(node, str):
        return True
    
    if isinstance(node, BinaryOperation):
        return node.operator == '+' and is_chain_of_string(node.operandl)
    
    return False
