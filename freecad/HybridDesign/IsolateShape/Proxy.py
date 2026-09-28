# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol

from Part import Compound

from ..utils.FreeCADInterfaces import FeatureLike, ShapeLike
from ..utils.PropDef import PropDef
from ..utils.utils import getSelectionEx

FEATURE_NAME = "IsolateShape"


class CurrentFeatureLike(FeatureLike, Protocol):
    pass


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        sel = getSelectionEx(hideSelection=True)

        elements: list[ShapeLike] = []
        for el, subNames in sel:
            if subNames != (""):
                for sName in subNames:
                    elements.append(el.getSubObject(sName))
            else:
                elements.append(el.Shape)

        result = Compound(elements)

        obj.Shape = result

        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        pass
        # obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)

    @classmethod
    def getFeatureName(cls) -> str:
        return FEATURE_NAME

    def add_properties(self, obj: CurrentFeatureLike):
        properties: list[tuple[str, PropDef]] = []
        for i, _ in CurrentFeatureLike.__dict__.items():
            if i[0] != "_":
                att = getattr(CurrentFeatureLike, i)
                properties.append((i, att))

        for name, prop in properties:
            if not hasattr(obj, name):
                obj.addProperty(prop.type, name, prop.section, prop.description)
                if prop.defVal:
                    setattr(obj, name, prop.defVal)

    def onChanged(self, obj: CurrentFeatureLike, prop):
        pass

    def __getstate__(self):
        return {"Type": self.Type}

    def __setstate__(self, state):
        self.Type = state.get("Type", self.getFeatureName())
