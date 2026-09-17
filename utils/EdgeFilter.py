# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Self, Literal
from Part import Edge, Face, Vertex #type: ignore
from utils.EdgeDef import EdgeDef
from utils.FaceDef import FaceDef
from utils.FreeCADInterfaces import Vector
from math import acos, degrees
from utils.utils import timing
import numpy as np


def pointOnLine(start: tuple[float, float, float], stop: tuple[float, float, float], p: tuple[float, float, float], tol: float=1e-3) -> bool:
    A = np.array(start, dtype=float)
    B = np.array(stop, dtype=float)
    P = np.array(p, dtype=float)

    AB = B - A
    AP = P - A

    ab_len_sq = np.dot(AB, AB)
    if ab_len_sq == 0:
        return bool(np.linalg.norm(P - A) < tol)

    t = np.dot(AP, AB) / ab_len_sq

    if t < -tol or t > 1 + tol:
        return False

    projection = A + t * AB

    return bool(np.linalg.norm(P - projection) < tol)

def sameDirection(v1: tuple[float, float, float], v2: tuple[float, float, float], tolerance_deg: float) -> bool:
    dot = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

    dot = max(-1.0, min(1.0, dot))

    angle_deg = degrees(acos(dot))
    return angle_deg <= tolerance_deg

class EdgeFilter:
    def __init__(self, edges: list[Edge] | list[Edge]) -> None:
        self._edges: list[EdgeDef] = [EdgeDef(i, j) for i, j in enumerate(edges, start=1)]
        self._compEdges: list[EdgeDef] = []
        self._compFaces: list[FaceDef] = []
        self._currFaces: list[FaceDef] = []
        self._result: list[EdgeDef] = self._edges

    def getResult(self) -> list[EdgeDef]:
        return self._result

    def getEdges(self) -> list[Edge]:
        return [i.edge for i in self._result]

    def addCompEdges(self, edges: list[Edge]) -> Self:
        self._compEdges = [EdgeDef(i, j) for i, j in enumerate(edges, start=1)]
        return self

    def addCompFaces(self, faces: list[Face]) -> Self:
        self._compFaces = [FaceDef(i, j) for i, j in enumerate(faces, start=1)]
        return self

    def addCurrFaces(self, faces: list[Face]) -> Self:
        self._currFaces = [FaceDef(i, j) for i, j in enumerate(faces, start=1)]
        return self

    def diffWithCompEdges(self) -> Self:
        newEdgePos: list[EdgeDef] = self._result
        prevEdgePos: list[EdgeDef] = self._compEdges
        newEdges: list[EdgeDef] = []

        for i in newEdgePos:
            newDefPoints = i.getDefPoints
            hasDuplicate = False
            for j in prevEdgePos:
                if newDefPoints == j.getDefPoints:
                    hasDuplicate = True
            if not hasDuplicate:
                newEdges.append(i)

        self._result = newEdges
        return self

    def intersectWithComp(self, tollerance: float) -> Self:
        newEdges: list[EdgeDef] = []

        for edge in self._result:
            for face in self._compFaces:
                verts: list[Vertex] = [Vertex(i) for i in edge.getDefPoints]
                dists = [vert.distToShape(face.topoFace)[0] for vert in verts]
                if all([i < tollerance for i in dists]):
                    newEdges.append(edge)
                    break

        self._result = newEdges
        return self

    def revIntersectWithComp(self, tollerance: float) -> Self:
        newEdges: list[EdgeDef] = self._result.copy()

        for edge in self._result:
            for face in self._compFaces:
                verts: list[Vertex] = [Vertex(i) for i in edge.getDefPoints]
                dists = [vert.distToShape(face.topoFace)[0] for vert in verts]
                if all([i < tollerance for i in dists]):
                    newEdges.remove(edge)
                    break

        self._result = newEdges
        return self

    def removeSeamEdges(self) -> Self:
        for edge in self._result:
            for face in self._currFaces:
                if edge.edge.isSeam(face.topoFace):
                    self._result.remove(edge)

        return self

    def removeSplitedDuplicates(self, tollerance: float=1e-3, nonLinearDetectionPolicy: Literal["None", "OCC", "SplitIntoLines"] = "SplitIntoLines", nonLinearSplitDist: float=1.0) -> Self:
        for newEdge in self._result:
            verts = [e for e in newEdge.getDefPoints]
            for oldEdge in self._compEdges:
                if nonLinearDetectionPolicy == "None":
                    dists = [v.distanceToLineSegment(oldEdge.startVec(), oldEdge.endVec()).Length for v in verts]
                    if all([x <= tollerance for x in dists]):
                        self._result.remove(newEdge)
                        break
                elif nonLinearDetectionPolicy == "SplitIntoLines":
                    discretisedPoints: list[Vector] = oldEdge.edge.discretize(Distance=nonLinearSplitDist)
                    dists = [[v.distanceToLineSegment(discretisedPoints[i], discretisedPoints[i+1]).Length for i in range(len(discretisedPoints) - 1)] for v in verts]
                    if all([all([y <= tollerance for y in x]) for x in dists]):
                        self._result.remove(newEdge)
                        break
                elif nonLinearDetectionPolicy =="OCC": 
                    dists = [oldEdge.edge.distToShape(Vertex(v))[0] for v in verts]
                    if all([x <= tollerance for x in dists]):
                        self._result.remove(newEdge)
                        break

        return self
    
    def getEdgesByDir(self, dirr: tuple[float, float, float], tolerance: float=1e-3) -> Self:
        newEdges: list[EdgeDef] = []
        for edge in self._result:
            if sameDirection(edge.getEdgeDir(absVal=True), dirr, tolerance):
                newEdges.append(edge)

        self._result = newEdges
        return self