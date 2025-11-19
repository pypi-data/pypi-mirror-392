import numpy as np

from aesoptparam import (
    AESOptArray,
    AESOptNumber,
    AESOptParameterized,
    AESOptString,
    Dict,
    ListOfParameterized,
    String,
    SubParameterized,
    copy_param,
    copy_param_ref,
)


class sub1_class(AESOptParameterized):
    """Docs sub1"""

    a = AESOptNumber(5.0, doc="Docs for sub1.a", bounds=(0, 10))
    b = AESOptArray(np.linspace(0, 10, 10), doc="Docs for sub1.b")
    c = AESOptArray(default_ref=".b", doc="Docs for sub1.c")
    e = AESOptArray(
        lambda self: np.full_like(self.b, self.a), shape=".b", doc="Docs for sub1.e"
    )
    f = AESOptArray(default_full=(".b", ".a"), doc="Docs for sub1.d")
    g = AESOptArray(default_full=(".b", 6.0), doc="Docs for sub1.g")
    h = AESOptArray(
        default_interp=(np.linspace(0, 10, 5), ".b", ".c"), doc="Docs for sub1.h"
    )
    i = AESOptString("sub1.Dummy", doc="Docs for sub1.i")
    j = AESOptString(".i", doc="Docs for sub1.j")
    k = AESOptString(lambda self: self.i + "2", doc="Docs for sub1.k")


class sub2_class(AESOptParameterized):
    """Docs sub2"""

    a = copy_param_ref(
        sub1_class.param.a, "..sub1.a", update=dict(doc="Docs for sub2.a")
    )
    b = AESOptNumber(default_ref="..a", doc="Docs for sub2.b")
    c = AESOptNumber(default_ref="..sub_list[0].a", doc="Docs for sub2.c")
    d = copy_param_ref(
        sub1_class.param.b, "..sub1.b", update=dict(doc="Docs for sub2.d")
    )
    e = AESOptArray(
        lambda self: (
            None if self.parent_object.sub1.b is None else self.parent_object.sub1.b + 1
        ),
        doc="Docs for sub2.e",
    )
    f = AESOptString("..f", doc="Docs for sub2.f")
    g = copy_param_ref(
        sub1_class.param.i, "..sub1.i", update=dict(doc="Docs for sub2.g")
    )
    h = AESOptString("..sub_list[0].f", doc="Docs for sub2.h")


class sub_list_class(AESOptParameterized):
    """Docs sub_list"""

    a = AESOptNumber(6.0, doc="Docs for sub_list.a")
    b = AESOptNumber(default_ref="..a", doc="Docs for sub_list.b")
    c = AESOptNumber(default_ref="..sub1.a", doc="Docs for sub_list.c")
    d = AESOptArray(default_ref="..d", doc="Docs for sub_list.d")
    e = AESOptArray(default_ref="..sub1.b", doc="Docs for sub_list.e")
    f = AESOptString(default_ref="..f", doc="Docs for sub_list.f")
    g = AESOptString(default_ref="..sub1.i", doc="Docs for sub_list.g")


class main(AESOptParameterized):
    """Main object"""

    version = String("0.0.0", readonly=True, precedence=0.0)
    name = String("Dummy", doc="Main dummy", precedence=0.01, constant=False)
    a = AESOptNumber(4.0, units="rad/s", doc="Docs for .a", bounds=(0, 10))
    b = AESOptNumber(default_ref=".sub1.a", units="m/s", doc="Docs for .b")
    c = AESOptNumber(default_ref=".sub_list[0].a", doc="Docs for .c")
    d = AESOptArray(
        default_ref=".sub1.b", units="mm/s", doc="Docs for .d", bounds=(0, 10)
    )
    e = AESOptArray(
        np.array([0, 1, 2, 3]),
        shape=4,
        units="mm/s",
        doc="Docs for .d",
        bounds=(0, 10),
        dtype=int,
    )
    f = AESOptString("Dummy", doc="Docs for .f")
    g = AESOptString(".f", doc="Docs for .g")
    h = AESOptString(lambda self: self.f + "2", doc="Docs for .h")
    i = Dict(doc="Docs for .i")
    sub1 = SubParameterized(sub1_class)
    sub2 = SubParameterized(sub2_class)
    sub_list = ListOfParameterized(sub_list_class)
    sub_list2 = ListOfParameterized(
        sub_list_class, default_call=lambda self: [self.add_sub_list2()]
    )

    def add_sub_list(self, **params):
        return self.add_ListOfParameterized_item(
            "sub_list", self.param.sub_list.item_type, **params
        )

    def add_sub_list2(self, **params):
        return self.add_ListOfParameterized_item(
            "sub_list2", self.param.sub_list2.item_type, **params
        )
