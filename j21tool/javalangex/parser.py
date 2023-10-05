
from javalang.parser import Parser
from javalang import tree
from javalang.tree import Literal
from javalang.tokenizer import Identifier, BasicType
from j21tool.javalangex import RecordDeclaration

class ParserEx(Parser):
    """"""

    def __init__(self, tokens):
        Parser.__init__(self, tokens)

    def parse_identifier_suffix(self):
        """patch for array instantiator method reference"""
        if self.try_accept('[', ']'):
            array_dimension = [None] + self.parse_array_dimension()
            # fix for the syntax of type[]::new.
            if self.try_accept('::'):
                method_reference, type_arguments = self.parse_method_reference()
                return tree.MethodReference(
                    expression=tree.Type(dimensions=array_dimension),
                    method=method_reference,
                    type_arguments=type_arguments)
            
            self.accept('.', 'class')
            return tree.ClassReference(type=tree.Type(dimensions=array_dimension))

        elif self.would_accept('('):
            arguments = self.parse_arguments()
            return tree.MethodInvocation(arguments=arguments)

        elif self.try_accept('.', 'class'):
            return tree.ClassReference()

        elif self.try_accept('.', 'this'):
            return tree.This()

        elif self.would_accept('.', '<'):
            next(self.tokens)
            return self.parse_explicit_generic_invocation()

        elif self.try_accept('.', 'new'):
            type_arguments = None

            if self.would_accept('<'):
                type_arguments = self.parse_nonwildcard_type_arguments()

            inner_creator = self.parse_inner_creator()
            inner_creator.constructor_type_arguments = type_arguments

            return inner_creator

        elif self.would_accept('.', 'super', '('):
            self.accept('.', 'super')
            arguments = self.parse_arguments()
            return tree.SuperConstructorInvocation(arguments=arguments)

        else:
            return tree.MemberReference()

    def parse_type_list(self):
        """patch for Java 8 type annotation"""
        types = list()
        annotations = []

        while True:
            if self.would_accept('@'):
                annotations = self.parse_annotations()

            if self.would_accept(BasicType):
                base_type = self.parse_basic_type()
                self.accept('[', ']')
                base_type.dimensions = [None]
            else:
                base_type = self.parse_reference_type()
                base_type.dimensions = []

            base_type.dimensions += self.parse_array_dimension()
            if annotations:
                base_type.annotations = annotations
                annotations = []

            types.append(base_type)

            if not self.try_accept(','):
                break

        return types
    
    def parse_type_argument(self):
        pattern_type = None
        base_type = None
        annotations = []

        if self.try_accept('?'):
            if self.tokens.look().value in ('extends', 'super'):
                pattern_type = self.tokens.next().value
            else:
                return tree.TypeArgument(pattern_type='?')
            
        if self.would_accept('@'):
            annotations = self.parse_annotations()

        if self.would_accept(BasicType):
            base_type = self.parse_basic_type()
            self.accept('[', ']')
            base_type.dimensions = [None]
        else:
            base_type = self.parse_reference_type()
            base_type.dimensions = []

        base_type.dimensions += self.parse_array_dimension()
        if annotations:
            base_type.annotations = annotations
            annotations = []
            
        return tree.TypeArgument(type=base_type,
                                 pattern_type=pattern_type)

    
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