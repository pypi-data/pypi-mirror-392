import textwrap

import param as pm
from param.serializer import JSONSerialization, UnserializableException


def JSONNullable_Ref_Function(json_type, allow_None, allow_Ref):
    "Express a JSON schema type as nullable or string with $ref or $function to easily support Parameters that allow_None"
    if any([allow_None, allow_Ref]):
        json_types = [json_type]
        if allow_Ref:
            json_types.append({"type": "string", "pattern": r"^(\$ref|\$function)"})
        if allow_None:
            json_types.append({"type": "null"})
        return {"anyOf": json_types}
    return json_type


class ASEOptJSONSerialization(JSONSerialization):
    @classmethod
    def schema(cls, pobj, safe=False, subset=None, skip_default_name=True):
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": cls._schema(pobj, safe, subset, skip_default_name),
        }

    @classmethod
    def _schema(cls, pobj, safe=False, subset=None, skip_default_name=True):
        schema = {}
        for name, p in pobj.param.objects("existing").items():
            if skip_default_name and (name == "name") and p.constant:
                continue
            if subset is not None and name not in subset:
                continue
            schema[name] = cls.param_schema(p.__class__.__name__, p, safe, subset)
            if p.doc:
                schema[name]["description"] = p.doc
        return schema

    @classmethod
    def param_schema(cls, ptype, p, safe=False, subset=None):
        if ptype in cls.unserializable_parameter_types:
            raise UnserializableException
        allow_Ref = False
        if isinstance(p, pm.String):
            schema = {"type": "string"}
            allow_Ref = True
        elif isinstance(p, pm.Number):
            # schema = getattr(cls, "number_schema")(p, safe=safe)
            schema = cls.declare_numeric_bounds(
                {"type": "number"}, p.bounds, p.inclusive_bounds
            )
            allow_Ref = True
        elif isinstance(p, pm.Array):
            schema = cls.array_schema(p, safe)
            if hasattr(p, "dtype"):
                if p.dtype is int:
                    schema["items"] = {"type": "integer"}
                else:
                    schema["items"] = {"type": "number"}
            if hasattr(p, "bounds"):
                schema["items"] = cls.declare_numeric_bounds(
                    schema["items"], p.bounds, p.inclusive_bounds
                )
            allow_Ref = True
        elif isinstance(p, pm.ClassSelector):
            schema = getattr(cls, "classselector_schema")(p, safe=safe)
        elif isinstance(p, pm.List):
            schema = getattr(cls, "list_schema")(p, safe=safe)
        else:
            method = cls._get_method(ptype, "schema")
            if method:
                schema = method(p, safe=safe)
            else:
                schema = {"type": ptype.lower()}
        if p.doc:
            schema["description"] = p.doc
        return JSONNullable_Ref_Function(schema, p.allow_None, allow_Ref)

    @classmethod
    def class__schema(cls, class_, safe=False):
        if isinstance(class_, tuple):
            return {"anyOf": [cls.class__schema(cls_) for cls_ in class_]}
        elif class_ in cls.json_schema_literal_types:
            return {"type": cls.json_schema_literal_types[class_]}
        elif issubclass(class_, pm.Parameterized):
            return {"type": "object", "properties": cls._schema(class_, safe)}
        else:
            return {"type": "object"}
