#!/usr/bin/python3

import sys
from wowool.entity_graph import EntityGraph, CollectedResults
from wowool.apps.entity_graph import APP_ID
from wowool.io.console import console
import json
from wowool.document import Document
from wowool.utility.diagnostics import print_diagnostics
from wowool.utility.default_arguments import make_document_collection
from wowool.utility import is_valid_kwargs
import logging


logger = logging.getLogger(__name__)


def parser_add_tool_entity_graph_arguments(parser):
    """
    This is the Entity Mapper
    """
    # add_argument_parser(parser)
    parser.add_argument(
        "-x",
        "--links",
        help="A json config file with the different arguments, :ref:`Entity Graph Configuration <apps_entity_graph_config>`",
    )
    parser.add_argument("-p", "--pipeline", help="pipeline to use.")
    parser.add_argument("-o", "--output_file", help="save to cvs format")

    # neo4j settings.
    parser.add_argument("--server", help="neo4j server use example: 'bolt://localhost:7687' ")
    parser.add_argument("--namespace", help="namespace in the dataset, default empty", default="")
    parser.add_argument("-u", "--user", help="user name", default="test")
    parser.add_argument("--password", help="password for the given connection", default="test")
    parser.add_argument(
        "-s",
        "--silent",
        default=False,
        action="store_true",
        help="Do not print individual rows.",
    )

    return parser


def clean_up(kwargs):
    keys = [k for k in kwargs]
    for key in keys:
        if not kwargs[key]:
            del kwargs[key]


def last(data):
    sz = len(data)
    for idx in range(sz):
        yield idx == (sz - 1), data[idx]


def check_link_file_is_json(link_fn):
    try:
        with open(link_fn, "r") as link_fh:
            return json.load(link_fh)
    except IOError as ioe:
        raise ValueError(f"Could not open the link file {link_fn}", ioe)
        exit(-1)


class CLI:
    def __init__(self, kwargs):
        self.kwargs = kwargs.copy()
        entity_graph_config = check_link_file_is_json(self.kwargs["links"])
        self.doc_collection = make_document_collection(**self.kwargs)
        self.add_entity_graph = EntityGraph(**entity_graph_config)
        self.silent = True if (is_valid_kwargs(kwargs, "silent") and kwargs["silent"] == True) else False

    def process(self, doc: Document):
        print(doc.id, file=sys.stderr)
        if not doc:
            # skip this document.
            return
        doc = self.add_entity_graph(doc)
        print_diagnostics(doc, console)

        return doc

    def run(self):
        collection = self.doc_collection
        if self.kwargs["server"]:
            from wowool.cypher.cypher_stream import CypherStream

            namespace = self.kwargs["namespace"] if self.kwargs["namespace"] else ""
            cs = CypherStream(namespace=namespace)

            if self.kwargs["server"] == "stdout":
                for ip in collection:
                    doc = self.process(self.run_pipeline(ip))
                    entity_graph_results = doc.results(APP_ID)
                    if entity_graph_results:
                        results = CollectedResults(entity_graph_results)
                        for cypher_query in cs(results):
                            # Note: do not use console print as it messes up stuff with '[]'
                            print(cypher_query, ";")

            else:
                from neo4j import GraphDatabase, basic_auth

                driver = GraphDatabase.driver(
                    self.kwargs["server"],
                    auth=basic_auth(self.kwargs["user"], self.kwargs["password"]),
                )

                with driver.session(database="neo4j") as neo4jdb:
                    for ip in collection:
                        doc = self.process(self.run_pipeline(ip))
                        entity_graph_results = doc.results(APP_ID)
                        if entity_graph_results:
                            results = CollectedResults(entity_graph_results)
                            for cypher_query in cs(results):
                                # Note: do not use console print as it messes up stuff with '[]'
                                print(cypher_query)
                                assert neo4jdb, "Something is wrong connecting to the database"
                                neo4jdb.run(cypher_query)

        elif self.kwargs["output_file"]:
            total_results = []
            total_headers = set()

            for ip in collection:
                doc = self.process(self.run_pipeline(ip))
                entity_graph_results = doc.results(APP_ID)
                if entity_graph_results:
                    results = CollectedResults(entity_graph_results).merge()
                    for header in results.headers:
                        total_headers.add(header)

                    for row in results.rows:
                        total_results.append(row)

            from wowool.utility.csv import to_csv

            print("output:", self.kwargs["output_file"], file=sys.stderr)
            to_csv(self.kwargs["output_file"], headers=total_headers, data=total_results)

        else:
            total = []
            for ip in collection:
                doc = self.process(self.run_pipeline(ip))
                entity_graph_results = doc.results(APP_ID)
                if entity_graph_results:
                    results = CollectedResults(entity_graph_results).merge()
                    item = {"id": doc.id, "links": [results.rows]}
                    total.append(item)
            print(json.dumps(total))
