# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
import FreeCADGui as Gui #type: ignore
from FreeCAD import ActiveDocument #type: ignore
from .Proxy import proxyCommand, FEATURE_NAME
from utils.runFeturelessCommand import runFeaturelessCommand
import os


class Command:
    iconPath: str = os.path.join(
            os.path.dirname(__file__),
            "..",
            "Assets",
            f"{FEATURE_NAME}_HybridDesign.svg"
        )

    def GetResources(self):
        return {
            "MenuText": f"{FEATURE_NAME}",
            "ToolTip": f"Create {FEATURE_NAME} object",
            "Pixmap" : self.iconPath
        }

    def Activated(self):
        runFeaturelessCommand(proxyCommand)

    def IsActive(self):
        return True

    @classmethod
    def getCommandName(cls) -> str:
        return FEATURE_NAME


Gui.addCommand(
    f"{FEATURE_NAME}",
    Command()
)
