from typing import TextIO

from forgeo.core import Model
from forgeo.discretization.validation.interpolator import is_interpolator_valid
from forgeo.discretization.validation.utils import _report_errors


def _diagnose_dataset(dataset):
    # TODO Could be used to valide interpolators too?
    if not dataset:
        return ["Dataset is empty"]
    # TODO Use enum for item.type
    unit = "Unit"
    erosion = "Erosion"
    contacts = ("Conformable", "Top", "Base", "Surface only")
    errors = [
        f"Unknown item type for '{item.name}': '{item.type}'"
        for item in dataset
        if item.type not in (unit, erosion, *contacts)
    ]
    if errors:
        # Skip other tests, as the invalid type will make error messages more confuse
        return errors
    if all(item.type not in ("Erosion", *contacts) for item in dataset):
        return ["Model does not declare any surface"]
    errors = ["Model pile is not valid, found:"]
    for prev, next in zip(dataset, dataset[1:]):
        prev_type = prev.type
        next_type = next.type
        invalid_configuration = (
            (prev_type == erosion and next_type in contacts)
            or (prev_type in contacts and next_type != unit)
            or (prev_type == unit and next_type == unit)
        )
        if invalid_configuration:
            above = f"{next_type.lower()} '{next.name}'"
            below = f"{prev_type.lower()} '{prev.name}'"
            errors.append(f"- {above} above {below}'")
    if len(errors) == 1:
        errors = []  # Only the first message from the list initialization
    return errors


def is_model_valid(
    model: Model, *, advanced_checks: bool = False, buffer: TextIO | None = None
):
    errors = _diagnose_dataset(model.dataset)
    if not model.interpolators:
        errors.extend("Interpolators not defined")
    _report_errors(errors, buffer)
    is_valid = len(errors) == 0
    for interpolator in model.interpolators:
        is_valid &= is_interpolator_valid(
            interpolator, advanced_checks=advanced_checks, buffer=buffer
        )
    return is_valid
