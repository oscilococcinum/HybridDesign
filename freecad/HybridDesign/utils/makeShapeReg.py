# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from collections.abc import Callable

from Part import Edge, Face, Vertex, Wire
from Part import __sortEdges__ as sortEdges
from Part import makeCompound, makeShell

from .FreeCADInterfaces import ShapeLike


def makeWire(edges: list[ShapeLike]) -> Wire:
    sortedEdges = sortEdges(edges)
    return Wire(sortedEdges)


extractionReg: dict[type, Callable[[list[ShapeLike]], ShapeLike]] = {
    Face: makeShell,
    Edge: makeWire,
    Vertex: makeCompound,
    Wire: Wire,
}


def makeShapeWithReg(subShapes: list[ShapeLike]) -> ShapeLike:
    if not all([type(subShapes[0]) is type(x) for x in subShapes]):
        raise RuntimeError("Selection has to contain elements of the same type!")
    creationFunc = extractionReg[type(subShapes[0])]
    return creationFunc(subShapes)
