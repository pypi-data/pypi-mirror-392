from typing import TextIO

from forgeo.core import InterpolationMethod, Interpolator
from forgeo.discretization.validation.utils import _report_errors


def is_interpolator_valid(
    interpolator: Interpolator,
    *,
    advanced_checks: bool = False,
    buffer: TextIO | None = None
):
    """Checks whether the parametrization of an interpolator is valid.
    If `strict` and the interpolator is not valid, raises an Exception.
    """
    if interpolator.method == InterpolationMethod.POTENTIAL:
        errors = _diagnose_gmlib_interpolator(interpolator, advanced_checks)
    elif interpolator.method == InterpolationMethod.ELEVATION_KRIGING:
        errors = _diagnose_functolite_interpolator(interpolator, advanced_checks)
    elif not InterpolationMethod.is_available(interpolator.method):
        errors = [f"Unknown interpolation method: {interpolator.method}"]
    else:
        errors = []  # Call external validator instead...
    _report_errors(errors, buffer)
    return len(errors) == 0


def _diagnose_gmlib_interpolator(interpolator, advanced_checks=False):
    errors = []
    # Check interpolation data:
    # Each surface must have observation data and the interpolator an orientation data
    has_orientation_data = False
    for item in interpolator.dataset:
        item_data = item.item_data
        if item.is_surface:
            if item_data is None or not item_data.has_observation_data():
                errors.append(f"Missing observation data in {item.name}")
        if item_data is not None and item_data.has_orientation_data():
            has_orientation_data = True
    if not has_orientation_data:
        errors.append("Missing orientation data")
    # Check variogram parameters
    varios = interpolator.variograms
    if varios is None or len(varios) == 0:
        errors.append("Variogram is not defined")
    elif (range_ := varios[0].range) is None or range_ <= 0:
        errors.append(f"Invalid range: {range_ = }")
    if advanced_checks:
        pass  # TODO Implement advanced check (try to interpolate)
    return errors


def _diagnose_functolite_interpolator(interpolator, advanced_checks=False):
    errors = []
    # Check interpolation data:
    # Only 1 surface, with at least 1 observation point
    nb_surfaces = 0
    for item in interpolator.dataset:
        if item.is_surface:
            nb_surfaces += 1
            if item.item_data is None or not item.item_data.has_observation_data():
                errors.append(f"Missing observation data in {item.name}")
    if nb_surfaces > 1:
        errors.append(
            f"Too many surfaces to interpolate with this method: {interpolator.method}"
        )
    # Check variogram parameters:
    varios = interpolator.variograms
    if varios is None or len(varios) == 0:
        errors.append("Variogram is not defined")
    else:
        if (range_ := varios[0].range) is None or range_ < 0:
            errors.append(f"Invalid range: {range_ = }")
        if (sill := varios[0].sill) is None or sill < 0:
            errors.append(f"Invalid sill: {sill = }")
    # Check neighborhood parameters:
    neigh = interpolator.neighborhood
    if neigh is None:
        errors.append("Neighborhood not defined")
    else:
        errors.extend(neigh.is_valid(with_details=True))  # Empty list if valid
    if advanced_checks:
        pass  # TODO Implement advanced check (try to interpolate)
    return errors
