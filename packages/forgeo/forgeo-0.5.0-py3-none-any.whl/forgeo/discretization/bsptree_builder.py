from copy import copy
from dataclasses import dataclass

import numpy as np
from gmlib import pypotential3D
from gmlib.common import OrientedEvaluation
from rigs import BSPTree, Discontinuities, Side

from forgeo.core import InterpolationMethod, Item
from forgeo.discretization.make_functors import (
    BoundaryWrapper,
    FaultWrapper,
    InterfaceWrapper,
    add_stops_on_relations,
    make_fault,
    make_interfaces,
    wrap_raster,
)
from forgeo.discretization.validation import is_valid

# FIXME Use rigs.utils.as_functor again when the "array copy" is no more needed
# from rigs.utils import as_functor


def as_functor(f, value=None):
    # FIXME Copied from rigs.utils: hack to ensure array evaluation works systematically
    if value is None:

        def _f(pts, res):

            try:
                res[:] = f(pts)
            except:
                # In some corner-cases of gmlib.ImplicitTopography, copying array
                # is required to avoid a RuntimeError("bad cast"). Fix incoming
                res[:] = f(pts.copy())

        return _f
    else:

        def _f(pts, res):
            res[:] = f(pts)
            res -= value

        return _f


@dataclass
class Node:
    id: int
    name: str
    functor: FaultWrapper | BoundaryWrapper | InterfaceWrapper | None
    color: str = None

    def is_fault(self):
        return isinstance(self.functor, FaultWrapper)


# FIXME Use rigs.gmconverter.topological instead to limit reimplementations?
def _sort_faults(relations):
    """According to the input "stops_on" relation table, computes the "rank" of each
    fault in the tree (the lower the rank, the closer the fault is from the tree root)

    The returned array contains the indices of the faults ordered by increasing ranking
    """
    # Find number of faults which stops on each one ( = sums of the relations matrix columns)
    # Note: relations[i, j] != 0 == fault_i stops on fault_j
    nb_faults = len(relations)
    # TODO Implement sum_col using a np.ndarray...
    sum_col = [0] * nb_faults  # Number of faults stoping on each fault
    for f1_idx in range(nb_faults):
        for f2_idx in range(nb_faults):
            if relations[f2_idx][f1_idx]:  # if f2 stops on f1
                sum_col[f1_idx] += 1
    # Find faults on which no other one stops on it
    faults = [i for i in range(nb_faults) if sum_col[i] == 0]
    # Sorting
    topo_sort = []
    # Process faults, starting from the most "minor" ones
    while faults:
        fault_idx = faults.pop(0)
        topo_sort.append(fault_idx)
        for idx in range(nb_faults):
            if relations[fault_idx][idx]:
                sum_col[idx] -= 1
                if sum_col[idx] == 0:
                    faults.append(idx)
    topo_sort.reverse()
    return topo_sort  # Fault indices ranked from "most important" too "least important"


def _other_side(s):
    if s == Side.first:
        return Side.second
    assert s == Side.second
    return Side.first


def _gmlib_scheme_enum(s):
    return {
        Side.first: OrientedEvaluation.always_negative,
        Side.second: OrientedEvaluation.always_positive,
    }[s]


class BSPTreeBuilder:
    def __init__(self):
        # The rigs.BSPTree that stores the relations between all surfaces
        self.tree = BSPTree()
        # Internal use: keeps track of all elements already added to the tree
        self._nodes = []  # list[Node]
        # Id of the node representing the topography in the tree, if present
        self.topography = None
        # Id of the node representing the first stratigraphic element in the
        # tree (i.e., the first functor to evaluate). Typically: the youngest
        # erosion if any, otherwise the oldest stratigraphic interface.
        self.domains_root = None
        # Maps a (sub)domain id to another domain id (some domains can be
        # artificially divided into subdomains when building the tree, notably
        # to account for several successive interfaces in the model)
        self.domains_map = {}
        # The rigs.Discontinuities that maps each stratigraphic interface to
        # the fautls that affect it
        self.discontinuities = None
        # Internal use: maps (finite) fault nodes to the nodes representing
        # their boundaries (used by the extension factory)
        self._boundaries = {}
        # Internal use: keeps track of all generated functor extensions, to
        # prevent garbage collection
        self._extensions = []
        # Callable that tells whether a tree node has an associated functor
        # (it represents a surface) or not (it represents a domain)
        self.is_functor = lambda _: True
        # Callable that tells whether a tree node  represents a fault or not
        # (it is either a stratigraphic contact or a domain)
        self.is_fault = lambda _: False

    @property
    def nb_nodes(self) -> int:
        return len(self._nodes)

    def exists(self, node) -> bool:
        if isinstance(node, Node):
            return self.exists(node.id)
        elif isinstance(node, (int, np.integer)):
            return any(s.id == node for s in self._nodes)
        elif isinstance(node, str):
            return any(s.name == node for s in self._nodes)
        raise TypeError(f"Invalid key: '{type(node) = }', should be 'int' or 'str'")

    def register_surface(self, name, wrapper, color=None) -> int:
        """Registration is used to prevent unwanted garbage collection.

        By default, registration supposes that the input surface (wrapper) has unique
        name and id. "Phantom" surfaces can also be registered by setting both their
        name and id to `None`. This will prevent them from being collected by GC, but
        it will not be possible to retrieve them afterward. Phantom surfaces are
        typically used to create on-demand functor extensions to evaluate on
        discontinuities.
        """
        sid = self.nb_nodes
        node = Node(sid, name, wrapper, color)
        assert not self.exists(node)
        self._nodes.append(node)
        return sid

    def register_unit(self, name, color=None) -> int:
        """Registration is used to prevent unwanted garbage collection."""
        sid = self.nb_nodes
        node = Node(sid, name, None, color)
        assert not self.exists(node)
        self._nodes.append(node)
        return sid

    def get(self, node: int | str) -> Node:
        """Returns the `Node` object whose name or id matches `node`"""
        assert self.exists(node)
        if isinstance(node, (int, np.integer)):
            return next((n for n in self._nodes if n.id == node), None)
        elif isinstance(node, str):
            return next((n for n in self._nodes if n.name == node), None)
        else:
            raise TypeError(f"Invalid key: '{type(node) = }', should be 'int' or 'str'")

    def to_dict(self) -> dict:
        """Returns all the parameters as a dictionary that matches `rigs` signature"""
        fields = [
            (f.field, f.value) if (f := n.functor) is not None else 2 * (None,)
            for n in self._nodes
        ]
        functors = [as_functor(f, v) if f is not None else None for f, v in fields]
        return dict(
            tree=self.tree,
            ids={n.name: n.id for n in self._nodes},
            names=[n.name for n in self._nodes],
            topography=self.topography,
            domains_root=self.domains_root,
            domains_map=self.domains_map,
            discontinuities=self.discontinuities,
            fields=fields,
            functors=functors,
            is_functor=self.is_functor,
            is_fault=self.is_fault,
            extension_factory=self.initialize_extension_factory(),
            colors=[s.color for s in self._nodes],
        )

    def _add_fault_network(self, fault_network):
        # Select the active faults
        active_faults = np.array(fault_network.active_faults)
        nb_faults = np.sum(active_faults)
        interpolators = np.array(fault_network.interpolators)[active_faults]
        dataset = np.array(fault_network.dataset)[active_faults]
        relations = fault_network.relations[active_faults, :][:, active_faults]
        nb_boundaries = sum(1 for item in dataset if item.extension is not None)
        # Computes faults rank (from "most important" too "least important")
        processing_order = _sort_faults(relations)

        def get_parent_idx(i):
            """Returns the "parent" of this fault, if any

            The parent is the fault satisfies 2 conditions:
            (1) this fault stops on it (equiv., the parent fault index in
            `processing_order` is lower than this fault index),
            (2) among all the faults that satisfies (1), the parent is the one with the
            highest rank (equiv., the fault with the highest index in
            `processing_order`)
            """
            rank_i = processing_order.index(i)
            for idx in reversed(processing_order[:rank_i]):
                if relations[i, idx]:  # if fault_i stops on fault_idx
                    return idx
            return None  # This fault does not stops on any other one

        tree = self.tree
        nb_nodes = nb_faults + nb_boundaries
        tree.minimum_number_of_nodes(nb_nodes)
        fault_barycenters = [
            np.mean(item.item_data.all_observations.values, axis=0) for item in dataset
        ]
        # Register all surfaces
        boundaries = {}  # {fault_id: boundary_id}
        # Warning: mandatory to register faults in the same order as in input network
        # Otherwise: "self.get(parent_idx)" returns an wrong parent as parent_uid
        # would be different from parent_idx
        for fault_idx in range(nb_faults):
            interpolator = interpolators[fault_idx]
            name, wrapper = make_fault(interpolator)
            color = interpolator.dataset[0].get_color()
            sid = self.register_surface(name, wrapper, color=color)
        # FIXME Patch to add gmlib boundaries once all pypot.Fault exist.
        # Clearly, we can do better, but it will work for now...
        for fault_idx in range(nb_faults):
            node = self.get(fault_idx)
            limits = np.arange(nb_faults)[relations[fault_idx]]
            if len(limits) > 0:
                limits = [self.get(l) for l in limits]
                assert limits
                add_stops_on_relations(node, limits)
        # Work on a copy as we will modify it while iterating
        for node in self._nodes.copy():
            if (boundary := node.functor.boundary) is not None:
                name = FaultWrapper.boundary_name(node.name)
                boundaries[node.id] = self.register_surface(name, boundary)
        # Add boundaries after faults, as faults indices (ranks) that we use later
        # to `tree.add_child(parent_idx, side, fault_idx)` are in [0, nb_faults[.
        # Inserting boundary i at the same time as fault i would mess up everything
        for sid, bid in boundaries.items():
            tree.set_boundary(sid, bid)
        self._boundaries = boundaries

        # For each fault stoping on at least one other fault, add a relation in the tree
        for fault_idx in processing_order:
            parent_idx = get_parent_idx(fault_idx)
            if parent_idx is not None:
                parent = self.get(parent_idx).functor
                if parent.field(fault_barycenters[fault_idx]) < 0:
                    side = Side.first
                else:
                    side = Side.second
                tree.add_child(parent_idx, side, fault_idx)

        assert tree.consistent_trees(verbose=True)
        assert tree.number_of_nodes() == nb_nodes
        assert self.nb_nodes == nb_nodes
        self.is_fault = lambda i: i < nb_nodes

    def _add_model(self, model):
        self._add_interfaces(model)
        self._add_units(model)

    def _add_interfaces(self, model):
        def is_erosion(interpolator):
            items = interpolator.dataset
            return len(items) == 1 and items[0].type == "Erosion"

        tree = self.tree
        assert self.nb_nodes == tree.number_of_nodes()
        all_interpolators = model.interpolators  # Ordered from oldest to youngest

        j = len(all_interpolators) - 1
        top_erosion = None
        domains_root = None
        while j >= 0:
            i = j
            while i >= 0 and not is_erosion(all_interpolators[i]):
                i -= 1
            if i >= 0:  # Erosion
                interfaces = make_interfaces(all_interpolators[i], self._nodes)
                name, wrapper = interfaces.popitem()
                assert len(interfaces) == 0
                color = model.get_item(name).get_color()
                cur_erosion = self.register_surface(name, wrapper, color=color)
                if top_erosion is not None:
                    tree.add_child(top_erosion, Side.first, cur_erosion)
                else:
                    # Note: there should be only 1 entry point for the stratigraphy
                    # So tree.add_node() should be called once and only once (?)
                    assert domains_root is None
                    domains_root = cur_erosion
                    tree.add_node(cur_erosion)
                top_erosion = cur_erosion
            side = Side.second if i >= 0 else Side.first
            prev_id = top_erosion
            for interpolator in all_interpolators[i + 1 : j + 1]:
                interfaces = make_interfaces(interpolator, self._nodes)
                for name, wrapper in interfaces.items():
                    color = model.get_item(name).get_color()
                    cur_id = self.register_surface(name, wrapper, color)
                    if prev_id is not None:
                        tree.add_child(prev_id, side, cur_id)
                    else:
                        # Note: there should be only 1 entry point for the stratigraphy
                        # So tree.add_node() should be called once and only once (?)
                        assert domains_root is None
                        domains_root = cur_id
                        tree.add_node(cur_id)
                    prev_id = cur_id
                    side = Side.second
            # Si on a trouve une erosion: on saute l'érosion
            # Sinon, aucune érosion, i = -1 donc on s'arrete
            j = i - 1
        assert tree.consistent_trees(verbose=True)
        self.domains_root = domains_root

    def _add_units(self, model):
        items = list(model.dataset)  # Copy to avoid modifying the original
        # Add fake units to ensure all model interfaces will have units both below and above them
        if items[0].is_surface:
            items.insert(0, Item("Below model", type="Unit"))
        if items[-1].is_surface:
            items.append(Item("Above model", type="Unit"))
        nb_items = len(items)
        interfaces = [i for i, item in enumerate(items) if item.is_surface]
        units = [i for i, item in enumerate(items) if not item.is_surface]
        assert len(units) + len(interfaces) == nb_items
        # Were all interfaces properly registered?
        assert all(self.get(items[i].name) is not None for i in interfaces)
        # Find units below / above each interface
        relations = {}
        for idx in interfaces:
            # Handles the possibility of multiple stacked erosions
            below = None
            i = idx
            while i > 0:
                i -= 1
                if i in units:
                    below = i
                    i = -1
            above = None
            i = idx
            while i < nb_items:
                i += 1
                if i in units:
                    above = i
                    i = nb_items
            # Consitency checks
            assert below is not None
            assert above is not None
            relations[idx] = (below, above)

        def _unique_name(name, already_used=set()):
            # Volontrily use already_used=set() rather than None!
            uid = -1
            new_name = name
            while new_name in already_used:
                uid += 1
                new_name = name + str(uid)
            already_used.add(new_name)
            return new_name

        # Add leaves to the BSPTree
        tree = self.tree
        nb_interfaces = tree.number_of_nodes()  # Capture before adding unit nodes
        domains_map = []
        for idx in interfaces:
            interface = self.get(items[idx].name)
            if len(tree.children(interface.id, Side.first)) == 0:
                unit = items[relations[idx][0]]
                unit_name = _unique_name(unit.name)
                uid = self.register_unit(unit_name, unit.get_color())
                domains_map.append((uid, unit_name, unit.name))
                tree.add_child(interface.id, Side.first, uid)
            if len(above := tree.children(interface.id, Side.second)) == 0:
                unit = items[relations[idx][1]]
                unit_name = _unique_name(unit.name)
                uid = self.register_unit(unit_name, unit.get_color())
                domains_map.append((uid, unit_name, unit.name))
                tree.add_child(interface.id, Side.second, uid)
        # Update other information
        for uid, uname, unit_name in domains_map:
            assert uname.startswith(unit_name)  # FIXME Test only
            self.domains_map[uid] = self.get(unit_name).id
        nb_nodes = tree.number_of_nodes()
        self.is_functor = lambda i: i < nb_interfaces or i >= nb_nodes

    def _set_discontinuities(self, model):
        # Note: faults are considered continuous. They can stop on other faults,
        # but they do not "cross" it (so they are not discontinuous across is)
        # So we only add modelling unit boundaries to rigs.Discontinuites

        # Reserve enough memory to avoid reallocations
        discontinuities = Discontinuities(self.tree.number_of_nodes())
        for interpolator in model.interpolators:
            # FIXME Pretty sure we should skip functolite interpolators while
            # gdmlib_extension factory is not implemented
            if not (faults := interpolator.discontinuities):
                continue
            assert all(self.exists(f) for f in faults)
            fault_ids = [self.get(f).id for f in faults]
            for item in interpolator.dataset:
                if item.is_surface:
                    sid = self.get(item.name).id
                    for fid in fault_ids:
                        discontinuities.add(sid, fid)  # sid is discontinuous across fid
        assert discontinuities.consistent_with(self.tree, verbose=True)
        self.discontinuities = discontinuities

    def _add_topography(self, topography):
        # Note: should be called last, as other surfaces (faults, stratigraphy)
        # added afterward will not cut by it (no tree.add_child(topo, other_surface))
        name, wrapper = wrap_raster(topography)
        topo_id = self.register_surface(name, wrapper)
        # Set topography above all pre-existing surfaces
        tree = self.tree
        roots = [root for root in tree.roots()]
        if not roots:
            tree.add_node(topo_id)
        else:
            for sid in roots:
                if sid != topo_id:
                    tree.add_child(topo_id, Side.first, sid)
        self.topography = topo_id
        assert tree.consistent_trees(verbose=True)

    @classmethod
    def from_fault_network(cls, fault_network) -> dict:
        """Setup the BSPTree and all related information required by rigs for
        generating representations of the input fault network
        """
        builder = cls()
        builder._add_fault_network(fault_network)
        return builder.to_dict()

    @classmethod
    def from_model(cls, model, fault_network=None) -> dict:
        """Setup the BSPTree and all related information required by rigs for
        generating representations of the input model

        If a fault network is provided, it will be included also
        """
        # FIXME fault_network should not be required
        # Related to model storing the name of the fault network instead of a pointer!
        builder = cls()
        if fault_network is not None:
            builder._add_fault_network(fault_network)
        builder._add_model(model)
        if fault_network is not None:
            builder._set_discontinuities(model)
        return builder.to_dict()

    @classmethod
    def from_params(
        cls,
        *,
        model=None,
        fault_network=None,
        topography=None,
        exact_discontinuities=True,
        **kwargs
    ) -> dict:
        """Setup the BSPTree and all related information required by rigs for
        generating representations of the input elements.

        Parameters
        ----------
        model: pile.Model (optional)
        fault_network: pile.FaultNetwork (optional)
        topography: pile.RasterDescription (optional)
        exact_discontinuities: bool
            If True (default), the exact intersections between faults and model
            elements will be computed. Otherwise, model elements will smear over
            faults (as if using a marching cube algorithm)
        """
        # Validity checks
        if fault_network is not None:
            pass  # TODO Implement validity checks
        if model is not None and not is_valid(model):
            return
        # Warning: Call order is important and should not be changed!
        builder = cls()
        # Step 1: Add faults if any
        if fault_network is not None:
            builder._add_fault_network(fault_network)
        else:
            exact_discontinuities = False
        # Step 2: Add stratigraphic model if any
        if model is not None:
            builder._add_model(model)
        else:
            exact_discontinuities = False
        # Step 3: Add topography if any
        if topography is not None:
            builder._add_topography(topography)
        # Step 4: if faults and stratigraphic model, add discontinuities
        # (if topopgrahy is present, it must be added before!)
        if exact_discontinuities:
            builder._set_discontinuities(model)
        return builder.to_dict()

    def initialize_extension_factory(self):
        if self.discontinuities is None:
            return None
        # We need to capture self.nb_nodes before any extension is generated
        # for consistency checks, so the closure
        nb_unextended_functors = self.nb_nodes

        def extension_factory(i, sides):
            assert i < nb_unextended_functors
            surface = self.get(i).functor
            method = surface.method
            if method == InterpolationMethod.POTENTIAL:
                functor, value = _gmlib_extension(self, i, sides)
            elif method == InterpolationMethod.ELEVATION_KRIGING:
                value = surface.value
                functor = as_functor(surface.field, value)
            self._extensions.append((functor, value))  # FIXME Is value really needed?
            return functor

        return extension_factory


def _get_gmlib_fault(builder, sid):
    field = builder.get(sid).functor.field
    assert isinstance(field, pypotential3D.Fault)
    return field


def _get_gmlib_ellipsoid(builder, sid):
    field = builder.get(sid).functor.field
    assert isinstance(field, pypotential3D.Ellipsoid)
    return field


def _gmlib_extension(builder, i, sides):
    """This function:
    - is used as a factory to generate factors on both sides of discontinuities
    - optimizes on the fly "as much as possible" the returned functors (so the
        mess inside...)

    args:
    i, int: index of the interface
    sides, Iterable[tuple[int, rigs.Side]]: list of (j, s), j = a discontinuity
    index, s = side on which to evaluate
    """

    assert 0 < len(sides)
    interface = builder.get(i)
    assert not interface.is_fault()
    interface = interface.functor
    di = interface.discontinuities
    assert len(sides) <= len(di.along)
    # First copy all drifts (coords + faults), then we will modify as we go
    # along only those that have a specific evaluation scheme and their and
    # those that depend on them.
    ext_drifts = copy(di.drifts)
    # Pour chacune des discontinuites
    for j, s in sides:
        assert ext_drifts[
            di.along[j]
        ].is_fault_drift  # assert not a "coord-based" drift
        # Force drift j evaluation side
        ext_drifts[di.along[j]] = ext_drifts[di.along[j]].change_evaluation(
            _gmlib_scheme_enum(s)
        )  # Note: change_evaluation returns a new Drift object
        # For each descendant k of drift j, REMOVE the contributions of all
        # descendants on the oppsite side of s (#optimisation)
        for k in builder.tree.descendance(j, _other_side(s)):
            if k in di.along:
                ext_drifts[di.along[k]] = ext_drifts[di.along[k]].change_evaluation(
                    OrientedEvaluation.always_outside
                )
        assert s in (Side.first, Side.second)
        # For each descendant k of j, on the side s where we will evaluate
        for k in builder.tree.descendance(j, s):
            if k in di.along:  # If k is a discontinuity and k affects i
                # UNSURE: Remove j from k limits because:
                # - we know we already are in j existance domain?
                # - or rather, we will evaluate ON j so we would have an
                # arbitrary behavior?
                assert _get_gmlib_fault(builder, k).number_of_boundaries() > 0
                unbounded_fault = _get_gmlib_fault(builder, k).remove_boundary(
                    _get_gmlib_fault(builder, j)
                )
                scheme = ext_drifts[di.along[k]].evaluation().scheme
                eid = builder._boundaries.get(k)
                if eid is not None:  # Finite fault
                    new_drift = pypotential3D.make_finite_drift(
                        unbounded_fault, _get_gmlib_ellipsoid(builder, eid), scheme
                    )
                else:
                    new_drift = pypotential3D.make_drift(unbounded_fault, scheme)
                # Update external drift
                ext_drifts[di.along[k]] = new_drift

    field = pypotential3D.alternate_drifts(interface.field, ext_drifts)
    value = interface.value
    return as_functor(field, value), value
