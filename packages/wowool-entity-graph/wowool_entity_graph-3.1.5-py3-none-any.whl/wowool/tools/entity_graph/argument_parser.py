from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase
from wowool.tools.entity_graph.cli import parser_add_tool_entity_graph_arguments


# fmt: off
class ArgumentParser(ArgumentParserBase):

    def __init__(self):
        """
        Wowool Portal Entity Graph
        """
        super(ArgumentParserBase, self).__init__(prog="entity_graph", description=ArgumentParser.__call__.__doc__)
        self.add_argument("-f", "--file", help="folder or file")
        self.add_argument("-i", "--text", help="The input text to process")
        self.add_argument("--lxware", help="location of the language files")
        parser_add_tool_entity_graph_arguments(self)

# fmt: on
