from .html_repr import display_json_data
from .json_utils import read_json, write_json


def copy_param(param, exclude=None, update=None):
    """Copy a Parameter, either a standalone `Parameter` (`AESOptNumber`, `AESOptArray`, ..) or from a `Parametrized` class (using `par_class.param.param_name`)

    Parameters
    ----------
    param : `Parameter`
        Parameter instance
    exclude : list, optional
        List of entries to exclude, by default None
    update : dict, optional
        Dict with values to update, by default None

    Returns
    -------
    `Parameter`
        Copy of parameter instance. Optionally without entries from `exclude` or updated values from `update`
    """
    if exclude is None:
        exclude = []
    if update is None:
        update = dict()
    kwargs = dict()
    for name in param._slot_defaults:
        val = getattr(param, name)
        if not name in exclude and val is not None:
            kwargs[name] = val
    for name, val in update.items():
        kwargs[name] = val

    return type(param)(**kwargs)


def copy_param_ref(param, ref, exclude=None, update=None):
    """Similar to `copy_param` but adding "default" to `exclude` and "default_ref" to `update` with value of `ref`

    Parameters
    ----------
    param : `Parameter`
        Parameter instance
    ref : str
        String with the reference path
    exclude : list, optional
        List of entries to exclude, by default None
    update : dict, optional
        Dict with values to update, by default None

    Returns
    -------
    `Parameter`
        Copy of parameter instance. Optionally without entries from `exclude` or updated values from `update`
    """
    if exclude is None:
        exclude = []
    if update is None:
        update = dict()
    if not "default" in exclude:
        exclude.append("default")
    update["default_ref"] = ref
    return copy_param(param, exclude, update)
