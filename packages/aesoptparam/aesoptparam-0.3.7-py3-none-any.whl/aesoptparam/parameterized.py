import json
import re

import numpy as np
import param as pm
from scipy.interpolate import PchipInterpolator

from .parameters import Function, ListOfParameterized, Reference
from .serializer import ASEOptJSONSerialization
from .utils import read_json, write_json
from .utils.html_repr import parameterized_repr_html, parameterized_repr_html_class
from .utils.units import convert_units


class AESOptParameterized(pm.Parameterized):
    """Base object inheriting from `param.Parameterized`. Adds specific methods for interacting with data in AESOpt models."""

    interpolator = PchipInterpolator

    def __init__(self, parent_object=None, **params):
        """Initialize object with parameters. **params are passed with the .from_dict. The parent_object argument allows nested objects to access data across the full data model"""
        self.parent_object = parent_object
        super().__init__()
        self.from_dict(params)

    def from_dict(self, dict_in):
        """Set parameters from `dict`"""
        for key, val in dict_in.items():
            if key in self.param:
                p = self.param[key]
                if hasattr(p, "readonly") and p.readonly:
                    if np.all(self[key] != val):
                        raise ValueError(
                            f"A parameter with readonly has a different value in the dict than currently in the object (given: self.{key}={self[key]}, dict_in['{key}']={val})"
                        )
                    continue
                if hasattr(self[key], "from_dict"):
                    self[key].from_dict(val)
                elif (
                    isinstance(self.param[key], pm.List)
                    and (self.param[key].item_type is not None)
                    and hasattr(self.param[key].item_type, "from_dict")
                ):
                    for i, el in enumerate(val):
                        if len(self[key]) > i:
                            self[key][i].from_dict(el)
                        else:
                            self[key].append(
                                self.param[key].item_type(self).from_dict(el)
                            )
                elif isinstance(self.param[key], pm.Array) and isinstance(val, list):
                    arr = np.asarray(val)
                    self[key] = arr
                else:
                    self[key] = val
        return self

    def as_dict(self, onlychanged=True, as_refs=False, as_funcs=False) -> dict:
        """Get object as dict. It also works for nested data structure, references and functions.

        Parameters
        ----------
        onlychanged : bool, optional
            Flag for only returning data that has been changed compared to the default, by default True
        as_refs : bool, optional
            Flag for returning the `Reference` instance instead of the values, by default False
        as_funcs : bool, optional
            Flag for returning the `Function` instance instead of the values, by default False

        Returns
        -------
        dict
            Object data as a dict
        """
        return self._as_dict(
            onlychanged=onlychanged, serialize=False, as_refs=as_refs, as_funcs=as_funcs
        )

    def as_serial(self, onlychanged=True, as_refs=True, as_funcs=True) -> dict:
        """Get instance as a serializable dict. It returns a `dict` with native python data types (e.g. `list`, `float`, `int`, `str`), which can be written to file with `json`, `yaml` and `toml`.
        It will also convert references (to `$ref *ref*`) and functions (to `$function *function string*`)

        Parameters
        ----------
        onlychanged : bool, optional
            Flag for only returning data that has been changed compared to the default, by default True
        as_refs : bool, optional
            Flag for returning the value from references or functions, by default True
        as_funcs : bool, optional
            Flag for returning the `Function` instance instead of the values, by default False

        Returns
        -------
        dict
            Object data as a dict
        """
        return self._as_dict(
            onlychanged=onlychanged, serialize=True, as_refs=as_refs, as_funcs=as_funcs
        )

    def _as_dict(
        self, onlychanged=True, serialize=False, as_refs=False, as_funcs=False
    ):
        out = dict()

        if onlychanged:
            vals = self._param__private.values
        else:
            vals = self.param.values()
            vals.update(self._param__private.values)

        for key, val in vals.items():
            p = self.param[key]  # Parameter instance
            if (key == "name") and p.constant:
                continue
            if onlychanged:
                if (val is None) or (val is p.default):
                    continue
                elif (
                    isinstance(val, np.ndarray)
                    and isinstance(p.default, np.ndarray)
                    and np.all(p.default.shape == val.shape)
                    and np.allclose(val, p.default)
                ):
                    continue
            if hasattr(val, "_as_dict"):
                out[key] = val._as_dict(
                    onlychanged=onlychanged,
                    serialize=serialize,
                    as_refs=as_refs,
                    as_funcs=as_funcs,
                )
                if not out[key]:
                    out.pop(key)
            elif isinstance(val, list) and len(val) > 0 and hasattr(val[0], "_as_dict"):
                out[key] = val.copy()
                for iel, el in enumerate(val):
                    out[key][iel] = el._as_dict(
                        onlychanged=onlychanged,
                        serialize=serialize,
                        as_refs=as_refs,
                        as_funcs=as_funcs,
                    )
                    if not out[key][iel]:
                        out[key][iel] = None
                if all([el is None for el in out[key]]):
                    out.pop(key)
            elif isinstance(val, Reference) and as_refs:
                out[key] = val
            elif isinstance(val, Function) and as_funcs:
                out[key] = val
            else:
                _val = self[key]
                out[key] = _val.copy() if hasattr(_val, "copy") else _val

            if serialize and (key in out):
                if isinstance(out[key], np.ndarray):
                    out[key] = out[key].tolist()
                elif isinstance(out[key], (Reference, Function)):
                    out[key] = str(out[key])
        return out

    def validate_array_shapes(self):
        """Validate that all arrays with a .shape attribute is consistent with this shape. Will also check nested objects."""
        for name, param in self.param.objects().items():
            if hasattr(param, "shape") and (param.shape is not None):
                shape_ref = self.get_shape_ref(param)
                if not np.all(self[name].shape == shape_ref):
                    raise ValueError(
                        f"For {self.nested_instance_name} the shape of {name} do not match {param.shape} ({name}.shape={self[name].shape}, shape_ref={shape_ref})"
                    )
            elif isinstance(param, ListOfParameterized):
                for el in self[name]:
                    if hasattr(el, "validate_array_shapes"):
                        el.validate_array_shapes()
            elif hasattr(self[name], "validate_array_shapes"):
                self[name].validate_array_shapes()

    def get_shape_ref(self, param):
        if isinstance(param.shape, tuple):
            shape_ref = tuple()
            for el in param.shape:
                if isinstance(el, (Reference, str)):
                    if not isinstance(self[el], np.ndarray):
                        return None
                    shape_ref += self[el].shape
                else:
                    shape_ref += (el,)
        elif isinstance(param.shape, Reference):
            if isinstance(self[param.shape], np.ndarray):
                shape_ref = self[param.shape].shape
            else:
                return None
        else:
            # Default to int
            shape_ref = (param.shape,)
        return shape_ref

    @property
    def nested_instance_name(self):
        """Nested instance name"""
        if self.has_parent():
            return self.parent_object.nested_instance_name + "." + self.name
        return self.name

    def interp(self, x, xp, yp, **interp_kwargs):
        """1D interpolation using SciPy interpolator (default to [`PChipInterpolator`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html#scipy.interpolate.PchipInterpolator)). Arguments (`x`, `xp`, `yp`) can either be strings (object-paths) or numpy arrays."""
        _x = x if isinstance(x, np.ndarray) else self[x]
        _xp = xp if isinstance(xp, np.ndarray) else self[xp]
        _yp = yp if isinstance(yp, np.ndarray) else self[yp]
        if any([el is None for el in [_x, _xp, _yp]]):
            return
        return self.interpolator(_xp, _yp, **interp_kwargs)(_x)

    def _repr_html_(self):
        return parameterized_repr_html(self, True, max_arr_size=50)

    def __getitem__(self, key):
        if isinstance(key, str):
            if ("." in key) or ("[" in key):
                path_list = path_to_path_list(key)
                out = self
                previous_empty = False
                for _key in path_list:
                    if isinstance(_key, str) and _key == "":
                        if previous_empty:
                            out = out.parent_object
                            previous_empty = False
                        else:
                            previous_empty = True
                    else:
                        if isinstance(_key, int) and len(out) <= _key:
                            # Return none if array is shorter
                            return None
                        out = out[_key]
                        previous_empty = False
                return out
            return getattr(self, key)
        elif isinstance(key, Reference):
            return self[key.path]
        super().__getattribute__(key)

    def __setitem__(self, key, val):
        if isinstance(key, str):
            return setattr(self, key, val)
        super().__setattr__(key, val)

    def get_val(self, name, units=None):
        """Get a value with other units"""
        self._validate_has_units(name)
        return convert_units(self[name], self.param[name].units, units)

    def set_val(self, name, val, units=None):
        """Get a value with other units"""
        self._validate_has_units(name)
        self[name] = convert_units(val, units, self.param[name].units)

    def _validate_has_units(self, name):
        if not hasattr(self.param[name], "units"):
            raise RuntimeError(
                f"parameter with name: {name} do not have units (the parameter do not have `units` attribute, type(.param[name])={type(self.param[name])})"
            )

    def add_ListOfParameterized_item(self, LOP_name, item_type, **kwargs):
        """Utility method to add Parameterized entries to a ListOfParameterized. It insure that the parent object is added. It is recommenced that this method is wrapped by a more specific method like `add_XX(self, **kwargs)` where the `LOP_name` and `item_type` is provided statically."""
        # Instantiate item_type
        item = item_type(parent_object=self, **kwargs)
        # Append the item to the list of ListOfParameterized
        if not LOP_name in self._param__private.values:
            self._param__private.values[LOP_name] = []
        self._param__private.values[LOP_name].append(item)
        # Return the item that is added
        return item

    def as_json(
        self, onlychanged=True, as_refs=True, as_funcs=True, **kwargs_json_dumps
    ):
        """Get data as a JSON string. `onlychanged` is a flag for only getting non default values."""
        return json.dumps(
            self.as_serial(onlychanged=onlychanged, as_refs=as_refs, as_funcs=as_funcs),
            **kwargs_json_dumps,
        )

    def write_json(
        self,
        filename,
        onlychanged=True,
        as_refs=True,
        as_funcs=True,
        **kwargs_json_dump,
    ):
        """Write data to a JSON file. `onlychanged` is a flag for only getting non default values."""
        with open(filename, "w") as file:
            json.dump(
                self.as_serial(
                    onlychanged=onlychanged, as_refs=as_refs, as_funcs=as_funcs
                ),
                file,
                **kwargs_json_dump,
            )
        return self

    def read_json(self, filename, asarray=True):
        """Read data from a JSON file."""
        data = read_json(filename, asarray)
        data.pop("$schema", None)
        self.from_dict(data)
        return self

    def as_json_schema(self, safe=False, subset=None, skip_default_name=True) -> dict:
        """Get object as a JSON schema

        Parameters
        ----------
        safe : bool, optional
            Flag for getting safe schema, by default False
        subset : list, optional
            List of names to skip, by default None
        skip_default_name : bool, optional
            Flag for skipping the default name when creating the schema, by default True

        Returns
        -------
        dict
            JSON Schema
        """
        return ASEOptJSONSerialization.schema(self, safe, subset, skip_default_name)

    def write_json_schema(
        self,
        filename,
        safe=False,
        subset=None,
        skip_default_name=True,
        **kwargs_json_dump,
    ):
        """Write object as a JSON schema file

        Parameters
        ----------
        filename : str,Path
            Filename for the JSON schema
        safe : bool, optional
            Flag for getting safe schema, by default False
        subset : list, optional
            List of names to skip, by default None
        skip_default_name : bool, optional
            Flag for skipping the default name when creating the schema, by default True

        Returns
        -------
        self
        """
        with open(filename, "w") as file:
            json.dump(
                self.as_json_schema(safe, subset, skip_default_name),
                file,
                **kwargs_json_dump,
            )
        return self

    def has_parent(self):
        return not self.parent_object is None

    def display(self, open=True, title=None, max_arr_size=50):
        """Method to display the settings and documentation of the current instance. Similar to just rendering the by last entry of the cell but allows a little more control

        Parameters
        ----------
        open : bool, optional
            Flag for opening or closing root the HTML table, by default True
        title : str, optional
            The string that will be shown as the root of the object, by default None
        max_arr_size : int, optional
            Maximum size of numeric arrays to render. Using `np.size(array) > max_arr_size`. Default will be determined based on the size of the data, `max_arr_size=[5, 10, 100]` for data with approx. size of [1000, 100, 10] size 100 arrays. Otherwise `max_array_size=-1` which means to render all arrays.
        """
        from IPython.display import display

        display(parameterized_repr_html_class(self, open, title, max_arr_size))


def path_to_path_list(path):
    """Converts an object path string to a `path_list`.

    Parameters
    ----------
    path : str
        Object path (e.g. `"key1.key2.key3[0].key4"`)

    Returns
    -------
    list
        List of keys and indices (e.g. `["key1","key2","key3",0,"key4"]`)

    Raises
    ------
    ValueError
        If indices are not integers (e.g. `key1[key3]` will fail)
    """
    path_list = []
    for name in path.split(".") if path.split(".") else [path]:
        if "[" in name:
            names = re.findall(r"([^\[\]]+)", name)
            if len(names) > 1:
                path_list.append(names[0])
                names = names[1:]
            for index in names:
                if not index.replace("-", "").replace("+", "").isdigit():
                    raise ValueError(
                        f"Indices need to integers: index={index} (name={name}, path={path})"
                    )
                path_list.append(int(index))
        else:
            path_list.append(name)
    return path_list
