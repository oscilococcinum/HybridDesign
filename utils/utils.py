# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
import Part #type: ignore
from functools import wraps
from time import time
from collections.abc import Callable
from typing import Any
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
import FreeCADGui as Gui
import FreeCAD as App
from utils.FreeCADInterfaces import Vector, ShapeLike
from collections import defaultdict
from utils.FaceDef import FaceDef
from utils.VertexDef import VertexDef


def getReferencedShapes(refShapes: list[tuple[FeatureLike, tuple[str]]]) -> list[ShapeLike]:
    shapes: list[ShapeLike] = []

    for feature, subnames in refShapes:
        for subname in subnames:
            shape = feature.Shape.getElement(subname)
            shapes.append(shape)

    return shapes

def getSelectionEx() -> list[tuple[FeatureLike, tuple[str]]]:
    refs = []
    for sel in Gui.Selection.getSelectionEx():
        if sel.SubElementNames:
            refs.append((sel.Object, sel.SubElementNames))
        else:
            refs.append((sel.Object, ('')))
    return refs

def timing(f: Callable[..., Any], args: bool=True) -> Callable[..., Any]:
    @wraps(f)
    def wrap(*args: list[Any], **kw: dict[Any, Any]):
            ts = time()
            result = f(*args, **kw)
            te = time()
            print('func:%r args:[%r, %r] took: %2.4f sec' % \
                (f.__name__, args, kw, te-ts))
            return result
    return wrap

def timingWOArgs(f: Callable[..., Any], args: bool=True) -> Callable[..., Any]:
    @wraps(f)
    def wrap(*args: list[Any], **kw: dict[Any, Any]):
            ts = time()
            result = f(*args, **kw)
            te = time()
            print('func:%r took: %2.4f sec' % \
                (f.__name__, te-ts))
            return result
    return wrap


def oldNormalOnShell(shell: ShapeLike, point: Vector) -> Vector:
    if not shell.Faces:
        raise ValueError("Shape contains no faces")

    pointVertex = Part.Vertex(point)

    bestDistance = float("inf")
    bestFace = None
    bestPoint = None

    for face in shell.Faces:
        distance, pointPairs, info = pointVertex.distToShape(face)

        if pointPairs and distance < bestDistance:
            bestDistance = distance
            bestFace = face
            bestPoint = pointPairs[0][0]


    if bestFace is None or bestPoint is None:
        raise RuntimeError("Could not find closest face on shell")

    u, v = bestFace.Surface.parameter(point)

    normal = bestFace.normalAt(u, v)
    normal.normalize()

    return normal#, bestPoint, bestFace

def newNormalOnShell(shell: ShapeLike, point: Vector) -> Vector:
    if not shell.Faces:
        raise ValueError("Shape contains no faces")

    hashToFace = {x.hashCode(): FaceDef(x.hashCode(), x, f"Face{i}") for i, x in enumerate(shell.Faces, start=1)}
    hashToVert = {x.hashCode(): VertexDef(x.hashCode(), x, f"Vertex{i}") for i, x in enumerate(shell.Vertexes, start=1)}

    faceToVertex = {f: f.Vertexes for f in shell.Faces}
    verToFaces: dict[ShapeLike, list[ShapeLike]] = defaultdict(list)
    for face, vers in faceToVertex.items():
        for ver in vers:
            verToFaces[ver].append(face)
    [print(f"{x}: {y}") for x, y in verToFaces.items()]

    surfaceVerts = [x for x in shell.Vertexes]
    surfaceDists = [(point - x.Point).Length for x in shell.Vertexes]
    #print(surfaceDists)
    index = surfaceDists.index(min(surfaceDists))
    #print(index)
    closestSurfaces = verToFaces[surfaceVerts[index]]
    #print(closestSurfaces)

    bestDistance = float("inf")
    bestFace = None

    for face in closestSurfaces:
        distance, _, _ = App.Vertex(point).distToShape(face)
        #print(distance)

        if distance < bestDistance:
            bestDistance = distance
            bestFace = face


    if bestFace is None:
        raise RuntimeError("Could not find closest face on shell")

    uv = bestFace.Surface.parameter(point)

    assert uv is tuple

    normal = bestFace.normalAt(uv[0], uv[1])
    normal.normalize()

    return normal#, bestPoint, bestFace
