from wowool.entity_graph.entity_graph import CollectedResults
from io import StringIO
from wowool.annotation import Concept


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
            next
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
    if isinstance(phrase, Concept):
        phrase = phrase.canonical
    init_caps = ""
    for char in phrase:
        if char == "'":
            init_caps += "\\'"
        else:
            init_caps += char
    return init_caps


def key_normalizer(key):
    """
    Put every first letter of every word into uppercase.
    """
    init_caps = ""
    for char in key:
        if char == " " or char == "-":
            init_caps += "_"
        elif char.isalnum():
            init_caps += char.upper()
    return init_caps


def get_properties(row: dict):
    if "attributes" in row:
        return row["attributes"]


class CypherStream:
    def __init__(self, namespace: str | None = None, collection_name=None, modifier=None, counters: list[str] = [], **kwargs):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.value_modifier = no_modifier
        self.key_modifier = no_modifier
        self.namespace = ""
        self.counters = set(counters)
        self.namespace = namespace if namespace else ""
        self.collection_name = collection_name if collection_name else ""
        if self.namespace:
            self.namespace = ":" + self.namespace
            if collection_name:
                self.namespace = self.namespace + ":" + str(collection_name)

    def __call__(self, result: CollectedResults):
        dff = result.df_from
        dfr = result.df_relation
        dft = result.df_to
        result_set = []
        for idx in range(len(dff)):
            # print(f"{idx}: {dff.loc[idx].to_json()} -> {dfr.loc[idx].to_json()} ->  {dft.loc[idx].to_json()}" )
            result_set.append(self.create_node(dff[idx]))
            result_set.append(self.create_node(dft[idx]))
            result_set.append(self.create_relation(dff[idx], dfr[idx], dft[idx]))
        return result_set

    def make_label(self, row, key_props=None):

        label = row["label"]
        strm = StringIO()
        strm.write("MERGE ")
        strm.write("(")
        strm.write(" o")
        strm.write(self.namespace + ":" + label)
        # strm.write(f":{label}")
        strm.write(" { name : '")
        strm.write(escape_quotes(row["name"]))
        strm.write("' ")
        strm.write("}")
        strm.write(") ")

        if self._requires_counter_default(label, "node"):
            strm.write(" ON CREATE SET o.cnt = 1 ON MATCH SET o.cnt = o.cnt + 1 ")

        properties = get_properties(row)
        if properties:
            for uri, value in properties.items():
                strm.write("")
                strm.write("SET o.")
                strm.write(uri)
                strm.write("=")
                if isinstance(value, str):
                    strm.write("'")
                    strm.write(escape_quotes(value))
                    strm.write("'")
                elif isinstance(value, list):
                    strm.write("'")
                    value.sort()
                    strm.write(escape_quotes(",".join(value)))
                    strm.write("'")
                else:
                    strm.write(escape_quotes(str(value)))
                strm.write(" ")

        strm.write("RETURN o.name")
        strm.seek(0)
        return strm.read()

    def create_node(self, row):
        return self.make_label(row)

    def _requires_counter(self, relation_label):
        return relation_label in self.counters

    def _requires_counter_default(self, relation_label, default_section):
        return self._requires_counter(relation_label) or self._requires_counter(default_section)

    def create_relation(self, from_key, relation, to_key, **kwargs):
        strm = StringIO()
        if "name" in relation:
            relation_label = key_modifier(relation["name"])
        else:
            relation_label = key_modifier(relation["label"])
        strm.write("MATCH (from")
        # strm.write(self.namespace + ":" + from_key["label"])
        strm.write(":" + from_key["label"])
        strm.write("{name:'")
        strm.write(escape_quotes(from_key["name"]))
        strm.write("'}),")
        strm.write("(to")
        # strm.write(self.namespace + ":" + to_key["label"])
        strm.write(":" + to_key["label"])
        strm.write(" {name:'")
        strm.write(escape_quotes(to_key["name"]))
        strm.write("'})")
        strm.write(" MERGE (from)-[r:")
        strm.write(relation_label)
        strm.write("]-")
        strm.write(">")
        strm.write("(to)")

        if self._requires_counter_default(relation_label, "relations"):
            strm.write(" ON CREATE SET r.cnt = 1 ON MATCH SET r.cnt = r.cnt + 1 ")

        if "inverse_label" in relation:
            strm.write(" MERGE (from)<-[:")
            strm.write(key_modifier(relation["inverse_label"]))
            strm.write("]-(to)")
        strm.seek(0)
        return strm.read()
