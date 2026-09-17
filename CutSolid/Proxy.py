# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Protocol
from utils.PropDef import PropDef, PropertyBool, PropertyLinkSubList, PropertyFloat, PropertyInteger
from utils.FreeCADInterfaces import FeatureLike, ShapeLike
from utils.utils import getSelectionEx

FEATURE_NAME = "CutSolid"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    RefShapes: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Input feature eg. Extract") #type: ignore
    ChosenResult: int = PropertyInteger("Shape", "", 1) #type: ignore


class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        #obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.RefShapes:
            obj.RefShapes = getSelectionEx()
            obj.RefShapes[0][0].Visibility = False

        currentShape: ShapeLike = obj.BaseFeature.Shape
        obj.Shape = currentShape

        objsToCutWith = [
            shape
            for ob, subname in obj.RefShapes
            for shape in ([ob.Shape.getElement(sb) for sb in subname] if subname else [ob.Shape])
        ]

        result: ShapeLike = currentShape.generalFuse(objsToCutWith)[0].getChildShapes("Solid")[obj.ChosenResult-1]

        if obj.CheckShape:
            result.check()

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
