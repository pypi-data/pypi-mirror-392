from typing import TextIO

from forgeo.core import Interpolator, Model
from forgeo.discretization.validation.interpolator import is_interpolator_valid
from forgeo.discretization.validation.model import is_model_valid


def _not_implemented_validator(
    obj, *, advanced_checks: bool = False, buffer: TextIO | None = None
):
    if buffer is not None:
        msg = f"Skipping validation checks on object '{obj}': not implemented yet\n"
        buffer.write(msg)
    return True


def _get_validator(obj):
    return {
        Model: is_model_valid,
        Interpolator: is_interpolator_valid,
    }.get(type(obj), _not_implemented_validator)


def is_valid(obj, *, advanced_checks: bool = False, buffer: TextIO | None = None):
    _is_valid = _get_validator(obj)
    return _is_valid(obj, advanced_checks=advanced_checks, buffer=buffer)
