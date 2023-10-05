
from javalang.tree import ClassDeclaration, FormalParameter
from j21tool.javalangex.tree import *

def to_record(ast):
    """ 
    If a class is marked as lombok @Value, convert to record.
    """    
    for i in range(0, len(ast.types)):
        c = ast.types[i]

        if is_value_object(c, ast.imports):
            ast.types[i] = convert_to_record(c)
            ast.imports = [imp for imp in ast.imports if imp.path != 'lombok.Value']
    
def is_value_object(c, imports):
    if not isinstance(c, ClassDeclaration):
        return False

    # has @lombok.Value
    has_value_annotation = any(ann.name == 'Value' for ann in c.annotations) \
        and any(imp.path == 'lombok.Value' and not imp.static for imp in imports)
    has_data_annotation = any(ann.name == 'Data' for ann in c.annotations) \
        and any(imp.path == 'lombok.Data' and not imp.static for imp in imports)
    has_builder_annotation = any(ann.name == 'Builder' for ann in c.annotations) \
        and any(imp.path == 'lombok.Builder' and not imp.static for imp in imports)
    # is a simple immutable value object
    return has_value_annotation and (not has_data_annotation) and (not has_builder_annotation)

def convert_to_record(class_def):

    parameters = []
    for field in class_def.fields:
        if 'static' not in field.modifiers and len(field.declarators) > 0:
            d = field.declarators[0]     
            parameters.append(
                FormalParameter(modifiers=[],
                    annotations=field.annotations,
                    type=field.type,
                    name=d.name,
                    varargs=False))
    
    record_def = RecordDeclaration(
        name=class_def.name,
        type_parameters=[],
        implements=class_def.implements,
        parameters=parameters,
        body=class_def.methods)

    record_def.modifiers = [m for m in class_def.modifiers if m in ['public', 'protected', 'private']]
    record_def._dirty = True
    print(f'record parameters ={record_def.parameters}')

    return record_def