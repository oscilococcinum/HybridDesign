# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol, Literal
from Part import Compound, BSplineSurface
from BOPTools.JoinAPI import connect
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool, PropertyInteger, PropertyFloat, PropertyEnumeration
from utils.FreeCADInterfaces import FeatureLike, ShapeLike, Vector
from utils.EdgeDef import EdgeDef
from utils.FaceDef import FaceDef
from utils.utils import getSelectionEx
from utils.FaceGraph import getFaceEdgeNameMap, reverseFaceToEdgeMap


FEATURE_NAME = "Extrapolate"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    Edges: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Edges to extrapolate from") #type: ignore
    Fuse: bool = PropertyBool("Shape", "If true, fuse parent shape with extrapolation.", False) #type: ignore
    Distance: float = PropertyFloat("Shape", "", 1.0) #type: ignore
    Algorythm: Literal["Approximate", "Interpolate"] = PropertyEnumeration("Algo", "", ["Interpolate", "Approximate"]) #type: ignore
    ApproxTol: float = PropertyFloat("Algo", "", 1e-3) #type: ignore
    MinSamples: int = PropertyInteger("Discretization", "", 4) #type: ignore
    AngularDiscTol: float = PropertyFloat("Discretization", "", 1) #type: ignore
    CurvatureDiscTol: float = PropertyFloat("Discretization", "", 0.01) #type: ignore



class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Edges:
            obj.Edges = getSelectionEx()
            obj.Edges[0][0].Visibility = False

        surrFeature = obj.Edges[0][0]
        surr: ShapeLike = obj.Edges[0][0].Shape
        edges = obj.Edges[0][1]

        faceToEdgeMap = getFaceEdgeNameMap(surr.Faces)
        edgeToFaceMap = reverseFaceToEdgeMap(faceToEdgeMap)

        edgeDefMap = {x.hashCode(): EdgeDef(x.hashCode(), x, f"Edge{i}", edgeToFaceMap[x.hashCode()]) for i, x in enumerate(surr.Edges, start=1)}
        faceDefMap = {x.hashCode(): FaceDef(x.hashCode(), x, f"Face{i}") for i, x in enumerate(surr.Faces, start=1)}

        selectedEdges = [edgeDefMap[surrFeature.getSubObject(x).hashCode()] for x in edges]

        ptsFaces: list[tuple[list[Vector], FaceDef]] = [(x.edge.discretize(Angular=obj.AngularDiscTol, Curvature=obj.CurvatureDiscTol, Minimum=obj.MinSamples), faceDefMap[x.parentFaces[0]]) for x in selectedEdges]

        for i in range(1, len(ptsFaces)):
            prev1 = ptsFaces[i-1][0][-1]
            prev2 = ptsFaces[i-1][0][0]
            nextt1 = ptsFaces[i][0][0]
            nextt2 = ptsFaces[i][0][-1]
            d = [(prev1 - nextt1).Length, (prev1 - nextt2).Length,
                 (prev2 - nextt1).Length, (prev2 - nextt2).Length]
            
            dimin = d.index(min(d))

            if dimin == 0:
                pass
            if dimin == 1:
                ptsFaces[i][0].reverse()
            if dimin == 2:
                ptsFaces[i-1][0].reverse()
            if dimin == 3:
                ptsFaces[i][0].reverse()
                ptsFaces[i-1][0].reverse()

        startPts: list[list[Vector]] = []
        endPts: list[list[Vector]] = []
        for _, (pts, face) in enumerate(ptsFaces):
            tmpStartPts = []
            tmpEndPts = []
            for j in range(len(pts)):
                uv: tuple[float, float] = face.Surface.parameter(pts[j])#type: ignore

                normal = face.topoFace.normalAt(*uv)

                if j < len(pts) - 1:
                    tangent = (pts[j] - pts[j+1]).normalize()
                else:
                    tangent = ((pts[j] - pts[j-1]).normalize()) * -1

                tmpStartPts.append(pts[j])
                tmpEndPts.append(pts[j] + normal.cross(tangent).normalize()* obj.Distance)

            startPts.append(tmpStartPts)
            endPts.append(tmpEndPts)


        resList = []
        for s, e in zip(startPts, endPts):
            bss = BSplineSurface()
            transposed = [list(row) for row in zip(s, e)]
            
            match obj.Algorythm:
                case "Interpolate":
                    bss.interpolate(transposed)
                case "Approximate":
                    bss.approximate(transposed, Tolerance=obj.ApproxTol)
                case _:
                    bss.approximate(transposed, Tolerance=obj.ApproxTol)

            
            resList.append(bss.toShape())
        result = Compound(resList)

        if obj.Fuse:
            resList.append(surr)
            result = connect(resList)
        else:
            result = Compound(resList)


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
