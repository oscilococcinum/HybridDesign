# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from dataclasses import dataclass, field
from functools import cached_property
from .FreeCADInterfaces import ShapeLike, Vector


@dataclass
class EdgeDef:
    id: int 
    edge: ShapeLike
    name: str | None = None
    parentFaces: list[int] = field(default_factory=list)

    @cached_property
    def getDefPoints(self, posintions: list[float] = [0, 0.25, .5, 0.75, 1]) -> tuple[Vector, ...]:
        return tuple(self.edge.valueAt(self.edge.FirstParameter + x * (self.edge.LastParameter - self.edge.FirstParameter)) for x in posintions)

    def startVec(self) -> Vector:
        return self.edge.firstVertex().Point

    def endVec(self) -> Vector:
        return self.edge.lastVertex().Point

    def getEdgeDir(self, absVal: bool=False) -> tuple[float, float, float]:
        start: Vector = self.getDefPoints[0]
        stop: Vector = self.getDefPoints[-1]
        dirr: Vector = stop - start

        if dirr.Length == 0:
            div = 1
        else:
            div = dirr.Length

        if absVal:
            return (abs(dirr.x/div), abs(dirr.y/div), abs(dirr.z/div))
        else:
            return (dirr.x/div, dirr.y/div, dirr.z/div)

    def isStraight(self, tollerance: float=1e-3) -> bool:
        vecs = self.getDefPoints
        dists = [v.distanceToLineSegment(self.startVec(), self.endVec()).Length for v in vecs]
        if all([x <= tollerance for x in dists]):
            return True
        else:
            return False
