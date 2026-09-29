# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from collections.abc import Callable
from typing import Literal, Protocol

from Part import Edge, Face, Solid, Vertex, Wire, makeCompound, makeShell

from ..utils.FreeCADInterfaces import FeatureLike, ShapeLike
from ..utils.PropDef import (
    PropDef,
    PropertyBool,
    PropertyEnumeration,
    PropertyFloat,
    PropertyInteger,
    PropertyLinkSubList,
)
from ..utils.utils import getReferencedShapes, getSelectionEx, timing
from ..utils.Walker import EdgeWalker, FaceWalker

FEATURE_NAME = "Extract"

extractionReg: dict[type, Callable[[list[ShapeLike]], ShapeLike]] = {
    Face: makeShell,
    Edge: Wire,
    Vertex: makeCompound,
}


def makeShapeWithReg(subShapes: list[ShapeLike]) -> ShapeLike:
    if not all([type(subShapes[0]) is type(x) for x in subShapes]):
        raise RuntimeError("Selection has to contain elements of the same type!")
    creationFunc = extractionReg[type(subShapes[0])]
    return creationFunc(subShapes)


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True)  # type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Contour to be extruded")  # type: ignore
    Propagation: Literal["None", "NearestNeighbours", "Tangent"] = PropertyEnumeration("Additional", "Propagation policy", ["None", "NearestNeighbours", "Tangent"])  # type: ignore
    AngleTol: float = PropertyFloat("Detection", "Angle tolerance", 1e-3)  # type: ignore
    EdgeSamples: int = PropertyInteger("Detection", "Number of edge split samples", 5)  # type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)
        self.elementsType: type | None = None

    @timing
    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx(hideSelection=True)

        currentShape: ShapeLike = obj.RefShapes[0][0].Shape
        obj.Shape = currentShape

        facesToJoin: list[ShapeLike] = getReferencedShapes(obj.RefShapes)

        self.elementsType = type(facesToJoin[0])

        if type(facesToJoin[0]) is Edge and obj.Propagation not in [
            "Tangent",
            "None",
        ]:
            obj.Propagation = "None"
        elif type(facesToJoin[0]) in [Vertex, Solid]:
            obj.Propagation = "None"
        else:
            pass

        if type(facesToJoin[0]) is Face:
            tgTrack = FaceWalker(currentShape)
            match obj.Propagation:
                case "NearestNeighbours":
                    nbs = tgTrack.walkNN(facesToJoin[0].hashCode())
                    result: ShapeLike = makeShapeWithReg(
                        [tgTrack.HashToFace[f].topoFace for f in nbs]
                    )
                case "Tangent":
                    tgHashFaces: list[int] = tgTrack.walkTangent(
                        facesToJoin[0].hashCode(), obj.AngleTol, obj.EdgeSamples
                    )
                    result: ShapeLike = makeShapeWithReg(
                        [tgTrack.HashToFace[f].topoFace for f in tgHashFaces]
                    )
                case "None":
                    result: ShapeLike = makeShapeWithReg(facesToJoin)
                case _:
                    raise RuntimeError("Invalid Propagation type!")
        elif type(facesToJoin[0]) is Edge:
            tgTrack = EdgeWalker(currentShape)
            match obj.Propagation:
                case "NearestNeighbours":
                    raise RuntimeError("Not implemented for this type of element!")
                case "Tangent":
                    tgHashFaces: list[int] = tgTrack.walkTangent(
                        facesToJoin[0].hashCode(), obj.AngleTol
                    )
                    print(tgHashFaces)
                    result: ShapeLike = makeShapeWithReg(
                        [tgTrack.HashToEdge[f].edge for f in tgHashFaces]
                    )
                case "None":
                    result: ShapeLike = makeShapeWithReg(facesToJoin)
                case _:
                    raise RuntimeError("Invalid Propagation type!")
        elif type(facesToJoin[0]) is Vertex:
            result: ShapeLike = makeShapeWithReg(facesToJoin)
        else:
            raise RuntimeError("Not implemented for this type of element!")

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
        elif self.elementsType is Edge:
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

    def onChanged(self, obj: CurrentFeatureLike, prop: str) -> None:
        pass

    def __getstate__(self):
        return {"Type": self.Type}

    def __setstate__(self, state):
        self.Type = state.get("Type", self.getFeatureName())
