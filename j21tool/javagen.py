from collections.abc import Sequence
from pathlib import Path
from javalang.tree import ClassDeclaration, Literal, MemberReference, ElementValuePair, Type, \
    ReturnStatement, BinaryOperation, LocalVariableDeclaration, StatementExpression, MethodInvocation, \
    ReferenceType, TypeParameter, ReturnStatement, MemberReference, ClassCreator, StatementExpression, \
    ClassReference, Assignment, This, LambdaExpression, MethodReference, IfStatement, BlockStatement, \
    ThrowStatement, FormalParameter, ForStatement, EnhancedForControl, \
    VariableDeclaration, TypeArgument

from j21tool.formatter import Formatter, PieceType
from j21tool.javalangex import RecordDeclaration
from j21tool.utils import ensure_dir_of_file, is_dirty

def generate_java(ast, original_code, output_pathname):
    """To generate a Java file given an AST"""

    ensure_dir_of_file(output_pathname)

    #with open(output_pathname + ".ast", mode="w", encoding="utf-8") as f:
    #    f.write(str(tree))
    if len(ast.types) > 0:
        ast.types[0]._dirty = True
    fmt = Formatter(original_code)
    format_java(fmt, ast)

    with open(output_pathname, "w", encoding="utf-8") as out:
        out.write(fmt.to_code())

def to_snippet(elem):
    fmt = Formatter(None)
    format_any(fmt, elem)
    return fmt.to_code()

def format_any(out, elem):
    """Format an object"""
    #print(f"elem type:{type(elem)} isseq:{isinstance(elem, Sequence)} {len(elem) if isinstance(elem, Sequence) else ''}")

    if isinstance(elem, Literal):
        out.add(elem.value)
    elif isinstance(elem, This):
        out.add('this')
    elif isinstance(elem, MethodInvocation):
        format_invocation(out, elem)        
    elif isinstance(elem, MemberReference):
        if elem.qualifier:
            out.add(elem.qualifier).add('.', PieceType.SELECTOR)
        out.add(elem.member)
    elif isinstance(elem, MethodReference):
        format_any(out, elem.expression)
        out.add('::', PieceType.TIGHT_BINARY_OP)
        format_any(out, elem.method)
    elif isinstance(elem, ReferenceType):
        format_type(out, elem)
    elif isinstance(elem, TypeArgument):
        format_type(out, elem.type)
    elif isinstance(elem, ClassCreator):
        out.add('new')
        format_type(out, elem.type)
        format_list(out, elem.arguments)
    elif isinstance(elem, ClassReference):
        format_type(out, elem.type)
        out.add(".class", PieceType.SELECTOR)
    elif isinstance(elem, Assignment):
        format_any(out, elem.expressionl)
        out.add('=', PieceType.ASSIGN)
        format_any(out, elem.value)
    elif isinstance(elem, LambdaExpression):
        format_list(out, elem.parameters)
        out.add('->', PieceType.BINARY_OP)
        format_any(out, elem.body)
    elif isinstance(elem, FormalParameter):
        format_annotations(out, elem.annotations)
        format_modifiers(out, elem.modifiers)
        format_type(out, elem.type)
        out.add(elem.name)
    elif isinstance(elem, ElementValuePair):
        out.add(elem.name).add('=', PieceType.ASSIGN)
        format_any(out, elem.value)
    elif isinstance(elem, list):
        format_open_list(out, elem)
    elif isinstance(elem, ReturnStatement):
        out.add("return")
        format_any(out, elem.expression)
        out.add(';', PieceType.END_OF_STATEMENT)
    elif isinstance(elem, LocalVariableDeclaration):
        format_local_var(out, elem)
    elif isinstance(elem, VariableDeclaration):
        format_var(out, elem)
    elif isinstance(elem, StatementExpression):
        format_stmt(out, elem)
    elif isinstance(elem, BinaryOperation):
        format_any(out, elem.operandl)
        out.add(elem.operator, PieceType.BINARY_OP)
        format_any(out, elem.operandr)
    elif isinstance(elem, IfStatement):
        out.add('if').add('(', PieceType.LPARENTHESIS)
        format_any(out, elem.condition)
        out.add(')', PieceType.RPARENTHESIS).add('{\n', PieceType.BEGIN_BLOCK)      
        format_any(out, elem.then_statement)
        out.add('}', PieceType.END_BLOCK)
        if elem.else_statement:
            out.add('else')
            if isinstance(elem.else_statement, IfStatement):
                format_any(out, elem.else_statement)
            else:
                out.add('{', PieceType.BEGIN_BLOCK)
                format_any(out, elem.else_statement)
                out.add('}', PieceType.END_BLOCK)
        else:
            out.add('\n')

    elif isinstance(elem, BlockStatement):
        for stmt in elem.statements:
            format_any(out, stmt)
    elif isinstance(elem, ForStatement):
        out.add('for').add('(', PieceType.LPARENTHESIS)
        format_any(out, elem.control)
        out.add(')', PieceType.RPARENTHESIS)
        out.add('{\n', PieceType.BEGIN_BLOCK)
        format_any(out, elem.body)
        out.add('}\n', PieceType.END_BLOCK)
    elif isinstance(elem, EnhancedForControl):
        format_any(out, elem.var)
        out.add(':')
        format_any(out, elem.iterable)
    elif isinstance(elem, ThrowStatement):
        out.add('throw')
        format_any(out, elem.expression)
    
    # append selectors
    if hasattr(elem, 'selectors') and elem.selectors:
        for sel in elem.selectors:
            out.add('.', PieceType.SELECTOR)
            format_any(out, sel)

def format_java(out, tree):
    # head
    pkg_level_doc = get_package_level_doc(tree)
    if pkg_level_doc is not None:
        out.add(pkg_level_doc).add("\n")

    if tree.package:
        out.add(f"package {tree.package.name};\n")
    
    # imports, google java format: static then regular.
    imports = tree.imports if tree.imports else []
    static_imports = sorted([imp.path for imp in imports if imp.static])
    if len(static_imports) > 0:
        out.add("\n")
    for p in static_imports:
        out.add(f"import static {p};\n")

    regular_imports = sorted([imp.path for imp in imports if not imp.static])
    if len(regular_imports) > 0:
        out.add("\n")
    for p in regular_imports:
        out.add(f"import {p};\n")

    # classes
    for t in tree.types:
        if isinstance(t, ClassDeclaration):            
            format_class(out, t)
        elif isinstance(t, RecordDeclaration):
            format_record(out, t)

def format_class(out, c):
    if not is_dirty(c):        
        out.write_original(c)        
        return
    
    out.add('\n')
    format_comment(out, c.documentation)
    format_annotations(out, c.annotations)
    format_modifiers(out, c.modifiers)
    out.add("class").add(c.name)
    if c.extends:
        out.add("extends")
        format_any(out, c.extends)
    if c.implements:
        out.add("implements")
        format_open_list(out, c.implements)

    out.add("{\n", PieceType.BEGIN_BLOCK)

    for f in c.fields:
        format_field(out, f)

    for ctr in c.constructors:
        format_method(out, ctr, ctr.name)

    for m in c.methods:
        format_method(out, m)

    out.add("}\n", PieceType.END_BLOCK)

def format_record(out, c):
    if not is_dirty(c):        
        out.write_original(c)        
        return
    
    out.add('\n')
    format_comment(out, c.documentation)
    format_annotations(out, c.annotations)
    format_modifiers(out, c.modifiers)
    out.add("record").add(c.name)

    format_list(out, c.parameters)

    if c.implements:
        out.add("implements")
        format_open_list(out, c.implements)

    out.add("{\n", PieceType.BEGIN_BLOCK)
    for m in c.methods:
        format_method(out, m)

    out.add("}\n", PieceType.END_BLOCK)

def format_list(out, lst):
    out.add('(', PieceType.LPARENTHESIS)
    format_open_list(out, lst)
    out.add(')', PieceType.RPARENTHESIS)

def format_open_list(out, lst):
    if lst:
        first = True
        for item in lst:
            if first:
                first = False
            else:
                out.add(',', PieceType.COMMA)
            format_any(out, item)

def format_annotations(out, annotations, change_line = False):
    """annotations"""
    if annotations:
        for a in annotations:
            format_annotation(out, a)
            if len(annotations) > 1:
                out.add('\n')
        if change_line and len(annotations) == 1:
            out.add('\n')

def format_annotation(out, a):
    """"""
    out.add(f"@{a.name}")
    if a.element:
        format_list(out, a.element)

def format_comment(out, doc):
    """format comment"""
    # todo rewrite
    if doc:
        out.add(doc)

def format_type(out, t):
    if t == None:
        out.add('void')
    else:   
        out.add(t.name)
        if isinstance(t, TypeParameter):
            if t.extends:
                out.add('extends').add(t.extends)

        elif isinstance(t, ReferenceType) and t.arguments:
            out.add('<')
            format_open_list(out, t.arguments)
            out.add('>')    

def format_field(out, field):
    """
      int FieldDeclaration(
        annotations=[], declarators=[VariableDeclarator(
          dimensions=[], initializer=Literal(postfix_operators=[], prefix_operators=[], qualifier=None, selectors=[], value=100), 
          name=x)], 
        documentation=None, 
        modifiers=set(), 
        type=BasicType(dimensions=[], name=int)
    );
    """
    format_comment(out, field.documentation)
    format_annotations(out, field.annotations)
    format_modifiers(out, field.modifiers)
    format_var(out, field)
    out.add(';', PieceType.END_OF_STATEMENT)

def format_local_var(out, v):
    # LocalVariableDeclaration(annotations=[], declarators=[
    #     VariableDeclarator(dimensions=[], initializer=BinaryOperation(operandl=MemberReference(member=X, postfix_operators=[], prefix_operators=[], qualifier=, selectors=[]), 
    #        operandr=Literal(postfix_operators=[], prefix_operators=[], qualifier=None, selectors=[], value=5), operator=+), 
    #      name=x)
    #   ], 
    #   modifiers=set(), 
    #   type=BasicType(dimensions=[], name=int))
    #format_comment(out, v.documentation)
    format_annotations(out, v.annotations)
    format_modifiers(out, v.modifiers)
    format_var(out, v)
    out.add(';', PieceType.END_OF_STATEMENT)
        
def format_var(out, v):
    format_type(out, v.type)
    for d in v.declarators:
        out.add(d.name)
        if d.initializer:
            out.add("=", PieceType.ASSIGN)
            format_any(out, d.initializer)       

def format_method(out, m, class_name = None):
    out.add('\n')
    format_comment(out, m.documentation)
    format_annotations(out, m.annotations)
    format_modifiers(out, m.modifiers)
    if m.type_parameters:
        out.add('<')
        format_open_list(out, m.type_parameters)
        out.add('>')

    if class_name:
        out.add(class_name)
    else:
        format_type(out, m.return_type)
        out.add(m.name)
    format_list(out, m.parameters)
    if m.throws:
        out.add('throws')
        format_open_list(out, m.throws)
    out.add('{\n', PieceType.BEGIN_BLOCK)
    # method body
    if m.body:
        for stmt in m.body:
            format_any(out, stmt)

    out.add('}\n', PieceType.END_BLOCK)

def format_stmt(out, stmt):
    # StatementExpression(expression=MethodInvocation(arguments=[BinaryOperation(operandl=Literal(postfix_operators=[], prefix_operators=[], qualifier=None, selectors=[], value="n="), operandr=MemberReference(member=n, postfix_operators=[], prefix_operators=[], qualifier=, selectors=[]), operator=+)], member=println, postfix_operators=[], prefix_operators=[], qualifier=System.out, selectors=[], type_arguments=None), label=None);
    format_any(out, stmt.expression)
    out.add(';', PieceType.END_OF_STATEMENT)

def format_invocation(out, inv):
    """ MethodInvocation(arguments=[BinaryOperation(operandl=Literal(postfix_operators=[], prefix_operators=[], qualifier=None, selectors=[], value="n="),
    #  operandr=MemberReference(member=n, postfix_operators=[], prefix_operators=[], qualifier=, selectors=[]), 
    #  operator=+)], 
    # member=println, postfix_operators=[], prefix_operators=[], qualifier=System.out, selectors=[], type_arguments=None), label=None);
    """
    if inv.qualifier:
        out.add(inv.qualifier).add('.', PieceType.SELECTOR)
    out.add(inv.member)
    format_list(out, inv.arguments)

MODIFIER_PRIORITIES = {
     'public': 1,
     'protected': 2,
     'private': 3,
     'abstract': 4,
     'static': 5,
     'final': 6,
     'transient': 7,
     'volatile': 8,
     'synchronized': 9,
     'native': 10,
     'default': 11,
     'strictfp': 12,
}

def format_modifiers(out, modifiers):
    if modifiers:
        for m in sorted(modifiers, key=lambda x: MODIFIER_PRIORITIES[x] or 99):
            out.add(m)

# def dump_type(java_type):
#     if java_type is None:
#         return "void"
#     elif isinstance(java_type, Type):
#         return java_type.name or 'void'
#     else:
#         return str(java_type)

def get_package_level_doc(tree):
    if tree.package and tree.package.documentation:
        return tree.package.documentation
    return None

