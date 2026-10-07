# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Literal, Protocol

from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeFilling
from OCC.Core.GeomAbs import GeomAbs_G1
from OCC.Core.TopoDS import topods
from Part import __fromPythonOCC__ as fromOCC
from Part import __toPythonOCC__ as toOCC

from FreeCAD import ActiveDocument

from ..utils.EdgeDef import EdgeDef
from ..utils.FaceDef import FaceDef
from ..utils.FaceGraph import reverseFaceToEdgeMap
from ..utils.FreeCADInterfaces import FeatureLike
from ..utils.PropDef import PropDef, PropertyEnumeration, PropertyLinkSubList
from ..utils.utils import getSelectionEx, sortEdges

FEATURE_NAME = "Fill"


class CurrentFeatureLike(FeatureLike, Protocol):
    Edges: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "")  # type: ignore
    Continuity: Literal["G0", "G1"] = PropertyEnumeration("Input", "", ["G0", "G1"])  # type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Edges:
            obj.Edges = getSelectionEx(hideSelection=True)

        match obj.Continuity:
            case "G1":

                shell = obj.Edges[0][0].Shape
                selEdgeDefs = {
                    obj.Edges[0][0]
                    .getSubObject(x)
                    .hashCode(): EdgeDef(
                        obj.Edges[0][0].getSubObject(x).hashCode(),
                        obj.Edges[0][0].getSubObject(x),
                        x,
                    )
                    for x in obj.Edges[0][1]
                }
                faceDefs = {
                    f.hashCode(): FaceDef(f.hashCode(), f, f"Face{i}")
                    for i, f in enumerate(shell.Faces, start=1)
                }
                edgeDefs = {
                    f.hashCode(): EdgeDef(f.hashCode(), f, f"Edge{i}")
                    for i, f in enumerate(shell.Edges, start=1)
                }

                faceEdgeMap = {
                    f.hashCode(): [e.hashCode() for e in f.Edges] for f in shell.Faces
                }
                edgeToFaceMap = reverseFaceToEdgeMap(faceEdgeMap)

                occSelectedEdgesToFaces = {
                    toOCC(edgeDefs[hsh].edge): toOCC(
                        faceDefs[edgeToFaceMap[hsh][0]].topoFace
                    )
                    for hsh, _ in selEdgeDefs.items()
                }

                fill = BRepOffsetAPI_MakeFilling()

                for occEdge, occFace in occSelectedEdgesToFaces.items():
                    fill.Add(
                        topods.Edge(occEdge), topods.Face(occFace), GeomAbs_G1, True
                    )

                fill.Build()
                result = fromOCC(fill.Shape())

            case "G0" | _:
                edgeNames = obj.Edges[0][1]

                edgeDict = {
                    obj.Edges[0][0].Shape.getElement(name): name for name in edgeNames
                }

                edges = sortEdges(list(edgeDict.keys()))

                boudaryEdges = tuple(edgeDict[edge] for edge in edges)

                fillObj = ActiveDocument.addObject("Surface::Filling", "Filling")

                fillObj.BoundaryEdges = [(obj.Edges[0][0], boudaryEdges)]
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
