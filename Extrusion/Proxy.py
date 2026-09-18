# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol, Literal
import FreeCAD as App
from utils.PropDef import PropDef, PropertyBool, PropertyLinkSubList, PropertyLinkSub, PropertyStringList, PropertyFloat, PropertyEnumeration
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.EdgeDef import EdgeDef
from utils.utils import getSelectionEx
from Part import Compound, makeShell

FEATURE_NAME = "Extrusion"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shapef", "If true, perform validity check on shape.", True) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Input feature or subshapes", ) #type: ignore
    CustomDirRef: tuple[FeatureLike, tuple[str]] = PropertyLinkSub("Direction", "Edge ref") #type: ignore
    Direction: Literal['X', 'Y', 'X', 'Vector', 'Custom'] = PropertyEnumeration("Direction", "Enable directional filtering", ["X", "Y", "Z", "Vector", "Custom"]) #type: ignore
    Vector: list[str] = PropertyStringList("Direction", "Custom vector dir", ["0", "0", "1"]) #type: ignore
    Magnitude: float = PropertyFloat("Direction", "Extrude magnitude.",  10.0) #type: ignore
    ReverseMagnitude: float = PropertyFloat("Direction", "Extrude reverse direction magnitude.",  0.0) #type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()
            obj.RefShapes[0][0].Visibility = False

        wires = [[ob.getSubObject(e) for e in el] for ob, el in obj.RefShapes]
        wiresConc = [item for sublist in wires for item in sublist]
        currentShape: ShapeLike = Compound(wiresConc)

        obj.Shape = currentShape

        match obj.Direction:
            case "X" | "Y" | "Z":
                dirDict = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1),}
                result: ShapeLike = currentShape.extrude(App.Vector(dirDict[obj.Direction]) * obj.Magnitude)
                if obj.ReverseMagnitude != 0.0:
                    revResult = currentShape.extrude(App.Vector(dirDict[obj.Direction]) * -obj.ReverseMagnitude)
                    for face in revResult.Faces:
                        face.reverse()
                        result.add(face)
            case "Vector":
                result: ShapeLike = currentShape.extrude(App.Vector([float(i) for i in obj.Vector]).normalize() * obj.ReverseMagnitude)
                if obj.ReverseMagnitude != 0.0:
                    revResult = currentShape.extrude(App.Vector([float(i) for i in obj.Vector]).normalize() * -obj.ReverseMagnitude)
                    for face in revResult.Faces:
                        face.reverse()
                        result.add(face)
            case "Custom":
                sourceObj, subName = obj.CustomDirRef
                e = sourceObj.getSubObject(subName[0])
                edge = EdgeDef(e.hashCode(), e)
                dir = App.Vector(edge.getEdgeDir()).normalize()
                result: ShapeLike = currentShape.extrude(dir * obj.Magnitude)
                if obj.ReverseMagnitude != 0.0:
                    revResult = currentShape.extrude(dir * -obj.ReverseMagnitude)
                    for face in revResult.Faces:
                        face.reverse()
                        result.add(face)

        result = makeShell(result.Faces)

        if obj.CheckShape:
            result.check()

        obj.Shape = result

        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)

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
