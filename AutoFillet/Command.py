# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
import FreeCADGui as Gui #type: ignore
from FreeCAD import ActiveDocument #type: ignore
from .Proxy import Proxy
from .VP import VP
from utils.CreatePDFeature import createPDFeature as createFeature


class Command:

    def GetResources(self):
        return {
            "MenuText": f"{Proxy.getFeatureName()}",
            "ToolTip": f"Create {Proxy.getFeatureName()} object",
            "Pixmap" : VP.iconPath
        }

    def Activated(self):
        createFeature(Proxy, VP, selectionReq=False) #type:ignore

    def IsActive(self):
        return True

    @classmethod
    def getCommandName(cls) -> str:
        return Proxy.getFeatureName()


Gui.addCommand(
    f"{Proxy.getFeatureName()}",
    Command()
)
