# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
import os

import FreeCADGui as Gui

from ..utils.runFeturelessCommand import runFeaturelessCommand
from .Proxy import FEATURE_NAME, proxyCommand


class Command:
    iconPath: str = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "Resources",
        "Icons",
        f"{FEATURE_NAME}_HybridDesign.svg",
    )

    def GetResources(self):
        return {
            "MenuText": f"{FEATURE_NAME}",
            "ToolTip": f"Create {FEATURE_NAME} object",
            "Pixmap": self.iconPath,
        }

    def Activated(self):
        runFeaturelessCommand(proxyCommand)

    def IsActive(self):
        return True

    @classmethod
    def getCommandName(cls) -> str:
        return FEATURE_NAME


Gui.addCommand(f"{FEATURE_NAME}", Command())
