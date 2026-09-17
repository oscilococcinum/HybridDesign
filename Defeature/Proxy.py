# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Protocol
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.utils import getSelectionEx

FEATURE_NAME = "Defeature"

class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Faces to be removed") #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()

        baseFeature: FeatureLike = obj.BaseFeature
        currentShape: ShapeLike = baseFeature.Shape.copy()

        obj.Shape = currentShape

        faces: list[str] = []
        print(obj.RefShapes)
        for feature, subNameList in obj.RefShapes:
            if feature is baseFeature:
                for faceName in subNameList:
                    faces.append(faceName)

        # For some reason defeaturing dosent accept faces from Shape.Faces list, this is a cheap hack that I used
        dirtyShapes = [getattr(currentShape, f"{f}") for f in faces]
        result: ShapeLike = currentShape.defeaturing(dirtyShapes)


        if obj.CheckShape:
            result.check()

        if len(currentShape.Faces) == len(result.Faces):
            raise RuntimeError("Defeaturing failed, try other combination of faces!")

        obj.Shape = result

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
