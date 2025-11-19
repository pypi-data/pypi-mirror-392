import os

import numpy as np
import pytest

from aesoptparam.utils.html_repr import json_data_render
from aesoptparam.utils.json_utils import is_valid_json, read_json, write_json

file_path = os.path.dirname(__file__)


def test_read_json():
    data = read_json(os.path.join(file_path, "dummy_instance.json"))

    assert isinstance(data, dict)
    assert len(data) == 15
    assert data["version"] == "0.0.0"
    assert isinstance(data["d"], np.ndarray)
    assert isinstance(data["e"], np.ndarray)
    assert isinstance(data["sub1"], dict)
    assert len(data["sub1"]) == 5
    assert isinstance(data["sub1"]["b"], np.ndarray)

    data = read_json(os.path.join(file_path, "dummy_instance.json"), False)

    assert isinstance(data, dict)
    assert len(data) == 15
    assert data["version"] == "0.0.0"
    assert isinstance(data["d"], list)
    assert isinstance(data["e"], list)
    assert isinstance(data["sub1"], dict)
    assert len(data["sub1"]) == 5
    assert isinstance(data["sub1"]["b"], list)


def test_write_json(tmp_path):
    # Input data
    data = dict(
        a="a",
        b=np.int16(2),
        c=np.float16(5.1),
        d=np.array([0, 2.0, 3.1]),
        e=dict(a="a", b=2, c=5.1, d=np.array([0, 2.0, 3.1])),
        f=[
            dict(a="a", b=2, c=5.1, d=np.array([0, 2.0, 3.1])),
            dict(a="a", b=2, c=5.1, d=np.array([0, 2.0, 3.1])),
        ],
        g=np.bool_(True),
    )
    filename = os.path.join(tmp_path, "dummy.json")

    # Write data file
    write_json(filename, data)

    # Read data back in
    _data = read_json(filename)
    assert isinstance(_data["a"], str)
    assert isinstance(_data["b"], int)
    assert isinstance(_data["c"], float)
    assert isinstance(_data["d"], np.ndarray)
    assert isinstance(_data["e"]["a"], str)
    assert isinstance(_data["e"]["b"], int)
    assert isinstance(_data["e"]["c"], float)
    assert isinstance(_data["e"]["d"], np.ndarray)
    assert isinstance(_data["f"][0]["a"], str)
    assert isinstance(_data["f"][0]["b"], int)
    assert isinstance(_data["f"][0]["c"], float)
    assert isinstance(_data["f"][0]["d"], np.ndarray)
    assert isinstance(_data["f"][1]["a"], str)
    assert isinstance(_data["f"][1]["b"], int)
    assert isinstance(_data["f"][1]["c"], float)
    assert isinstance(_data["f"][1]["d"], np.ndarray)

    _data = read_json(filename, False)

    # Raise if not converting numpy
    with pytest.raises(TypeError, match="is not JSON serializable"):
        write_json(filename, data, False)

    # Raise if not converting numpy
    with pytest.raises(TypeError, match="is not JSON serializable"):
        write_json(filename, object())

    # Write data file
    write_json(filename, _data, False)


def test_is_valid_json():
    data = dict(
        a="a",
        b=2,
        c=5.1,
        d=np.array([0, 2.0, 3.1]),
        e=dict(a="a", b=2, c=5.1, d=np.array([0, 2.0, 3.1])),
        f=[
            dict(a="a", b=2, c=5.1, d=np.array([0, 2.0, 3.1])),
            dict(a="a", b=2, c=5.1, d=np.array([0, 2.0, 3.1])),
        ],
    )

    assert is_valid_json(data, True)

    assert is_valid_json(data) is False

    data["d"] = data["d"].tolist()
    data["e"]["d"] = data["e"]["d"].tolist()
    data["f"][0]["d"] = data["f"][0]["d"].tolist()
    data["f"][1]["d"] = data["f"][1]["d"].tolist()

    assert is_valid_json(data)


def test_json2html():
    data = dict(
        a=0.2,
        b=[0.1, 0.2],
        c=np.array([0.2, 0.3]),
        d=dict(a=0.1, b=dict(a=0.1)),
        e=[
            dict(a=0.2),
            dict(a=0.3),
            dict(a=[0.1, 0.2, 0.3]),
            dict(a=[dict(a=0.1), 0.5, "str"]),
        ],
    )
    json_data_render(data)._repr_html_()
    json_data_render(data, True)._repr_html_()
    json_data_render(data, fields=["e", 3, "a", 0])._repr_html_()
    json_data_render(data, fields=[["e", 2, "a"], ["e", 3, "a", 0]])._repr_html_()
    json_data_render(data, True, fields=["e", 3, "a", 0])._repr_html_()
    json_data_render(data, True, fields=[["d", "b"], ["e", 3, "a", 0]])._repr_html_()

    json_data_render([data])._repr_html_()
    json_data_render(5.0)._repr_html_()

    big_array_dict = {
        "a" + str(i): np.random.rand(*size)
        for i, size in enumerate(
            [(5,), (50,), (100,), (1000,), (100, 100), (10, 10, 10)]
        )
    }
    out1 = json_data_render(big_array_dict)._repr_html_()
    out2 = json_data_render(big_array_dict, max_arr_size=-1)._repr_html_()
    assert out1.__sizeof__() < out2.__sizeof__()

    with pytest.raises(ValueError, match="`fields` has to be"):
        json_data_render(data, fields="test")._repr_html_()
