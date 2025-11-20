from pprint import pformat

from yaml import safe_dump


def format_yaml(obj):
    return safe_dump(obj, indent=2)


def format_expand(obj):
    def __format(section):
        for key in section:
            if isinstance(section[key], dict):
                for row in __format(section[key]):
                    yield f"{key}:{row}"
            else:
                yield f"{key}\t{section[key]}"

    return "\n".join(__format(obj))


def format_pprint(obj):
    return pformat(obj)


formatters = {
    "yaml": format_yaml,
    "expand": format_expand,
    "pprint": format_pprint,
}
