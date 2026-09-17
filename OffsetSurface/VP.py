# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from .Proxy import FEATURE_NAME
import FreeCADGui as Gui #type: ignore
import os


class VP:
    iconPath: str = os.path.join(
            os.path.dirname(__file__),
            "..",
            "Assets",
            f"{FEATURE_NAME}_HybridDesign.svg"
        )


    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def setupContextMenu(self, vobj, menu):
        pass
        # call PartDesign command directly
        #action = menu.addAction("Set Tip")
        #action.triggered.connect(lambda: Gui.runCommand("PartDesign_MoveTip"))

    def updateData(self, obj, prop):
        pass

    def getDisplayModes(self, vobj):
        return []

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vobj, prop):
        pass

    def getIcon(self):
        return VP.iconPath

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
