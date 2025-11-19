from dataclasses import dataclass
from typing import Any

import numpy as np
from functolite.functors import UniversalKrigingFunctor
from galopy.model import add_nugget, create_geostatistical_model
from galopy.neighborhood import create_geostatistical_neighborhood
from gmlib import pypotential2D, pypotential3D
from gmlib.common import CovarianceData

from forgeo.core import InterpolationMethod, Neighborhood


@dataclass
class DiscInfo:
    # k = fault surface id (and index) in BSPTreeBuilder
    # v = fault surface drift function index in self.drifts
    along: dict  # dict[int: int]
    drifts: list  # list[pypot.Drift]


# Over-encapsulation, but best clean/quick compromise to integrate boundaries
# into the overall code logic
@dataclass
class BoundaryWrapper:
    method: InterpolationMethod
    field: pypotential3D.Ellipsoid | Any  # TODO to investigate for functolite...

    @property
    def value(self):
        return None


@dataclass
class FaultWrapper:
    method: InterpolationMethod
    field: pypotential3D.Fault | Any  # TODO to investigate for functolite...
    boundary: BoundaryWrapper

    @property
    def value(self):
        return None

    @staticmethod
    def boundary_name(fault_name):
        return fault_name + "-boundary"

    @classmethod
    def wrap(cls, method, fault, boundary):
        if boundary is not None:
            boundary = BoundaryWrapper(method, boundary)
        return cls(method, fault, boundary)


@dataclass
class InterfaceWrapper:
    method: InterpolationMethod
    field: Any  # type(pypot.potential_field) | type(functolite.ImplicitFunctor)
    value: float
    discontinuities: Any  # DiscInfo


def _get_item_dim(item):
    if item.item_data is None:
        return None
    return item.item_data.ambient_space_dimension


def _make_potential_field(interpolator, discontinuous_drifts=None):
    """
    interpolator: pile.Interpolator
    discontinuous_drifts: optionnel, dict[int: pypotential3D.potential_field]
    """
    assert interpolator.method == InterpolationMethod.POTENTIAL
    range_ = interpolator.variograms[0].range
    nugget_ = interpolator.variograms[0].nugget or 0.0
    drift_order = interpolator.drift_order
    items = interpolator.dataset
    dim = {dim for item in items if (dim := _get_item_dim(item)) is not None}
    assert len(dim) == 1
    dim = dim.pop()
    pypot = {2: pypotential2D, 3: pypotential3D}
    assert dim in pypot
    pypot = pypot[dim]
    # Collect all orientations (locations and unit normals)
    orientations = []
    for item in items:
        if (data := item.item_data) is not None:
            if (ori := data.orientations) is not None:
                orientations.append(ori)
            if (ori_only := data.orientations_only) is not None:
                orientations.append(ori_only)
    assert (
        orientations
    ), "At least one of the interpolator's items must have orientation data "

    def stack_array_list(arrays):
        assert isinstance(arrays, list)
        assert all(isinstance(a, np.ndarray) for a in arrays)
        if len(arrays) > 1:
            arrays = np.vstack(arrays)
        elif len(arrays) == 1:
            arrays = arrays[0]
        else:
            arrays = None
        return arrays

    def concatenate_orientations(orientations):
        locs = [
            values
            for data in orientations
            if (values := data.locations.values) is not None
        ]
        vecs = [
            values
            for data in orientations
            if (values := data.normals.values) is not None
        ]
        return stack_array_list(locs), stack_array_list(vecs)

    locs, vecs = concatenate_orientations(orientations)
    gradients = pypot.gradient_data(locs, vecs)
    # collect interfaces
    interfaces = []
    for item in items:
        if item.is_surface:
            # for each item stack observations and orientations location
            item_data = item.item_data
            # FIXME Do we need to systematically check whether item_data.observations
            # and/or item_data.orientations is None (as in concatenate_orientations?)
            if item_data.observations:
                if item_data.orientations:
                    interfaces.append(
                        np.vstack(
                            [
                                item_data.observations.values,
                                item_data.orientations.locations.values,
                            ]
                        )
                    )
                else:
                    interfaces.append(item_data.observations.values)
            else:
                interfaces.append(item_data.orientations.locations.values)
    assert len(interfaces) >= 1
    # Parameters to be stored in interpolator
    covdata = CovarianceData(1.0, range_, gradient_nugget=0.0, potential_nugget=nugget_)
    drifts = pypot.drift_basis(drift_order)
    discontinuities = None  # Used later in the gmlib_extension factory
    if discontinuous_drifts is not None:
        along = {}
        for idx, drift in discontinuous_drifts.items():
            drifts.append(drift)
            along[idx] = len(drifts) - 1
        discontinuities = DiscInfo(along, drifts)

    field = pypot.potential_field(
        covdata, gradients, pypot.interface_data(interfaces), drifts
    )
    isovalues = [np.mean(field(s)) for s in interfaces]
    return field, isovalues, discontinuities


def make_gmlib_fault(interpolator):
    assert len(interpolator.dataset) == 1
    fault_item = interpolator.dataset[0]
    fault, *_ = _make_potential_field(interpolator)
    fault = pypotential3D.Fault(fault)
    if (ellipsoid := fault_item.extension) is not None:
        axes = fault_item.get_principal_axes()
        assert axes is not None
        radii = ellipsoid.radius
        ellipsoid = pypotential3D.Ellipsoid(
            pypotential3D.Point(ellipsoid.center),
            (
                pypotential3D.Vector(radii[0] * axes[0]),  # Along strike
                pypotential3D.Vector(radii[1] * axes[1]),  # Along dip
                pypotential3D.Vector(radii[2] * axes[2]),  # Vertical
            ),
        )
        fault.stops_on(ellipsoid)
    return fault_item.name, FaultWrapper.wrap(
        interpolator.method, fault, boundary=ellipsoid
    )


def set_gmlib_fault_boundaries(node, limits):
    assert len(limits) > 0
    fault = node.functor.field
    assert isinstance(fault, pypotential3D.Fault)
    limits = [s.functor.field for s in limits]
    for field in limits:
        assert isinstance(field, pypotential3D.Fault)
        fault.stops_on(field)
    # We may have an ellipsoid as boundary
    assert len(limits) <= fault.number_of_boundaries()


def make_functolite_fault(*args, **kwargs):
    # TODO To implement
    def _make_ellipsoid(ellipsoid):
        pass

    return 2 * (None,)


def make_fault(interpolator):
    method = interpolator.method
    assert InterpolationMethod.is_available(method)
    if method == InterpolationMethod.POTENTIAL:
        return make_gmlib_fault(interpolator)
    elif method == InterpolationMethod.ELEVATION_KRIGING:
        return make_functolite_fault(interpolator)
    else:
        raise NotImplementedError("TODO: Authorize custom interpolation methods")


def add_stops_on_relations(node, limits):
    method = node.functor.method
    assert InterpolationMethod.is_available(method)
    if method == InterpolationMethod.POTENTIAL:
        return set_gmlib_fault_boundaries(node, limits)


def make_gmlib_series(interpolator, nodes=None):
    # interpolator: forgeo.core.Interpolator
    # nodes: Iterable[forgeo.discretization.bsptree_builder.Node]
    def make_drift(fault):
        assert isinstance(fault, FaultWrapper)
        field = fault.field
        boundary = fault.boundary
        if boundary is None:
            return pypotential3D.make_drift(field)
        return pypotential3D.make_finite_drift(field, boundary.field)

    method = interpolator.method
    names = [item.name for item in interpolator.dataset if item.is_surface]
    if nodes and interpolator.discontinuities:
        drifts = {
            s.id: make_drift(s.functor)
            for s in nodes
            if (s.is_fault() and s.name in interpolator.discontinuities)
        }
    else:
        drifts = None
    field, isovalues, discontinuities = _make_potential_field(interpolator, drifts)
    assert len(names) == len(isovalues)
    return {
        name: InterfaceWrapper(method, field, value, discontinuities)
        for name, value in zip(names, isovalues)
    }


def make_functolite_interface(interpolator, nodes=None):
    method = interpolator.method
    assert method == InterpolationMethod.ELEVATION_KRIGING
    assert len(interpolator.dataset) == 1
    item = interpolator.dataset[0]
    assert item.is_surface
    vario = interpolator.variograms[0]
    model = create_geostatistical_model(
        ndim=2,
        type=vario.model,
        range=vario.range,
        sill=vario.sill,
        max_drift_degree=interpolator.drift_order,
    )
    nugget = vario.nugget
    if nugget is not None and nugget > 0:
        model = add_nugget(model, nugget)
    neigh = interpolator.neighborhood
    # FIXME Unsure we should authorize neigh to be None (for reproducibility)
    if neigh is None:
        neigh = Neighborhood.create_moving()
    neigh = create_geostatistical_neighborhood(
        ndim=2,
        unique_neighborhood=False,
        max_search_distance=neigh.max_search_distance,
        nb_max_samples=neigh.nb_max_neighbors,
        nb_min_samples=neigh.nb_min_neighbors,
        nb_angular_sectors=neigh.nb_angular_sectors,
        nb_max_samples_per_sector=neigh.nb_max_neighbors_per_sector,
    )
    data = item.item_data
    if not data.orientations:
        assert data.observations
        data = data.observations.values
    elif not data.observations:
        assert data.orientations
        data = data.orientations.locations.values
    else:
        data = np.vstack(
            [
                data.observations.values,
                data.orientations.locations.values,
            ]
        )
    functor = UniversalKrigingFunctor(data, model, neigh).as_implicit_functor()
    discontinuities = None  # TODO Implement DiscInfo
    return {item.name: InterfaceWrapper(method, functor, None, discontinuities)}


def make_interfaces(interpolator, nodes=None):
    """Returns a map `{interface_name: InterfaceWrapper}` for each item in the
    input interpolator dataset
    """
    method = interpolator.method
    assert InterpolationMethod.is_available(method)
    if method == InterpolationMethod.POTENTIAL:
        return make_gmlib_series(interpolator, nodes)
    elif method == InterpolationMethod.ELEVATION_KRIGING:
        return make_functolite_interface(interpolator, nodes)
    else:
        raise NotImplementedError("TODO: Authorize custom interpolation methods")


def wrap_raster(raster):
    field = pypotential3D.ImplicitTopography(
        pypotential3D.ElevationRaster(
            raster.origin, raster.steps, raster.shape, raster.values
        )
    )
    return raster.name, InterfaceWrapper(InterpolationMethod.RASTER, field, None, None)
