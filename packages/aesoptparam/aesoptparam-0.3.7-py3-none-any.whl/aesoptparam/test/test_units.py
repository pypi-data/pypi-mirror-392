import os

import numpy as np
import pytest

from aesoptparam.utils.units import (
    NumberDict,
    PhysicalUnit,
    _find_unit,
    add_offset_unit,
    add_unit,
    convert_units,
    import_library,
    simplify_unit,
    unit_conversion,
)


def test_UnknownKeyGives0():
    # a NumberDict instance should initilize using integer and non-integer indices
    # a NumberDict instance should initilize all entries with an initial
    # value of 0
    x = NumberDict()

    # integer test
    assert x[0] == 0

    # string test
    assert x["t"] == 0


def test__add__KnownValues():
    # __add__ should give known result with known input
    # for non-string data types, addition must be commutative

    x = NumberDict()
    y = NumberDict()
    x["t1"], x["t2"] = 1, 2
    y["t1"], y["t2"] = 2, 1

    result1, result2 = x + y, y + x
    assert np.all((3, 3) == (result1["t1"], result1["t2"]))
    assert np.all((3, 3) == (result2["t1"], result2["t2"]))


def test__sub__KnownValues():
    # __sub__ should give known result with known input
    # commuting the input should result in equal magnitude, opposite sign

    x = NumberDict()
    y = NumberDict()
    x["t1"], x["t2"] = 1, 2
    y["t1"], y["t2"] = 2, 1

    result1, result2 = x - y, y - x
    assert np.all((-1, 1) == (result1["t1"], result1["t2"]))
    assert np.all((1, -1) == (result2["t1"], result2["t2"]))


def test__mul__KnownValues():
    # __mul__ should give known result with known input

    x = NumberDict([("t1", 1), ("t2", 2)])
    y = 10

    result1, result2 = x * y, y * x
    assert np.all((10, 20) == (result1["t1"], result1["t2"]))
    assert np.all((10, 20) == (result2["t1"], result2["t2"]))


def test__div__KnownValues():
    # __div__ should give known result with known input

    x = NumberDict()
    x = NumberDict([("t1", 1), ("t2", 2)])
    y = 10.0
    result1 = x / y
    assert np.all((0.1, 0.20) == (result1["t1"], result1["t2"]))


with open(
    os.path.join(os.path.dirname(__file__), "../utils/unit_library.ini")
) as default_lib:
    _unitLib = import_library(default_lib)


def _get_powers(**powdict):
    powers = [0] * len(_unitLib.base_types)
    for name, power in powdict.items():
        powers[_unitLib.base_types[name]] = power
    return powers


def test_repr_str():
    # __repr__should return a string which could be used to contruct the
    # unit instance, __str__ should return a string with just the unit
    # name for str

    u = _find_unit("d")

    assert repr(u) == "PhysicalUnit({'d': 1},86400.0,%s,0.0)" % _get_powers(time=1)
    assert str(u) == "<PhysicalUnit d>"


def test_cmp():
    # should error for incompatible units, if they are compatible then it
    # should cmp on their factors

    x = _find_unit("d")
    y = _find_unit("s")
    z = _find_unit("ft")

    assert x > y
    assert x == x
    assert y < x

    with pytest.raises(TypeError, match="Units 'd' and 'ft' are incompatible."):
        x < z


known__mul__Values = (
    ("1m", "5m", 5),
    ("1cm", "1cm", 1),
    ("1cm", "5m", 5),
    ("7km", "1m", 7),
)


def test_multiply():
    # multiplication should error for units with offsets

    x = _find_unit("g")
    y = _find_unit("s")
    z = _find_unit("degC")

    assert x * y == PhysicalUnit(
        {"s": 1, "kg": 1}, 0.001, _get_powers(mass=1, time=1), 0
    )
    assert y * x == PhysicalUnit(
        {"s": 1, "kg": 1}, 0.001, _get_powers(mass=1, time=1), 0
    )

    with pytest.raises(
        TypeError,
        match="Can't multiply units: either 'g' or 'degC' has a non-zero offset.",
    ):
        x * z


def test_division():
    # division should error when working with offset units

    w = _find_unit("kg")
    x = _find_unit("g")
    y = _find_unit("s")
    z = _find_unit("degC")

    quo = w / x
    quo2 = x / y

    assert np.all(quo == PhysicalUnit({"kg": 1, "g": -1}, 1000.0, _get_powers(), 0))
    assert np.all(
        quo2 == PhysicalUnit({"s": -1, "g": 1}, 0.001, _get_powers(mass=1, time=-1), 0),
    )
    quo = y / 2.0
    assert np.all(quo == PhysicalUnit({"s": 1, "2.0": -1}, 0.5, _get_powers(time=1), 0))
    quo = 2.0 / y
    assert np.all(quo == PhysicalUnit({"s": -1, "2.0": 1}, 2, _get_powers(time=-1), 0))
    with pytest.raises(
        TypeError,
        match="Can't divide units: either 'g' or 'degC' has a non-zero offset.",
    ):
        x / z


known__pow__Values = (("1V", 3), ("1m", 2), ("1.1m", 2))


def test_pow():
    # power should error for offest units and for non-integer powers

    x = _find_unit("m")
    y = _find_unit("degF")

    z = x**3
    assert np.all(z == _find_unit("m**3"))
    x = z ** (1.0 / 3.0)  # checks inverse integer units
    assert np.all(x == _find_unit("m"))
    z = 5.2 * x**2  # Test with value
    x = z ** (1.0 / 2.0)
    assert np.all(x == (np.sqrt(5.2) * _find_unit("m")))
    x = _find_unit("m")

    # test offset units:
    with pytest.raises(
        TypeError,
        match="Can't exponentiate unit 'degF' because it has a non-zero offset.",
    ):
        y**17

    # test non-integer powers
    with pytest.raises(
        TypeError,
        match="Can't exponentiate unit 'm': only integer and inverse integer exponents are allowed.",
    ):
        x**1.2

    with pytest.raises(
        TypeError,
        match="Can't exponentiate unit 'm': only integer and inverse integer exponents are allowed.",
    ):
        x ** (5.0 / 2.0)


def test_compare():
    x = _find_unit("m")
    y = _find_unit("degF")

    with pytest.raises(TypeError, match="Units 'm' and 'degF' are incompatible."):
        x > y


known__conversion_factor_to__Values = (
    ("1m", "1cm", 100),
    ("1s", "1ms", 1000),
    ("1ms", "1s", 0.001),
)


def test_conversion_tuple_to():
    # test_conversion_tuple_to shoudl error when units have different power
    # lists

    w = _find_unit("cm")
    x = _find_unit("m")
    y = _find_unit("degF")
    z1 = _find_unit("degC")

    # check for non offset units
    assert np.all(w.conversion_tuple_to(x) == (1 / 100.0, 0))

    # check for offset units
    result = y.conversion_tuple_to(z1)
    np.testing.assert_almost_equal(result[0], 0.556, 3)
    np.testing.assert_almost_equal(result[1], -32.0, 3)
    np.testing.assert_almost_equal

    # check for incompatible units
    with pytest.raises(
        TypeError,
        match="Units 'm' and 'degC' are incompatible.",
    ):
        x.conversion_tuple_to(z1)


def test_name():
    # name should return a mathematically correct representation of the
    # unit
    x1 = _find_unit("m")
    x2 = _find_unit("kg")
    y = 1 / x1
    assert np.all(y.name() == "1/m")
    y = 1 / x1 / x1
    assert np.all(y.name() == "1/m**2")
    y = x1**2
    assert np.all(y.name() == "m**2")
    y = x2 / (x1**2)
    assert np.all(y.name() == "kg/m**2")


def test_unit_conversion():
    assert np.all(unit_conversion("km", "m") == (1000.0, 0.0))

    with pytest.raises(
        ValueError,
        match="The units '1.0' are invalid.",
    ):
        unit_conversion("km", 1.0)


def test_unit_simplification():
    test_strings = [
        "ft/s*s",
        "m/s*s",
        "m * ft * cm / km / m",
        "s/s",
        "m ** 7 / m ** 5",
    ]

    correct_strings = ["ft", "m", "ft*cm/km", None, "m**2"]

    for test_str, correct_str in zip(test_strings, correct_strings):
        simplified_str = simplify_unit(test_str)
        assert np.all(simplified_str == correct_str)


def test_atto_seconds():
    # The unit 'as' was bugged because it is a python keyword.

    fact = unit_conversion("s", "as")
    assert abs(fact[0] - 1e18) / 1e18 < 1e-15

    # Make sure regex for 'as' doesn't pick up partial words.
    fact = unit_conversion("aslug*as*as", "aslug*zs*zs")
    assert abs(fact[0] - 1e6) / 1e6 < 1e-15

    # Make sure simplification works.
    simple = simplify_unit("m*as/as")
    assert np.all(simple == "m")

    simple = simplify_unit("as**6/as**4")
    assert np.all(simple == "as**2")


def test_add_unit():
    with pytest.raises(
        KeyError,
        match="Unit 'ft' already defined with different factor or powers.",
    ):
        add_unit("ft", "20*m")

    with pytest.raises(
        KeyError,
        match="Unit 'degR' already defined with different factor or powers.",
    ):
        add_offset_unit("degR", "degK", 20, 10)


def test_various():
    # Test .in_base_units
    x = _find_unit("kg*Pa")
    assert x.in_base_units() == _find_unit("kg**2/(m*s**2)")
    x = _find_unit("m**-1")
    assert x.in_base_units() == _find_unit("1/m")

    # .is_dimensionless
    x = _find_unit("Pa")
    assert not x.is_dimensionless()
    assert (x / _find_unit("N/m**2")).is_dimensionless()

    # .is_angle
    assert not x.is_angle()
    x = _find_unit("rad")
    assert x.is_angle()
    x = _find_unit("rad/s")
    assert not x.is_angle()

    # Double letter unit prefix
    x = _find_unit("dam")
    assert x == 10 * _find_unit("m")

    # Invalid prefix
    units = "xxm"
    with pytest.raises(ValueError, match=f"The units '{units}' are invalid."):
        x = _find_unit(units, True)
    # Should not fail without flag
    x = _find_unit(units)

    # convert_unit
    ounits = "Pa"
    val = 4 * _find_unit(ounits)
    nunits = "hPa"
    # Return current val
    nval = convert_units(val, None)
    assert nval == val

    # simplify_units
    out = simplify_unit(None)
    assert out is None
