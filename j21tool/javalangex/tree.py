from javalang.tree import TypeDeclaration

class RecordDeclaration(TypeDeclaration):
    attrs = ("type_parameters", "implements", "parameters")
