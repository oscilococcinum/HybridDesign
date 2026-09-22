# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol
from Part import makeSolid #type: ignore
from utils.PropDef import PropDef, PropertyBool, PropertyLinkSubList, PropertyFloat, PropertyEnumeration
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.utils import getSelectionEx

FEATURE_NAME = "ThickenSurface"


offsetModeDict = {
        "skin":0,
        "pipe":1,
        "rectoVerso":2,
}

joinModeDict = {
        "arcs": 0,
        "tangent": 1,
        "intersection": 2,
}

class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Input feature eg. Extract") #type: ignore
    Offset: float = PropertyFloat("Shape", "Offset value", 1.0)  #type: ignore
    Tollerance: float = PropertyFloat("Shape", "Tollerance value", 1e-3) #type: ignore
    Inter: bool = PropertyBool("Shape", "Check intersection", False) #type: ignore
    SelfInter: bool = PropertyBool("Shape", "Check self intersection", False) #type: ignore
    OffsetMode: str = PropertyEnumeration("Shape", "Offset mode", [x for x in offsetModeDict.keys()]) #type: ignore
    Join: str = PropertyEnumeration("Shape", "Method of offsetting non-tangent joints", [x for x in joinModeDict.keys()]) #type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()
            obj.RefShapes[0][0].Visibility = False

        currentShape: ShapeLike = obj.RefShapes[0][0].Shape
        obj.Shape = currentShape

        if obj.BaseFeature:
            newShape: ShapeLike = makeSolid(currentShape.makeOffsetShape(obj.Offset, obj.Tollerance, obj.Inter, obj.SelfInter, offsetModeDict[obj.OffsetMode], joinModeDict[obj.Join], True))
            result: ShapeLike = obj.BaseFeature.Shape.fuse(newShape)
        else:
            result: ShapeLike = makeSolid(currentShape.makeOffsetShape(obj.Offset, obj.Tollerance, obj.Inter, obj.SelfInter, offsetModeDict[obj.OffsetMode], joinModeDict[obj.Join], True))

        if obj.CheckShape:
            result.check()

        obj.Shape = result

        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        pass
        #obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)

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
