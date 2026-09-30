# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol

from Part import Edge, Face, Vertex, Wire

from ..utils.FreeCADInterfaces import FeatureLike
from ..utils.makeShapeReg import makeShapeWithReg
from ..utils.PropDef import PropDef, PropertyBool, PropertyFloat, PropertyLinkSubList
from ..utils.utils import getSelectionEx

FEATURE_NAME = "Join"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True)  # type: ignore
    Shapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Edges to extrapolate from")  # type: ignore
    Tol: float = PropertyFloat("Shape", "", 1e-3)  # type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)
        self.elementsType: type | None = None

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Shapes:
            obj.Shapes = getSelectionEx(hideSelection=True)
            shapesT: tuple[list[FeatureLike], list[list[str]]] = tuple(list(row) for row in zip(*obj.Shapes))  # type: ignore
        else:
            shapesT = [list(row) for row in zip(*obj.Shapes)]  # type: ignore

        fShape = obj.Shapes[0][0].Shape
        fSubName = obj.Shapes[0][1][0]
        self.elementsType = type(fShape.getElement(fSubName))

        result = makeShapeWithReg([x.Shape for x in shapesT[0]])

        if obj.CheckShape:
            result.check()
        obj.Shape = result

        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        if self.elementsType is Face:
            obj.ViewObject.ShapeColor = (0 / 255, 177 / 255, 255 / 255)

            obj.ViewObject.LineColor = (25 / 255, 25 / 255, 25 / 255)
            obj.ViewObject.PointColor = (25 / 255, 25 / 255, 25 / 255)
            obj.ViewObject.PointSize = 2
        elif self.elementsType in [Edge, Wire]:
            obj.ViewObject.LineColor = (255 / 255, 0 / 255, 255 / 255)
            obj.ViewObject.PointColor = (255 / 255, 0 / 255, 255 / 255)

            obj.ViewObject.ShapeColor = (114 / 255, 121 / 255, 128 / 255)
            obj.ViewObject.PointSize = 2
        elif self.elementsType is Vertex:
            obj.ViewObject.PointColor = (255 / 255, 0 / 255, 255 / 255)
            obj.ViewObject.PointSize = 4

            obj.ViewObject.LineColor = (25 / 255, 25 / 255, 25 / 255)
            obj.ViewObject.ShapeColor = (114 / 255, 121 / 255, 128 / 255)

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
