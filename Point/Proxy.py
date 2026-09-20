# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Literal, Protocol

from FreeCAD import Vector
from Part import Vertex

from utils.FreeCADInterfaces import FeatureLike
from utils.PropDef import PropDef, PropertyEnumeration, PropertyStringList

# from utils.utils import getSelectionEx

FEATURE_NAME = "Point"


class CurrentFeatureLike(FeatureLike, Protocol):
    OriginType: Literal["Absolute", "Point"] = PropertyEnumeration("Input", "", ["Absolute", "Point"])  # type: ignore
    Coords: list[str] = PropertyStringList("Input", "", ["0", "0", "0"])  # type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        vec = Vector([float(obj.Coords[i]) for i in range(3)])
        result = Vertex(vec)

        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        # obj.ViewObject.ShapeColor = (0 / 255, 177 / 255, 255 / 255)
        # obj.ViewObject.LineColor = (255/255, 0/255, 255/255)
        obj.ViewObject.PointColor = (255 / 255, 0 / 255, 255 / 255)
        obj.ViewObject.PointSize = 4

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
