# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol

from FreeCAD import Vector
from Part import Edge, LineSegment, Wire

from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.PropDef import PropDef, PropertyLinkSubList
from utils.utils import getSelectionEx

FEATURE_NAME = "Line"


class CurrentFeatureLike(FeatureLike, Protocol):
    Verts: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "")  # type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Verts:
            obj.Verts = getSelectionEx(hideSelection=True)

        vecs: list[Vector] = []

        for feature, names in obj.Verts:
            if names == (""):
                vecs.append(feature.Shape.Vertexes[0].Point)
            else:
                for n in names:
                    sh = feature.Shape.getElement(n)
                    vecs.append(sh.Point)

        edges: list[ShapeLike] = []

        for i in range(1, len(vecs)):
            prev = vecs[i - 1]
            curr = vecs[i]
            edge = Edge(LineSegment(prev, curr))
            edges.append(edge)

        result = Wire(edges)

        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        # obj.ViewObject.ShapeColor = (0 / 255, 177 / 255, 255 / 255)
        obj.ViewObject.LineColor = (255 / 255, 0 / 255, 255 / 255)
        obj.ViewObject.PointColor = (255 / 255, 0 / 255, 255 / 255)
        # obj.ViewObject.PointSize = 4

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
