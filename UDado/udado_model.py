class Attribute:

    ID_KEY = "id"
    OBJECTIVE_KEY = "objective"
    GT_CONST_KEY = "gt"
    LT_CONST_KEY = "lt"
    EQ_CONST_KEY = "eq"

    def __init__(self, a_dkt: "dict[str, any]") -> None:
        self.id = a_dkt[self.ID_KEY]
        self.objective = a_dkt.get(self.OBJECTIVE_KEY, 0)
        self.gt = a_dkt.get(self.GT_CONST_KEY)
        self.lt = a_dkt.get(self.LT_CONST_KEY)
        self.eq = a_dkt.get(self.EQ_CONST_KEY)
    
    def to_dict(self) -> "dict[str, any]":
        autodict = {self.ID_KEY: self.id, self.OBJECTIVE_KEY: self.objective}
        if self.gt:
            autodict[self.GT_CONST_KEY] = self.gt
        if self.lt:
            autodict[self.LT_CONST_KEY] = self.lt
        if self.eq:
            autodict[self.EQ_CONST_KEY] = self.eq
        return autodict

from typing import Union
class Device:

    ID_KEY = "id"
    ATTRIBUTES_KEY = "attributes"

    def __init__(self, d_dkt: "dict[str, Union[str, dict[str, any]]]") -> None:
        self.id = d_dkt[self.ID_KEY]
        self.attributes = d_dkt.get(self.ATTRIBUTES_KEY, {})
    
    def to_dict(self) -> "dict[str, any]":
        return {self.ID_KEY: self.id, self.ATTRIBUTES_KEY: self.attributes}