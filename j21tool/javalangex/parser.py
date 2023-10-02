
from javalang.parser import Parser
from j21tool.javalangex import RecordDeclaration

class ParserEx(Parser):
    """"""

    def __init__(self, tokens):
        Parser.__init__(self, tokens)

    def parse_class_or_interface_declaration(self):
        modifiers, annotations, javadoc = self.parse_modifiers()
        type_declaration = None

        token = self.tokens.look()
        if token.value == 'class':
            type_declaration = self.parse_normal_class_declaration()
        elif token.value == 'enum':
            type_declaration = self.parse_enum_declaration()
        elif token.value == 'interface':
            type_declaration = self.parse_normal_interface_declaration()
        elif token.value == 'record':
            type_declaration = self.parse_record_declaration()
        elif self.is_annotation_declaration():
            type_declaration = self.parse_annotation_type_declaration()
        else:
            self.illegal("Expected type declaration")

        type_declaration._position = token.position
        type_declaration.modifiers = modifiers
        type_declaration.annotations = annotations
        type_declaration.documentation = javadoc

        return type_declaration

    def parse_record_declaration(self):
        name = None
        type_params = None
        implements = None
        body = None

        self.accept('record')

        name = self.parse_identifier()

        if self.would_accept('<'):
            type_params = self.parse_type_parameters()

        parameters = self.parse_formal_parameters()

        if self.try_accept('implements'):
            implements = self.parse_type_list()

        body = self.parse_class_body()

        return RecordDeclaration(name=name,
                                 type_parameters=type_params,
                                 implements=implements,
                                 parameters=parameters,
                                 body=body)