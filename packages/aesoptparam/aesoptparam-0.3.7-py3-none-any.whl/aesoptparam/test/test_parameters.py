import numpy as np
import pytest

from aesoptparam import (
    AESOptArray,
    AESOptBoolean,
    AESOptInteger,
    AESOptNumber,
    AESOptParameterized,
    AESOptString,
    ListOfParameterized,
    SubParameterized,
)
from aesoptparam.parameters import Function, Reference


def test_SubParameterized():
    class dummy_sub(AESOptParameterized):
        """Dummy doc"""

        x = AESOptNumber(0.0, doc="Dummy number")

    class dummy_main(AESOptParameterized):
        subData = SubParameterized(dummy_sub)

    dum_main = dummy_main()
    assert dum_main.param.subData.class_ is dummy_sub
    assert isinstance(dum_main.subData, dummy_sub)
    assert dum_main.param.subData.__doc__ == "Dummy doc"
    assert dum_main.subData.parent_object is dum_main

    with pytest.raises(ValueError, match="value must be an instance of dummy_sub"):
        dum_main.subData = object()

    # Deleting the object by None
    dum_main.subData = None


def test_ListOfParameterized():
    class dummy_item(AESOptParameterized):
        """Dummy doc"""

        x = AESOptNumber(0.0, doc="Dummy number")

    class dummy(AESOptParameterized):
        lop = ListOfParameterized(dummy_item)

        def add_dummy_item(self, **param):
            dum_item = dummy_item(self, **param)
            self.lop.append(dum_item)
            return dum_item

    dum_ins = dummy()
    dum_ins.add_dummy_item()

    assert dum_ins.param.lop.doc == "Dummy doc"
    assert dum_ins.lop[0].parent_object is dum_ins

    # Add a default item
    class dummy(AESOptParameterized):
        lop = ListOfParameterized(
            dummy_item, default_call=lambda self: [self.add_dummy_item()]
        )

        def add_dummy_item(self, **param):
            dum_item = dummy_item(self, **param)
            if not "lop" in self._param__private.values:
                self._param__private.values["lop"] = []
            self._param__private.values["lop"].append(dum_item)
            return dum_item

    dum_ins = dummy()
    assert dum_ins.param.lop.doc == "Dummy doc"
    assert dum_ins.lop[0].parent_object is dum_ins

    # Only testing that it runs
    html = dum_ins._repr_html_()

    with pytest.raises(RuntimeError, match="`default_call` need to be"):
        ListOfParameterized(dummy_item, default_call="Not a function")

    with pytest.raises(ValueError, match="`.default_call` need to return"):

        class dummy(AESOptParameterized):
            lop = ListOfParameterized(
                dummy_item, default_call=lambda self: self.add_dummy_item()
            )

            def add_dummy_item(self, **param):
                dum_item = dummy_item(self, **param)
                if not "lop" in self._param__private.values:
                    self._param__private.values["lop"] = []
                self._param__private.values["lop"].append(dum_item)
                return dum_item

        dum_ins = dummy()
        dum_ins.lop


def test_AESOptString():

    val = "Dummy"

    class dummy(AESOptParameterized):
        x = AESOptString(val)
        y = AESOptString(default_ref=".x")
        z = AESOptString(lambda self: self.x + " + a little")
        a = AESOptString(".x")

    dum_ins = dummy()
    assert dum_ins.x == val
    assert dum_ins.y == val
    assert dum_ins.z == val + " + a little"
    assert dum_ins.a == val
    assert dum_ins.param.x.default == val
    assert dum_ins.param.y.default_ref == ".x"
    assert isinstance(dum_ins.param.z.default, Function)
    assert isinstance(dum_ins.param.a.default, Reference)
    assert dum_ins.param.a.default == ".x"

    dum_ins.a = lambda self: self.x + " + extra bit"
    dum_ins.x = "Dummy2"
    assert dum_ins.a == "Dummy2 + extra bit"
    assert isinstance(dum_ins._param__private.values["a"], Function)

    dum_ins.a = "$function lambda self: self.x + ' + extra bit2'"
    dum_ins.x = "Dummy3"
    assert dum_ins.a == "Dummy3 + extra bit2"
    assert isinstance(dum_ins._param__private.values["a"], Function)

    with pytest.raises(ValueError):
        dum_ins.x = 1.0

    with pytest.raises(ValueError, match="`default_ref` need to be"):
        AESOptString(default_ref=5)


def test_AESOptNumber():
    # Test it adds units
    x = AESOptNumber(0.0, doc="Dummy number", units="m")
    assert hasattr(x, "units")
    assert x.units == "m"

    class dummy(AESOptParameterized):
        x = AESOptNumber(0.0, bounds=(0, 1))
        y = AESOptNumber(default_ref=".x", bounds=(0, 1))
        z = AESOptNumber(lambda self: self.x + 1.0, bounds=(0, 1))
        a = AESOptNumber(".x", bounds=(0, 1))

    dum_ins = dummy()
    assert dum_ins.x == 0.0
    assert dum_ins.y == 0.0
    assert dum_ins.z == 1.0
    assert dum_ins.a == 0.0
    assert dum_ins.param.x.default == 0.0
    assert dum_ins.param.y.default_ref == ".x"
    assert isinstance(dum_ins.param.z.default, Function)
    assert isinstance(dum_ins.param.a.default, Reference)
    assert dum_ins.param.a.default == ".x"

    dum_ins.a = lambda self: self.x + 5.0
    dum_ins.x = 1.0
    assert dum_ins.a == 6.0
    assert isinstance(dum_ins._param__private.values["a"], Function)

    dum_ins.a = "$function lambda self: self.x + 6.0"
    dum_ins.x -= 0.5
    assert dum_ins.a == 6.5
    assert isinstance(dum_ins._param__private.values["a"], Function)

    with pytest.raises(ValueError):
        dum_ins.x = np.linspace(0, 10, 10)

    with pytest.raises(ValueError, match="units is not valid "):
        AESOptNumber(units="XX")

    with pytest.raises(ValueError, match="`default_ref` need to be"):
        AESOptNumber(default_ref=5)

    AESOptNumber(units="mm/kg**3*Pa")


def test_AESOptInteger():
    # Test it adds units
    x = AESOptInteger(0, doc="Dummy integer", units="m")
    assert hasattr(x, "units")
    assert x.units == "m"

    class dummy(AESOptParameterized):
        x = AESOptInteger(0, bounds=(0, 10))
        y = AESOptInteger(default_ref=".x", bounds=(0, 10))
        z = AESOptInteger(lambda self: self.x + 1, bounds=(0, 10))
        a = AESOptInteger(".x", bounds=(0, 10))

    dum_ins = dummy()
    assert dum_ins.x == 0
    assert dum_ins.y == 0
    assert dum_ins.z == 1
    assert dum_ins.a == 0
    assert dum_ins.param.x.default == 0
    assert dum_ins.param.y.default_ref == ".x"
    assert isinstance(dum_ins.param.z.default, Function)
    assert isinstance(dum_ins.param.a.default, Reference)
    assert dum_ins.param.a.default == ".x"

    dum_ins.a = lambda self: self.x + 5
    dum_ins.x = 1
    assert dum_ins.a == 6
    assert isinstance(dum_ins._param__private.values["a"], Function)

    dum_ins.a = "$function lambda self: self.x + 6"
    dum_ins.x -= 1
    assert dum_ins.a == 6
    assert isinstance(dum_ins._param__private.values["a"], Function)

    with pytest.raises(ValueError):
        dum_ins.x = 2.5

    with pytest.raises(ValueError):
        dum_ins.x = 20


def test_AESOptArray():
    class dummy(AESOptParameterized):
        x = AESOptArray()
        y = AESOptArray(default_full=(".x", 5))

    dum = dummy()
    assert dum.y is None
    dum.x = np.linspace(0, 1, 10)
    assert dum.y.shape == (10,)
    np.testing.assert_almost_equal(dum.y, 5)

    class dummy(AESOptParameterized):
        a = AESOptArray()
        b = AESOptArray(default_ref=".a")
        c = AESOptArray(
            lambda self: self.a + 1.0 if isinstance(self.a, np.ndarray) else self.a
        )
        d = AESOptArray(default_full=(".a", 5))
        e = AESOptArray(default_full=((".a", 7), 6))
        f = AESOptArray(default_interp=(np.linspace(0, 1, 5), ".a", ".c"))
        g = AESOptArray(".a")
        h = AESOptArray(np.linspace(0, 1, 5))
        i = AESOptArray(default_interp=(".h", ".a", ".c"))
        j = AESOptArray(shape=".h")
        k = AESOptArray(shape=(".h",))
        l = AESOptArray(shape=(".h", ".a"))
        m = AESOptArray(shape=(".h", ".a", 5))
        n = AESOptArray(np.arange(3, 25))

    dum = dummy()
    assert dum.b is None
    assert dum.c is None
    assert dum.d is None
    assert dum.e is None
    assert dum.f is None
    assert dum.g is None
    assert dum.i is None

    for key, par in dum.param.objects().items():
        if key == "name":
            continue
        val = dum[key]
        val_pp = dum._param__private.values.get(key, None)
        par.repr_html(val, val_pp)

    dum.a = np.linspace(0, 1, 10)
    # b
    assert dum.b.shape == (10,)
    np.testing.assert_almost_equal(dum.b, dum.a)
    assert (
        isinstance(dum.param.b.default_ref, Reference)
        and dum.param.b.default_ref == ".a"
    )
    assert isinstance(dum.param.b.shape, Reference) and dum.param.b.shape == ".a"

    # c
    assert dum.c.shape == (10,)
    np.testing.assert_almost_equal(dum.c, dum.a + 1.0)
    assert isinstance(dum.param.c.default, Function)

    # d
    assert dum.d.shape == (10,)
    np.testing.assert_almost_equal(dum.d, 5)
    assert dum.param.d.default is None
    assert isinstance(dum.param.d.shape, Reference) and dum.param.d.shape == ".a"

    # e
    assert np.all(dum.e.shape == (10, 7))
    np.testing.assert_almost_equal(dum.e, 6)
    assert dum.param.e.default is None
    assert (
        isinstance(dum.param.e.shape[0], Reference)
        and dum.param.e.shape[0].path == ".a"
    )
    assert dum.param.e.shape[1] == 7

    # f
    assert np.all(dum.f.shape == (5,))
    np.testing.assert_almost_equal(dum.f, dum.interp(np.linspace(0, 1, 5), ".a", ".c"))
    assert dum.param.f.default is None
    assert np.all(dum.param.f.shape == (5,))

    # g
    assert dum.g.shape == (10,)
    np.testing.assert_almost_equal(dum.g, dum.a)
    assert isinstance(dum.param.g.default, Reference) and dum.param.g.default == ".a"
    assert isinstance(dum.param.g.shape, Reference) and dum.param.g.shape == ".a"

    # h
    assert dum.h.shape == (5,)
    np.testing.assert_almost_equal(dum.h, np.linspace(0, 1, 5))
    assert isinstance(dum.param.h.default, np.ndarray)

    # i
    assert dum.param.i.shape.path == ".h"
    np.testing.assert_almost_equal(dum.i, dum.f)
    assert dum.param.i.default is None
    assert np.all(dum.i.shape == (5,))
    assert np.all(dum.get_shape_ref(dum.param.i) == (5,))

    # j
    assert dum.param.j.shape.path == ".h"
    assert np.all(dum.get_shape_ref(dum.param.j) == (5,))

    # k
    assert len(dum.param.k.shape) == 1
    assert dum.param.k.shape[0].path == ".h"
    assert np.all(dum.get_shape_ref(dum.param.k) == (5,))

    # l
    assert len(dum.param.l.shape) == 2
    assert dum.param.l.shape[0].path == ".h"
    assert dum.param.l.shape[1].path == ".a"
    assert np.all(dum.get_shape_ref(dum.param.l) == (5, 10))

    # m
    assert len(dum.param.m.shape) == 3
    assert dum.param.m.shape[0].path == ".h"
    assert dum.param.m.shape[1].path == ".a"
    assert dum.param.m.shape[2] == 5
    assert np.all(dum.get_shape_ref(dum.param.m) == (5, 10, 5))

    # n
    out = dum.as_dict(onlychanged=False)
    assert "n" in out

    # Updating with scalar value
    dum.b = 5.0
    np.testing.assert_almost_equal(dum.b, np.full_like(dum.a, 5.0))

    # Dynamically updating shape
    dum.param.m.shape = (".a", ".h", 6)
    assert np.all(dum.get_shape_ref(dum.param.m) == (10, 5, 6))

    # repr_html
    for key, par in dum.param.objects().items():
        if key == "name":
            continue
        is_default = (not key in dum._param__private.values) or (
            dum._param__private.values[key] is None
        )
        par.repr_html(dum[key], is_default)

    arr = np.linspace(0, 1, 10)
    num_arr = AESOptArray(arr, bounds=(0, 1), units="m", shape=".x")

    assert num_arr.units == "m"
    assert num_arr.shape == ".x"

    with pytest.raises(ValueError, match="must be less than"):
        num_arr = AESOptArray(arr, bounds=(0, 1), inclusive_bounds=(True, False))

    with pytest.raises(ValueError, match="must be greater than"):
        num_arr = AESOptArray(arr, bounds=(0, 1), inclusive_bounds=(False, True))

    arr = np.linspace(0, 1.1, 10)
    with pytest.raises(ValueError, match="must be at most"):
        num_arr = AESOptArray(arr, bounds=(0, 1))

    arr = np.linspace(-0.1, 1.0, 10)
    with pytest.raises(ValueError, match="must be at least"):
        num_arr = AESOptArray(arr, bounds=(0, 1))

    with pytest.raises(ValueError, match="default_full must be a tuple"):
        num_arr = AESOptArray(arr, default_full=5)

    with pytest.raises(ValueError, match="shape as a tuple need to have item-types"):
        num_arr = AESOptArray(arr, default_full=((object(), "x"), 1))

    with pytest.raises(ValueError, match="default_full must be a tuple"):
        num_arr = AESOptArray(arr, default_full=("x", object()))

    with pytest.raises(ValueError, match="default_interp must be a tuple"):
        num_arr = AESOptArray(arr, default_interp=5)

    with pytest.raises(ValueError, match="default_interp must be a tuple"):
        num_arr = AESOptArray(arr, default_interp=(".a", ".b", 5))

    with pytest.raises(ValueError, match="Array dtype must be a subclass"):
        num_arr = AESOptArray(np.array(["1", "2"]))

    with pytest.raises(ValueError, match="Array dtype must be a subclass"):
        num_arr = AESOptArray(arr, dtype=int)

    with pytest.raises(ValueError, match="shape need to be of type tuple"):
        num_arr = AESOptArray(arr, shape=object())

    with pytest.raises(ValueError, match="value must be an instance of"):
        num_arr = AESOptArray(object())

    with pytest.raises(ValueError, match="units is not valid "):
        AESOptArray(units="XX")

    with pytest.raises(
        ValueError, match="Scaler values can only be assigned to AESOptArray "
    ):
        dum.a = 1.0

    AESOptArray(units="mm/kg**3*Pa")


def test_AESOptBoolean():
    class dummy(AESOptParameterized):
        x = AESOptBoolean(True)
        y = AESOptBoolean(default_ref=".x")
        z = AESOptBoolean(lambda self: not self.x)
        a = AESOptBoolean(".x")

    dum_ins = dummy()

    assert dum_ins.x is True
    assert dum_ins.y is True
    assert dum_ins.z is False
    assert dum_ins.a is True
    assert dum_ins.param.x.default is True
    assert dum_ins.param.y.default_ref == ".x"
    assert isinstance(dum_ins.param.z.default, Function)
    assert isinstance(dum_ins.param.a.default, Reference)
    assert dum_ins.param.a.default == ".x"

    dum_ins.a = lambda self: not self.x
    dum_ins.x = False
    assert dum_ins.a is True
    assert isinstance(dum_ins._param__private.values["a"], Function)

    dum_ins.a = "$function lambda self: not self.x"
    dum_ins.x = True
    assert dum_ins.a is False
    assert isinstance(dum_ins._param__private.values["a"], Function)

    with pytest.raises(ValueError):
        dum_ins.x = 1.0

    with pytest.raises(ValueError):
        dum_ins.x = 0

    with pytest.raises(ValueError):
        dum_ins.x = "str"


def test_Reference():
    # From path
    ref = Reference(".a")
    assert ref.path == ".a"
    assert ref == ".a"  # __eq__
    assert repr(ref) == ".a"
    assert str(ref) == "$ref .a"

    ref = Reference("$ref .a")
    assert ref.path == ".a"
    assert ref == ".a"  # __eq__
    assert repr(ref) == ".a"
    assert str(ref) == "$ref .a"

    with pytest.raises(ValueError, match="Object path need to start with `.`"):
        Reference("a")
    with pytest.raises(ValueError, match="Object path need to start with `.`"):
        Reference("$refa")
    with pytest.raises(ValueError, match="Object path need to start with `.`"):
        Reference("$ref  a")

    with pytest.raises(ValueError, match="Object path can not contain spaces or tabs"):
        Reference(".a.b c")
    with pytest.raises(ValueError, match="Object path can not contain spaces or tabs"):
        Reference("$ref .a.b c")


def test_Function():
    temp_fun = lambda self: self + 5
    fun1 = Function(temp_fun)
    assert str(fun1) == "$function lambda self: self + 5"
    assert repr(fun1).startswith("<$function id=")
    assert fun1.method(1) == 6

    def test_function(self):
        return self + 6

    fun2 = Function(test_function)
    assert str(fun2) == "$function def test_function(self):\n        return self + 6"
    assert repr(fun2).startswith("<$function id=")
    assert fun2.method(1) == 7

    fun3 = Function("$function lambda self: self + 7")
    assert str(fun3) == "$function lambda self: self + 7"
    assert repr(fun3).startswith("<$function id=")
    assert fun3.method(1) == 8

    fun4 = Function("$function def test_function(self):\n    return self + 8")
    assert str(fun4) == "$function def test_function(self):\n    return self + 8"
    assert repr(fun4).startswith("<$function id=")
    assert fun4.method(1) == 9

    with pytest.raises(ValueError, match="`method` need to be a `callable` or"):
        Function("lambda self: self + 7")

    with pytest.raises(ValueError, match="`method` need to be a `callable` or"):
        Function(5)
