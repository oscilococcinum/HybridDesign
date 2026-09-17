# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Protocol, Literal
from Part import makeShell #type: ignore
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool, PropertyEnumeration, PropertyFloat, PropertyInteger
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.FaceGraph import getFaceEdgeNameMap, buildFaceGraph
from utils.FaceWalker import FaceWalker
from utils.utils import getReferencedShapes, getSelectionEx
from utils.utils import timing

FEATURE_NAME = "Extract"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Contour to be extruded") #type: ignore
    Propagation: Literal["None", "NearestNeighbours", "Tangent"] = PropertyEnumeration("Additional", "Propagation policy", ["None", "NearestNeighbours", "Tangent"]) #type: ignore
    AngleTol: float = PropertyFloat("Detection", "Angle tolerance", 1e-3) #type: ignore
    EdgeSamples: int = PropertyInteger("Detection", "Number of edge split samples", 5) #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    @timing
    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()
            obj.RefShapes[0][0].Visibility = False

        currentShape: ShapeLike = obj.RefShapes[0][0].Shape
        obj.Shape = currentShape

        facesToJoin: list[ShapeLike] = getReferencedShapes(obj.RefShapes)
        #ODO toooo slow propably hashing is to slow
        tgTrack = FaceWalker(currentShape)
        match obj.Propagation:
            case "NearestNeighbours":
                nbs = tgTrack.walkNN(facesToJoin[0].hashCode())
                result: ShapeLike = makeShell([tgTrack.HashToFace[f].topoFace for f in nbs])
            case "Tangent":
                tgHashFaces: list[int] = tgTrack.walkTangent(facesToJoin[0].hashCode(), obj.AngleTol, obj.EdgeSamples)
                result: ShapeLike = makeShell([tgTrack.HashToFace[f].topoFace for f in tgHashFaces])
            case _:
                result: ShapeLike = makeShell(facesToJoin)

        if obj.CheckShape:
            result.check()

        obj.Shape = result

        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)


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
