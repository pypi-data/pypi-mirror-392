from pathlib import Path
from wowool.annotation import Concept


available_functions = {
    "upper()": str.upper,
    "lower()": str.lower,
    "title()": str.title,
}

available_document_functions = {
    "name": Path.name,
    "stem": Path.stem,
}

# TODO: remove stem as it is depreciated and use lemma
known_properties = {"canonical", "stem", "literal", "text", "lemma"}


def make_variable_description(variable):
    return variable.split(".")


VARIABLE_DOCUMENT = "document"


def get_canonical(concept, context):
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


def resolve_variable(variable: str, concept: Concept | None, context: dict):
    try:
        variable_description = make_variable_description(variable)
        var = None
        if len(variable_description) >= 2 and variable_description[0] == VARIABLE_DOCUMENT and variable_description[1] == "id":
            if context and VARIABLE_DOCUMENT in context:
                document = context[VARIABLE_DOCUMENT]  # noqa
            else:
                return None
            var = Path(document.id)
            idx = 2
            while idx < len(variable_description) and var:
                if variable_description[idx] in available_document_functions:
                    if isinstance(var, str):
                        var = Path(var)
                    var = getattr(var, variable_description[idx], None)
                elif variable_description[idx] in available_functions:
                    if isinstance(var, Path):
                        var = str(var)
                    var = available_functions[variable_description[idx]](var)
                else:
                    return None
                    # var = getattr(var, variable_description[idx], None)

                idx += 1
            return str(var)

        if concept is None:
            return None

        for var_name in variable_description:
            if var is None:
                if var_name == concept.uri:
                    var = concept
                else:
                    return None
            elif isinstance(var, Concept):
                if var_name == "canonical":
                    var = get_canonical(var, context)
                elif var_name in available_functions:
                    var = available_functions[var_name](var.canonical)
                else:
                    if var_name in var.attributes:
                        var = var.attributes[var_name]
                    elif var_name in known_properties:
                        var = getattr(var, var_name, None)
                        if var == None:
                            return None
                    else:
                        var = var.find(var_name)
                        if var == None:
                            return None
            elif isinstance(var, str):
                if var_name in available_functions:
                    var = available_functions[var_name](var)
            elif isinstance(var, list):
                if var_name in available_functions:
                    for idx in range(var):
                        var[idx] = available_functions[var_name](var[idx])
            else:
                return None
        if isinstance(var, Concept):
            return get_canonical(var, context)
        return var
    except Exception:
        return None
