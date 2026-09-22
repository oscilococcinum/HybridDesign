# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from utils.FreeCADInterfaces import ShapeLike
from collections import defaultdict
from dataclasses import dataclass
from utils.LazyShapeDict import LazyFaceDict, LazyEdgeDict, LazyVertDict
from functools import cached_property


@dataclass
class FaceWalker:
    currentShape: ShapeLike

    def __post_init__(self) -> None:
        self.HashToFace = LazyFaceDict(self.currentShape.Faces)
        self.HashToEdge = LazyEdgeDict(self.currentShape.Edges)

    @cached_property
    def FacesToEdges(self) -> dict[int, list[int]]:
        return {x.hashCode(): [y.hashCode() for y in x.Edges] for x in self.currentShape.Faces}

    @cached_property
    def EdgeToFace(self) -> dict[int, list[int]]:
        edgeToFaces: dict[int, list[int]] = defaultdict(list)

        for face, edges in self.FacesToEdges.items():
            for edge in edges:
                edgeToFaces[edge].append(face)

        return edgeToFaces

    def checkTan(self, faceHashed: int, edgeHashed: int, nextFaceHashed: int, angle_tol: float = 1e-3, samples: int = 5) -> bool: 

        if not (face_a := self.HashToFace[faceHashed].topoFace): raise RuntimeError("No hashcode in current faces container")
        if not (edge := self.HashToEdge[edgeHashed].edge): raise RuntimeError("No hashcode in current edge container")
        if not (face_b := self.HashToFace[nextFaceHashed].topoFace): raise RuntimeError("No hashcode in current faces container")

        u0, u1 = edge.ParameterRange

        for i in range(samples):
            t = i / (samples - 1)
            u = u0 + t * (u1 - u0)

            point = edge.valueAt(u)

            uv_a = face_a.Surface.parameter(point)
            uv_b = face_b.Surface.parameter(point)#type:ignore

            assert isinstance(uv_a, tuple)
            assert isinstance(uv_b, tuple)

            n_a = face_a.normalAt(*uv_a)
            n_b = face_b.normalAt(*uv_b)

            n_a.normalize()
            n_b.normalize()

            if abs(n_a.dot(n_b)) < 1.0 - angle_tol: #type:ignore
                return False
        return True

    def walkTangent(self, start_face: int, angleTol: float = 1e-6, samples: int = 5) -> list[int]:
        visited: set[int] = {start_face}
        stack: list[int] = [start_face]

        while stack:
            face = stack.pop()

            for edge in self.FacesToEdges.get(face, []):
                for other_face in self.EdgeToFace[edge]:

                    if other_face in visited:
                        continue

                    if not self.checkTan(face, edge, other_face, angleTol, samples):
                        continue

                    visited.add(other_face)
                    stack.append(other_face)

        return list(visited)

    def walkNN(self, startFace: int) -> list[int]:
        edges = self.FacesToEdges[startFace]
        fcs = [self.EdgeToFace[x] for x in edges]
        return list({x for sublist in fcs for x in sublist})

    def walkEnclose(self, start_face: int, enclosingFaces: list[int]) -> list[int]:
        visited: set[int] = {start_face}
        stack: list[int] = [start_face]

        while stack:
            face = stack.pop()

            for edge in self.FacesToEdges.get(face, []):
                for other_face in self.EdgeToFace[edge]:

                    if other_face in visited:
                        continue

                    if face in enclosingFaces:
                        continue
                    #if not self.checkTan(face, edge, other_face, angleTol, samples):
                    #    continue

                    visited.add(other_face)
                    stack.append(other_face)

        return list(visited)


@dataclass
class EdgeWalker:
    currentShape: ShapeLike

    def __post_init__(self) -> None:
        self.HashToVert = LazyVertDict(self.currentShape.Vertexes)
        self.HashToEdge = LazyEdgeDict(self.currentShape.Edges)

    @cached_property
    def EdgesToVerts(self) -> dict[int, list[int]]:
        return {x.hashCode(): [y.hashCode() for y in x.Vertexes] for x in self.currentShape.Edges}

    @cached_property
    def VertToEdge(self) -> dict[int, list[int]]:
        vertToEdges: dict[int, list[int]] = defaultdict(list)

        for edge, verts in self.EdgesToVerts.items():
            for vert in verts:
                vertToEdges[vert].append(edge)

        return vertToEdges

    def checkTan(self, edgeHashed: int, nextEdgeHashed: int, angle_tol: float=1e-3) -> bool: 
        if not (edge := self.HashToEdge[edgeHashed]): raise RuntimeError("No hashcode in current edge container")
        if not (nextEdge := self.HashToEdge[nextEdgeHashed]): raise RuntimeError("No hashcode in current edge container")

        conChecks = [
            (edge.startVec() - nextEdge.startVec()).Length,
            (edge.startVec() - nextEdge.endVec()).Length,
            (edge.endVec() - nextEdge.startVec()).Length,
            (edge.endVec() - nextEdge.endVec()).Length
        ]

        i = conChecks.index(min(conChecks))
        match i:
            case 0:
                eT = edge.edge.tangentAt(edge.edge.FirstParameter)
                neT = nextEdge.edge.tangentAt(nextEdge.edge.FirstParameter)
                return 1.0 - angle_tol < abs(eT.dot(neT)) < 1.0 + angle_tol
            case 1:
                eT = edge.edge.tangentAt(edge.edge.FirstParameter)
                neT = nextEdge.edge.tangentAt(nextEdge.edge.LastParameter)
                return 1.0 - angle_tol < abs(eT.dot(neT)) < 1.0 + angle_tol
            case 2:
                eT = edge.edge.tangentAt(edge.edge.LastParameter)
                neT = nextEdge.edge.tangentAt(nextEdge.edge.FirstParameter)
                return 1.0 - angle_tol < abs(eT.dot(neT)) < 1.0 + angle_tol
            case 3:
                eT = edge.edge.tangentAt(edge.edge.LastParameter)
                neT = nextEdge.edge.tangentAt(nextEdge.edge.LastParameter)
                return 1.0 - angle_tol < abs(eT.dot(neT)) < 1.0 + angle_tol
            case _:
                raise RuntimeError("Cannot check tangency!")

    def walkTangent(self, startEdge: int, angleTol: float=1e-3) -> list[int]:
        visited: set[int] = {startEdge}
        stack: list[int] = [startEdge]

        while stack:
            edge = stack.pop()

            for iEdge in self.EdgesToVerts.get(edge, []):
                for otherEdge in self.VertToEdge[iEdge]:

                    if otherEdge in visited:
                        continue

                    if not self.checkTan(edge, otherEdge, angleTol):
                        continue

                    visited.add(otherEdge)
                    stack.append(otherEdge)

        return list(visited)