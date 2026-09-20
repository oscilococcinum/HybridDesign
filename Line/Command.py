# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
import FreeCADGui as Gui  # type: ignore
from FreeCAD import ActiveDocument  # type: ignore

from utils.CreateSurfaceFeature import createSurfaceFeature as createFeature

from .Proxy import Proxy
from .VP import VP


class Command:

    def GetResources(self):
        return {
            "MenuText": f"{Proxy.getFeatureName()}",
            "ToolTip": f"Create {Proxy.getFeatureName()} object",
            "Pixmap": VP.iconPath,
        }

    def Activated(self):
        createFeature(Proxy, VP, selectionReq=True)

    def IsActive(self):
        return True

    @classmethod
    def getCommandName(cls) -> str:
        return Proxy.getFeatureName()


Gui.addCommand(f"{Proxy.getFeatureName()}", Command())
