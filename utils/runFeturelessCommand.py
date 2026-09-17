# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
import FreeCADGui as Gui #type: ignore
import FreeCAD as App #type: ignore
from collections.abc import Callable


def runFeaturelessCommand(proxyCommand: Callable[..., None], selectionReq: bool = True):
    if not (doc := App.ActiveDocument): raise RuntimeError("No Active document")
    if not (guiDoc := Gui.ActiveDocument): raise RuntimeError("No Active document")
    if not (activeView := guiDoc.ActiveView): raise RuntimeError(f"No Active View, {type(activeView)}")
    if selectionReq and not (sel := Gui.Selection.getSelection()): raise RuntimeError(f"No input feature selected")
    proxyCommand()
    doc.recompute()