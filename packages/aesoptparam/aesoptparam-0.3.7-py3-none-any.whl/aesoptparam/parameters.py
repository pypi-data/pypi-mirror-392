import typing
from inspect import getsource, signature

import numpy as np
import param as pm

from .utils.html_repr import value_ref_default_repr_html
from .utils.units import valid_units


class SubParameterized(pm.ClassSelector):
    @typing.overload
    def __init__(
        self,
        class_,
        *,
        default=None,
        instantiate=True,
        is_instance=True,
        allow_None=False,
        doc=None,
        label=None,
        precedence=None,
        constant=False,
        readonly=False,
        pickle_default_value=True,
        per_instance=True,
        allow_refs=False,
        nested_refs=False,
    ): ...

    def __init__(self, class_, *, default=pm.Undefined, doc=pm.Undefined, **params):
        """Include a Parameterized class as a parameter. A direct child `param.ClassSelector` for including nested Parameterized model in a Parameterized model. Default to an empty instance of the class and adding the doc string from the class."""
        if default is pm.Undefined:
            default = lambda self: class_(parent_object=self)
        if (doc is pm.Undefined) and (class_.__doc__):
            doc = class_.__doc__
        super().__init__(class_=class_, default=default, doc=doc, **params)
        self._validate(self.default)

    def __get__(self, obj, objtype):
        out = super().__get__(obj, objtype)
        if callable(out):
            if len(signature(out).parameters) == 1:
                obj._param__private.values[self.name] = out(obj)
            else:
                obj._param__private.values[self.name] = out()
            return super().__get__(obj, objtype)
        return out

    def _validate_class_(self, val, class_, is_instance):
        if val is None:
            return
        if not callable(val):
            if not (isinstance(val, class_)):
                class_name = class_.__name__
                raise ValueError(
                    f"{pm.parameters._validate_error_prefix(self)} value must be an instance of {class_name}, not {val!r}."
                )


class ListOfParameterized(pm.List):
    __slots__ = ["identifier", "default_call"]
    _slot_defaults = dict(pm.List._slot_defaults, identifier="name", default_call=None)

    @typing.overload
    def __init__(
        self,
        item_type,
        identifier,
        *,
        default=[],
        instantiate=True,
        bounds=(0, None),
        allow_None=False,
        doc=None,
        label=None,
        precedence=None,
        constant=False,
        readonly=False,
        pickle_default_value=True,
        per_instance=True,
        allow_refs=False,
        nested_refs=False,
        default_call=None,
    ): ...

    def __init__(self, item_type, identifier="name", *, default_call=None, **params):
        """List of Parameterized objects. Adds a html render and unique object identifier. A direct child of `param.List`"""
        self.identifier = identifier
        if default_call is not None and not callable(default_call):
            raise RuntimeError(
                f"`default_call` need to be a callable or None (given: {default_call})"
            )
        self.default_call = default_call
        super().__init__(item_type=item_type, **params)
        if (self.doc is None) and (self.item_type.__doc__):
            self.doc = self.item_type.__doc__

    def __get__(self, obj, objtype):
        out = super().__get__(obj, objtype)
        if not out and self.default_call is not None:
            val = self.default_call(obj)
            if not isinstance(val, list):
                raise ValueError(
                    f"`.default_call` need to return a list (gives: `type(default_call(obj))`={type(self.default_call(obj))})"
                )
            obj._param__private.values[self.name] = self.default_call(obj)
            return super().__get__(obj, objtype)
        return out


class BaseRefFunc:
    def __init__(
        self,
        default=pm.Undefined,
        *,
        default_ref=pm.Undefined,
        **params,
    ):
        if self._is_ref(default):
            default = Reference(default)
        elif self._is_func(default):
            default = Function(default)
        if not (default_ref is pm.Undefined or default_ref is None) and (
            not isinstance(default_ref, (str, Reference))
        ):
            raise ValueError(
                f"`default_ref` need to be of type string (given: type(default_ref)={type(default_ref)})"
            )
        self.default_ref = None
        if not (default_ref is pm.Undefined or default_ref is None):
            self.default_ref = (
                default_ref
                if isinstance(default_ref, Reference)
                else Reference(default_ref)
            )
        super().__init__(default=default, **params)

    def __get__(self, obj, objtype):
        out = super().__get__(obj, objtype)
        if isinstance(out, Function):
            return out.method(obj)
        elif isinstance(out, Reference):
            return obj[out]
        elif out is None:
            if isinstance(self.default_ref, Reference):
                return obj[self.default_ref]
        return out

    def __set__(self, obj, val):
        if not isinstance(val, Function) and self._is_func(val):
            val = Function(val)
        elif not isinstance(val, Reference) and self._is_ref(val):
            val = Reference(val)
        return super().__set__(obj, val)

    def _validate_value(self, val, allow_None):
        if isinstance(val, (Function, Reference)):
            return
        return super()._validate_value(val, allow_None)

    def _is_func(
        self,
        func,
    ):
        return (
            callable(func)
            or isinstance(func, Function)
            or (isinstance(func, str) and func.startswith("$function"))
        )

    def _is_ref(self, ref):
        return isinstance(ref, Reference) or (
            isinstance(ref, str)
            and ((ref.startswith(".") and not ref[1] == "/") or ref.startswith("$ref"))
        )

    def repr_html(self, val, val_pp, max_arr_size=50):
        return value_ref_default_repr_html(self, val, val_pp, max_arr_size)


class BaseRefFuncUnits(BaseRefFunc):
    def __init__(
        self,
        default=pm.Undefined,
        *,
        units=pm.Undefined,
        **params,
    ):
        if (not units is pm.Undefined) and (not valid_units(units)):
            raise ValueError(f"units is not valid (given: {units})")
        self.units = units
        super().__init__(default=default, **params)


class AESOptString(BaseRefFunc, pm.String):
    __slots__ = ["default_ref"]

    _slot_defaults = dict(
        pm.String._slot_defaults,
        default=None,
        allow_None=True,
        default_ref=None,
    )

    @typing.overload
    def __init__(
        self,
        default="",
        *,
        regex=None,
        doc=None,
        label=None,
        precedence=None,
        instantiate=False,
        constant=False,
        readonly=False,
        pickle_default_value=True,
        allow_None=False,
        per_instance=True,
        allow_refs=False,
        nested_refs=False,
        default_ref=None,
    ): ...

    def __init__(self, default=None, **param):
        super().__init__(default=default, **param)


class AESOptNumber(BaseRefFuncUnits, pm.Number):
    __slots__ = ["units", "default_ref"]

    _slot_defaults = dict(
        pm.Number._slot_defaults,
        default=None,
        units=None,
        allow_None=True,
        default_ref=None,
    )

    @typing.overload
    def __init__(
        self,
        default=None,
        *,
        bounds=None,
        softbounds=None,
        inclusive_bounds=(True, True),
        is_instance=True,
        allow_None=False,
        doc=None,
        label=None,
        precedence=None,
        instantiate=True,
        constant=False,
        readonly=False,
        pickle_default_value=True,
        per_instance=True,
        allow_refs=False,
        nested_refs=False,
        units=None,
        default_ref=None,
    ): ...

    def __init__(self, default=None, **param):
        super().__init__(default=default, **param)

    def _validate_value(self, val, allow_None):
        if isinstance(val, np.ndarray):
            raise ValueError(
                f"{pm._utils._validate_error_prefix(self)} only takes numeric values, "
                f"not {type(val)}."
            )
        return super()._validate_value(val, allow_None)

    def _validate_bounds(self, val, bounds, inclusive_bounds):
        if isinstance(val, (Reference, Function)):
            return
        return super()._validate_bounds(val, bounds, inclusive_bounds)


class AESOptInteger(AESOptNumber, pm.Integer):
    _slot_defaults = dict(
        pm.Integer._slot_defaults,
        default=None,
        units=None,
        allow_None=True,
        default_ref=None,
    )


class AESOptArray(BaseRefFuncUnits, pm.Array):
    __slots__ = [
        "bounds",
        "softbounds",
        "inclusive_bounds",
        "units",
        "dtype",
        "shape",
        "default_full",
        "default_interp",
        "default_ref",
    ]

    _slot_defaults = dict(
        pm.Array._slot_defaults,
        default=None,
        bounds=None,
        softbounds=None,
        inclusive_bounds=(True, True),
        units=None,
        dtype=np.number,
        shape=None,
        default_full=None,
        default_interp=None,
        default_ref=None,
    )

    @typing.overload
    def __init__(
        self,
        default=None,
        *,
        bounds=None,
        softbounds=None,
        inclusive_bounds=(True, True),
        is_instance=True,
        allow_None=False,
        doc=None,
        label=None,
        precedence=None,
        instantiate=True,
        constant=False,
        readonly=False,
        pickle_default_value=True,
        per_instance=True,
        allow_refs=False,
        nested_refs=False,
        units=None,
        dtype=np.number,
        shape=None,
        default_full=None,
        default_interp=None,
        default_ref=None,
    ): ...

    def __init__(
        self,
        default=pm.Undefined,
        *,
        bounds=pm.Undefined,
        softbounds=pm.Undefined,
        inclusive_bounds=pm.Undefined,
        dtype=np.number,
        shape=pm.Undefined,
        default_full=pm.Undefined,
        default_interp=pm.Undefined,
        default_ref=pm.Undefined,
        **params,
    ):
        """Numeric numpy array. Adds bound checking, shape, dtype, units, etc. A direct child of `param.Array`
        For `bounds`, `softbounds` and `inclusive_bounds` see `param.Number`.
        `default` can either be a string with the variable to default to or it can a a callable with one argument which is going to be the Parameterized instance (e.g. `lambda self: self._param__private.values["x"]` will make the variable default to the parameter "x")
        `units` should be a `str` following [OpenMDAO: Specifying Units for Variables](https://openmdao.org/newdocs/versions/latest/features/core_features/working_with_components/units.html?highlight=units)
        `dtype` should be a numpy dtype class. Default to `numpy.number`.
        `shape` should be one of `int`: static shape, `str`: shape like another parameter (using object-path), `tuple`: multi-dim, where each dim can be either `int` or `str`.
        `default_full` should be a tuple of length 2 with items: 1: shape-like input (`int`, `str` or `tuple`) see above, 2: value to fill with (`float`, `int`)
        `default_interp` should be a tuple of length 3 with items (each can be either `numpy.ndarray` or `str`): 1: new grid (`x`), 2: old grid (`xp`), 3: old values (`yp`).
        """
        self.bounds = bounds
        self.softbounds = softbounds
        self.inclusive_bounds = inclusive_bounds
        self.dtype = dtype
        if (not default_full is pm.Undefined) and (
            not isinstance(default_full, tuple)
            or not self._validate_shape(default_full[0])
            or not isinstance(default_full[1], (float, int, str))
        ):
            raise ValueError(
                f"default_full must be a tuple of length 2, with the first element should be shape compliant (tuple, str, int) and the second the value to fill with (given: {default_full})"
            )
        if not default_full is pm.Undefined and isinstance(default_full, tuple):
            self.default_full = [
                Reference(el) if isinstance(el, str) else el for el in default_full
            ]
            if isinstance(self.default_full[0], tuple):
                self.default_full[0] = tuple(
                    Reference(el) if isinstance(el, str) else el
                    for el in default_full[0]
                )
            self.default_full = tuple(self.default_full)
        else:
            self.default_full = default_full
        if (not default_interp is pm.Undefined) and (
            not isinstance(default_interp, tuple)
            or not all([isinstance(el, (str, np.ndarray)) for el in default_interp])
        ):
            raise ValueError(
                f"default_interp must be a tuple of length 3, with elements of either str, numpy.ndarray (given: {default_interp})"
            )
        if not default_interp is pm.Undefined and isinstance(default_interp, tuple):
            self.default_interp = tuple(
                Reference(el) if isinstance(el, str) else el for el in default_interp
            )
        else:
            self.default_interp = default_interp
        if shape is pm.Undefined:
            if self._is_ref(default):
                shape = default
            elif isinstance(self.default_full, tuple):
                shape = self.default_full[0]
            elif isinstance(self.default_interp, tuple):
                if isinstance(self.default_interp[0], Reference):
                    shape = self.default_interp[0]
                else:
                    shape = self.default_interp[0].shape
            elif not (default_ref is pm.Undefined or default_ref is None):
                shape = default_ref
        if isinstance(shape, str):
            shape = Reference(shape)
        elif isinstance(shape, tuple):
            shape = tuple(Reference(el) if isinstance(el, str) else el for el in shape)
        self._validate_shape(shape)
        self.shape = shape
        if self._is_ref(default) or self._is_func(default):
            params["instantiate"] = False
        super().__init__(default=default, default_ref=default_ref, **params)

    def _validate_shape(self, shape):
        if not (shape is pm.Undefined or shape is None):
            if isinstance(shape, tuple):
                if not all([isinstance(el, (Reference, str, int)) for el in shape]):
                    raise ValueError(
                        f"shape as a tuple need to have item-types of either str,int. ([type(el) for el in shape])={[type(el) for el in shape]})"
                    )
            elif not isinstance(shape, (Reference, str, int)):
                raise ValueError(
                    f"shape need to be of type tuple, str, int (given: type(shape)={type(shape)})"
                )
        return True

    def _validate_bounds(self, val, bounds, inclusive_bounds):
        if (
            bounds is None
            or (val is None and self.allow_None)
            or callable(val)
            or isinstance(val, str)
        ):
            return
        vmin, vmax = bounds
        incmin, incmax = inclusive_bounds
        if vmax is not None:
            if incmax is True:
                if np.any(val > vmax):
                    raise ValueError(
                        f"{pm.parameters._validate_error_prefix(self)} must be at most "
                        f"{vmax}, not {val}."
                    )
            else:
                if np.any(val >= vmax):
                    raise ValueError(
                        f"{pm.parameters._validate_error_prefix(self)} must be less than "
                        f"{vmax}, not {val}."
                    )

        if vmin is not None:
            if incmin is True:
                if np.any(val < vmin):
                    raise ValueError(
                        f"{pm.parameters._validate_error_prefix(self)} must be at least "
                        f"{vmin}, not {val}."
                    )
            else:
                if np.any(val <= vmin):
                    raise ValueError(
                        f"{pm.parameters._validate_error_prefix(self)} must be greater than "
                        f"{vmin}, not {val}."
                    )

    def _validate_dtype(self, val, dtype):
        if isinstance(val, np.ndarray):
            if not np.issubdtype(val.dtype, dtype):
                raise ValueError(
                    f"Array dtype must be a subclass of {self.dtype} but it is {val.dtype} (is validated with `numpy.issubdtype`)"
                )

    def _validate_class_(self, val, class_, is_instance):
        if val is None:
            return
        elif isinstance(val, (Reference, Function)):
            return
        else:
            if not (isinstance(val, class_)):
                class_name = class_.__name__
                raise ValueError(
                    f"{pm.parameters._validate_error_prefix(self)} value must be an instance of {class_name}, not {val!r}."
                )

    def _validate(self, val):
        super()._validate(val)
        self._validate_dtype(val, self.dtype)
        self._validate_bounds(val, self.bounds, self.inclusive_bounds)

    def __get__(self, obj, objtype):
        out = super().__get__(obj, objtype)
        if out is None:
            if not self.default_full is None:
                shape_ref = obj.get_shape_ref(self)
                if not shape_ref is None:
                    if isinstance(self.default_full[1], Reference):
                        val = obj[self.default_full[1]]
                    else:
                        val = self.default_full[1]
                    return np.full(shape_ref, val)
            elif not self.default_interp is None:
                return obj.interp(*self.default_interp)
        return out

    def __set__(self, obj, val):
        if not isinstance(val, str) and np.isscalar(val):
            if self.shape is not None:
                val = np.full(obj.get_shape_ref(self), val)
            else:
                raise ValueError(
                    f"Scaler values can only be assigned to AESOptArray if it has a defined shape (given: val={val})"
                )
        return super().__set__(obj, val)


class AESOptBoolean(BaseRefFunc, pm.Boolean):

    __slots__ = ["default_ref"]

    _slot_defaults = dict(
        pm.Boolean._slot_defaults,
        default=None,
        allow_None=True,
        default_ref=None,
    )

    @typing.overload
    def __init__(
        self,
        default=None,
        *,
        allow_None=False,
        doc=None,
        label=None,
        precedence=None,
        instantiate=False,
        constant=False,
        readonly=False,
        pickle_default_value=True,
        per_instance=True,
        allow_refs=False,
        nested_refs=False,
        default_ref=None,
    ): ...

    def __init__(self, default=None, **param):
        super().__init__(default=default, **param)

    def _validate_value(self, val, allow_None):
        if (
            not (
                val is None
                or isinstance(val, bool)
                or self._is_ref(val)
                or self._is_func(val)
            )
            and self.default_ref is None
        ):
            raise ValueError(
                f"Either `value`, `default` or `default_ref` need to be set (given: {val})"
            )
        if self._is_ref(val) or self._is_func(val) or self.default_ref is not None:
            return
        super()._validate_value(val, allow_None)


class Reference:
    def __init__(self, path: str) -> None:
        if path.startswith("$ref "):
            path = path[5:]
        self.is_valid_object_path(path)
        self.path = path

    def is_valid_object_path(self, path):
        if not path.startswith("."):
            raise ValueError(
                f"Object path need to start with `.` or `$ref ` (given: path={path})"
            )
        if " " in path or "\t" in path:
            raise ValueError(
                f"Object path can not contain spaces or tabs (given: path={path})"
            )
        return True

    def __str__(self):
        return f"$ref {self.path}"

    def __repr__(self):
        return self.path

    def __eq__(self, val):
        return self.path == val


class Function:
    def __init__(self, method) -> None:
        if isinstance(method, str) and method.startswith("$function "):
            method_source = method[10:]
            if method_source.startswith("def "):
                method_name = method_source[4:].split("(")[0]
                exec(method_source)
                method = eval(method_name)
            else:
                method = eval(method_source)
            method.method_source = method_source

        if not callable(method):
            raise ValueError(
                f"`method` need to be a `callable` or string starting with `$function ` (given: method={method})"
            )
        self.method = method

    @property
    def source_str(self):
        if hasattr(self.method, "method_source"):
            return self.method.method_source
        method_source = getsource(self.method).strip()
        if "lambda" in method_source:
            method_source = "lambda" + "lambda".join(method_source.split("lambda")[1:])
        return method_source

    def __str__(self):
        return f"$function {self.source_str}"

    def __repr__(self) -> str:
        return f"<$function id={id(self.method)}>"
