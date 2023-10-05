"""
Utilities
"""
import os
from os import path
from collections.abc import Sequence
from javalang.ast import Node, walk_tree
from javalang.tree import CompilationUnit, ClassDeclaration, Import, PackageDeclaration
from j21tool.javalangex import PositionEx

def is_dirty(node):
    if hasattr(node, "_dirty") and node._dirty:
        return True
    return True

    # if not hasattr(node, 'chidren'):
    #     print(f"node {node} has not children")
    #     return False
    
    # for child in node.children():
    #     if is_dirty(child):
    #         return True
    # return False

# ------------------------------------------------------------------------------
# -- Misc --    
def go_over_positions(node):
    if node == None:
        print(f"None node: {node}")
        return
    
    position = node._position if hasattr(node, "_position") else None
    if position != None:
        start = position.start
        end = position.end
    else:
        start = -1
        end = -1

    for child in _get_children(node):        
        go_over_positions(child)

        if hasattr(child, '_position'):
            if child.position.start >= 0 and child.position.start < start:
                start = child.position.start
            if child.position.end >= 0 and end < child.position.end:
                end = child.position.end
    
    print(f"position of {type(node)} start={start} end={end}")
    if position == None:
        node._position = PositionEx(1, 1, start, end)
    elif position.start != start or position.end != end:
        node._position = position._replace(start = start, end = end)

def _get_children(node):
    if node and isinstance(node, Node):
        for child in node.children:
            if isinstance(child, Sequence) or isinstance(child, set):
                for item in child:
                    if isinstance(item, Node):
                        yield item
            elif isinstance(child, Node):
                yield child


def ensure_dir(dir_name):
    if not path.exists(dir_name):
        os.makedirs(dir_name)

def ensure_dir_of_file(filename):
    ensure_dir(path.dirname(path.realpath(filename)))

def find_sub_list(lst, sub_lst):
    """find a sub list in a list"""
    sub_list_len = len(sub_lst)
    for i in range(0, len(lst) - sub_list_len + 1):
        found = True
        for j in range(0, sub_list_len):
            if lst[i + j] != sub_lst[j]:
                found = False
                break
        if found:
            return i
    return -1

def get_single_elem(lst):
    """."""
    print(f"len={len(lst)}")
    assert lst != None and len(lst) == 1
    return lst[0]

def capitalize(s):
    """Capitalize the first character."""
    return s[0].upper() + s[1:]

def get_method_signature(package_name, class_def, method_def):
    """."""
    params_str = ''
    return f"{package_name}.{class_def.name}.{method_def.name}({params_str})"

def create_tree(package_name, class_name):
    """Create an empty AST."""   
    package = PackageDeclaration(name = package_name)
    imports = []

    # attrs = ("type_parameters", "extends", "implements")
    # attrs = ("name", "body")
    class_def = ClassDeclaration(
        name = class_name,
        body = []
    )
    # attrs = ("package", "imports", "types")
    tree = CompilationUnit(package = package,
                           imports = imports,
                           types = [class_def])
    return tree

def add_import(tree, import_path, is_static = False):
    """."""
    if any(import_def.path == import_path for import_def in tree.imports):
        return
    
    #class Import(Node):
    # attrs = ("path", "static", "wildcard")
    tree.imports.append(Import(path=import_path, static = is_static, wildcard = False))

def add_method_if_absent(class_def, code_snippet):
    """."""
    method_defs = parse_methods(code_snippet)
    for method_def in method_defs:
        if any(m.name == method_def.name for m in class_def.methods):
            continue
        if class_def.body is None:
            class_def.body = []
        class_def.body.append(method_def)    

def parse_methods(code):
    """parse Java methods in a code snippet."""
    tree = javalang.parse.parse( \
f"""class Dummy {{
    {code}
}}
""")
    return tree.types[0].methods

def search_tree(ast, predict):
    for path, node in walk_tree(ast):
        if predict(node):
            return path, node
    return None, None
