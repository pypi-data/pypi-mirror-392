import json
import os

import numpy as np
import pytest
from jsonschema import validate
from jsonschema.validators import Draft7Validator
from param.serializer import UnserializableException

from aesoptparam import (
    AESOptNumber,
    AESOptParameterized,
    Callable,
    ClassSelector,
    ListSelector,
    copy_param,
    copy_param_ref,
)
from aesoptparam.example import main as main_example
from aesoptparam.parameters import Function, Reference

file_path = os.path.dirname(__file__)


def test_AESOptParameterized():
    dummy_parent = object()

    class dummy(AESOptParameterized):
        pass

    dum_ins = dummy(dummy_parent)
    assert isinstance(dum_ins.parent_object, object)
    assert dum_ins.parent_object is dummy_parent

    default_array = np.linspace(0, 10, 10)
    main_ins = main_example(
        xx="dummy"
    )  # Inputs which is not a parameters should be skipped
    assert not hasattr(main_ins, "xx")
    main_ins.add_sub_list()

    # as_dict with only default
    main_ins.sub1  # To insure that one sub param is initialized
    out = main_ins.as_dict()
    assert len(out) == 1

    out_all = main_ins.as_dict(False)

    # Main
    assert len(out_all) == 15
    assert main_ins.a == 4.0
    assert main_ins.b == 5.0
    assert main_ins.param.b.default_ref == ".sub1.a"
    assert main_ins.c == 6.0
    assert main_ins.param.c.default_ref == ".sub_list[0].a"
    np.testing.assert_almost_equal(main_ins.d, default_array)
    assert main_ins.param.d.default_ref == ".sub1.b"
    assert main_ins.f == "Dummy"
    assert main_ins.g == "Dummy"
    assert main_ins.h == "Dummy2"

    # Sub1
    assert len(out_all["sub1"]) == 10
    assert main_ins.sub1.a == 5.0
    np.testing.assert_almost_equal(main_ins.sub1.b, default_array)
    np.testing.assert_almost_equal(main_ins.sub1.c, main_ins.sub1.b)
    assert main_ins.sub1.param.c.default_ref == ".b"
    np.testing.assert_almost_equal(
        main_ins.sub1.e, np.full_like(default_array, main_ins.sub1.a)
    )
    assert isinstance(main_ins.sub1.param.e.default, Function)
    np.testing.assert_almost_equal(main_ins.sub1.f, main_ins.sub1.e)
    assert main_ins.sub1.param.f.default_full == (".b", ".a")
    assert main_ins.sub1.g.shape == (10,)
    np.testing.assert_almost_equal(main_ins.sub1.g, 6.0)
    assert main_ins.sub1.param.g.default_full == (".b", 6.0)
    np.testing.assert_almost_equal(
        main_ins.sub1.h, main_ins.sub1.param.h.default_interp[0]
    )
    assert main_ins.sub1.param.h.default_interp[1:] == (".b", ".c")
    assert main_ins.sub1.i == "sub1.Dummy"
    assert main_ins.sub1.j == "sub1.Dummy"
    assert main_ins.sub1.k == "sub1.Dummy2"
    # Sub2
    assert len(out_all["sub2"]) == 8
    assert main_ins.sub2.a == main_ins.sub1.a
    assert main_ins.sub2.b == main_ins.a
    assert main_ins.sub2.c == main_ins.sub_list[0].a
    np.testing.assert_almost_equal(main_ins.sub2.d, main_ins.sub1.b)
    np.testing.assert_almost_equal(main_ins.sub2.e, main_ins.sub1.b + 1)
    assert main_ins.sub2.f == main_ins.f
    assert main_ins.sub2.g == main_ins.sub1.i
    assert main_ins.sub2.h == main_ins.sub_list[0].f
    # Sub_list
    assert len(out_all["sub_list"]) == 1
    assert len(out_all["sub_list"][0]) == 7
    assert main_ins.sub_list[0].a == 6.0
    assert main_ins.sub_list[0].b == main_ins.a
    assert main_ins.sub_list[0].c == main_ins.sub1.a
    np.testing.assert_almost_equal(main_ins.sub_list[0].d, main_ins.d)
    np.testing.assert_almost_equal(main_ins.sub_list[0].e, main_ins.sub1.b)
    assert main_ins.sub_list[0].f == main_ins.f
    assert main_ins.sub_list[0].g == main_ins.sub1.i
    # Sub_list2
    assert len(out_all["sub_list2"]) == 1
    assert len(out_all["sub_list2"][0]) == 7
    assert main_ins.sub_list2[0].a == 6.0
    assert main_ins.sub_list2[0].b == main_ins.a
    assert main_ins.sub_list2[0].c == main_ins.sub1.a
    np.testing.assert_almost_equal(main_ins.sub_list2[0].d, main_ins.d)
    np.testing.assert_almost_equal(main_ins.sub_list2[0].e, main_ins.sub1.b)
    assert main_ins.sub_list2[0].f == main_ins.f
    assert main_ins.sub_list2[0].g == main_ins.sub1.i

    # Validating array shapes
    main_ins.name = "main"
    main_ins.validate_array_shapes()
    new_array = default_array[:-1]
    main_ins.d = new_array
    with pytest.raises(ValueError, match=r"For main the shape of d"):
        main_ins.validate_array_shapes()
    main_ins.d = default_array
    main_ins.validate_array_shapes()
    main_ins.sub1.c = new_array
    with pytest.raises(ValueError, match=r"For main.sub1_class[\d]+ the shape of c"):
        main_ins.validate_array_shapes()
    main_ins.sub1.c = default_array
    main_ins.validate_array_shapes()
    main_ins.sub2.d = new_array
    with pytest.raises(ValueError, match=r"For main.sub2_class[\d]+ the shape of d"):
        main_ins.validate_array_shapes()
    main_ins.sub2.d = default_array
    main_ins.validate_array_shapes()
    main_ins.sub_list[0].d = new_array
    with pytest.raises(
        ValueError, match=r"For main.sub_list_class[\d]+ the shape of d"
    ):
        main_ins.validate_array_shapes()
    main_ins.sub_list[0].d = default_array
    main_ins.validate_array_shapes()

    # get/set units
    np.testing.assert_almost_equal(
        main_ins.get_val("a", "rpm"), main_ins.a * 30 / np.pi
    )
    np.testing.assert_almost_equal(main_ins.get_val("b", "mm/s"), main_ins.b * 1e3)
    np.testing.assert_almost_equal(main_ins.get_val("d", "m/s"), main_ins.d * 1e-3)
    main_ins.set_val("a", 1, "rpm")
    np.testing.assert_almost_equal(main_ins.a, np.pi / 30)
    main_ins.set_val("b", 1, "mm/s")
    np.testing.assert_almost_equal(main_ins.b, 1e-3)
    main_ins.set_val("d", np.ones(5) * 1e-2, "m/s")
    np.testing.assert_almost_equal(main_ins.d, 1e1)

    # has_parent
    assert main_ins.has_parent() is False
    assert main_ins.sub1.has_parent() is True

    # Raises
    with pytest.raises(TypeError, match="Units"):
        main_ins.get_val("a", "kg")
    with pytest.raises(TypeError, match="Units"):
        main_ins.set_val("a", 1, "kg")

    with pytest.raises(RuntimeError, match="parameter with name"):
        main_ins.get_val("sub1")
    with pytest.raises(RuntimeError, match="parameter with name"):
        main_ins.set_val("sub1", 5)

    with pytest.raises(TypeError, match="attribute name must be string, not 'tuple'"):
        main_ins[(0, 0)]

    with pytest.raises(TypeError, match="attribute name must be string, not 'tuple'"):
        main_ins[(0, 0)] = 5

    with pytest.raises(ValueError, match="Indices need to integers:"):
        main_ins[".d[XX]"]

    # Testing that it runs
    main_ins.i = dict(
        a=0.2, b=[0.1, 0.2], c=np.array([0.2, 0.3]), d=dict(a=0.1, b=dict(a=0.1))
    )
    main_ins._repr_html_()


def test_AESOptParameterized_json(tmp_path):
    # Tests .read_json, .from_dict, .as_serial, .as_dict
    dum = main_example()

    # %% .read_json and .from_dict
    dum.read_json(os.path.join(file_path, "dummy_instance.json"))
    # main
    assert dum.a == 0.2
    assert dum.b == 0.2
    assert (
        isinstance(dum._param__private.values["b"], Reference)
        and dum._param__private.values["b"] == ".a"
    )
    assert dum.c == 0.3
    assert (
        isinstance(dum._param__private.values["c"], Reference)
        and dum._param__private.values["c"] == ".sub_list[1].a"
    )
    np.testing.assert_almost_equal(dum.d, [0.0, 1.0, 2.0, 3.2])
    assert isinstance(dum.d, np.ndarray)
    assert np.issubdtype(dum.d.dtype, np.number)
    np.testing.assert_almost_equal(dum.e, [1, 2, 10])
    assert isinstance(dum.e, np.ndarray)
    assert np.issubdtype(dum.e.dtype, int)
    assert dum.name == "New main name"
    assert dum.f == "Test"
    assert dum.g == "Test3"
    assert (
        isinstance(dum._param__private.values["g"], Reference)
        and dum._param__private.values["g"] == ".h"
    )
    assert dum.h == "Test3"
    assert isinstance(dum._param__private.values["h"], Function)

    # main.sub1
    assert dum.sub1.a == 0.1
    np.testing.assert_almost_equal(dum.sub1.b, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    assert isinstance(dum.sub1.b, np.ndarray)
    assert np.issubdtype(dum.sub1.b.dtype, np.number)
    np.testing.assert_almost_equal(dum.sub1.c, dum.sub1.b)
    assert (
        isinstance(dum.sub1._param__private.values["c"], Reference)
        and dum.sub1._param__private.values["c"] == ".b"
    )
    np.testing.assert_almost_equal(dum.sub1.e, np.full_like(dum.sub1.b, dum.a))
    assert isinstance(dum.sub1.e, np.ndarray)
    assert np.issubdtype(dum.sub1.e.dtype, np.number)
    assert isinstance(dum.sub1._param__private.values["e"], Function)
    np.testing.assert_almost_equal(dum.sub1.f, [0, 1, 2, 3, 4])
    assert isinstance(dum.sub1._param__private.values["f"], np.ndarray)
    assert np.issubdtype(dum.sub1._param__private.values["f"].dtype, np.number)

    # main.sub2
    assert dum.sub2.a == 0.3

    # main.sub_list
    assert len(dum.sub_list) == 2
    assert dum.sub_list[0].a == 0.1
    assert dum.sub_list[1].a == 0.3

    with pytest.raises(
        ValueError, match="A parameter with readonly has a different value"
    ):
        dum.from_dict({"version": "0.0.1"})

    # %% .as_dict(onlychanged=True, as_refs=True, as_funcs=True)
    dict_rep = dum.as_dict(onlychanged=True, as_refs=True, as_funcs=True)
    # main
    assert isinstance(dict_rep, dict)
    assert len(dict_rep) == 13
    assert dict_rep["a"] == 0.2
    assert dict_rep["b"] == ".a"
    assert isinstance(dict_rep["b"], Reference)
    assert dict_rep["c"] == ".sub_list[1].a"
    assert isinstance(dict_rep["c"], Reference)
    np.testing.assert_almost_equal(dict_rep["d"], [0.0, 1.0, 2.0, 3.2])
    assert isinstance(dict_rep["d"], np.ndarray)
    assert np.issubdtype(dict_rep["d"].dtype, np.number)
    np.testing.assert_almost_equal(dict_rep["e"], [1, 2, 10])
    assert isinstance(dict_rep["e"], np.ndarray)
    assert np.issubdtype(dict_rep["e"].dtype, int)
    assert dict_rep["name"] == "New main name"

    # main.sub1
    assert isinstance(dict_rep["sub1"], dict)
    assert len(dict_rep["sub1"]) == 5
    assert dict_rep["sub1"]["a"] == 0.1
    np.testing.assert_almost_equal(
        dict_rep["sub1"]["b"], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )
    assert isinstance(dict_rep["sub1"]["b"], np.ndarray)
    assert np.issubdtype(dict_rep["sub1"]["b"].dtype, np.number)
    assert dict_rep["sub1"]["c"] == ".b"
    assert isinstance(dict_rep["sub1"]["c"], Reference)
    assert isinstance(dict_rep["sub1"]["e"], Function)
    np.testing.assert_almost_equal(dict_rep["sub1"]["f"], [0, 1, 2, 3, 4])
    assert isinstance(dict_rep["sub1"]["f"], np.ndarray)
    assert np.issubdtype(dict_rep["sub1"]["f"].dtype, np.number)

    # main.sub2
    assert isinstance(dict_rep["sub2"], dict)
    assert len(dict_rep["sub2"]) == 1
    assert dict_rep["sub2"]["a"] == 0.3

    # main.sub_list
    assert isinstance(dict_rep["sub_list"], list)
    assert len(dict_rep["sub_list"]) == 2
    assert isinstance(dict_rep["sub_list"][0], dict)
    assert len(dict_rep["sub_list"][0]) == 1
    assert dict_rep["sub_list"][0]["a"] == 0.1
    assert isinstance(dict_rep["sub_list"][1], dict)
    assert len(dict_rep["sub_list"][1]) == 1
    assert dict_rep["sub_list"][1]["a"] == 0.3

    # %% .as_dict(onlychanged=False, as_refs=False, as_funcs=False)
    dict_rep = dum.as_dict(onlychanged=False, as_refs=False, as_funcs=False)
    # main
    assert isinstance(dict_rep, dict)
    assert len(dict_rep) == 15
    assert dict_rep["a"] == 0.2
    assert dict_rep["b"] == dict_rep["a"]
    assert dict_rep["c"] == dict_rep["sub_list"][1]["a"]
    np.testing.assert_almost_equal(dict_rep["d"], [0.0, 1.0, 2.0, 3.2])
    assert isinstance(dict_rep["d"], np.ndarray)
    assert np.issubdtype(dict_rep["d"].dtype, np.number)
    np.testing.assert_almost_equal(dict_rep["e"], [1, 2, 10])
    assert isinstance(dict_rep["e"], np.ndarray)
    assert np.issubdtype(dict_rep["e"].dtype, int)
    assert dict_rep["name"] == "New main name"
    assert dict_rep["version"] == "0.0.0"

    # main.sub1
    assert isinstance(dict_rep["sub1"], dict)
    assert len(dict_rep["sub1"]) == 10
    assert dict_rep["sub1"]["a"] == 0.1
    np.testing.assert_almost_equal(
        dict_rep["sub1"]["b"], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )
    assert isinstance(dict_rep["sub1"]["b"], np.ndarray)
    assert np.issubdtype(dict_rep["sub1"]["b"].dtype, np.number)
    np.testing.assert_almost_equal(dict_rep["sub1"]["c"], dict_rep["sub1"]["b"])
    np.testing.assert_almost_equal(
        dict_rep["sub1"]["e"], np.full_like(dict_rep["sub1"]["b"], dict_rep["a"])
    )
    np.testing.assert_almost_equal(dict_rep["sub1"]["f"], [0, 1, 2, 3, 4])
    assert isinstance(dict_rep["sub1"]["f"], np.ndarray)
    assert np.issubdtype(dict_rep["sub1"]["f"].dtype, np.number)
    np.testing.assert_almost_equal(
        dict_rep["sub1"]["g"], np.full_like(dict_rep["sub1"]["b"], 6.0)
    )
    np.testing.assert_almost_equal(dict_rep["sub1"]["h"], np.linspace(0, 10, 5))

    # main.sub2
    assert isinstance(dict_rep["sub2"], dict)
    assert len(dict_rep["sub2"]) == 8
    assert dict_rep["sub2"]["a"] == 0.3
    assert dict_rep["sub2"]["b"] == dict_rep["a"]
    assert dict_rep["sub2"]["c"] == dict_rep["sub_list"][0]["a"]
    np.testing.assert_almost_equal(dict_rep["sub2"]["d"], dict_rep["sub1"]["b"])
    np.testing.assert_almost_equal(dict_rep["sub2"]["e"], dict_rep["sub1"]["b"] + 1)

    # main.sub_list
    assert isinstance(dict_rep["sub_list"], list)
    assert len(dict_rep["sub_list"]) == 2
    for iel, el in enumerate(dict_rep["sub_list"]):
        assert isinstance(el, dict)
        assert len(el) == 7
        a_val = 0.1 if iel == 0 else 0.3
        assert el["a"] == a_val
        assert el["b"] == dict_rep["a"]
        assert el["c"] == dict_rep["sub1"]["a"]
        np.testing.assert_almost_equal(el["d"], dict_rep["d"])
        np.testing.assert_almost_equal(el["e"], dict_rep["sub1"]["b"])

    # %% .as_serial(onlychanged=True, as_refs=True, as_funcs=True)
    json_rep = dum.as_serial(onlychanged=True, as_refs=True, as_funcs=True)
    # main
    assert isinstance(json_rep, dict)
    assert len(json_rep) == 13
    assert json_rep["a"] == 0.2
    assert json_rep["b"] == "$ref .a"
    assert json_rep["c"] == "$ref .sub_list[1].a"
    np.testing.assert_almost_equal(json_rep["d"], [0.0, 1.0, 2.0, 3.2])
    assert isinstance(json_rep["d"], list)
    np.testing.assert_almost_equal(json_rep["e"], [1, 2, 10])
    assert isinstance(json_rep["e"], list)
    assert json_rep["name"] == "New main name"

    # main.sub1
    assert isinstance(json_rep["sub1"], dict)
    assert len(json_rep["sub1"]) == 5
    assert json_rep["sub1"]["a"] == 0.1
    np.testing.assert_almost_equal(
        json_rep["sub1"]["b"], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )
    assert isinstance(json_rep["sub1"]["b"], list)
    assert json_rep["sub1"]["c"] == "$ref .b"
    assert (
        json_rep["sub1"]["e"]
        == "$function lambda self: np.full_like(self.b, self['..a'])"
    )
    np.testing.assert_almost_equal(json_rep["sub1"]["f"], [0, 1, 2, 3, 4])
    assert isinstance(json_rep["sub1"]["f"], list)

    # main.sub2
    assert isinstance(json_rep["sub2"], dict)
    assert len(json_rep["sub2"]) == 1
    assert json_rep["sub2"]["a"] == 0.3

    # main.sub_list
    assert isinstance(json_rep["sub_list"], list)
    assert len(json_rep["sub_list"]) == 2
    assert isinstance(json_rep["sub_list"][0], dict)
    assert json_rep["sub_list"][0]["a"] == 0.1
    assert isinstance(json_rep["sub_list"][1], dict)
    assert json_rep["sub_list"][1]["a"] == 0.3

    # main.sub_list2
    assert isinstance(json_rep["sub_list2"], list)
    assert len(json_rep["sub_list2"]) == 1
    assert isinstance(json_rep["sub_list2"][0], dict)
    assert isinstance(json_rep["sub_list2"][0], dict)
    assert json_rep["sub_list2"][0]["a"] == 0.1

    # JSON data
    with open(os.path.join(file_path, "dummy_instance.json"), "r") as file:
        json_data = json.load(file)
    json_data.pop("version")
    json_data.pop("$schema")
    assert json_rep == json_data
    assert json.loads(dum.as_json(onlychanged=True)) == json_rep

    # %% .as_serial(onlychanged=False, as_refs=False, as_funcs=False)
    json_rep = dum.as_serial(onlychanged=False, as_refs=False, as_funcs=False)
    # main
    assert isinstance(json_rep, dict)
    assert len(json_rep) == 15
    assert json_rep["a"] == 0.2
    assert json_rep["b"] == json_rep["a"]
    assert json_rep["c"] == json_rep["sub_list"][1]["a"]
    np.testing.assert_almost_equal(json_rep["d"], [0.0, 1.0, 2.0, 3.2])
    assert isinstance(json_rep["d"], list)
    np.testing.assert_almost_equal(json_rep["e"], [1, 2, 10])
    assert isinstance(json_rep["e"], list)
    assert json_rep["name"] == "New main name"
    assert json_rep["version"] == "0.0.0"

    # main.sub1
    assert isinstance(json_rep["sub1"], dict)
    assert len(json_rep["sub1"]) == 10
    assert json_rep["sub1"]["a"] == 0.1
    np.testing.assert_almost_equal(
        json_rep["sub1"]["b"], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )
    assert isinstance(json_rep["sub1"]["b"], list)
    np.testing.assert_almost_equal(json_rep["sub1"]["c"], json_rep["sub1"]["b"])
    np.testing.assert_almost_equal(
        json_rep["sub1"]["e"], np.full_like(json_rep["sub1"]["b"], json_rep["a"])
    )
    assert isinstance(json_rep["sub1"]["e"], list)
    np.testing.assert_almost_equal(json_rep["sub1"]["f"], [0, 1, 2, 3, 4])
    assert isinstance(json_rep["sub1"]["f"], list)
    np.testing.assert_almost_equal(
        json_rep["sub1"]["g"], np.full_like(json_rep["sub1"]["b"], 6.0)
    )
    assert isinstance(json_rep["sub1"]["g"], list)
    np.testing.assert_almost_equal(json_rep["sub1"]["h"], np.linspace(0, 10, 5))
    assert isinstance(json_rep["sub1"]["h"], list)

    # main.sub2
    assert isinstance(json_rep["sub2"], dict)
    assert len(json_rep["sub2"]) == 8
    assert json_rep["sub2"]["a"] == 0.3
    assert json_rep["sub2"]["b"] == json_rep["a"]
    assert json_rep["sub2"]["c"] == json_rep["sub_list"][0]["a"]
    np.testing.assert_almost_equal(json_rep["sub2"]["d"], json_rep["sub1"]["b"])
    np.testing.assert_almost_equal(
        json_rep["sub2"]["e"], [el + 1 for el in json_rep["sub1"]["b"]]
    )

    # main.sub_list
    assert isinstance(json_rep["sub_list"], list)
    assert len(json_rep["sub_list"]) == 2
    for iel, el in enumerate(json_rep["sub_list"]):
        assert isinstance(el, dict)
        assert len(el) == 7
        a_val = 0.1 if iel == 0 else 0.3
        assert el["a"] == a_val
        assert el["b"] == json_rep["a"]
        assert el["c"] == json_rep["sub1"]["a"]
        np.testing.assert_almost_equal(el["d"], json_rep["d"])
        assert isinstance(el["d"], list)
        np.testing.assert_almost_equal(el["e"], json_rep["sub1"]["b"])
        assert isinstance(el["e"], list)

    # Round trip json conversion
    dum.write_json(os.path.join(tmp_path, "temp.json"), False)
    dum2 = main_example().read_json(os.path.join(tmp_path, "temp.json"))
    assert dum.as_serial(onlychanged=False) == dum2.as_serial(onlychanged=False)
    # %% Test function setting
    dum.sub1.e = lambda self: np.full_like(self.b, self["..a"])
    json_rep = dum.as_serial(onlychanged=True, as_refs=True, as_funcs=True)
    assert (
        json_rep["sub1"]["e"]
        == '$function lambda self: np.full_like(self.b, self["..a"])'
    )

    def test_function(self):
        return np.full_like(self.b, self["..a"] + 1)

    dum.sub1.e = test_function
    json_rep = dum.as_serial(onlychanged=True, as_refs=True, as_funcs=True)
    assert (
        json_rep["sub1"]["e"]
        == '$function def test_function(self):\n        return np.full_like(self.b, self["..a"] + 1)'
    )


def test_AESOptParameterized_schema(tmp_path):
    dum = main_example().read_json(os.path.join(file_path, "dummy_instance.json"))

    # Write schema to file
    temp_schema = os.path.join(tmp_path, "dummy_schema.json")
    dum.write_json_schema(temp_schema)
    # Serialize default
    # Get schemas
    with open(temp_schema, "r") as file:
        schema_temp = json.load(file)
    with open(os.path.join(file_path, "dummy_schema.json"), "r") as file:
        schema = json.load(file)
    assert schema == schema_temp
    # Validate schema is Draft 7 valid
    Draft7Validator.check_schema(schema)
    # Check that it is a valid schema
    validate(instance=dum.as_serial(), schema=schema)

    # Check subset
    json_schema = dum.as_json_schema(subset=["a"])
    assert len(json_schema["properties"]) == 1
    assert "a" in json_schema["properties"]

    # Add a listselector to use default schema writer
    dum.param.add_parameter(
        "dummy_listselector", ListSelector(["one"], objects=["one", "two", "three"])
    )
    # Add empty class selector
    dum.param.add_parameter("dummy_classselector_empty", ClassSelector(class_=object))
    # Add class selector with multiple
    dum.param.add_parameter(
        "dummy_classselector_multi", ClassSelector(class_=(list, tuple))
    )
    # Add class selector with float
    dum.param.add_parameter(
        "dummy_classselector_float", ClassSelector(class_=float, allow_None=False)
    )
    json_schema = dum.as_json_schema()
    assert "enum" in json_schema["properties"]["dummy_listselector"]["items"]
    assert len(json_schema["properties"]["dummy_classselector_empty"]) == 1
    assert "anyOf" in json_schema["properties"]["dummy_classselector_multi"]
    assert (
        json_schema["properties"]["dummy_classselector_float"]["anyOf"][0]["type"]
        == "number"
    )

    # Fail with param.Callable
    dum.param.add_parameter("dummy_call", Callable())
    with pytest.raises(UnserializableException):
        dum.as_json_schema()


def test_copy_param():
    default = 0.5
    doc = "test"
    p = AESOptNumber(default, doc=doc, per_instance=False)
    p2 = copy_param(p)
    assert p2.default == default
    assert p2.doc == doc
    assert p2.per_instance is False

    p3 = copy_param_ref(p, ".p")
    assert p3.default is None
    assert p3.default_ref == ".p"
    assert p3.doc == doc
    assert p3.per_instance is False


if __name__ == "__main__":
    dum = main_example()
    dum.write_json_schema(os.path.join(file_path, "dummy_schema.json"), indent=4)
