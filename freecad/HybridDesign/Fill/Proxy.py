# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol

from FreeCAD import ActiveDocument
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeFilling
from OCC.Core.GeomAbs import GeomAbs_G1

from ..utils.FreeCADInterfaces import FeatureLike, ShapeLike
from ..utils.PropDef import PropDef, PropertyLinkSubList
from ..utils.utils import getSelectionEx, sortEdges

FEATURE_NAME = "Fill"


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

        # TODO try pythonOCC egPart.__toPythonOCC__(FreeCAD.ActiveDocument.Extract.Shape)
        edgeNames = obj.Verts[0][1]

        edgeDict = {obj.Verts[0][0].Shape.getElement(name): name for name in edgeNames}

        edges = sortEdges(list(edgeDict.keys()))

        boudaryEdges = tuple(edgeDict[edge] for edge in edges)

        fillObj = ActiveDocument.addObject("Surface::Filling", "Filling")

        fillObj.BoundaryEdges = [(obj.Verts[0][0], boudaryEdges)]
        fillObj.recompute()

        result = fillObj.Shape.copy()

        ActiveDocument.removeObject(fillObj.Name)

        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0 / 255, 177 / 255, 255 / 255)
        # obj.ViewObject.LineColor = (255 / 255, 0 / 255, 255 / 255)
        # obj.ViewObject.PointColor = (255 / 255, 0 / 255, 255 / 255)
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
