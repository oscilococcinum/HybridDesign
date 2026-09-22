# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol
from Part import makeShell, BSplineCurve, Compound, Vertex #type: ignore
import FreeCAD as App #type: ignore
import FreeCADGui as Gui# type: ignore
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool, PropertyInteger, PropertyFloat
from utils.FreeCADInterfaces import FeatureLike, ShapeLike, Vector
from utils.utils import getSelectionEx
from utils.utils import timing, newNormalOnShell

FEATURE_NAME = "PararellCurve"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    BaseSurface: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Surface that the wire is offseted on") #type: ignore
    Wire: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Wire to be offseted") #type: ignore
    Offset: float = PropertyFloat("Shape", "Wire offset", 5.0) #type: ignore
    EdgeSamples: int = PropertyInteger("Detection", "Number of edge split samples", 200) #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    @timing
    def execute(self, obj: CurrentFeatureLike):
        if not obj.Wire and not obj.BaseSurface:
            obj.Wire = [getSelectionEx()[0]]
            obj.BaseSurface = [getSelectionEx()[1]]

        currentShape: ShapeLike = obj.Wire[0][0].Shape
        obj.Shape = currentShape

        wire: ShapeLike = obj.Wire[0][0].Shape
        surface: ShapeLike = obj.BaseSurface[0][0].Shape

        spinePts: list[Vector] = wire.discretize(Number=obj.EdgeSamples)
        wireTangents = [(spinePts[x] - spinePts[x-1]).normalize() for x in range(1, len(spinePts))]
        surfaceNormals = [newNormalOnShell(surface, x) for x in spinePts]
        inwardTangent = [x.cross(y).normalize() * obj.Offset + z for x, y, z in zip(wireTangents, surfaceNormals, spinePts)]

        curve = BSplineCurve()
        curve.interpolate(inwardTangent)
        #result = curve.toShape()
        result = Compound([Vertex(x) for x in inwardTangent])

        if obj.CheckShape:
            result.check()
        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)
        obj.ViewObject.LineColor = (255/255, 0/255, 255/255)
        obj.ViewObject.PointColor = (255/255, 0/255, 255/255)


    @classmethod
    def getFeatureName(cls) -> str:
        return FEATURE_NAME

    def add_properties(self, obj: CurrentFeatureLike):
        properties: list[tuple[str, PropDef]] = []
        for i, _ in CurrentFeatureLike.__dict__.items():
            if i[0] != '_':
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
