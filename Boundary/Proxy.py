# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Protocol
from Part import Compound #type:ignore
from utils.PropDef import PropDef, PropertyBool, PropertyFloat, PropertyInteger, PropertyLinkSubList
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.FaceGraph import getFaceEdgeNameMap, reverseFaceToEdgeMap
from utils.utils import getSelectionEx
from utils.EdgeDef import EdgeDef
from utils.FaceDef import FaceDef

FEATURE_NAME = "Boundary"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    ChosenResult: int = PropertyInteger("Shape", "", 1) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Open surface") #type: ignore
    BSplineApprox: bool = PropertyBool("Approx", "If true, approximate wire with BSpline.", False) #type: ignore
    Tol2d: float = PropertyFloat("Approx", "2D tollerance", 1e-4) #type: ignore
    Tol3d: float = PropertyFloat("Approx", "3D tollerance", 1e-4)  #type: ignore
    MaxSegments: int = PropertyInteger("Approx", "Maximum number of segments produced", 1000)  #type: ignore
    MaxDegree: int = PropertyInteger("Approx", "Maximum degree of BSpline", 10) #type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()

        currentShape: ShapeLike = obj.RefShapes[0][0].Shape

        edgeDefMap = {x.hashCode(): EdgeDef(x.hashCode(), x, f"Edge{i}") for i, x in enumerate(currentShape.Edges, start=1)}

        faceToEdgeMap = getFaceEdgeNameMap(currentShape.Faces)
        edgeToFaceMap = reverseFaceToEdgeMap(faceToEdgeMap)

        lonleyEdges = [k for k, v in edgeToFaceMap.items() if len(v) == 1]
        edges = [edgeDefMap[hsh].edge for hsh in lonleyEdges]

        comp = Compound(edges)

        if obj.BSplineApprox:
            wire = comp.makeWires("").Wires[obj.ChosenResult-1].approximate(Tol2d=obj.Tol2d,Tol3d=obj.Tol3d,MaxSegments=obj.MaxSegments,MaxDegree=obj.MaxDegree).toShape()
        else:
            wire = comp.makeWires("").Wires[obj.ChosenResult-1]

        result: ShapeLike = wire

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
