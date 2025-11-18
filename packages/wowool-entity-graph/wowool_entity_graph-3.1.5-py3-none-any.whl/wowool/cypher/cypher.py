from wowool.diagnostic import Diagnostics
from wowool.document import Document
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)
from wowool.cypher.app_id import APP_ID
from wowool.entity_graph.app_id import APP_ID as APP_ID_ENTITY_GRAPH
from wowool.entity_graph.entity_graph import CollectedResults


class Cypher:

    ID = APP_ID

    def __init__(
        self,
        namespace: str | None = None,
        collection: str | None = None,
        counters: list[str] | None = None,
        graph_data_id=APP_ID_ENTITY_GRAPH,
        line_sep: str | None = None,
    ):
        """
        Initialize the Cypher application

        :param namesapce: The cypher namespace
        :param source: str

        """
        self.namespace = namespace
        self.collection = collection
        self.graph_data_id = graph_data_id
        self.line_sep = line_sep
        self.counters = counters if counters else []

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: Document, diagnostics: Diagnostics) -> Document:
        """
        :param document: The document to be processed and create the cypher script
        :type document: Document

        :returns: The given document with the cypher script. See the :ref:`JSON format <json_apps_cypher>`
        """
        if not document.has_results(self.graph_data_id):
            diagnostics.add("Missing entity graph results", "Cypher", "Critical")
            return

        json_results = document.results(self.graph_data_id)
        results = CollectedResults(json_results)

        from wowool.cypher.cypher_stream import CypherStream

        cypher = CypherStream(self.namespace, self.collection, counters=self.counters)
        lines = [line for line in cypher(results)]
        if self.line_sep is None:
            document.add_results(APP_ID, {"cypher": lines})
        else:
            cypher_script = self.line_sep.join(lines)
            cypher_script += self.line_sep
            document.add_results(APP_ID, {"cypher": cypher_script})
        return document
