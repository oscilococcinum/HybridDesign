# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol
from Part import BSplineCurve
import FreeCAD as App
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool, PropertyLength, PropertyInteger, PropertyFloat
from utils.FreeCADInterfaces import FeatureLike, ShapeLike, Vector
from utils.utils import getSelectionEx
from utils.utils import timing
import math

FEATURE_NAME = "CurvedHelix"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Contour to be extruded") #type: ignore
    Radius: float = PropertyLength("Shape", "Angle tolerance", 5.0) #type: ignore
    EdgeSamples: int = PropertyInteger("Detection", "Number of edge split samples", 200) #type: ignore
    Turns: float = PropertyFloat("Shape", "Angle tolerance", 8.0) #type: ignore
    InitialAngle: float = PropertyFloat("Shape", "Starting Angle", 0.0) #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    @timing
    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()

        currentShape: ShapeLike = obj.RefShapes[0][0].Shape
        obj.Shape = currentShape
        wire = currentShape.Wires[0]

        samples = obj.EdgeSamples
        radius = obj.Radius
        turns = obj.Turns

        spinePts: list[Vector]
        spinePts = wire.discretize(Number=samples)

        spiralPts = []

        for i in range(samples):

            P = spinePts[i]

            T: Vector
            # tangent
            if i == 0:
                T = spinePts[1] - spinePts[0]
            elif i == samples - 1:
                T = spinePts[-1] - spinePts[-2]
            else:
                T = spinePts[i + 1] - spinePts[i - 1]

            T.normalize()

            # build local frame
            up = App.Vector(0, 0, 1)

            if abs(T.dot(up)) > 0.95: #type: ignore
                up = App.Vector(1, 0, 0)

            X = up.cross(T)
            X.normalize()

            Y = T.cross(X)
            Y.normalize()

            angle = math.radians(obj.InitialAngle) + 2.0 * math.pi * turns * i / (samples - 1)

            offset = (                
                X * (radius * math.cos(angle))
                + Y * (radius * math.sin(angle)) #type: ignore
            )

            spiralPts.append(P + offset)

        # show points connected by spline
        curve = BSplineCurve()
        curve.interpolate(spiralPts)
        result = curve.toShape()

        if obj.CheckShape:
            result.check()
        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)
        obj.ViewObject.LineColor = (255/255, 0/255, 255/255)


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
