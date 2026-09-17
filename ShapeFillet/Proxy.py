# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol
from Part import Compound, Vertex
from BOPTools.GeneralFuseResult import GeneralFuseResult
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool, PropertyInteger, PropertyFloat
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.EdgeDef import EdgeDef
from utils.utils import getSelectionEx


FEATURE_NAME = "ShapeFillet"


#TODO does not work not idealy intersecting surafces
class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    Fillet: bool = PropertyBool("Shape", "If true, perform fillet on intersection.", True) #type: ignore
    Surfaces: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Surface that the wire is offseted on") #type: ignore
    Radius: float = PropertyFloat("Shape", "Fillet radius", 1.0) #type: ignore
    FirstChosenResult: int = PropertyInteger("Result", "", 1) #type: ignore
    SecondChosenResult: int = PropertyInteger("Result", "", 3) #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Surfaces:
            obj.Surfaces = getSelectionEx()
            obj.Surfaces[0][0].Visibility = False
            obj.Surfaces[1][0].Visibility = False

        firstSur = obj.Surfaces[0][0].Shape
        secondSur = obj.Surfaces[1][0].Shape

        listOfShapes = [firstSur, secondSur]

        intersection: ShapeLike = firstSur.section(secondSur)

        pieces, map = listOfShapes[0].generalFuse(listOfShapes[1:], 1e-3)
        gr = GeneralFuseResult(listOfShapes, (pieces, map))
        gr.splitAggregates()
        comp = Compound(gr.pieces)
        compResult = comp.Shells[obj.FirstChosenResult-1]
        result = compResult.fuse(comp.Shells[obj.SecondChosenResult-1])

        #TODO speedup new edges search
        edgesToFillet: list[EdgeDef] = []
        for i, edge in enumerate(result.Edges, start=1):
            e = EdgeDef(0, edge, None)
            for iEdge in intersection.Edges:
                if all([iEdge.distToShape(Vertex(p))[0] < 1e-3 for p in e.getDefPoints ]):
                    edgesToFillet.append(EdgeDef(i, edge, f"Edge{i}"))

        if obj.Fillet:
            result = result.makeFillet(obj.Radius, [e.edge for e in edgesToFillet])
        
        if obj.CheckShape:
            result.check()
        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)
        #obj.ViewObject.LineColor = (255/255, 0/255, 255/255)
        #obj.ViewObject.PointColor = (255/255, 0/255, 255/255)


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
