import logging
from pathlib import Path

from yaml import safe_dump, safe_load

logger = logging.getLogger(__name__)


def load(path: Path):
    logger.debug("Reading from %s", path)
    with path.open() as fp:
        return safe_load(fp)


def write(path: Path, data):
    logger.debug("Writing to %s", path)
    with path.open(mode="w") as fp:
        return safe_dump(data, fp)


def get(data, lookup, *, delimiter=":"):
    # If we have more tokens to look at
    if delimiter in lookup:
        key, rest = lookup.split(delimiter, 1)
        # If our key is in the data, keep looking with the rest
        if key in data:
            return get(data=data[key], lookup=rest, delimiter=delimiter)
        # otherwise return
        return None
    if lookup in data:
        return data[lookup]


def set(data, lookup, value, *, delimiter=":"):
    # If we still have a delimiter, then we have a nested structure
    # we need to work through
    if delimiter in lookup:
        key, rest = lookup.split(delimiter, 1)
        if key not in data:
            data[key] = {}

        return set(data=data[key], lookup=rest, value=value, delimiter=delimiter)
    if lookup in data:
        old = data[lookup]
        data[lookup] = value
        return old, value

    data[lookup] = value
    return None, value
