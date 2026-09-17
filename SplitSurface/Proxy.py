# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from typing import Protocol
from Part import Compound
from BOPTools.GeneralFuseResult import GeneralFuseResult
from utils.PropDef import PropDef, PropertyLinkSubList, PropertyBool, PropertyInteger
from utils.FreeCADInterfaces import FeatureLike
from utils.utils import getSelectionEx

FEATURE_NAME = "SplitSurface"


class CurrentFeatureLike(FeatureLike, Protocol):
    CheckShape: bool = PropertyBool("Shape", "If true, perform validity check on shape.", True) #type: ignore
    Surface: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Surface that will be splited") #type: ignore
    SplitTool: list[tuple[FeatureLike, tuple[str]]] = PropertyLinkSubList("Input", "Spliting tool eg. surface") #type: ignore
    Result: int = PropertyInteger("Result", "", 1) #type: ignore

class Proxy:
    def __init__(self, obj: CurrentFeatureLike):
        obj.Proxy = self
        self.Type = self.getFeatureName()
        self.add_properties(obj)

    def execute(self, obj: CurrentFeatureLike):
        if not obj.Surface and not obj.SplitTool:
            obj.Surface = [getSelectionEx()[0]]
            obj.SplitTool = [getSelectionEx()[1]]
            obj.Surface[0][0].Visibility = False
            obj.SplitTool[0][0].Visibility = False

        firstSur = obj.Surface[0][0].Shape
        secondSur = obj.SplitTool[0][0].Shape
        listOfShapes = [firstSur, secondSur]

        pieces, map = listOfShapes[0].generalFuse(listOfShapes[1:], 1e-3)
        gr = GeneralFuseResult(listOfShapes, (pieces, map))
        gr.splitAggregates()
        comp = Compound(gr.pieces)
        result = comp.Shells[obj.Result-1]

        if obj.CheckShape:
            result.check()
        obj.Shape = result
        self.setViewObjectAttrs(obj)

    def setViewObjectAttrs(self, obj: CurrentFeatureLike) -> None:
        obj.ViewObject.ShapeColor = (0/255, 177/255, 255/255)
        #obj.ViewObject.LineColor = (255/255, 0/255, 255/255)
        #obj.ViewObject.PointColor = (255/255, 0/255, 255/255)


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
