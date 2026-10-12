# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol

from Part import (
    BSplineCurve,
    Vertex,
)

import FreeCAD as App

# from ..utils.EdgeDef import EdgeDef
# from ..utils.FaceDef import FaceDef
# from ..utils.FaceGraph import reverseFaceToEdgeMap
from ..utils.FreeCADInterfaces import FeatureLike, ShapeLike, Vector
from ..utils.PropDef import PropDef, PropertyFloat, PropertyInteger, PropertyLinkSubList
from ..utils.utils import getReferencedShapes, getSelectionEx

FEATURE_NAME = "OffsetCurve"


def getTangents(curveD: list[Vector]) -> list[Vector]:
    tangents = [(curveD[i - 1] - curveD[i]).normalize() for i in range(1, len(curveD))]
    tangents.insert(0, (curveD[-1] - curveD[-2]).normalize() * -1)

    return tangents.copy()


def getNormals(curveD: list[Vector], face: ShapeLike) -> list[Vector]:
    normals: list[Vector] = []
    for v in curveD:
        uv = face.Surface.parameter(v)
        assert isinstance(uv, tuple), "uv is not a tuple"
        normals.append(face.normalAt(*uv))

    return normals.copy()


class CurrentFeatureLike(FeatureLike, Protocol):
    Curve: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "")  # type: ignore
    Face: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "")  # type: ignore
    Offset: float = PropertyFloat("Offset", "", 1.0)  # type: ignore
    Steps: int = PropertyInteger("Offset", "", 10)  # type: ignore
    Samples: int = PropertyInteger("Curve", "", 10)  # type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Curve:
            obj.Curve = [getSelectionEx(hideSelection=False)[0]]
            obj.Face = [getSelectionEx(hideSelection=False)[1]]

        curve = getReferencedShapes(obj.Curve)[0]
        face = getReferencedShapes(obj.Face)[0]

        curveD = curve.discretize(obj.Samples)
        tangents = getTangents(curveD)
        normals = getNormals(curveD, face)
        cross = [x.cross(y).normalize() for x, y in zip(tangents, normals)]

        ds: float = obj.Offset / obj.Steps
        s = 0
        while s < obj.Offset:
            s += ds

            curveD = [x + y * ds for x, y in zip(curveD, cross)]
            curveD = [face.distToShape(Vertex(x))[1][0][1] for x in curveD]
            tangents = getTangents(curveD)
            normals = getNormals(curveD, face)
            cross = [x.cross(y).normalize() for x, y in zip(tangents, normals)]

        bsc = BSplineCurve()
        bsc.interpolate(curveD)
        bscs = bsc.toShape()

        obj.Shape = face.makeParallelProjection(bscs, App.Vector((0, 0, 1)))
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        # obj.ViewObject.ShapeColor = (0 / 255, 177 / 255, 255 / 255)
        # obj.ViewObject.AngularDeflection = "10 deg"
        obj.ViewObject.LineColor = (255 / 255, 0 / 255, 255 / 255)
        obj.ViewObject.PointColor = (255 / 255, 0 / 255, 255 / 255)
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
