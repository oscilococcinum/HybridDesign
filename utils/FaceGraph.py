# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from utils.FreeCADInterfaces import ShapeLike
from collections import defaultdict

class FaceGraph:
    def __init__(self) -> None:
        self.neighbours: dict[int, set[int]] = {}

    def addFace(self, face: int) -> None:
        if face not in self.neighbours:
            self.neighbours[face] = set()

    def connect(self, face_a: int, face_b: int) -> None:
        self.addFace(face_a)
        self.addFace(face_b)

        self.neighbours[face_a].add(face_b)
        self.neighbours[face_b].add(face_a)

    def getNeighbours(self, face: int) -> set[int]:
        return self.neighbours.get(face, set())


def buildFaceGraph(face_to_edges: dict[int, list[int]]) -> FaceGraph:
    graph = FaceGraph()

    edge_to_faces: dict[int, list[int]] = {}

    for face, edges in face_to_edges.items():
        graph.addFace(face)

        for edge in edges:
            if edge not in edge_to_faces:
                edge_to_faces[edge] = []

            edge_to_faces[edge].append(face)

    for faces in edge_to_faces.values():
        for index, face_a in enumerate(faces):
            for face_b in faces[index + 1:]:
                graph.connect(face_a, face_b)

    return graph

def getFaceEdgeNameMap(faces: list[ShapeLike]) -> dict[int, list[int]]:
    return {face.hashCode(): [edge.hashCode() for edge in face.Edges] for face in faces}

def reverseFaceToEdgeMap(facesToEdges: dict[int, list[int]]) -> dict[int, list[int]]:
    edgeToFaces: dict[int, list[int]] = defaultdict(list)

    for face, edges in facesToEdges.items():
        for edge in edges:
            edgeToFaces[edge].append(face)

    return dict(edgeToFaces)
