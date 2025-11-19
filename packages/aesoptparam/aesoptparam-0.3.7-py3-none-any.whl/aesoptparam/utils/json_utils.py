import json

import numpy as np


def read_json(filename, asarray=True, **json_load_kwargs):
    """Read a json file. Optionally convert data with list of numbers to numpy array.

    Simple wrapper for:

        with open(filename, "r") as file:
            out = json.load(file, object_hook=NpDecode_object_hook if asarray else None)
        return out

    Parameters
    ----------
    filename : str
        Name of the file to load
    asarray : bool, optional
        Flag for converter list of numbers to numpy array, by default True

    Returns
    -------
    dist, list
        Data from the json file
    """
    with open(filename, "r") as file:
        out = json.load(
            file,
            object_hook=JSONNumpyDecode_object_hook if asarray else None,
            **json_load_kwargs
        )
    return out


def write_json(filename, data, convert_numpy=True, **json_dump_kwargs):
    """Write JSON compatible data to file. Optionally convert numpy data.

    Simple wrapper:

        with open(filename, "w") as file:
            json.dump(data, file, cls=NpEncoder if convert_numpy else None)

    Parameters
    ----------
    filename : str
        Name of the JSON file to write
    data : dict, list
        Data to be written to file
    convert_numpy : bool, optional
        Flag for converting numpy data as a part of the writing process, by default True
    """
    with open(filename, "w") as file:
        json.dump(
            data,
            file,
            cls=JSONNumpyEncoder if convert_numpy else None,
            **json_dump_kwargs
        )


class JSONNumpyEncoder(json.JSONEncoder):
    """Encodes numpy types to python buildin

    Usages:

        with open("data.json", "w") as file:
            out = json.dump(file, cls=NpEncoder)
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(JSONNumpyEncoder, self).default(obj)


def JSONNumpyDecode_object_hook(obj):
    """JSON `object_hook` to converter list of numbers to numpy arrays

    Usages:

        with open("data.json", "r") as file:
            out = json.load(file, object_hook=NpDecode_object_hook)

    Parameters
    ----------
    obj : dict
        JSON compliant dict

    Returns
    -------
    dict
        Dict with all list of numbers replaced as numpy arrays
    """
    for name, val in obj.items():
        if isinstance(val, list) and np.issubdtype(np.asarray(val).dtype, np.number):
            obj[name] = np.asarray(val)
    return obj


def is_valid_json(data, allow_numpy=False):
    """Verify if data is JSON valid. Optionally (`allow_numpy=True`) it will allow numpy.

    Parameters
    ----------
    data : dict, list
        Data to verify if is JSON valid
    allow_numpy : bool, optional
        Flag for allowing numpy data, by default False

    Returns
    -------
    dict,list
        Returns JSON valid data. (If `allow_numpy=True` numpy data will be converted to lists and build-in data types)
    """
    try:
        return json.loads(
            json.dumps(data, cls=JSONNumpyEncoder if allow_numpy else None)
        )
    except:
        return False
