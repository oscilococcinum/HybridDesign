# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Protocol, Literal
import FreeCADGui as Gui #type: ignore
import FreeCAD as App #type: ignore
from utils.PropDef import PropDef, PropertyEnumeration, PropertyFloat, PropertyStringList, PropertyLength, PropertyBool
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.EdgeDef import EdgeDef
from utils.EdgeFilter import EdgeFilter

FEATURE_NAME = "AutoFillet"

class CurrentFeatureLike(FeatureLike, Protocol):
    DirectionalFiltering: Literal["Any", "X", "Y", "Z", "Custom"] = PropertyEnumeration("Direction", "Enable directional filtering", ["Any", "X", "Y", "Z", "Custom"])  #type: ignore
    Tolerance: float = PropertyLength("Detection", "Geometric tolerance used to compare previous and current edges.", 0.001) #type: ignore
    FilterType: Literal["New Edges", "Intersection", "ReverseIntersection", "Any"] = PropertyEnumeration("Filter", "Select type of filter that will be applied", ["New Edges", "Intersection", "ReverseIntersection", "Any"])  #type: ignore
    DetectedEdges: list[str] = PropertyStringList("Detection", "All edges detected as created by the BaseFeature operation.") #type: ignore
    DirTolerance: float = PropertyFloat("Direction", "Tollerance of direnction in degres", 1e-3) #type: ignore
    Radius: float = PropertyLength("Fillet", "Fillet radius.", 2.0) #type: ignore
    NonLinearSplitDist: float = PropertyLength("Detection", "When policy is SplitIntoLines it defines step bewtwen cuts.", 1.0) #type: ignore
    NonLinearDetectionPolicy: Literal["OCC", "SplitIntoLines", "None"] = PropertyEnumeration("Detection", "Select type of policy that will be applied", ["None", "SplitIntoLines", "OCC"]) #type: ignore
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)


    def execute(self, obj: CurrentFeatureLike):
        baseFeature: FeatureLike = obj.BaseFeature
        currentShape: ShapeLike = baseFeature.Shape.copy()

        match obj.FilterType:
            case "New Edges":
                previousFeature: FeatureLike = baseFeature.BaseFeature
                previousShape: ShapeLike = previousFeature.Shape
                edges: list[EdgeDef] = (EdgeFilter(currentShape.Edges)
                                        .addCompEdges(previousShape.Edges)
                                        .addCurrFaces(currentShape.Faces)
                                        .diffWithCompEdges()
                                        .removeSplitedDuplicates(tollerance=obj.Tolerance,
                                                                 nonLinearDetectionPolicy=obj.NonLinearDetectionPolicy,
                                                                 nonLinearSplitDist=obj.NonLinearSplitDist)
                                        .removeSeamEdges()
                                        .getResult())
            case "Intersection":
                previousFeature: FeatureLike = baseFeature.BaseFeature
                previousShape: ShapeLike = previousFeature.Shape
                edges: list[EdgeDef] = (EdgeFilter(currentShape.Edges)
                                        .addCompEdges(previousShape.Edges)
                                        .addCompFaces(previousShape.Faces)
                                        .addCurrFaces(currentShape.Faces)
                                        .diffWithCompEdges()
                                        .intersectWithComp(obj.Tolerance)
                                        .removeSplitedDuplicates(tollerance=obj.Tolerance,
                                                                 nonLinearDetectionPolicy=obj.NonLinearDetectionPolicy,
                                                                 nonLinearSplitDist=obj.NonLinearSplitDist)
                                        .removeSeamEdges()
                                        .getResult())
            case "ReverseIntersection":
                previousFeature: FeatureLike = baseFeature.BaseFeature
                previousShape: ShapeLike = previousFeature.Shape
                edges: list[EdgeDef] = (EdgeFilter(currentShape.Edges)
                                        .addCompEdges(previousShape.Edges)
                                        .addCompFaces(previousShape.Faces)
                                        .addCurrFaces(currentShape.Faces)
                                        .diffWithCompEdges()
                                        .revIntersectWithComp(obj.Tolerance)
                                        .removeSplitedDuplicates(tollerance=obj.Tolerance,
                                                                 nonLinearDetectionPolicy=obj.NonLinearDetectionPolicy,
                                                                 nonLinearSplitDist=obj.NonLinearSplitDist)
                                        .removeSeamEdges()
                                        .getResult())
            case _:
                edges: list[EdgeDef] = [EdgeDef(i, e) for i, e  in enumerate(currentShape.Edges)]

        match obj.DirectionalFiltering:
            case "X" | "Y" | "Z":
                dirDict = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1),}
                edges: list[EdgeDef] = EdgeFilter([e.edge for e in edges]).getEdgesByDir(dirDict[obj.DirectionalFiltering], obj.DirTolerance).getResult()
            case _:
                pass

        obj.DetectedEdges = [f'Edge{i.id}' for i in edges]
        obj.Shape = currentShape
        result: ShapeLike = currentShape.makeFillet(obj.Radius, [e.edge for e in edges])
        if obj.CheckShape: result.check()
        obj.Shape = result

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
