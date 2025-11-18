from __future__ import annotations
import pyquoks.utils


class Model:
    """
    Class for storing parameters and models

    **Optional attributes**::

        _ATTRIBUTES = {"beatmap_id", "score_id"}

        _OBJECTS = {"scores": ScoreModel}

    Attributes:
        _ATTRIBUTES: Set of parameters that stored in this model
        _OBJECTS: Dictionary with attributes and their models
        _data: Initial data that was passed into object
    """

    _ATTRIBUTES: set[str] | None

    _OBJECTS: dict[str, type] | None

    _data: dict

    def __init__(self, data: dict) -> None:
        self._data = data

        if hasattr(self, "_ATTRIBUTES"):
            if isinstance(self._ATTRIBUTES, set):
                for attribute in self._ATTRIBUTES:
                    setattr(self, attribute, self._data.get(attribute, None))
        else:
            self._ATTRIBUTES = None

        if hasattr(self, "_OBJECTS"):
            if isinstance(self._OBJECTS, dict):
                for attribute, object_class in self._OBJECTS.items():
                    try:
                        setattr(self, attribute, object_class(self._data.get(attribute)))
                    except:
                        setattr(self, attribute, None)
        else:
            self._OBJECTS = None


class Container:
    """
    Class for storing lists of models and another parameters

    **Optional attributes**::

        _ATTRIBUTES = {"beatmap_id", "score_id"}

        _OBJECTS = {"beatmap": BeatmapModel}

        _DATA = {"scores": ScoreModel}

    Attributes:
        _ATTRIBUTES: Set of parameters that stored in this container
        _OBJECTS: Dictionary with attributes and their models
        _DATA: Dictionary with attribute and type of models stored in list
        _data: Initial data that was passed into object
    """

    _ATTRIBUTES: set[str] | None

    _OBJECTS: dict[str, type] | None

    _DATA: dict[str, type] | None

    _data: dict | list[dict]

    def __init__(self, data: dict | list[dict]) -> None:
        self._data = data

        if isinstance(self._data, dict):
            if hasattr(self, "_ATTRIBUTES"):
                if isinstance(self._ATTRIBUTES, set):
                    for attribute in self._ATTRIBUTES:
                        setattr(self, attribute, self._data.get(attribute, None))
            else:
                self._ATTRIBUTES = None

            if hasattr(self, "_OBJECTS"):
                if isinstance(self._OBJECTS, dict):
                    for attribute, object_class in self._OBJECTS.items():
                        try:
                            setattr(self, attribute, object_class(self._data.get(attribute)))
                        except:
                            setattr(self, attribute, None)
            else:
                self._OBJECTS = None
        elif isinstance(self._data, list):
            if hasattr(self, "_DATA"):
                if isinstance(self._DATA, dict):
                    for attribute, object_class in self._DATA.items():
                        try:
                            setattr(self, attribute, [object_class(data) for data in self._data])
                        except:
                            setattr(self, attribute, None)
            else:
                self._DATA = None


class Values(pyquoks.utils._HasRequiredAttributes):
    """
    Class for storing various parameters and values

    **Required attributes**::

        _ATTRIBUTES = {"settings", "path"}

    Attributes:
        _ATTRIBUTES: Attributes that can be stored in this class
    """

    _REQUIRED_ATTRIBUTES = {
        "_ATTRIBUTES",
    }

    _ATTRIBUTES: set[str]

    def __init__(self, **kwargs) -> None:
        self._check_attributes()

        for attribute in self._ATTRIBUTES:
            setattr(self, attribute, kwargs.get(attribute, getattr(self, attribute, None)))

    def update(self, **kwargs) -> None:
        """
        Updates provided attributes in object
        """

        self.__init__(**kwargs)
