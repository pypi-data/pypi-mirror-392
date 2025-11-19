import sys
from gc import get_referents
from types import FunctionType, ModuleType

import numpy as np
import param as pm
from param.parameterized import truncate

from .json_utils import is_valid_json

try:
    import markdown

    has_markdown = True
except ImportError:  # pragma: no cover
    has_markdown = False

html_repr_settings = {"max_arr_size": 30}


def param_html_repr(
    key, val, parameter, parametrized, vallen=30, max_arr_size=None
):  # pragma: no cover
    """HTML representation for a single Parameter object and its value"""

    if hasattr(parameter, "bounds"):
        if parameter.bounds is None:
            range_ = ""
        elif hasattr(parameter, "inclusive_bounds"):
            bl, bu = parameter.bounds
            il, iu = parameter.inclusive_bounds

            lb = "" if bl is None else (">=" if il else ">") + str(bl)
            ub = "" if bu is None else ("<=" if iu else "<") + str(bu)
            range_ = lb + (", " if lb and bu else "") + ub
        else:
            range_ = repr(parameter.bounds)
    elif hasattr(parameter, "objects") and parameter.objects:
        range_ = ", ".join(list(map(repr, parameter.objects)))
    elif hasattr(parameter, "class_"):
        if isinstance(parameter.class_, tuple):
            range_ = (
                "type=<code>"
                + " | ".join(kls.__name__ for kls in parameter.class_)
                + "</code>"
            )
        else:
            range_ = f"type=<code>{parameter.class_.__name__}</code>"
    elif hasattr(parameter, "regex") and parameter.regex is not None:
        range_ = f"regex({parameter.regex})"
    else:
        range_ = ""

    if parameter.readonly:
        range_ = " ".join(s for s in ["<i>read-only</i>", range_] if s)
    elif parameter.constant:
        range_ = " ".join(s for s in ["<i>constant</i>", range_] if s)

    if getattr(parameter, "shape", False):
        if len(range_) > 0:
            range_ += "<br>"
        range_ += f"shape=<code>{parameter.shape}</code>"
    if getattr(parameter, "item_type", False):
        if isinstance(parameter.item_type, tuple):
            item_type = " | ".join(kls.__name__ for kls in parameter.item_type)
        else:
            item_type = parameter.item_type.__name__
        if len(range_) > 0:
            range_ += "<br>"
        range_ += f"item_type=<code>{item_type}</code>"

    units = getattr(parameter, "units", False)
    if units is None:
        units = "-"
    elif isinstance(units, str):
        units = f"<code>{units}</code>"
    else:
        units = ""

    if isinstance(val, pm.Parameterized) or (
        type(val) is type and issubclass(val, pm.Parameterized)
    ):
        # value = val.param._repr_html_(open=False)
        value = parameterized_repr_html(val, open=False)
    elif (
        isinstance(val, list) and len(val) > 0 and isinstance(val[0], pm.Parameterized)
    ):
        value = ListOfParameterized_repr_html(
            key, val, parameter.identifier, False, max_arr_size
        )
    elif hasattr(val, "_repr_html_"):
        value = val._repr_html_()
    elif hasattr(parametrized.param[key], "repr_html"):
        val_pp = parametrized._param__private.values.get(key, None)
        value = parametrized.param[key].repr_html(val, val_pp, max_arr_size)
    else:
        value = repr_val(val, max_arr_size)

    doc = parameter.doc.strip() if parameter.doc else ""
    if doc.startswith("\x1b"):
        doc = ""
    elif "\n\x1b" in doc:
        doc = doc.split("\n\x1b")[0]
    if has_markdown:
        doc = markdown.markdown(doc)

    return (
        f"<tr>"
        f'  <td><p style="margin-bottom: 0px;">{key}</p></td>'
        f'  <td style="max-width: 300px; text-align:left;">{doc}</td>'
        f'  <td style="text-align:left;">{parameter.__class__.__name__}</td>'
        f'  <td style="max-width: 300px;">{range_}</td>'
        f'  <td style="max-width: 100px;">{units}</td>'
        f'  <td style="min-width: 300px; text-align:left;">{value}</td>'
        f"</tr>\n"
    )


def parameterized_repr_html(p, open, title=None, max_arr_size=None):  # pragma: no cover
    """HTML representation for a Parameterized object"""
    # Changed the layout to set value at the end to make display of nested objects better
    # as well as adding documentation column that is markdown rendered
    if isinstance(p, pm.Parameterized):
        if title is None:
            cls = p.__class__
            title = cls.name + "()"
        value_field = "Value"
    else:
        if title is None:
            cls = p
            title = cls.name
        value_field = "Default"
    openstr = " open" if open else ""
    precedence = sorted(
        [
            (0.5 if el.precedence is None else el.precedence, name)
            for name, el in p.param.objects().items()
        ]
    )
    contents_list = []
    for _, name in precedence:
        # Skip .name if it is the default name
        if (name == "name") and (
            p.param[name].doc == "\n        String identifier for this object."
        ):
            continue
        contents_list.append(
            param_html_repr(name, p[name], p.param[name], p, max_arr_size=max_arr_size)
        )
    contents = "".join(contents_list)
    return (
        f'<details {openstr} style="border-width:1px;border-radius:25px;">\n'
        ' <summary style="display:list-item; outline:none;padding-left:10px;">\n'
        f"  <tt>{title}</tt>\n"
        " </summary>\n"
        ' <div style="padding-left:10px; padding-bottom:5px;">\n'
        '  <table style="max-width:100%;">\n'
        f'   <tr><th style="text-align:left;">Name</th><th style="text-align:left;">Documentation</th><th style="text-align:left;">Type</th><th>Range</th><th>Units</th><th style="text-align:left;">{value_field}</th></tr>\n'
        f"{contents}\n"
        "  </table>\n </div>\n</details>\n"
    )


def ListOfParameterized_repr_html(
    title, items, identifier, open=True, max_arr_size=None
):  # pragma: no cover
    """HTML render an ListOfParameterized as a one column table with each element in the list. Each element is identified by an `identifier`."""
    openstr = " open" if open else ""
    contents = "".join(
        [
            "<tr><td>"
            + parameterized_repr_html(
                val,
                False,
                val.__class__.name + f"({identifier}=<code>{val[identifier]}</code>)",
                max_arr_size=max_arr_size,
            )
            + "<td></tr>"
            for val in items
        ]
    )
    return (
        f"<details {openstr}>\n"
        ' <summary style="display:list-item; outline:none;">\n'
        f"  <tt>{title}</tt>\n"
        " </summary>\n"
        ' <div style="padding-left:10px; padding-bottom:5px;">\n'
        '  <table style="max-width:100%;">\n'
        f"   <tr><th></th></tr>\n"
        f"{contents}\n"
        "  </table>\n </div>\n</details>\n"
    )


def value_ref_default_repr_html(
    parameter, val, val_pp, max_arr_size
):  # pragma: no cover
    """HTML render of a parameter with reference and/or default states. `val` is the parameter value after full evaluation (as seen by the user). `val_pp` is the value from `._param__private.values` which is the value that is stored."""
    from ..parameters import Function, Reference

    if val_pp is None and not parameter.default is None:
        val_pp = parameter.default
    if isinstance(val_pp, Reference):
        title, value = ref_html_repr(val, val_pp, max_arr_size)
    elif isinstance(val_pp, Function):
        title = f"<i>$function:</i> {repr_val(val, max_arr_size)}"
        value = f"<i>definition:</i> <code>{val_pp.source_str}</code><br>"
    elif (val_pp is None) and (not val is None):
        if hasattr(parameter, "default_full") and (not parameter.default_full is None):
            title = f"<i>default full:</i> {repr_val(val, max_arr_size)}"
            value = f"<i>full args:</i> {parameter.default_full}"
        elif hasattr(parameter, "default_interp") and (
            not parameter.default_interp is None
        ):
            title = f"<i>default interp:</i> {repr_val(val, max_arr_size)}"
            value = f"<i>interp args:</i> {parameter.default_interp}"
        elif hasattr(parameter, "default_ref") and (not parameter.default_ref is None):
            title, value = ref_html_repr(val, parameter.default_ref, max_arr_size)
        else:
            return "None"
    elif isinstance(val, (float, int)):
        return str(val)
    elif isinstance(parameter, pm.String) and isinstance(val, str):
        return repr_val(val, max_arr_size)
    elif (val_pp is None) and (val is None):
        return "None"
    else:
        return repr_val(val, max_arr_size)
    return (
        f"<details>\n"
        ' <summary style="display:list-item; outline:none;">\n'
        f"  <tt>{title}</tt>\n"
        " </summary>\n"
        ' <div style="padding-left:10px; padding-bottom:5px;">\n'
        f"{value}\n"
        "</div>\n</details>\n"
    )


def repr_val(val, max_arr_size):
    if isinstance(val, str):
        return "'" + val + "'"
    elif isinstance(val, (dict, list, np.ndarray)) and is_valid_json(val, True):
        val = json2html(
            is_valid_json(val, True),
            title=f"{truncate(repr(val))}",
            max_arr_size=max_arr_size,
            display_inline=True,
        )
    return str(val)


def ref_html_repr(val, val_pp, max_arr_size):
    title = f"<i>$ref:</i> {repr_val(val, max_arr_size)}"
    value = f"<i>path:</i> <code>{val_pp.path.strip()}</code>"
    return title, value


class parameterized_repr_html_class:

    def __init__(self, parameterized_ins, open=True, title=None, max_arr_size=None):
        self.parameterized_ins = parameterized_ins
        self.open = open
        self.title = title
        self.max_arr_size = max_arr_size

    def _repr_html_(self):
        return parameterized_repr_html(
            self.parameterized_ins, self.open, self.title, self.max_arr_size
        )


# %% JSON dict render
def json2html(
    data_in,
    open_default=False,
    fields=None,
    max_arr_size=None,
    title=None,
    display_inline=False,
):
    # %% Setting/checking default input
    # Ensuring open_fields is a list of list's
    if not (fields is None or isinstance(fields, bool)):
        if not isinstance(fields, list):
            raise ValueError(f"`fields` has to be a list (given: {fields})")
        if not isinstance(fields[0], list):
            fields = [fields]
    # If root object should be open
    open = open_default
    if isinstance(fields, bool):
        open = fields
        fields = None
    elif fields is not None:
        open = True
    openstr = " open" if open else ""
    # Setting max_arr_size
    if max_arr_size is None:
        data_size = get_data_size(data_in)
        if data_size > 1_000_000:  # Rough size of 1000 size 100 arrays
            max_arr_size = 5
        elif data_size > 100_000:  # Rough size of 100 size 100 arrays
            max_arr_size = 10
        elif data_size > 10_000:  # Rough size of 10 size 100 arrays
            max_arr_size = 100
        else:
            max_arr_size = -1  # Print all data
    # Title
    if title is None:
        title = truncate(repr(data_in))
    # Displaying inline
    details_style = ""
    if display_inline is True:
        details_style = "style='display: inline;'"

    if isinstance(data_in, dict):
        contents, _ = _dict2html_tree(data_in, open_default, fields, max_arr_size)
    elif isinstance(data_in, list):
        contents, _ = _list2html_tree(data_in, open_default, fields, max_arr_size)
    else:
        contents = _item2html_tree("", data_in, open_default, fields, max_arr_size)
    return (
        f"<details {openstr} {details_style}>\n"
        ' <summary style="display:list-item; outline:none;">\n'
        f"  <tt>{title}</tt>\n"
        " </summary>\n"
        ' <div style="padding-left:10px; padding-bottom:5px;">\n'
        '  <table style="max-width:100%;">\n'
        f"{contents}\n"
        "  </table>\n </div>\n</details>\n"
    )


def _item2html_tree(name, item, open_default, fields, max_arr_size):
    if isinstance(item, (dict, list)):
        _fields = remove_name_from_fields(name, fields)
        if isinstance(item, dict):
            content, size = _dict2html_tree(item, open_default, _fields, max_arr_size)
        else:
            content, size = _list2html_tree(item, open_default, _fields, max_arr_size)
        value = _collaps_item(item, content, open_str(name, open_default, fields))
        if isinstance(name, str):
            name = f"'{name}'"
        name = f"{name} |{size}| :"
    else:
        if isinstance(name, str):
            name = f"'{name}'"
        name = f"{name} :"
        if isinstance(item, str):
            value = f"'{item}'"
        else:
            value = item
    return _add_HTML_row(name, value)


def _add_HTML_row(name, value):
    return (
        f"<tr>"
        f'  <td><p style="margin-bottom: 0px; margin-top: 0px;">{name}</p></td>'
        f'  <td style="text-align:left;">{value}</td>'
        f"</tr>\n"
    )


def _dict2html_tree(dict_in, open_default, fields, max_arr_size):
    out = ""
    for name, item in dict_in.items():
        out += _item2html_tree(name, item, open_default, fields, max_arr_size)
    return out, len(dict_in)


def _list2html_tree(list_in, open_default, open_fields, max_arr_size):
    out = ""
    if (
        max_arr_size > 0
        and _is_numeric_array(list_in)
        and np.asarray(list_in).size > max_arr_size
    ):
        array = np.asarray(list_in)
        out += _add_HTML_row("min", repr(float(array.min())))
        out += _add_HTML_row("max", repr(float(array.max())))
        size = repr(array.shape).strip("(),")
    else:

        for iel, el in enumerate(list_in):
            out += _item2html_tree(iel, el, open_default, open_fields, max_arr_size)
        size = len(list_in)
    return out, size


def _is_numeric_array(list_in):
    """Method to test if a `list` or nested `list`'s only contains `float`'s or `int`'s. Testing by casting to an array and check the resulting `.dtype`.

    Parameters
    ----------
    list_in : Any
        Data to test

    Returns
    -------
    bool
        Flag, `True` means the list is a `list` or nested `list`'s of numbers.
    """
    try:
        if np.issubdtype(np.asarray(list_in).dtype, np.number):
            return True
        return False
    except:
        return False


def _collaps_item(item, content, open):
    return (
        f"<details {open}>\n"
        ' <summary style="display:list-item; outline:none;">\n'
        f"  <tt>{truncate(repr(item), 15)}</tt>\n"
        " </summary>\n"
        ' <div style="padding-left:10px; padding-bottom:5px;">\n'
        '<table style="max-width:100%;">\n'
        f"{content}\n"
        "</table>\n </div>\n</details>\n"
    )


def is_open(name, open_default, fields):
    open = open_default
    if fields is not None and any(
        [(name == el[0]) or (el[0] is True) for el in fields if isinstance(el, list)]
    ):
        return not open
    return open


def open_str(name, open_default, fields):
    open = is_open(name, open_default, fields)
    return " open" if open else ""


def remove_name_from_fields(name, fields):
    if fields is None:
        return None
    out = []
    for el in fields:
        if isinstance(el, list) and ((el[0] == name) or (el[0] is True)):
            if len(el) > 1:
                out.append(el[1:])
            else:
                out.append("")
        else:
            out.append(el)
    return out


# From: https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
BLACKLIST = type, ModuleType, FunctionType


def get_data_size(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError("getsize() does not take argument of type: " + str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


class json_data_render:
    """Converting JSON data to a HTML table with collapsible nested list and dict's

    Parameters
    ----------
    data_in : dict, list
        JSON compliant dict and list
    open_default : bool, optional
        Flag for default opening or closing collapsible entries, by default False
    fields : list, bool, optional
        list or list of list of names to open or close (opposed to open_default). `True` means that it should open the root - `False` close the root, by default None
    max_arr_size : int, optional
        Maximum size of numeric arrays to render. Using `np.size(array) > max_arr_size`. Default will be determined based on the size of the data, `max_arr_size=[5, 10, 100]` for data with approx. size of [1000, 100, 10] size 100 arrays. Otherwise `max_array_size=-1` which means to render all arrays.

    Returns
    -------
    str
        Representation of the data as a HTML table with collapsible entries

    Raises
    ------
    ValueError
        If fields are not a list or None
    """

    def __init__(self, data_in, open_default=False, fields=None, max_arr_size=None):
        self.open_default = open_default
        self.fields = fields
        self.max_arr_size = max_arr_size
        self.json_data = is_valid_json(data_in, True)

    def _repr_html_(self):
        return json2html(
            self.json_data, self.open_default, self.fields, self.max_arr_size
        )


def display_json_data(data_in, open_default=False, fields=None, max_arr_size=None):
    """Display json like data as an HTML tree

    Simple wrapper for:

        display(json_data_render(json_data))

    Parameters
    ----------
    data_in : dict, list
        JSON compliant dict and list
    open_default : bool, optional
        Flag for default opening or closing collapsible entries, by default False
    fields : list, optional
        list or list of list of names to open or close (opposed to open_default). `True` means that it should open the root - `False` close the root, by default None
    max_arr_size : int, optional
        Maximum size of numeric arrays to render. Using `np.size(array) > max_arr_size`. Default will be determined based on the size of the data, `max_arr_size=[5, 10, 100]` for data with approx. size of [1000, 100, 10] size 100 arrays. Otherwise `max_array_size=-1` which means to render all arrays.
    """
    from IPython.display import display

    display(json_data_render(data_in, open_default, fields, max_arr_size))
