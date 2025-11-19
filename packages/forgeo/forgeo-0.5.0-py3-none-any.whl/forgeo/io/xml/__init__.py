import sys
import xml.etree.ElementTree as et
from functools import cmp_to_key
from importlib.metadata import entry_points
from pathlib import Path

from forgeo.io.xml import builtins, custom
from forgeo.io.xml.base import Serializer, WrongSerializationTarget

# If you want to add custom serializer from package foo to the list of forgeo serializers
# use the entrypoint "forgeo.io.xml.serializer"
# Just add the following line to foo's pyproject.toml where custom quand be any meaningful name
# [project.entry-points."forgeo.io.xml.serializer"]
# customm_serializer = "foo.subpackage:CustomSerializer"
# another_serializer = "foo.subpackage:AnotherSerializer"


def _collect_serializers():
    # shipped serializers
    serializers = [serializer for serializer in builtins.serializers] + [
        serializer for serializer in custom.serializers
    ]
    assert sys.version_info >= (3, 9)
    if sys.version_info >= (3, 10):
        group = entry_points(group="forgeo.io.xml.serializer")
    else:
        group = entry_points()["forgeo.io.xml.serializer"]
    serializers.extend(eps.load() for eps in group)

    # sort serializers according to their target
    # we want to consider derived class first
    def cmp(s1, s2):
        t1 = s1.target
        t2 = s2.target
        if issubclass(t1, t2):
            if t1 == t2:
                return 0
            return -1
        return 1

    serializers.sort(key=cmp_to_key(cmp))
    return serializers


# serializers are collected upon import
_serializers_collection = None


def check_serializers():
    global _serializers_collection
    if _serializers_collection is None:
        _serializers_collection = _collect_serializers()
    return _serializers_collection


def dump(x, path=None, **kwargs):
    check_serializers()
    node = None
    for serializer in _serializers_collection:
        try:
            node = serializer.dump(x, **kwargs)
            break
        except WrongSerializationTarget:
            pass
    else:
        raise RuntimeError(f"No serializer found to dump: {type(x)}")
    if path is not None:
        et.ElementTree(node).write(Path(path).as_posix())
    return node


def load(e):
    check_serializers()
    if isinstance(e, Path):
        e = et.parse(e.as_posix()).getroot()
    elif isinstance(e, (bytes, str)):
        e = et.fromstring(e)
    for serializer in _serializers_collection:
        try:
            return serializer.load(e)
        except WrongSerializationTarget:
            pass
    else:
        raise RuntimeError(f"No serializer found to load: {e.tag}")


def deep_copy(element):
    from forgeo.core import Interpolator

    cls = type(element)
    for serializer in check_serializers():
        if serializer.target == cls:
            copy = serializer.load(serializer.dump(element))
            if cls == Interpolator:
                copy.dataset = [
                    get_complete_item(element, item) for item in copy.dataset
                ]
            return copy
    raise TypeError(f"Unknown serializer for class {cls}")


def get_complete_item(interp, incomplete_item):
    # Inspired from pile.Model serializer, as InterpolatorSerializer only
    # saves a couple (item_name, item_type) instead of a whole item
    for item in interp.dataset:
        if item.name == incomplete_item.name:
            new_item = deep_copy(item)
            new_item.type = incomplete_item.type
            return new_item
    raise ValueError(f"Unknown item name: {incomplete_item.name}")
