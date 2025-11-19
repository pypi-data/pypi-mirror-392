from forgeo.core.erosion import Erosion


class ModellingUnit:
    """Represents a modelling unit in a hierarchical structure.

    Attributes
    ----------
    name : str
        The name of the modelling unit.
    description : list
        List of subunits or erosions describing the modelling unit.
    info : any, optional
        Additional information about the modelling unit.
    """

    def __init__(self, name, description=None, info=None):
        self.name = name
        self.description = description or []
        self.info = info

    def __getitem__(self, name):
        """Get a subunit or erosion thanks to its name.

        Parameters
        ----------
        name : str
            The name of the subunit or erosion to retrieve.

        Returns
        -------
        ModellingUnit or Erosion or None
            The subunit or erosion with the specified name, or None if not found.
        """
        for unit in self.description:
            if unit.name == name:
                return unit
            if isinstance(unit, ModellingUnit):
                subunit = unit[name]
                if subunit is not None:
                    return subunit

    def hasChildren(self):
        """Checks if the modelling unit has subunits.

        Returns
        -------
        bool
            True if the modelling unit has subunits, False otherwise.
        """
        return len(self.description) > 0

    def append(self, element):
        """Appends a subunit or erosion to the modelling unit.
        Checks if the element's name does not already exists in the modelling unit.

        Parameters
        ----------
        element : ModellingUnit or Erosion
            The subunit or erosion to append.
        """
        assert isinstance(element, (ModellingUnit, Erosion))
        assert self[element.name] is None
        self.description.append(element)

    def insertAt(self, element, index):
        """Inserts a subunit or erosion at a specific index.
        Checks if the element's name does not already exists in the modelling unit.

        Parameters
        ----------
        element : ModellingUnit or Erosion
            The subunit or erosion to insert.
        index : int
            The index at which to insert the element.
        """
        assert isinstance(element, (ModellingUnit, Erosion))
        assert self[element.name] is None
        self.description.insert(index, element)

    def insertAbove(self, element, target_element):
        """Inserts a subunit or erosion above a target subunit.
        Checks if the element's name does not already exists in the modelling unit,
        and if the target element's name does exist in the modelling unit.

        Parameters
        ----------
        element : ModellingUnit or Erosion
            The subunit or erosion to insert.
        target_element : ModellingUnit or Erosion
            The target subunit above which to insert the element.
        """
        assert isinstance(element, (ModellingUnit, Erosion))
        assert isinstance(target_element, (ModellingUnit, Erosion))
        assert self[element.name] is None
        assert self[target_element.name] is not None
        self.insertAt(element, self.description.index(target_element))

    def insertBelow(self, element, target_element):
        """Inserts a subunit or erosion below a target subunit.
        Checks if the element's name does not already exists in the modelling unit,
        and if the target element's name does exist in the modelling unit.

        Parameters
        ----------
        element : ModellingUnit or Erosion
            The subunit or erosion to insert.
        target_element : ModellingUnit or Erosion
            The target subunit below which to insert the element.
        """
        assert isinstance(element, (ModellingUnit, Erosion))
        assert isinstance(target_element, (ModellingUnit, Erosion))
        assert self[element.name] is None
        assert self[target_element.name] is not None
        self.insertAt(element, self.description.index(target_element) + 1)

    def removeUnit(self, element):
        """Removes a subunit or erosion from the modelling unit.

        Parameters
        ----------
        element : ModellingUnit or Erosion
            The subunit or erosion to remove.
        """
        assert isinstance(element, (ModellingUnit, Erosion))
        for unit in self.description:
            if unit == element:
                self.description.remove(unit)
            elif isinstance(unit, ModellingUnit) and unit.hasChildren():
                unit.removeUnit(element)

    def subunits(self, depth=1, include_erosions=True):
        """Generates an iterator on the subunits of the modelling unit,
        up to a specified depth.

        Parameters
        ----------
        depth : int, optional
            The maximum depth to add subunits. Default is 1.
        include_erosions : bool, optional
            Adds the erosions names if True, else not.
        """
        if depth == 0:
            return
        for element in self.description:
            if include_erosions or not isinstance(element, Erosion):
                yield element
            if isinstance(element, ModellingUnit) and element.hasChildren():
                yield from element.subunits(depth - 1, include_erosions)

    def display(self, depth=1, include_erosions=True):
        """Displays the hierarchical structure of the modelling unit.

        Parameters
        ----------
        depth : int, optional
            The maximum depth to display subunits. Default is 1.
        include_erosions : bool, optional
            Displays the erosions names if True, else not.
        """

        def display_recursive(unit, current_depth):
            print("  " * current_depth + unit.name)
            if current_depth < depth:
                for element in unit.subunits(1, include_erosions):
                    if isinstance(element, Erosion):
                        print(f"--- {element} ---")
                    elif isinstance(element, ModellingUnit):
                        display_recursive(element, current_depth + 1)

        display_recursive(self, 0)

    def __repr__(self):
        """Returns a string representation of the ModellingUnit instance."""
        pile_str = self.name
        if self.hasChildren():
            pile_str += ": [ "
            for elt in self.description:
                pile_str += repr(elt) + " "
            pile_str += "]"
        return pile_str
