from pathlib import Path
import hashlib
from dataclasses import dataclass
import logging
from wowool.annotation import Concept
from wowool.entity_graph.app_id import APP_ID
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.document.analysis.document import AnalysisDocument
from typing import List, Dict, cast
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)
from wowool.string import camelize
from re import sub
from wowool.native.core.analysis import (
    get_internal_concept,
    add_internal_concept_attribute,
    get_internal_concept_args,
    add_internal_concept,
)
from collections import defaultdict
from wowool.entity_graph.resolve_variable import resolve_variable
from wowool.entity_graph.objects import (
    Node,
    ContentName,
    ContentLiteral,
    ContentSlot,
    ContentURI,
    NodeCandidate,
    Slot,
    Link,
    LinkCandidate,
    StaticNode,
    DataNode,
    split_name,
    StoreType,
)

import copy
from wowool.document.analysis.utilities import get_pipeline_concepts

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# cannot import the ID from the packages as the packages may not be there
# you can run the entity_graph without topics or themes.
APP_ID_TOPIC_IDENTIFIER = "wowool_topics"
APP_ID_THEMES = "wowool_themes"


logger = logging.getLogger("entity_graph")

THIS_DIR = Path(__file__).parent

# some const variables.
URI = "uri"
NAME = "name"
RELATION = "relation"
LEN_RELATION = len(RELATION)
DELIMITER = "delimiter"
SLOT = "slot"
FROM = "from"
LEN_FROM = len(FROM)
TO = "to"
LEN_TO = len(TO)
LABEL = "label"
SCOPE = "scope"
CONTENT = "content"
COUNT = "count"
CONCEPT = "concept"
ATTRIBUTES = "attributes"
OPTIONAL = "default"
ACTION = "action"
FROM_TO_DELIMITER = set([FROM, TO, RELATION])
SUPPORTED_ACTIONS = set(["link_attribute"])
ELEMENTS = "nodes"
URI_DOCUMENT = "document"
VARIABLE_DOCUMENT = "document"
NODE_IDX = 0
NODE_DATA = 1
NODE_CONTEXT = 2
PROPERTIES = "attributes"


SPECIAL_URIS = {
    "Subject": {"child_uri": ["Person", "Company", "NP", "PronPhrase"]},
    "Object": {"child_uri": ["Person", "Company", "NP", "PronPhrase", "AdjP"]},
}


@dataclass
class Scope:
    """Class for keeping track of an item in inventory."""

    begin: int = 0
    end: int = 0


@dataclass
class NodeInfo:
    idx: int
    data: dict
    concept: Concept | None = None


def find_index_in_concepts(concepts: list[Concept], concept: Concept, offset: int):
    for idx, c in enumerate(concepts[offset:]):
        if c == concept:
            return idx + offset
    # look also above in cas it the same begin and end offset.
    idx = offset - 1

    while idx >= 0:
        if concepts[idx] == concept:
            return idx
        if concepts[idx].begin_offset != concept.begin_offset or concepts[idx].end_offset != concept.end_offset:
            break
        idx -= 1

    return -1


def create_scope(concepts: list[Concept], scope_concept: Concept, outer_scope: Scope):
    eidx = outer_scope.end
    cidx = outer_scope.begin + 1
    while cidx != eidx:
        concept = concepts[cidx]
        if concept.end_offset >= scope_concept.end_offset:
            end_idx = cidx + 1 if concept.end_offset == scope_concept.end_offset else cidx
            return Scope(outer_scope.begin + 1, end_idx)
        cidx += 1


class MergedResults:
    def __init__(self, headers: List[str], rows: List[Dict]):
        self.headers = headers
        self.rows = rows

    def __rep__(self):
        print(f"<MergedResults {self.headers}>")

    def to_json(self):
        return {"headers": self.headers, "rows": self.rows}


def flatten_attributes(structured_dict):
    if "attributes" in structured_dict:
        retval = {"label": structured_dict["label"], "name": structured_dict["name"]}
        for key, values in structured_dict["attributes"].items():
            retval[key] = values
        return retval
    else:
        return structured_dict


def is_uri_content(el):
    if isinstance(el, (Node, Slot)):
        if isinstance(el.content, ContentURI):
            return True


def is_uri_node(el):
    if el:
        if isinstance(el, NodeCandidate):
            el = el.element
        return is_uri_content(el)


def make_offset_mappings(concepts: list[Concept]):
    retval = defaultdict(list)
    for concept in [c for c in concepts if c.has_canonical()]:
        retval[(concept.begin_offset, concept.end_offset)].append(concept)

    return retval


def resolve_document_fstring(slot, _context):
    try:
        fvalue = slot.content.name
        resolved_value = resolve_variable(fvalue, None, _context)
        if resolved_value is None:
            return "None"
        return resolved_value

    except Exception:
        # it ok if we fail at this point, they will be filled in later when we see then
        # But there could be a initial to set document info.
        pass


def detect_output_format(jo: list):
    if len(jo) > 0 and jo[0].get("from", None) is not None:
        return "graph"
    return "table"


class CollectedResults:
    """
    The Graph information result object that contains 3 dict. The `from`, `relation` and `to`.
    These dict's can be accessed separately or merged into one dict.

    .. code-block:: python

        analyzer = Language("english")
        entities = Domain("english-entity")
        entity_graph = EntityGraph( movie_link_config )
        for idx, doc in enumerate(Corpus("english/movies").random(2)):
            # adding custom slots from Type -> folder name.
            entity_graph.slots["Type"] = {"data" : f"{Path(document.id()).parent.name}" }
            doc = entity_graph(self.movies(entities(analyzer(doc))))
            print(f"{doc.id()}") # print the document id
            print(results.entity_graph)

    """

    __slots__ = ["df_from", "df_relation", "df_to"]

    def __init__(self, data=None):
        self.df_from = []
        self.df_relation = []
        self.df_to = []
        if data:
            self.from_json(data)

    def _append(self, from_key, relation, to_key):
        logger.debug(f"Append: {from_key}, {relation}, {to_key}")
        self.df_from.append(from_key)
        self.df_relation.append(relation)
        self.df_to.append(to_key)

    def results(self) -> MergedResults:
        tbl_size = len(self.df_from)
        idx = 0
        retval = []
        headers = set()
        while idx < tbl_size:
            dm = (
                {f"{FROM}_{key}": value for key, value in flatten_attributes(self.df_from[idx]).items()}
                | {f"{RELATION}_{key}": value for key, value in flatten_attributes(self.df_relation[idx]).items()}
                | {f"{TO}_{key}": value for key, value in flatten_attributes(self.df_to[idx]).items()}
            )
            for k in dm:
                if k not in headers:
                    headers.add(k)
            retval.append(dm)
            idx += 1
        headers = sorted(headers)
        return MergedResults(headers, retval)

    def merge(self):
        """
        return a merged list with the different fields.
        """
        import json

        tbl_size = len(self.df_from)
        idx = 0
        retval = []
        uniq_entries = set()
        headers = set()
        while idx < tbl_size:
            dm = (
                {f"{FROM}_{key}": value for key, value in flatten_attributes(self.df_from[idx]).items()}
                | {f"{RELATION}_{key}": value for key, value in flatten_attributes(self.df_relation[idx]).items()}
                | {f"{TO}_{key}": value for key, value in flatten_attributes(self.df_to[idx]).items()}
            )
            for k in dm:
                if k not in headers:
                    headers.add(k)
            row_str = json.dumps(dm)
            row_hash = hashlib.sha1(row_str.encode()).hexdigest()
            if row_hash not in uniq_entries:
                uniq_entries.add(row_hash)
                retval.append(dm)
            idx += 1

        headers = sorted(headers)

        return MergedResults(headers, retval)

    def __rep__(self):
        self.merge()

    def __str__(self):
        return str(self.merge())

    def to_json(self):
        return [{FROM: f, RELATION: r, TO: t} for f, r, t in zip(self.df_from, self.df_relation, self.df_to)]

    def from_json(self, data):
        if detect_output_format(data) == "graph":
            for item in data:
                self.df_from.append(item[FROM])
                self.df_relation.append(item[RELATION])
                self.df_to.append(item[TO])
        else:
            for item in data:
                from_key = {k[LEN_FROM + 1 :]: v for k, v in item.items() if k.startswith(f"{FROM}_")}
                relation = {k[LEN_RELATION + 1 :]: v for k, v in item.items() if k.startswith(f"{RELATION}_")}
                to_key = {k[LEN_TO + 1 :]: v for k, v in item.items() if k.startswith(f"{TO}_")}
                self.df_from.append(from_key)
                self.df_relation.append(relation)
                self.df_to.append(to_key)


def clean_label(phrase):
    """
    Put every first letter of every word into uppercase.
    """
    init_caps = ""
    for char in phrase:
        if char == " " or char == "-":
            init_caps += "_"
        elif char.isalnum():
            init_caps += char

    return init_caps


class EntityGraphException(RuntimeError):
    pass


def get_special_child_uris(uri):
    if parent := SPECIAL_URIS.get(uri, None):
        for sub_uri in parent["child_uri"]:
            yield (sub_uri)


def _find_label_in_slots(slots, label2find):
    if label2find in slots:
        slot = slots[label2find]
        return slot.label
    return None


def make_scope(link_info):
    if isinstance(link_info, str):
        return Node(label=link_info, content=ContentName(name=link_info))
    else:
        raise ValueError(f"Unsupported scope type: {link_info}, only supports str")


def get_store_type(slot_):
    store = slot_.get("store", "sentence")
    if store == "last_seen":
        return StoreType.LAST_SEEN
    elif store == "first_seen":
        return StoreType.FIRST_SEEN
    elif store == "sentence":
        return StoreType.SENTENCE
    else:
        raise ValueError(f"Unsupported 'store' value: {store}, supported values are [ 'last_seen', 'first_seen' ].")


def make_slot(key: str, slot_):
    if label := extract_label(slot_):
        name = slot_.get(NAME, None)
        if name is None:
            name = label

        store_type = get_store_type(slot_)
        return Slot(
            store_type=store_type,
            key=key,
            content=ContentName(name),
            label=label,
            properties=get_property_keys(slot_),
        )


def convert_to_label(name: str):
    if name.find(".") == -1:
        return name
    if name.isupper():
        return name
    return camelize(sub(r"[.()]", " ", name))


def extract_label(node_config: dict | str):
    if isinstance(node_config, str):
        return node_config
    name = node_config.get(NAME, None)
    if name:
        label = node_config.get(LABEL, convert_to_label(name))
        return label
    else:
        if label := node_config.get(LABEL, None):
            return label
        else:
            raise ValueError(f"Missing key '{NAME}' or '{LABEL} in node configuration: {node_config}")


def get_property_keys(node_config: dict):
    return node_config.get(PROPERTIES, {})


def check_link_config(link):
    if not isinstance(link, dict):
        raise ValueError("Invalid link configuration: link must be a dictionary")
    if FROM not in link:
        raise ValueError(f"Invalid link configuration: link requires '{FROM}' key")
    if RELATION not in link:
        raise ValueError(f"Invalid link configuration: link requires '{RELATION}' key")
    if TO not in link:
        raise ValueError(f"Invalid link configuration: link requires '{TO}' key")


def make_uri_node_from_dict(node_config: dict) -> Node:
    name = node_config.get(NAME, None)
    label = extract_label(node_config)
    if name:
        node = Node(label=label, content=ContentName(name=name))
        node.properties = get_property_keys(node_config)
        return node
    else:
        return Node(label=label, content=ContentName(name=label))


def isValidLinkResult(concepts, from_nodes, to_nodes, relation_nodes, from_node_idx, to_node_idx):
    from_node = from_nodes[from_node_idx]
    to_node = to_nodes[to_node_idx]
    if from_node.idx < to_node.idx:
        # normal order of concepts.
        lhs_idx = from_node.idx
        rhs_idx = to_node.idx
        lhs_node_concept = from_node.concept
        lhs_node_uri = lhs_node_concept.uri
        rhs_node_concept = to_node.concept
        if not rhs_node_concept:
            return True
        rhs_node_uri = rhs_node_concept.uri
        stage = 0
        concept_range = concepts[lhs_idx : rhs_idx + 1]
        for concept in concept_range:
            if stage == 0:
                if concept.uri == lhs_node_uri:
                    continue
                elif concept.uri == rhs_node_uri:
                    stage = 1
            elif stage == 1:
                if concept.uri == lhs_node_uri:
                    return False
        return True

    else:
        # the to is before the from
        lhs_idx = to_node.idx
        rhs_idx = from_node.idx
        lhs_node_concept = to_node.concept
        if not lhs_node_concept:
            return True
        lhs_node_uri = lhs_node_concept.uri
        rhs_node_concept = from_node.concept
        if not rhs_node_concept:
            return True
        rhs_node_uri = rhs_node_concept.uri
        stage = 0
        concept_range = concepts[lhs_idx:]
        for concept in concept_range:
            if stage == 0:
                if concept.uri == lhs_node_uri:
                    continue
                elif concept.uri == rhs_node_uri:
                    stage = 1
            elif stage == 1:
                if concept.uri == lhs_node_uri:
                    return False
        return True


class EntityGraph:
    """
    Class to generate Graph information in json format.

    .. code-block:: python

        analyzer = Language(language="english")
        entities = Domain("english-entity")
        links = [{ "source":{"name": "Person", "label": "MyPerson"}, "target": {"name": "Company"}, "relation": "PersonCompany"}]

        entity_graph = EntityGraph( links=links, nodes=nodes )
        for idx, doc in enumerate(Corpus("english/movies").random(2)):
            doc = entity_graph(self.movies(entities(analyzer(doc))))
            print(doc.entity_graph)
    """

    ID = APP_ID
    docs = """The Entity Graph application produces a list of links between entities."""

    def __init__(
        self,
        links: list[dict] | None = None,
        nodes: dict[str, dict] | None = None,
        topics: dict | None = None,
        themes: dict | None = None,
        output_format: str = "graph",
        add_offsets: bool = False,
    ):
        """
        Initialize a :class:`EntityGraph` instance

        :param links: A list of the links we want to create.
        :type links: A ``list(dict)`` ex: [ {"source":{ },"target": { },"relation":{ } } , ...  ]
        :param nodes: A list of the Concept that we want to remember to create links.
        :type nodes: A ``list(dict)`` ex: [ {"person" : { "name":"Person" } }, ...  ]
        :param topics: Configuration on node you want to attach the topics to.
        :type topics: A ``dict``  ex: {"target": "Document"}
        :param themes: Configuration on node you want to attach the themes to.
        :type themes: A ``dict``  ex: {"target": "Document"}
        :param output_format: The output format for the entity graph.
        :type output_format: str, can be "graph" or "table"
        """
        self.egc = {}
        self.concept_filter = set()
        self.known_concepts = None
        self.output_format = output_format
        self.add_offsets = add_offsets
        # add slots back in
        self.__init__slots_and_nodes(nodes)
        # self.add_default_document_slot()
        self.__init_topic_identifier(topics)
        self.__init_semantic_themes(themes)
        self._generate_link_candidates(links)
        self.document = None
        self.entities_to_add = []

    def cleanup_slots(self):
        only_slots = {k: v for k, v in self.key_2_slots.items() if isinstance(v, Slot) and v.store_type != StoreType.SENTENCE}
        self.key_2_slots = only_slots
        only_slots = {k: v for k, v in self.uri_2_slots.items() if isinstance(v, Slot) and v.store_type != StoreType.SENTENCE}
        self.uri_2_slots = only_slots

    def add_default_document_slot(self):
        if URI_DOCUMENT not in self.key_2_slots:
            self.key_2_slots[URI_DOCUMENT] = make_slot(URI_DOCUMENT, {NAME: "document.id"})

    def get_element_or_slot(self, key: str | dict):
        if isinstance(key, dict):
            name = key.get(NAME, None)
            if name:
                uri, property = split_name(name)
                if uri == ELEMENTS:
                    uri = property
                if uri:
                    if uri in self.config_key_2_slots:
                        node = self.config_key_2_slots[uri]
                        label = key.get(LABEL, node.label)
                        if isinstance(node, Slot):
                            return Slot(
                                store_type=node.store_type,
                                key=uri,
                                content=node.content,
                                label=label,
                                properties=get_property_keys(key),
                                optional=node.optional,
                            )
                        else:
                            return Node(
                                label=label,
                                content=ContentName(name=key[NAME]),
                                optional=key.get(OPTIONAL),
                                properties=get_property_keys(key),
                            )
                    else:
                        node = make_uri_node_from_dict(key)
                        return node
                else:
                    raise ValueError(f"Invalid element configuration: element '{key}' not found in nodes")

            else:
                if label := key.get(LABEL, None):
                    return Node(label=label, content=ContentName(name=label))
                else:
                    raise ValueError(f"Invalid element configuration: missing key 'name' in {key}")

        else:
            if key in self.config_key_2_slots:
                el = self.config_key_2_slots[key]
                label = el.label if el.label else key
                properties = el.properties
                optional = el.optional
                if el.content.name.startswith("document."):
                    el.store_type = StoreType.FIRST_SEEN

                if el.store_type == StoreType.SENTENCE:
                    return Node(label=label, content=ContentName(name=key), properties=properties, optional=optional)
                else:
                    return Slot(
                        store_type=el.store_type, key=key, label=label, content=el.content, properties=properties, optional=optional
                    )
            return Node(label=key, content=ContentName(name=key))
        return None

    def __init__slots_and_nodes(self, nodes: dict[str, dict]):
        self.config_key_2_slots = {}
        self.config_uri_2_slots = {}
        if nodes:
            for key, el in nodes.items():
                # new keyword is store in the element.
                if element := make_slot(key, el):
                    self.config_key_2_slots[key] = element
                    if not isinstance(element.content, ContentLiteral):
                        self.config_uri_2_slots[element.content.uri] = element
                else:
                    raise ValueError(f"Invalid 'Node.store' configuration: {el}")

    def add_scope_uris(self, uri: str):
        if self.scope_uris is None:
            self.scope_uris = set()
        self.scope_uris.add(uri)

    def _generate_link_candidates(self, links):
        self.config_link_candidates = {}
        link_id = 0
        if links:
            for link in links:
                check_link_config(link)

                if TO in link:
                    # check if the to is a slot or element.
                    to_ = self.get_element_or_slot(link[TO])
                    if OPTIONAL in link[TO]:
                        optional = link[TO].pop(OPTIONAL)
                        to_.optional = StaticNode(label=optional[LABEL], value=optional[CONTENT])

                if RELATION in link:
                    relation_ = self.get_element_or_slot(link[RELATION])

                    if relation_:
                        el = relation_
                        if OPTIONAL in link[RELATION]:
                            optional = link[RELATION].pop(OPTIONAL)
                            el.optional = StaticNode(label=optional[LABEL], value=optional[CONTENT])

                scope_ = None
                if SCOPE in link:
                    scope_ = make_scope(link[SCOPE])
                    if isinstance(scope_.content, ContentName):
                        uri: str = scope_.content.uri

                if FROM in link:
                    from_ = self.get_element_or_slot(link[FROM])
                    el = from_
                    uri = el.content.uri
                    if uri in self.config_key_2_slots:
                        el = self.config_key_2_slots[uri]
                        uri = el.content.uri

                    action = link.get(ACTION)
                    if action and action not in SUPPORTED_ACTIONS:
                        raise ValueError(f"Unsupported action '{action}' in link: '{link}' configuration.")
                    link_ = Link(from_=from_, to_=to_, relation_=relation_, scope=scope_, action=action)
                    link_candidate = LinkCandidate(link_)
                    link_candidate.candidate_type = "links"
                    link_candidate.link_id = link_id
                    link_id += 1
                    if isinstance(link_.from_, Slot) and not isinstance(link_.to_, Slot):
                        # swap the from and to for the search and set a flag to swap them when done
                        link_.swap_from_to = True
                        link_.from_, link_.to_ = link_.to_, link_.from_
                        uri = link_.from_.label

                    if uri not in self.config_link_candidates:
                        self.config_link_candidates[uri] = []
                    self.config_link_candidates[uri].append(link_candidate)

    def is_content_uri(self, content: ContentName | str):
        if self.known_concepts is None:
            self.known_concepts = get_pipeline_concepts(self.document)
        if isinstance(content, ContentName):
            if content.uri in self.known_concepts:
                return True
        elif content in self.known_concepts:
            return True
        return False

    def add_np_on_subject_object(self, uri: str):
        for sub_uri in get_special_child_uris(uri):
            self.concept_filter.add(sub_uri)

    def assign_content_field(self, document: AnalysisDocument, node: Node):
        if node.content.uri == ELEMENTS:
            if node.content.property not in self.key_2_slots:
                raise EntityGraphException(f"Node {node.content.property} not found in nodes")
            node.content = ContentSlot(node.content.name)
            slot = self.key_2_slots[node.content.property]
            self.add_np_on_subject_object(slot.content.uri)

            # if slot.label:
            #     node.label = slot.label
            # slot.content = ContentSlot(slot.content.name)
            return slot

        elif isinstance(node, Slot) and node.key in self.key_2_slots:
            node.content = ContentSlot(node.content.name)
            slot = self.key_2_slots[node.key]
            if node.label is None:
                node.label = slot.label
        elif isinstance(node, Node) and node.content.name in self.key_2_slots:
            slot = self.key_2_slots[node.content.name]
            if self.is_content_uri(slot.content):
                node.content = ContentURI(slot.content.name)
                self.concept_filter.add(node.content.uri)
                if node.content.property and self.is_content_uri(node.content.property):
                    self.concept_filter.add(node.content.property)
                self.add_np_on_subject_object(node.content.uri)
            else:
                node.content = ContentLiteral(slot.content.name)
            if node.label is None:
                node.label = slot.label
        elif self.is_content_uri(node.content):
            self.concept_filter.add(node.content.uri)
            self.add_np_on_subject_object(node.content.uri)
            node.content = ContentURI(node.content.name)
        else:
            node.content = ContentLiteral(node.content.name)
        return node

    def generate_matching_info(self, document: AnalysisDocument):
        self.document = document
        self.scope_uris = None
        self.concept_filter = set()
        self.link_candidates = copy.deepcopy(self.config_link_candidates)
        self.key_2_slots = copy.deepcopy(self.config_key_2_slots)
        self.uri_2_slots = {}

        for key, slot_el in self.key_2_slots.items():
            if isinstance(slot_el, Slot):
                uri = slot_el.content.uri
                self.uri_2_slots[uri] = slot_el
                if uri not in self.link_candidates:
                    self.link_candidates[uri] = []
                self.link_candidates[uri].append(NodeCandidate(slot_el))
            if self.is_content_uri(slot_el.content):
                self.concept_filter.add(uri)

        for link_candidates in self.link_candidates.values():
            for link_candidate in link_candidates:
                if isinstance(link_candidate, LinkCandidate):
                    link: Link = link_candidate.link
                    if link.scope:
                        self.concept_filter.add(link.scope.content.name)
                        self.uri_2_slots[link.scope.content.name] = link.scope
                        self.add_scope_uris(link.scope.content.name)
                    link.from_ = self.assign_content_field(document, link.from_)
                    link.to_ = self.assign_content_field(document, link.to_)
                    link.relation_ = self.assign_content_field(document, link.relation_)

        self.cleanup_slots()

        self.all_data_node_2_concept_filter(self.topic_data, document)
        self.all_data_node_2_concept_filter(self.theme_data, document)

        # need to add the topics and themes to the concept filter if requested

    def all_data_node_2_concept_filter(self, data_node, document: AnalysisDocument):
        if data_node and data_node.slot:
            if self.is_content_uri(data_node.slot.content):
                self.concept_filter.add(data_node.slot.content.uri)

    def __init_topic_identifier(self, description):
        self.topic_identifier = None
        self.topic_data = self.__init_node_data("topics", description)

    def __init_semantic_themes(self, description):
        self.semantic_themes = None
        self.theme_data = self.__init_node_data("themes", description)

    def __init_node_data(self, name: str, description: dict):

        if description is None:
            return None

        node_data = None
        #  check that there is a node that we can attach the topics to.
        if TO not in description:
            raise EntityGraphException(f"""missing "{TO}" field in {name} description. "{name}" : {{ "{TO}": "element_name" }} """)

        if slot := self.get_element_or_slot(description[TO]):
            if slot.content.uri == URI_DOCUMENT:
                node_data = DataNode(key=slot.key, label=slot.label, slot=slot)
            else:
                if isinstance(description[TO], str):
                    label = slot.label
                else:
                    label = extract_label(description[TO])
                node_data = DataNode(label=label, slot=slot)

        else:
            raise EntityGraphException(f"The {name} field has to be linked to a existing element.")

        # threshold for the nr of topics default will be 5.
        node_data.count = description[COUNT] if COUNT in description else 5
        return node_data

    def reset_link_exist(self):
        self.unique_links = set()

    def does_link_exist(self, from_node: NodeInfo, relation_node: NodeInfo, to_node: NodeInfo):
        if to_node.concept is None:
            # we are linking to a data node, so we do not need to check if it exists.
            return False
        from_idx = from_node.concept.begin_offset if isinstance(from_node.concept, Concept) else from_node.idx
        to_idx = to_node.concept.begin_offset if isinstance(to_node.concept, Concept) else to_node.idx

        if from_idx == to_idx:
            # we do not want to link to the same node.
            # so we say it's already there to skip it
            return True
        relation_idx = relation_node.concept.begin_offset if isinstance(relation_node.concept, Concept) else relation_node.idx
        values = [from_idx, relation_idx, to_idx]
        values.sort()
        values = [v for v in map(str, values)]
        key = "".join(map(str, values))
        if key in self.unique_links:
            return True
        self.unique_links.add(key)
        return False

    def _create_relation(self, from_key, relation, to_key, **kwargs):
        # self.unique_links[]
        # logger.debug(f"Create: {from_key}-{relation}-{to_key}")
        self.results._append(from_key, relation, to_key)

    def _add_data_collection_to_slot(self, data, data_label, slot_value: NodeInfo, count: int = 5):
        for item in data[:count]:
            topic_node = {LABEL: data_label, NAME: item["name"]}
            self._create_relation(topic_node, {LABEL: data_label}, slot_value.data)

    def _add_slot_to_slot(
        self,
        from_slot_name,
        from_slot_value,
        rel_slot_name,
        to_slot_name,
        to_slot_value,
        to_slot_data=None,
    ):

        from_data = {LABEL: from_slot_name, NAME: from_slot_value}
        if to_slot_data:
            to_data = {LABEL: to_slot_name, NAME: to_slot_value, **to_slot_data}
        else:
            to_data = {LABEL: to_slot_name, NAME: to_slot_value}

        self._create_relation(from_data, {LABEL: rel_slot_name}, to_data)

    def _clear_slots(self):
        for slot_name in self.key_2_slots:
            if self.key_2_slots[slot_name].data:
                self.key_2_slots[slot_name].data = None

    def _get_document_node_data(self, document, themes):
        content_text = ""
        if themes and len(themes):
            content_text = "themes:"
            content_text += " ,".join([theme["theme"] for theme in themes])
            content_text += ".\n\n"
        content_text += snippet_cleaner(document.text).strip()[: self.content_data_size]
        sha = hashlib.sha1(content_text.encode())
        return sha.hexdigest(), content_text

    def required_concepts(self, concept: Concept) -> bool:
        return concept.uri in self.concept_filter

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        try:
            document = self.__process__(document, diagnostics)
        except Exception as e:
            print(f"Error: {e}")
            diagnostics.add(Diagnostic(document.id, f"{APP_ID}: {e}", DiagnosticType.Error))
        return document

    def add_entity_to_document(self, document: AnalysisDocument, node: NodeInfo):
        if node.concept is None or node.concept.uri == node.data[LABEL]:
            return
        # insert concept if not exists
        entity_uri = node.data[LABEL]
        self.entities_to_add.append((node.concept.begin_offset, node.concept.end_offset, entity_uri, node.concept))

    def insert_new_entities(self, document: AnalysisDocument):

        for node in self.entities_to_add:
            begin_offset, end_offset, entity_uri, concept = node
            analysis = document.analysis
            entity_internal = get_internal_concept_args(analysis, begin_offset, end_offset, entity_uri)
            if entity_internal is None:
                entity_internal = add_internal_concept(analysis, begin_offset, end_offset, entity_uri)
                if entity_internal:
                    for key, values in concept.attributes.items():
                        for value in values:
                            add_internal_concept_attribute(analysis, entity_internal, key, value)

    def __process__(self, document: AnalysisDocument, diagnostics: Diagnostics):
        """
        The EntityGraph is a callable object so you can pass it a document.

        .. code-block:: python

                # create a EntityGraph
                entity_graph = EntityGraph( link_config )
                # get the analysis of your input
                doc = entities(analyzer(input_text))
                # pass it to the entity graph object.
                doc = entity_graph(doc)
                print(doc.entity_graph)

        """
        assert isinstance(document, AnalysisDocument), "Only wowool.document.Document object supported."

        if not document.analysis:
            raise EntityGraphException("""missing document analysis data """)

        self.generate_matching_info(document)
        self.entities_to_add = []

        _context = {VARIABLE_DOCUMENT: document}

        themes = document.results(APP_ID_THEMES)
        if self.key_2_slots:
            for slot_name in self.key_2_slots:
                # delete previous expression slots data in the slots
                slot = self.key_2_slots[slot_name]
                slot.data = None

        self.results = CollectedResults()

        if self.theme_data and themes and self.theme_data.slot and self.theme_data.slot.content.uri == URI_DOCUMENT:
            slot = self.theme_data.slot
            if slot.data is None:
                slot.data = resolve_document_fstring(slot, _context)
            if slot.data is not None:
                label = self.theme_data.label if self.theme_data.label else slot.label
                if slot_node := self.make_node(label=label, link_node=slot, context=_context):
                    self._add_data_collection_to_slot(themes, data_label="theme", slot_value=slot_node, count=self.theme_data.count)
                themes = None
        else:
            if self.theme_data is not None:
                diagnostics.add(
                    Diagnostic(
                        document.id,
                        f"{APP_ID}: Themes requested but not passed in the pipeline, add 'themes.app'",
                        DiagnosticType.Warning,
                    )
                )

        # Add the topics to a given node
        topics = document.results(APP_ID_TOPIC_IDENTIFIER)

        if self.topic_data and topics and self.topic_data.slot and self.topic_data.slot.content.uri == URI_DOCUMENT:
            slot = self.topic_data.slot
            if slot.data is None:
                slot.data = resolve_document_fstring(slot, _context)
            if slot.data is not None:
                label = self.topic_data.label if self.topic_data.label else slot.label
                if slot_node := self.make_node(label=label, link_node=slot, context=_context):
                    self._add_data_collection_to_slot(topics, data_label="topic", slot_value=slot_node, count=self.topic_data.count)
                topics = None
        else:
            if self.topic_data is not None:
                diagnostics.add(
                    Diagnostic(
                        document.id,
                        f"{APP_ID}: Topics requested but not passed in the pipeline, add 'topics.app'",
                        DiagnosticType.Warning,
                    )
                )

        self.scopes = defaultdict(list)

        for sent in document.analysis:
            all_concepts = [concept for concept in Concept.iter(sent)]
            _context["offset_mappings"] = make_offset_mappings(all_concepts)
            concepts = [concept for concept in all_concepts if self.required_concepts(concept)]

            for idx, concept in enumerate(concepts):
                logger.debug(f"- Candidates: {idx}: {concept._annotation_idx}  {concept=} {concept.literal}")

            nrof_concepts = len(concepts)
            unique_uri = set()
            for cidx, concept in enumerate(concepts):
                unique_uri.add(concept.uri)

                if concept.uri in self.uri_2_slots:
                    logger.debug(f" -- SLOT concept {concept.uri=} {concept.literal=}")
                    slot_name = concept.uri
                    slot = self.uri_2_slots[slot_name]
                    if slot.store_type == StoreType.FIRST_SEEN and slot.data is None:
                        self.uri_2_slots[slot_name].data = concept
                    elif slot.store_type == StoreType.LAST_SEEN:
                        self.uri_2_slots[slot_name].data = concept

                    if topics and self.topic_data and self.topic_data.slot.content.uri == slot_name:
                        if slot_node := self.make_node(
                            concept=slot.data, link_node=self.topic_data.slot, context=_context, label=self.topic_data.label
                        ):
                            self._add_data_collection_to_slot(topics, data_label="topic", slot_value=slot_node, count=self.topic_data.count)
                        topics = None

                    if themes and self.theme_data and self.theme_data.slot.content.uri == slot_name:
                        if slot_node := self.make_node(
                            concept=slot.data, link_node=self.theme_data.slot, context=_context, label=self.theme_data.label
                        ):
                            self._add_data_collection_to_slot(themes, data_label="theme", slot_value=slot_node, count=self.theme_data.count)
                        themes = None

                if self.scope_uris and concept.uri in self.scope_uris:
                    logger.debug(f"  -- SCOPE concept {concept.uri=} {concept.literal=}")
                    self.scopes[concept.uri].append((cidx, concept))

            self.reset_link_exist()
            for uri in unique_uri:
                if uri in self.link_candidates:
                    # print(f"-> LINK: {self.link_candidates[concept.uri]=}")
                    for link_candidate in self.link_candidates[uri]:
                        if hasattr(link_candidate, "element") and isinstance(link_candidate.element, Slot):
                            continue
                        link = link_candidate.link

                        from_link = link.from_
                        to_link = link.to_
                        rel_link = link.relation_

                        link_scope = None
                        # if link.scope is not None:
                        #     scope_uri = link.scope.content.uri
                        #     if scope_uri not in self.scopes:
                        #         continue
                        #     else:
                        #         list_of_scopes = self.scopes[scope_uri]
                        #         scope_item = self.find_scope(list_of_scopes, concept)
                        #         if scope_item:
                        #             scope_idx, scope_concept = scope_item
                        #             link_scope = create_scope(
                        #                 concepts,
                        #                 scope_concept,
                        #                 Scope(scope_idx, nrof_concepts),
                        #             )
                        #         else:
                        #             continue

                        _scope = link_scope
                        last_valid_to_index = -1
                        from_nodes = self.find_node(concepts, from_link, _scope, _context)
                        for from_node_idx, from_node in enumerate(from_nodes):
                            scope_item = None
                            link_scope = None
                            if link.scope is not None:
                                scope_uri = link.scope.content.uri
                                if scope_uri not in self.scopes:
                                    continue
                                else:
                                    list_of_scopes = self.scopes[scope_uri]
                                    concept = from_node.concept
                                    scope_item = self.find_scope(list_of_scopes, concept)
                                    if not scope_item:
                                        continue
                                    else:
                                        scope_idx, scope_concept = scope_item
                                        link_scope = create_scope(
                                            concepts,
                                            scope_concept,
                                            Scope(scope_idx, nrof_concepts),
                                        )

                            # here we have all the nodes with a given uri.
                            # from_node = from_nodes[0]
                            # next_idx = min(cidx + 1, nrof_concepts)
                            # _next_scope = link_scope

                            to_nodes = self.find_node(concepts, to_link, link_scope, _context)
                            if not to_nodes:
                                if to_link.optional:
                                    to_nodes = make_default_node(to_link.optional)
                                if not to_nodes:
                                    logger.debug(f"!!! No to node found! {to_link}")
                                    continue
                            # TODO: add exclude filters.
                            # # check the index , if -1 it's from a slot so it's valid.
                            # if to_nodes[0].idx != -1:
                            #     # else if the to is smaller then the from then we do not want it.
                            #     # it means that the to_node is before the from node.
                            #     if to_nodes[0].idx <= from_nodes[0][0]:
                            #         continue

                            relation_nodes = self.find_node(concepts, rel_link, link_scope, _context)
                            if not relation_nodes:
                                if rel_link.optional:
                                    relation_nodes = make_default_node(rel_link.optional)
                                if not relation_nodes:
                                    logger.debug(f"!!! No relation found! {rel_link} , {relation_nodes}")
                                    continue

                            relation_node = relation_nodes[0]

                            for to_node_idx, to_node in enumerate(to_nodes):
                                if link.swap_from_to:
                                    from_node, to_node = to_node, from_node
                                if self.does_link_exist(from_node, relation_node, to_node):
                                    continue
                                if (from_node.data is not None) and (relation_node.data is not None) and (to_node.data is not None):
                                    valid_link = isValidLinkResult(
                                        concepts, from_nodes, to_nodes, relation_nodes, from_node_idx, to_node_idx
                                    )
                                    self.add_entity_to_document(document, from_node)
                                    self.add_entity_to_document(document, to_node)
                                    self.add_entity_to_document(document, relation_node)
                                    if from_node.concept == to_node.concept:
                                        valid_link = False
                                    if valid_link:
                                        self._create_relation(
                                            from_node.data,
                                            relation_node.data,
                                            to_node.data,
                                        )
                                        # add the to_node item as a attribute to the from_node
                                        # print("------>>>>>", link)
                                        if link.action == "link_attribute":
                                            if isinstance(from_node.concept, Concept):
                                                if interal_concept := get_internal_concept(document.analysis, from_node.concept):
                                                    key = relation_node.data[LABEL]
                                                    add_internal_concept_attribute(
                                                        document.analysis, interal_concept, key, to_node.data[NAME]
                                                    )
                                                    document.analysis.reset()

                                        if is_uri_node(to_link) and is_uri_node(from_link) and to_link.content.uri == from_link.content.uri:
                                            #  in case we are dealing with the same concept , then we cannot limit the scope.
                                            pass
                                        else:
                                            last_valid_to_index = max(to_node.idx, from_node.idx)

        self._clear_slots()
        self.insert_new_entities(document)
        graph_json_results = self.results.to_json()
        if self.output_format == "table":
            table_result = CollectedResults(graph_json_results).merge()
            document.add_results(APP_ID, table_result.rows)
        elif self.output_format == "graph":
            document.add_results(APP_ID, graph_json_results)
        return document

    def find_scope(self, list_of_scopes, concept: Concept):
        for scope_idx, scope in list_of_scopes:
            if concept.begin_offset >= scope.begin_offset and concept.end_offset <= scope.end_offset:
                return scope_idx, scope
        return None

    def get_slot(self, link_node):
        if hasattr(link_node, "key") and link_node.key:
            if slot := self.key_2_slots.get(link_node.key, None):
                return slot
        if hasattr(link_node, "content"):
            slot_link = link_node.content
            if slot := self.key_2_slots.get(slot_link.property, None):
                return slot

    def find_node(self, concepts, link_node, scope, _context) -> List[NodeInfo]:

        if isinstance(link_node.content, ContentLiteral):
            return [NodeInfo(-1, {LABEL: link_node.label, NAME: link_node.label}, None)]

        nodes = cast(list[NodeInfo], [])
        if isinstance(link_node, Slot):
            if slot := self.get_slot(link_node):
                if slot.data is None:
                    fstring = slot.content.name
                    try:
                        # logger.debug(f"Slot data not set ! {slot}")
                        if slot.content.name.startswith(f"{VARIABLE_DOCUMENT}.id"):
                            # fstring = fstring.replace(f"{VARIABLE_DOCUMENT}.id", "document")
                            document = _context[VARIABLE_DOCUMENT]  # noqa
                        elif slot.content.name.startswith(VARIABLE_DOCUMENT):
                            document = _context[VARIABLE_DOCUMENT]  # noqa
                        slot.data = resolve_variable(fstring, None, _context)
                    except Exception as ex:
                        logger.debug(f"Slot data not set !  {slot} Exception:{ex} ")

                # TODO check type slot.content.type == ContentType.URI
                if slot.data is not None:
                    if isinstance(slot.data, Concept):
                        label = link_node.label if link_node.label else slot.label
                        node = self.make_node(concept=slot.data, link_node=slot, context=_context, label=label)
                        if node:
                            return [node]
                    else:

                        return [make_str_node_v2(link_node.label, str(slot.data))]
            return nodes

        elif isinstance(link_node.content, ContentURI):
            indexes = find_in_scope(concepts, link_node.content, scope)
            if indexes:

                for idx in indexes:
                    sub_nodes = self.make_nodes(concept=concepts[idx], link_node=link_node, context=_context)
                    for node in sub_nodes:
                        if node.concept:
                            sub_idx = find_index_in_concepts(concepts, node.concept, idx)
                            if sub_idx != -1:
                                nodes.append(NodeInfo(idx=sub_idx, data=node.data, concept=concepts[sub_idx]))
                        else:
                            nodes.append(NodeInfo(idx=idx, data=node.data, concept=concepts[idx]))
                return nodes
            else:
                logger.debug(f"Invalid idx, {link_node}, {scope}")

        return nodes

    def get_canonical(self, concept, context):
        if concept.has_canonical():
            return concept.canonical
        else:
            key = (concept.begin_offset, concept.end_offset)
            if key in context["offset_mappings"]:
                candidates = context["offset_mappings"][key]
                for candidate in candidates:
                    if candidate.has_canonical():
                        return candidate.canonical
        return concept.canonical

    def eval_node_fstring(self, fstring: str, is_concept, concept, context):
        # fvalue = fstring
        value = resolve_variable(fstring, concept, context)
        return value

    def make_node(self, concept=None, link_node=None, slot=None, context=None, label=None) -> NodeInfo | None:
        # prepare a node to create a link
        node = NodeInfo(idx=-1, data={}, concept=None)
        is_concept = isinstance(concept, Concept)
        if is_concept and self.add_offsets:
            node.data["begin_offset"] = concept.begin_offset
            node.data["end_offset"] = concept.end_offset

        if isinstance(link_node, Node):
            node.data[LABEL] = link_node.label

        if is_concept:
            node.concept = concept
            if LABEL not in node.data:
                node.data[LABEL] = concept.uri

        value = self.eval_node_fstring(link_node.content.name, is_concept, concept, context)
        if value:
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            node.data[NAME] = value
        else:
            return None

        properties = None
        if isinstance(link_node, Node):
            if link_node.label:
                node.data[LABEL] = link_node.label
            properties = link_node.properties

        if label:
            node.data[LABEL] = label

        if properties:
            for key, content in properties.items():
                value = self.eval_node_fstring(content, is_concept, concept, context)
                if value:
                    if "attributes" in node.data:
                        node.data["attributes"][key] = value
                    else:
                        node.data["attributes"] = {key: value}
        return node

    def make_nodes(self, concept=None, link_node=None, context=None, label=None):
        # prepare a node to create a link
        nodes = []
        concepts = []
        is_concept = True
        value = None
        link_sub_node = None

        if link_node.content.name == concept.uri:
            # check for special child uri like for subject and object
            for child_uri in get_special_child_uris(concept.uri):
                sub_collection = concept.find(child_uri)
                if sub_collection:
                    value = sub_collection
                    link_sub_node = Node(link_node.label, ContentName(name=child_uri))
                    break

        if value is None:
            value = self.eval_node_fstring(link_node.content.name, is_concept, concept, context)
        if value:
            if isinstance(value, list):
                concepts = value
                if link_sub_node is None:
                    link_sub_node = (
                        Node(link_node.label, ContentName(name=link_node.content.property))
                        if self.is_content_uri(link_node.content.property)
                        else link_node
                    )
                for value in concepts:
                    # sub_link_node =
                    node = None
                    if isinstance(value, Concept):
                        node = self.make_node(concept=value, link_node=link_sub_node, context=context, label=label)
                    elif isinstance(value, str):
                        node = make_str_node_v2(link_node.label, value)
                    if node:
                        nodes.append(node)
            elif isinstance(value, Concept):
                node = self.make_node(concept=value, link_node=link_node, context=context, label=label)
                if node:
                    return [node]
            else:
                node = self.make_node(concept=concept, link_node=link_node, context=context, label=label)
                if node:
                    return [node]

        return nodes


def make_str_node_v2(label, name):
    return NodeInfo(idx=-1, data={LABEL: label, NAME: name})


def make_default_node(link):
    return [NodeInfo(idx=-1, data={LABEL: link.label, NAME: link.value})]


def find_in_scope(concepts, link_node_content, scope):
    uri = link_node_content.uri
    indexes = []
    if scope is None:
        scope = Scope(0, len(concepts))
    if scope:
        cidx = scope.begin
        logger.debug(f"find_in_scope: {concepts}, {uri}, {scope}")
        while cidx < scope.end:
            if concepts[cidx].uri == uri:
                # if link_node_content.property:
                #     end_offset = concepts[cidx].end_offset
                #     cidx += 1
                #     len_concepts = len(concepts)
                #     while cidx < len_concepts and concepts[cidx].end_offset <= end_offset:
                #         if concepts[cidx].uri == link_node_content.property:
                #             indexes.append(cidx)
                #         cidx += 1
                # else:
                indexes.append(cidx)
            cidx += 1
    # else:
    #     for idx, concept in enumerate(concepts):
    #         if concept.uri == uri:
    #             indexes.append(idx)
    return indexes


def key_modifier(phrase):
    """
    Put every first letter of every word into uppercase.
    """
    init_caps = ""
    for char in phrase:
        if char == " " or char == "-":
            init_caps += "_"
        elif char.isalnum():
            init_caps += char.upper()
    return init_caps


def no_modifier(x):
    return x


def to_init_caps(phrase):
    """
    Put every first letter of every word into uppercase.
    """

    initial = True
    init_caps = ""
    for char in phrase:
        if char == " " or char == "-":
            init_caps += char
            initial = True
        # Take away apostrophe, neo4j cannot deal with them
        if char == "'":
            continue
        elif initial:
            init_caps += char.upper()
            initial = None
        else:
            init_caps += char.lower()
    return init_caps


def escape_quotes(phrase):
    """
    escape the single quotes.
    """
    init_caps = ""
    for char in phrase:
        if char == "'":
            init_caps += "\\'"
        else:
            init_caps += char
    return init_caps


def snippet_cleaner(phrase):
    """
    Put every first letter of every word into uppercase.
    """
    init_caps = ""
    for char in phrase:
        if char == "'":
            init_caps += " "
        elif char.isalnum() or char.isspace():
            init_caps += char
    return init_caps
