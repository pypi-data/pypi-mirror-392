#!/usr/bin/env python3
"""
ddresolve - Distributed Directory name resolver
Copyright 2025 Kevin Steen
"""
from pathlib import Path
from logging import getLogger

log = getLogger(__name__)

MAX_NAMEPARTS = 15
_db_path: Path = Path("~/.local/share/petnames/").expanduser()
METADATA_FIELDS = [
    "suggested_name",
    "lifetime",
]


def _get_fields(text_record, prop, meta=True):
    """Return selected field from text_record

    prop: Specifies which property to return or 'all'
    meta: if True (default) metadata fields are included in the result
    """
    prop = prop.strip().lower()
    result = {"properties": []}
    log.debug("Looking for property: %s", prop)
    for line in text_record.splitlines():
        log.debug("line:%s", line)
        field, value = line.split('=')
        field = field.strip()
        if meta:
            if field in METADATA_FIELDS:
                log.debug("Found meta property: %s, %s", field, value.strip())
                result[field] = value.strip()
            elif prop == 'all' or field == prop:
                log.debug("Found property: %s, %s", field, value.strip())
                result["properties"].append((field, value.strip()))
        else:  # No meta
            if field in METADATA_FIELDS:
                pass
            elif field == prop:
                log.debug("Returning property value: %s", value.strip())
                return value.strip()
            elif prop == 'all':
                log.debug("Found property: %s, %s", field, value.strip())
                result["properties"].append((field, value.strip()))
    return result


def resolve(name, prop="desthash", meta=False):
    """Resolve name and return properties stored under that name

    property:
        Specifies which target type to return or 'all'. Default: 'desthash'
    meta:
        if True, metadata fields are included in the result. See METADATA_FIELDS
        Default: False
    """
    if not name:
        raise ValueError("Name cannot be empty")
    prop = prop.strip().lower()
    namespath = _db_path / "local"
    for count, namepart in enumerate(_parse_name(name)):
        if count >= MAX_NAMEPARTS:
            raise ValueError("Too many name components")

        log.debug("Local search for %s", namepart)
        target = list(namespath.glob(namepart + ".txt", case_sensitive=False))
        log.debug("Checking: %s", namespath / (namepart + ".txt"))
        if target:
            target = target[0]
            log.debug("Found target: %s", target)
            return _get_fields(target.read_text(), prop, meta)
        log.debug("Not found: %s", namespath / (namepart + ".txt"))

        target = list(namespath.glob(namepart, case_sensitive=False))
        log.debug("Checking: %s", namespath / namepart)
        if target:  # Collection. Go around again
            log.debug("Found collection: %s", target[0])
            namespath = target[0]
            continue
        log.debug("Not found: %s", namespath / namepart)
    return None


def get_dbpath() -> Path:
    return _db_path

def set_dbpath(newpath):
    global _db_path
    _db_path = Path(newpath)

def _parse_name(name):
    for char in ":/\r\n":
        if char in name:
            raise ValueError('Names may not contain "{char}"')
    for n in name.split('.'):
        if n: yield n


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    import sys

    if len(sys.argv) > 1:
        print(resolve(*sys.argv[1:]))
