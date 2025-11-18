from dataclasses import dataclass, field
from enum import Enum


class ContentType(Enum):
    URI = 0
    FORMAT = 1
    STRING = 2


def split_name(name: str):
    parts = name.split(".")
    uri = parts[0]
    if len(parts) == 1:
        return uri, str()
    rest = ".".join(parts[1:])
    return uri, rest


@dataclass
class ContentName:
    name: str
    uri: str | None = None
    property: str | None = None

    def __post_init__(self):
        if self.uri is None:
            self.uri, self.property = split_name(self.name)


@dataclass
class ContentURI:
    name: str
    uri: str | None = None
    property: str | None = None

    def __post_init__(self):
        if self.uri is None:
            self.uri, self.property = split_name(self.name)


@dataclass
class ContentSlot(ContentURI): ...


@dataclass
class ContentLiteral:
    value: str


@dataclass
class StaticNode:
    label: str
    value: str


@dataclass
class Node:
    label: str
    content: ContentName | ContentSlot | ContentURI | ContentLiteral | None = None
    properties: dict[str, ContentName] = field(default_factory=dict)
    optional: None | StaticNode = None


class StoreType(Enum):
    SENTENCE = 0
    FIRST_SEEN = 1
    LAST_SEEN = 2


@dataclass
class Slot:
    store_type: StoreType
    key: str
    content: ContentName
    data = None
    label: str | None = None
    properties: dict[str, ContentName] = field(default_factory=dict)
    optional: None | StaticNode = None


@dataclass
class NodeCandidate:
    element: Node
    link_id: int | None = None
    candidate_type: str | None = None


@dataclass
class Link:
    from_: Node
    to_: Node
    relation_: Node
    scope: str | None = None
    action: str | None = None
    swap_from_to: bool = False


@dataclass
class LinkCandidate:
    link: Link
    link_id: int | None = None
    candidate_type: str | None = None


@dataclass
class DataNode:
    label: str
    count: int = 5
    key: str | None = None
    slot: Slot | None = None
